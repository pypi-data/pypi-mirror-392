from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
import respx
from httpx import AsyncClient, NetworkError, Response

from cxr_sdk import (
    CXRClient,
    CXRClientConfig,
    CXRClientError,
    JobStatus,
    PendingResult,
    PollTimeoutError,
)


@pytest_asyncio.fixture
async def client():
    config = CXRClientConfig(
        base_url="https://api.cxr.test/v1",
        client_id="client-123",
        client_secret="secret-xyz",
    )
    async with CXRClient(config) as sdk:
        yield sdk


@pytest_asyncio.fixture
async def dict_client():
    config = CXRClientConfig(
        base_url="https://api.cxr.test/v1",
        client_id="client-123",
        client_secret="secret-xyz",
        return_models=False,
    )
    async with CXRClient(config) as sdk:
        yield sdk


def _mock_token(mock_router: respx.Router) -> None:
    mock_router.post("https://api.cxr.test/v1/auth/token").mock(
        return_value=Response(200, json={"accessToken": "token", "tokenType": "Bearer", "expiresIn": 3600})
    )


@respx.mock
@pytest.mark.asyncio
async def test_submit_claim(client: CXRClient):
    _mock_token(respx.mock)
    respx.post("https://api.cxr.test/v1/claims/submit").mock(
        return_value=Response(202, json={"jobId": "job-1", "status": "queued"})
    )

    payload = {"claimId": "CLM-1"}
    result = await client.submit_claim(payload, idempotency_key="abc")
    assert result.jobId == "job-1"
    request = respx.calls.last.request
    assert request.headers["Idempotency-Key"] == "abc"


@respx.mock
@pytest.mark.asyncio
async def test_get_claim_and_results(client: CXRClient):
    _mock_token(respx.mock)
    respx.get("https://api.cxr.test/v1/claims/job-1").mock(
        return_value=Response(200, json={"jobId": "job-1", "status": "completed"})
    )
    respx.get("https://api.cxr.test/v1/claims/job-1/results").mock(
        return_value=Response(200, json={"jobId": "job-1", "status": "completed", "verdict": "review", "explanation": {}, "financialImpact": {}})
    )

    status_payload = await client.get_claim("job-1")
    assert status_payload.status == JobStatus.completed

    result = await client.get_results("job-1")
    assert result.verdict == "review"


@respx.mock
@pytest.mark.asyncio
async def test_pending_results(client: CXRClient):
    _mock_token(respx.mock)
    respx.get("https://api.cxr.test/v1/claims/job-2/results").mock(
        return_value=Response(202, json={"status": "processing"})
    )

    pending = await client.get_results("job-2")
    assert isinstance(pending, PendingResult)
    assert pending.status == JobStatus.processing


@respx.mock
@pytest.mark.asyncio
async def test_get_benchmarks(client: CXRClient):
    _mock_token(respx.mock)
    respx.get("https://api.cxr.test/v1/benchmarks").mock(
        return_value=Response(200, json={"generatedAt": "2025-11-13T00:00:00Z", "metrics": {"precision": 0.9, "recall": 0.36, "dollarPrecision": 0.87, "dollarRecall": 0.32, "sampleSize": 2000}})
    )

    benchmarks = await client.get_benchmarks()
    assert benchmarks.metrics.precision == 0.9


@respx.mock
@pytest.mark.asyncio
async def test_get_benchmark_history(client: CXRClient):
    _mock_token(respx.mock)
    respx.get("https://api.cxr.test/v1/benchmarks/history").mock(
        return_value=Response(200, json=[{"generatedAt": "2025-11-12T00:00:00Z", "metrics": {"precision": 0.88, "recall": 0.35, "dollarPrecision": 0.9, "dollarRecall": 0.33, "sampleSize": 2100}}])
    )

    history = await client.get_benchmark_history(limit=25)
    assert len(history) == 1
    assert history[0].metrics.precision == 0.88


@respx.mock
@pytest.mark.asyncio
async def test_submit_and_wait_success(client: CXRClient):
    _mock_token(respx.mock)
    respx.get("https://api.cxr.test/v1/claims/job-42/results").mock(
        side_effect=[
            Response(202, json={"status": "processing"}),
            Response(200, json={
                "jobId": "job-42",
                "status": "completed",
                "verdict": "review",
                "explanation": {},
                "financialImpact": {"recovered": 125.0},
            }),
        ]
    )

    result = await client.submit_and_wait("job-42", interval=0.01, timeout=1.0)
    assert result.status == JobStatus.completed
    assert result.financialImpact["recovered"] == 125.0


@respx.mock
@pytest.mark.asyncio
async def test_submit_and_wait_timeout(client: CXRClient):
    _mock_token(respx.mock)
    respx.get("https://api.cxr.test/v1/claims/job-99/results").mock(
        return_value=Response(202, json={"status": "processing"})
    )

    with pytest.raises(PollTimeoutError):
        await client.submit_and_wait("job-99", interval=0.01, timeout=0.05)


@respx.mock
@pytest.mark.asyncio
async def test_get_results_failed(client: CXRClient):
    _mock_token(respx.mock)
    respx.get("https://api.cxr.test/v1/claims/job-77/results").mock(
        return_value=Response(202, json={"status": "failed", "error": {"message": "engine error"}})
    )

    with pytest.raises(CXRClientError):
        await client.get_results("job-77")


@respx.mock
@pytest.mark.asyncio
async def test_return_dict_mode(dict_client: CXRClient):
    _mock_token(respx.mock)
    respx.get("https://api.cxr.test/v1/claims/job-55/results").mock(
        return_value=Response(200, json={
            "jobId": "job-55",
            "status": "completed",
            "verdict": "approve",
            "explanation": {},
            "financialImpact": {},
        })
    )

    result = await dict_client.get_results("job-55")
    assert isinstance(result, dict)
    assert result["verdict"] == "approve"


@respx.mock
@pytest.mark.asyncio
async def test_benchmark_history_dict_mode(dict_client: CXRClient):
    _mock_token(respx.mock)
    respx.get("https://api.cxr.test/v1/benchmarks/history").mock(
        return_value=Response(200, json=[{"generatedAt": "2025-11-11T00:00:00Z", "metrics": {"precision": 0.85, "recall": 0.34, "dollarPrecision": 0.88, "dollarRecall": 0.31, "sampleSize": 1900}}])
    )

    history = await dict_client.get_benchmark_history(limit=10)
    assert isinstance(history, list)
    assert history[0]["metrics"]["precision"] == 0.85


@respx.mock
@pytest.mark.asyncio
async def test_token_renewal_on_expiry(client: CXRClient):
    """Test that token is automatically renewed when expired."""
    _mock_token(respx.mock)
    
    # First token request
    respx.post("https://api.cxr.test/v1/auth/token").mock(
        return_value=Response(200, json={"accessToken": "token-1", "tokenType": "Bearer", "expiresIn": 1})
    )
    respx.get("https://api.cxr.test/v1/claims/job-1").mock(
        return_value=Response(200, json={"jobId": "job-1", "status": "completed"})
    )
    
    # Use token
    await client.get_claim("job-1")
    
    # Wait for token to expire (simulate by setting expiry in past)
    import time
    client._token_expiry = time.time() - 100
    
    # Second token request (renewal)
    respx.post("https://api.cxr.test/v1/auth/token").mock(
        return_value=Response(200, json={"accessToken": "token-2", "tokenType": "Bearer", "expiresIn": 3600})
    )
    
    # Should trigger token renewal
    await client.get_claim("job-1")
    
    # Verify token was renewed
    assert client._token == "token-2"


@respx.mock
@pytest.mark.asyncio
async def test_token_renewal_before_expiry(client: CXRClient):
    """Test that token is renewed 30 seconds before expiry."""
    _mock_token(respx.mock)
    
    # Set token to expire in 20 seconds (within 30s threshold)
    import time
    client._token = "old-token"
    client._token_expiry = time.time() + 20
    
    respx.post("https://api.cxr.test/v1/auth/token").mock(
        return_value=Response(200, json={"accessToken": "new-token", "tokenType": "Bearer", "expiresIn": 3600})
    )
    respx.get("https://api.cxr.test/v1/claims/job-1").mock(
        return_value=Response(200, json={"jobId": "job-1", "status": "completed"})
    )
    
    await client.get_claim("job-1")
    
    # Should have renewed token
    assert client._token == "new-token"


@respx.mock
@pytest.mark.asyncio
async def test_authentication_error_handling(client: CXRClient):
    """Test handling of authentication failures."""
    respx.post("https://api.cxr.test/v1/auth/token").mock(
        return_value=Response(401, json={"error": "Invalid credentials"})
    )
    
    with pytest.raises(CXRClientError, match="Unable to obtain access token"):
        await client.get_claim("job-1")


@respx.mock
@pytest.mark.asyncio
async def test_http_error_handling(client: CXRClient):
    """Test handling of HTTP errors in API calls."""
    _mock_token(respx.mock)
    respx.get("https://api.cxr.test/v1/claims/job-1").mock(
        return_value=Response(500, json={"error": "Internal server error"})
    )
    
    with pytest.raises(CXRClientError, match="claim status request failed"):
        await client.get_claim("job-1")


@respx.mock
@pytest.mark.asyncio
async def test_network_error_handling(client: CXRClient):
    """Test handling of network errors."""
    _mock_token(respx.mock)
    respx.get("https://api.cxr.test/v1/claims/job-1").mock(side_effect=NetworkError("Connection failed"))
    
    with pytest.raises(CXRClientError, match="claim status request failed"):
        await client.get_claim("job-1")


@respx.mock
@pytest.mark.asyncio
async def test_bulk_submit_claims(client: CXRClient):
    """Test bulk submission of multiple claims."""
    _mock_token(respx.mock)
    
    # Mock multiple submissions
    respx.post("https://api.cxr.test/v1/claims/submit").mock(
        side_effect=[
            Response(202, json={"jobId": "job-1", "status": "queued"}),
            Response(202, json={"jobId": "job-2", "status": "queued"}),
            Response(202, json={"jobId": "job-3", "status": "queued"}),
        ]
    )
    
    claims = [
        {"claimId": "CLM-1"},
        {"claimId": "CLM-2"},
        {"claimId": "CLM-3"},
    ]
    
    # Submit all claims concurrently
    results = await asyncio.gather(*[client.submit_claim(claim) for claim in claims])
    
    assert len(results) == 3
    assert results[0].jobId == "job-1"
    assert results[1].jobId == "job-2"
    assert results[2].jobId == "job-3"


@respx.mock
@pytest.mark.asyncio
async def test_bulk_submit_and_wait(client: CXRClient):
    """Test bulk submission with waiting for results."""
    _mock_token(respx.mock)
    
    # Mock submissions
    respx.post("https://api.cxr.test/v1/claims/submit").mock(
        side_effect=[
            Response(202, json={"jobId": "job-1", "status": "queued"}),
            Response(202, json={"jobId": "job-2", "status": "queued"}),
        ]
    )
    
    # Mock results polling
    respx.get("https://api.cxr.test/v1/claims/job-1/results").mock(
        side_effect=[
            Response(202, json={"status": "processing"}),
            Response(200, json={
                "jobId": "job-1",
                "status": "completed",
                "verdict": "review",
                "explanation": {},
                "financialImpact": {},
            }),
        ]
    )
    respx.get("https://api.cxr.test/v1/claims/job-2/results").mock(
        side_effect=[
            Response(202, json={"status": "processing"}),
            Response(200, json={
                "jobId": "job-2",
                "status": "completed",
                "verdict": "approve",
                "explanation": {},
                "financialImpact": {},
            }),
        ]
    )
    
    claims = [{"claimId": "CLM-1"}, {"claimId": "CLM-2"}]
    
    # Submit and wait for all
    submissions = await asyncio.gather(*[client.submit_claim(claim) for claim in claims])
    results = await asyncio.gather(*[
        client.submit_and_wait(sub.jobId, interval=0.01, timeout=1.0) 
        for sub in submissions
    ])
    
    assert len(results) == 2
    assert results[0].verdict == "review"
    assert results[1].verdict == "approve"


@respx.mock
@pytest.mark.asyncio
async def test_bulk_submit_with_partial_failures(client: CXRClient):
    """Test bulk submission handling partial failures."""
    _mock_token(respx.mock)
    
    respx.post("https://api.cxr.test/v1/claims/submit").mock(
        side_effect=[
            Response(202, json={"jobId": "job-1", "status": "queued"}),
            Response(400, json={"error": "Invalid claim"}),
            Response(202, json={"jobId": "job-3", "status": "queued"}),
        ]
    )
    
    claims = [
        {"claimId": "CLM-1"},
        {"claimId": "CLM-INVALID"},
        {"claimId": "CLM-3"},
    ]
    
    # Submit with error handling
    results = []
    errors = []
    for claim in claims:
        try:
            result = await client.submit_claim(claim)
            results.append(result)
        except CXRClientError as e:
            errors.append(e)
    
    assert len(results) == 2
    assert len(errors) == 1
    assert "claim submission failed" in str(errors[0])


@respx.mock
@pytest.mark.asyncio
async def test_tenant_header_inclusion(client: CXRClient):
    """Test that tenant header is included when configured."""
    config = CXRClientConfig(
        base_url="https://api.cxr.test/v1",
        client_id="client-123",
        client_secret="secret-xyz",
        tenant="tenant-abc",
    )
    async with CXRClient(config) as tenant_client:
        _mock_token(respx.mock)
        respx.post("https://api.cxr.test/v1/claims/submit").mock(
            return_value=Response(202, json={"jobId": "job-1", "status": "queued"})
        )
        
        await tenant_client.submit_claim({"claimId": "CLM-1"})
        request = respx.calls.last.request
        assert request.headers["X-CXR-Tenant-ID"] == "tenant-abc"


@respx.mock
@pytest.mark.asyncio
async def test_idempotency_key_reuse(client: CXRClient):
    """Test that same idempotency key returns same job."""
    _mock_token(respx.mock)
    respx.post("https://api.cxr.test/v1/claims/submit").mock(
        return_value=Response(202, json={"jobId": "job-1", "status": "queued"})
    )
    
    claim = {"claimId": "CLM-1"}
    key = "idempotent-key-123"
    
    result1 = await client.submit_claim(claim, idempotency_key=key)
    result2 = await client.submit_claim(claim, idempotency_key=key)
    
    assert result1.jobId == result2.jobId


@respx.mock
@pytest.mark.asyncio
async def test_submit_claims_bulk(client: CXRClient):
    """Test bulk submission helper method."""
    _mock_token(respx.mock)
    
    respx.post("https://api.cxr.test/v1/claims/submit").mock(
        side_effect=[
            Response(202, json={"jobId": f"job-{i}", "status": "queued"})
            for i in range(1, 6)
        ]
    )
    
    claims = [{"claimId": f"CLM-{i}"} for i in range(1, 6)]
    results = await client.submit_claims_bulk(claims, max_concurrent=3)
    
    assert len(results) == 5
    assert all(r.jobId.startswith("job-") for r in results)


@respx.mock
@pytest.mark.asyncio
async def test_submit_and_wait_bulk(client: CXRClient):
    """Test bulk wait helper method."""
    _mock_token(respx.mock)
    
    job_ids = ["job-1", "job-2", "job-3"]
    
    for job_id in job_ids:
        respx.get(f"https://api.cxr.test/v1/claims/{job_id}/results").mock(
            side_effect=[
                Response(202, json={"status": "processing"}),
                Response(200, json={
                    "jobId": job_id,
                    "status": "completed",
                    "verdict": "review",
                    "explanation": {},
                    "financialImpact": {},
                }),
            ]
        )
    
    results = await client.submit_and_wait_bulk(job_ids, interval=0.01, timeout=1.0)
    
    assert len(results) == 3
    assert all(r.status == JobStatus.completed for r in results)
