# DeployGuard Demo App

![DeployGuard Logo](https://img.shields.io/badge/DeployGuard-Blue%2FGreen%20Demo-blue?style=for-the-badge&logo=docker)
![Python Version](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)

## Purpose

**DeployGuard Demo App** is a lightweight, production-ready demonstration application engineered specifically for DevOps pipelines incorporating **Docker**, **Jenkins CI/CD**, **Amazon ECR**, and **AWS ECS Fargate** with **Blue/Green deployments**.

It demonstrates core SRE & DevOps patterns:
- **Zero-downtime Blue/Green deployments** (traffic routing between `BLUE` and `GREEN` slots).
- **Version visibility and tracking** (prominent UI indicators for LinkedIn / portfolio demos).
- **Automated health check validation** (AWS ECS ALB integration).
- **Rollback simulation** via intentional health endpoint degradation.

---

## Architecture

![Architecture Diagram](./Architecture%20diagaram.png)

---

## Features

- ⚡ **Lightweight & High-Performance**: Built using FastAPI and Uvicorn.
- 🎨 **DevOps SRE Dashboard Aesthetic**: Dark theme with slot indicators and completed pipeline stages.
- 🔄 **Live Status Polling**: Dynamic UI updates without page reloads.
- 🐳 **Single Docker Container**: Packaged in a minimal `python:3.12-slim` container with native Python Docker `HEALTHCHECK`.
- 🧪 **100% Test Coverage**: Complete unit test suite using `pytest`.

---

## Environment Variables

The application dynamically renders deployment details provided via environment variables.

| Environment Variable | Description | Local Default | Production Example |
| :--- | :--- | :--- | :--- |
| `APP_VERSION` | Application semver release tag | `dev` | `v1.0.0` |
| `ENVIRONMENT` | Target deployment environment | `local` | `production` |
| `DEPLOYMENT_SLOT` | Active Blue/Green deployment slot (`BLUE` / `GREEN`) | `LOCAL` | `BLUE` |
| `COMMIT_SHA` | Git commit SHA digest | `unknown` | `a82fc91` |
| `BUILD_NUMBER` | Jenkins build execution ID | `0` | `12` |
| `FORCE_UNHEALTHY` | Simulates failed health check when set to `true` | `false` | `false` |

---

## API Endpoints

| Method | Endpoint | Description | Expected Status |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Renders the HTML SRE Dashboard | `200 OK` |
| `GET` | `/health` | ECS/ALB Health Check endpoint | `200 OK` (or `503` if forced) |
| `GET` | `/version` | Returns application version & deployment slot JSON | `200 OK` |
| `GET` | `/api/info` | Returns complete deployment metadata & operational status | `200 OK` |

---

## Screenshots

### Application Dashboard
![Dashboard](./dashboard%20image.png)

### Jenkins CI/CD Pipeline
![Jenkins Stages](./jenkins%20stages%20.png)

### Trivy Vulnerability Scan
![Trivy Scan Output](./trivy%20scan%20output%20.png)

### Amazon ECR
![ECR Image](./ECR%20image.png)

### AWS Infrastructure & Deployment
**Application Load Balancer:**
![ALB](./alb%20.png)

**Target Groups:**
![Target Groups](./target%20groups.png)

**Blue/Green Deployment Config:**
![Blue Green Deployment Config](./blue%20green%20deployment%20config.png)

**CloudWatch Logs:**
![CloudWatch Logs](./cloudwatch%20logs.png)

---

## Local Development

### 1. Setup Virtual Environment & Dependencies
```bash
cd deployguard-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Application Locally
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open `http://localhost:8000` in your web browser.

---

## Running Tests

Execute the unit test suite using `pytest`:
```bash
pytest -v
```

---

## Running with Docker

### 1. Build Docker Image
```bash
docker build -t deployguard-app:latest .
```

### 2. Run Container as BLUE Slot (v1.0.0)
```bash
docker run -d \
  -p 8000:8000 \
  --name deployguard-blue \
  -e APP_VERSION=v1.0.0 \
  -e ENVIRONMENT=production \
  -e DEPLOYMENT_SLOT=BLUE \
  -e COMMIT_SHA=a82fc91 \
  -e BUILD_NUMBER=12 \
  deployguard-app:latest
```
Access dashboard at `http://localhost:8000`.

### 3. Run Container as GREEN Slot (v2.0.0)
```bash
docker stop deployguard-blue && docker rm deployguard-blue

docker run -d \
  -p 8000:8000 \
  --name deployguard-green \
  -e APP_VERSION=v2.0.0 \
  -e ENVIRONMENT=production \
  -e DEPLOYMENT_SLOT=GREEN \
  -e COMMIT_SHA=f92c184 \
  -e BUILD_NUMBER=13 \
  deployguard-app:latest
```

---

## Simulating an Unhealthy Deployment (Rollback Demonstration)

To demonstrate how AWS ECS / ALB prevents promotion of broken deployments:

```bash
docker stop deployguard-green && docker rm deployguard-green

docker run -d \
  -p 8000:8000 \
  --name deployguard-unhealthy \
  -e APP_VERSION=v2.1.0-broken \
  -e ENVIRONMENT=production \
  -e DEPLOYMENT_SLOT=GREEN \
  -e FORCE_UNHEALTHY=true \
  deployguard-app:latest
```

### Test `/health` Endpoint:
```bash
curl -i http://localhost:8000/health
```
**Response Output:**
```http
HTTP/1.1 503 Service Unavailable
content-type: application/json

{"status":"unhealthy"}
```

In AWS ECS Fargate, this HTTP 503 response causes target group health checks to fail, automatically halting traffic shifting and triggering an automated rollback to the healthy slot!

---

## Clean Up
```bash
docker stop deployguard-unhealthy && docker rm deployguard-unhealthy
```   
