# sqs-to-s3-worker

A lightweight Python worker that consumes messages from an AWS SQS queue and persists each message as a timestamped `.txt` file in S3. Designed to run as a short-lived Kubernetes Job triggered by KEDA on Spot instances provisioned by Karpenter.

## Features

- Polls SQS with long-polling (5 s wait), processes exactly one message per run, then exits
- Writes message body to S3 with a `YYYY-MM-DD-HH-MM-SS.txt` key
- Authenticates to AWS exclusively via IRSA (IAM Roles for Service Accounts) — no static credentials
- Containerised with a minimal Python 3.12 slim image
- Linted with `ruff` and unit-tested with `pytest`
- CI/CD via GitHub Actions: lint → test → build → Trivy scan → push to ECR → GitOps update

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.12 |
| AWS SDK | boto3 |
| Lint | ruff |
| Test | pytest |
| Container | Docker (python:3.12-slim) |
| CI/CD | GitHub Actions |
| Registry | Amazon ECR |

## Getting Started

### Prerequisites

- Python 3.12
- AWS credentials with SQS and S3 permissions (for local runs)
- Docker (for building the image)

### Installation

```bash
git clone https://github.com/MrJoRnO/sqs-to-s3-worker.git
cd sqs-to-s3-worker

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Usage

```bash
export SQS_QUEUE_URL="https://sqs.eu-central-1.amazonaws.com/<account-id>/<queue-name>"
export S3_BUCKET_NAME="sqs-job-test"

python -m src.main
```

### Running Tests

```bash
pytest tests/ -v
```

### Lint

```bash
ruff check src/ tests/
```

### Building the Docker Image

```bash
docker build \
  --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
  --build-arg GIT_SHA="$(git rev-parse HEAD)" \
  -t sqs-to-s3-worker:local .
```

## CI/CD

| Workflow | Trigger | What it does |
|---|---|---|
| `CI — Lint & Test` | Push to any branch, PR to `dev`/`main` | Runs ruff + pytest |
| `CD — Build, Scan & GitOps Update` | CI passes on `dev` or `main` | Builds image, scans with Trivy (CRITICAL), pushes to ECR, updates image tag in the config repo |

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `AWS_CI_ROLE_ARN` | IAM role ARN for GitHub Actions OIDC (keyless auth) |
| `GHA_PAT` | Personal Access Token with `repo` scope for pushing to the config repo |

## Project Structure

```
.
├── src/
│   └── main.py              # Worker entrypoint
├── tests/
│   └── test_main.py         # Unit tests with mocked AWS clients
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
└── .github/workflows/
    ├── ci.yml
    └── cd.yml
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Commit your changes and open a pull request targeting `dev`
4. CI must pass before merge
