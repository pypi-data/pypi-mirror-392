from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import httpx
from pydantic import BaseModel, Field, ValidationError, ConfigDict

__all__ = [
    "CXRClient",
    "CXRClientConfig",
    "CXRClientError",
    "PollTimeoutError",
    "JobStatus",
    "JobSubmissionResponse",
    "JobStatusResponse",
    "PendingResult",
    "ClaimResultResponse",
    "BenchmarkSnapshot",
]


class CXRClientError(RuntimeError):
    """SDK-level error wrapper."""


class PollTimeoutError(CXRClientError):
    """Raised when submit_and_wait exceeds the provided timeout."""


class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"


@dataclass(slots=True)
class CXRClientConfig:
    base_url: str
    client_id: str
    client_secret: str
    timeout: float = 10.0
    tenant: Optional[str] = None
    return_models: bool = True


class TokenResponse(BaseModel):
    accessToken: str = Field(..., alias="accessToken")
    tokenType: str = Field(..., alias="tokenType")
    expiresIn: int = Field(..., alias="expiresIn")


class JobSubmissionResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    jobId: str
    status: JobStatus


class JobStatusResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True, extra="allow")

    jobId: str
    status: JobStatus
    submittedAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    progress: Optional[float] = 0.0
    failure: Optional[Dict[str, Any]] = None


class PendingResult(BaseModel):
    model_config = ConfigDict(use_enum_values=True, extra="allow")

    status: JobStatus = JobStatus.processing
    detail: Optional[Dict[str, Any]] = None

    def ready(self) -> bool:
        return False


class ClaimResultResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True, extra="allow")

    jobId: str
    status: JobStatus
    verdict: str
    explanation: Dict[str, Any]
    financialImpact: Optional[Dict[str, Any]] = None
    reportId: Optional[str] = None


class BenchmarkMetrics(BaseModel):
    precision: float
    recall: float
    dollarPrecision: float
    dollarRecall: float
    sampleSize: int


class BenchmarkSnapshot(BaseModel):
    generatedAt: datetime
    metrics: BenchmarkMetrics


class CXRClient:
    def __init__(self, config: CXRClientConfig, *, transport: Optional[httpx.AsyncBaseTransport] = None) -> None:
        self._config = config
        self._token: Optional[str] = None
        self._token_expiry: float = 0
        self._client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            transport=transport,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def _ensure_token(self) -> str:
        now = time.time()
        if self._token and now < self._token_expiry - 30:
            return self._token

        try:
            response = await self._client.post(
                "/auth/token",
                json={"clientId": self._config.client_id, "clientSecret": self._config.client_secret},
            )
            response.raise_for_status()
            token_payload = TokenResponse.model_validate(response.json())
        except (httpx.HTTPError, ValidationError) as exc:
            raise CXRClientError(f"Unable to obtain access token: {exc}") from exc

        self._token = token_payload.accessToken
        self._token_expiry = now + token_payload.expiresIn
        return self._token

    async def _auth_headers(self, *, idempotency_key: Optional[str] = None) -> Dict[str, str]:
        token = await self._ensure_token()
        headers = {"Authorization": f"Bearer {token}"}
        if self._config.tenant:
            headers["X-CXR-Tenant-ID"] = self._config.tenant
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    def _maybe_return(self, payload: BaseModel | PendingResult) -> Union[BaseModel, Dict[str, Any]]:
        if self._config.return_models:
            return payload
        return payload.model_dump(mode="json")

    @staticmethod
    def _coerce_status(value: Optional[str]) -> JobStatus:
        if not value:
            return JobStatus.processing
        try:
            return JobStatus(value)
        except ValueError:
            return JobStatus.processing

    async def submit_claim(
        self,
        claim_payload: Dict[str, Any],
        *,
        idempotency_key: Optional[str] = None,
    ) -> Union[JobSubmissionResponse, Dict[str, Any]]:
        headers = await self._auth_headers(idempotency_key=idempotency_key)
        payload = {"claim": claim_payload}
        try:
            response = await self._client.post("/claims/submit", json=payload, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise CXRClientError(f"claim submission failed: {exc}") from exc

        submission = JobSubmissionResponse.model_validate(response.json())
        return self._maybe_return(submission)

    async def get_claim(self, job_id: str) -> Union[JobStatusResponse, Dict[str, Any]]:
        headers = await self._auth_headers()
        try:
            response = await self._client.get(f"/claims/{job_id}", headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise CXRClientError(f"claim status request failed: {exc}") from exc

        status_payload = JobStatusResponse.model_validate(response.json())
        return self._maybe_return(status_payload)

    async def _get_results_internal(self, job_id: str) -> Union[ClaimResultResponse, PendingResult]:
        headers = await self._auth_headers()
        try:
            response = await self._client.get(f"/claims/{job_id}/results", headers=headers)
            if response.status_code == 202:
                payload = response.json() if response.content else {}
                status = self._coerce_status(payload.get("status"))
                if status is JobStatus.failed:
                    raise CXRClientError(f"claim {job_id} failed: {payload.get('error') or payload}")
                pending = PendingResult(status=status, detail=payload if payload else None)
                return pending
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise CXRClientError(f"claim results request failed: {exc}") from exc
        except httpx.HTTPError as exc:
            raise CXRClientError(f"claim results request failed: {exc}") from exc

        result_payload = ClaimResultResponse.model_validate(response.json())
        return result_payload

    async def get_results(self, job_id: str) -> Union[ClaimResultResponse, PendingResult, Dict[str, Any]]:
        payload = await self._get_results_internal(job_id)
        return self._maybe_return(payload)

    async def submit_and_wait(
        self,
        job_id: str,
        *,
        interval: float = 1.0,
        timeout: float = 60.0,
    ) -> Union[ClaimResultResponse, Dict[str, Any]]:
        deadline = time.monotonic() + timeout
        while True:
            payload = await self._get_results_internal(job_id)
            if isinstance(payload, ClaimResultResponse):
                return self._maybe_return(payload)
            if time.monotonic() >= deadline:
                raise PollTimeoutError(f"Timed out waiting for job {job_id}")
            await asyncio.sleep(interval)

    async def get_benchmarks(self) -> Union[BenchmarkSnapshot, Dict[str, Any]]:
        headers = await self._auth_headers()
        try:
            response = await self._client.get("/benchmarks", headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise CXRClientError(f"benchmark request failed: {exc}") from exc

        snapshot = BenchmarkSnapshot.model_validate(response.json())
        return self._maybe_return(snapshot)

    async def get_benchmark_history(self, *, limit: Optional[int] = None) -> Union[List[BenchmarkSnapshot], List[Dict[str, Any]]]:
        headers = await self._auth_headers()
        params = {"limit": limit} if limit is not None else None
        try:
            response = await self._client.get("/benchmarks/history", headers=headers, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise CXRClientError(f"benchmark history request failed: {exc}") from exc

        history = [BenchmarkSnapshot.model_validate(item) for item in response.json()]
        if self._config.return_models:
            return history
        return [snapshot.model_dump(mode="json") for snapshot in history]

    async def __aenter__(self) -> "CXRClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    def submit_claim_sync(
        self, claim_payload: Dict[str, Any], *, idempotency_key: Optional[str] = None
    ) -> Union[JobSubmissionResponse, Dict[str, Any]]:
        return asyncio.run(self.submit_claim(claim_payload, idempotency_key=idempotency_key))

    def get_claim_sync(self, job_id: str) -> Union[JobStatusResponse, Dict[str, Any]]:
        return asyncio.run(self.get_claim(job_id))

    def get_results_sync(self, job_id: str) -> Union[ClaimResultResponse, PendingResult, Dict[str, Any]]:
        return asyncio.run(self.get_results(job_id))

    def submit_and_wait_sync(
        self, job_id: str, *, interval: float = 1.0, timeout: float = 60.0
    ) -> Union[ClaimResultResponse, Dict[str, Any]]:
        return asyncio.run(self.submit_and_wait(job_id, interval=interval, timeout=timeout))

    def get_benchmarks_sync(self) -> Union[BenchmarkSnapshot, Dict[str, Any]]:
        return asyncio.run(self.get_benchmarks())

    def get_benchmark_history_sync(self, *, limit: Optional[int] = None) -> Union[List[BenchmarkSnapshot], List[Dict[str, Any]]]:
        return asyncio.run(self.get_benchmark_history(limit=limit))

    async def submit_claims_bulk(
        self,
        claims: List[Dict[str, Any]],
        *,
        max_concurrent: int = 10,
        idempotency_key_fn: Optional[Callable[[int, Dict[str, Any]], str]] = None,
    ) -> List[Union[JobSubmissionResponse, Dict[str, Any]]]:
        """
        Submit multiple claims concurrently with rate limiting.
        
        Args:
            claims: List of claim payloads to submit
            max_concurrent: Maximum number of concurrent submissions
            idempotency_key_fn: Optional function to generate idempotency keys: (index, claim) -> str
        
        Returns:
            List of submission responses in the same order as input claims
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def submit_with_semaphore(claim: Dict[str, Any], index: int) -> Union[JobSubmissionResponse, Dict[str, Any]]:
            async with semaphore:
                idempotency_key = idempotency_key_fn(index, claim) if idempotency_key_fn else None
                return await self.submit_claim(claim, idempotency_key=idempotency_key)
        
        return await asyncio.gather(*[submit_with_semaphore(claim, idx) for idx, claim in enumerate(claims)])

    async def submit_and_wait_bulk(
        self,
        job_ids: List[str],
        *,
        interval: float = 1.0,
        timeout: float = 60.0,
        max_concurrent: int = 10,
    ) -> List[Union[ClaimResultResponse, Dict[str, Any]]]:
        """
        Wait for multiple jobs to complete concurrently.
        
        Args:
            job_ids: List of job IDs to wait for
            interval: Polling interval in seconds
            timeout: Maximum time to wait per job
            max_concurrent: Maximum number of concurrent polling operations
        
        Returns:
            List of result responses in the same order as input job_ids
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def wait_with_semaphore(job_id: str) -> Union[ClaimResultResponse, Dict[str, Any]]:
            async with semaphore:
                return await self.submit_and_wait(job_id, interval=interval, timeout=timeout)
        
        return await asyncio.gather(*[wait_with_semaphore(job_id) for job_id in job_ids])
