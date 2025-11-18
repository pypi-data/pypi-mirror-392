from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from .client import (
    CXRClient,
    CXRClientConfig,
    CXRClientError,
    JobStatus,
    PollTimeoutError,
)

_SAMPLE_PAYLOAD: Dict[str, Any] = {
    "claimId": "CLM-QUICKSTART",
    "metadata": {"reviewThreshold": 0.8},
    "lines": [
        {"procedureCode": "99213", "billedAmount": 120.0, "paidAmount": 80.0},
        {"procedureCode": "93000", "billedAmount": 85.0, "paidAmount": 50.0},
    ],
}


def _load_payload(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return _SAMPLE_PAYLOAD
    data = Path(path).read_text()
    return json.loads(data)


def _infer(value: Optional[str], env_key: str) -> str:
    if value:
        return value
    env_value = os.getenv(env_key)
    if env_value:
        return env_value
    raise SystemExit(f"Missing required value for {env_key} (pass as argument or export environment variable)")


async def _run_quickstart(args: argparse.Namespace) -> None:
    base_url = _infer(args.base_url, "CXR_BASE_URL")
    client_id = _infer(args.client_id, "CXR_CLIENT_ID")
    client_secret = _infer(args.client_secret, "CXR_CLIENT_SECRET")
    tenant = args.tenant or os.getenv("CXR_TENANT_ID")

    config = CXRClientConfig(
        base_url=base_url,
        client_id=client_id,
        client_secret=client_secret,
        tenant=tenant,
        return_models=True,
    )

    payload = _load_payload(args.payload)

    async with CXRClient(config) as client:
        submission = await client.submit_claim(payload, idempotency_key=args.idempotency_key)
        job_id = submission.jobId
        print(f"Submitted job {job_id} with status {submission.status}")

        try:
            result = await client.submit_and_wait(job_id, interval=args.interval, timeout=args.timeout)
        except PollTimeoutError as exc:
            raise SystemExit(str(exc)) from exc

        if result.status is JobStatus.completed:
            print(f"Job {job_id} completed with verdict: {result.verdict}")
        else:
            print(f"Job {job_id} returned status {result.status}")
        if result.financialImpact:
            print("Financial impact:", json.dumps(result.financialImpact, indent=2))
        if args.print_explanation and result.explanation:
            print("Explanation:", json.dumps(result.explanation, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CXR SDK helper CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    quick = subparsers.add_parser("quickstart", help="Submit a sample claim and wait for results")
    quick.add_argument("--base-url", help="Gateway base URL (defaults to $CXR_BASE_URL)")
    quick.add_argument("--client-id", help="Client identifier (defaults to $CXR_CLIENT_ID)")
    quick.add_argument("--client-secret", help="Client secret (defaults to $CXR_CLIENT_SECRET)")
    quick.add_argument("--tenant", help="Tenant identifier (defaults to $CXR_TENANT_ID)")
    quick.add_argument("--payload", help="Path to custom claim payload JSON")
    quick.add_argument("--idempotency-key", help="Optional idempotency key to attach")
    quick.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds")
    quick.add_argument("--timeout", type=float, default=60.0, help="Timeout in seconds")
    quick.add_argument(
        "--print-explanation",
        action="store_true",
        help="Include the full explanation payload in stdout",
    )

    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "quickstart":
        try:
            asyncio.run(_run_quickstart(args))
        except CXRClientError as exc:
            raise SystemExit(f"SDK error: {exc}") from exc
    else:
        parser.print_help()
        raise SystemExit(1)


if __name__ == "__main__":
    main()
