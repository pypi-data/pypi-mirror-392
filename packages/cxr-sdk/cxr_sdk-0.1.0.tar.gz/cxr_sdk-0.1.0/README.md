# CXR SDK

Official Python SDK for the CXR SaaS API - Claim Reasoning Engine.

## Installation

```bash
pip install cxr-sdk
```

## Quick Start

```python
import asyncio
from cxr_sdk import CXRClient, CXRClientConfig

async def main():
    config = CXRClientConfig(
        base_url="https://api.cxr.cloud/v1",
        client_id="your-client-id",
        client_secret="your-client-secret",
    )
    
    async with CXRClient(config) as client:
        # Submit a claim
        submission = await client.submit_claim({
            "claimId": "CLM-001",
            "lines": [
                {"procedureCode": "99213", "billedAmount": 120.0, "paidAmount": 80.0}
            ]
        })
        
        # Wait for results
        result = await client.submit_and_wait(submission.jobId)
        print(f"Verdict: {result.verdict}")

asyncio.run(main())
```

## Features

- **Automatic Token Renewal**: Tokens are automatically refreshed before expiry
- **Bulk Operations**: Submit and process multiple claims concurrently
- **Error Handling**: Comprehensive error handling with retry patterns
- **Type Safety**: Full type hints and Pydantic models
- **Async/Await**: Built on async/await for high performance

## Examples

See the `examples/` directory for:
- `basic_quickstart.py` - Basic claim submission workflow
- `bulk_submission.py` - Bulk claim processing
- `error_handling.py` - Error handling patterns
- `benchmark_analysis.py` - Benchmark metrics analysis
- `sdk_demo.ipynb` - Interactive Jupyter notebook

## API Reference

### CXRClient

Main client class for interacting with the CXR API.

#### Methods

- `submit_claim(claim_payload, *, idempotency_key=None)` - Submit a single claim
- `submit_claims_bulk(claims, *, max_concurrent=10)` - Submit multiple claims concurrently
- `get_claim(job_id)` - Get job status
- `get_results(job_id)` - Get claim results
- `submit_and_wait(job_id, *, interval=1.0, timeout=60.0)` - Submit and wait for results
- `submit_and_wait_bulk(job_ids, *, interval=1.0, timeout=60.0, max_concurrent=10)` - Wait for multiple jobs
- `get_benchmarks()` - Get current benchmark metrics
- `get_benchmark_history(*, limit=None)` - Get benchmark history

## Requirements

- Python >= 3.10
- httpx >= 0.28
- pydantic >= 2.5

## License

Proprietary - CXR Labs

