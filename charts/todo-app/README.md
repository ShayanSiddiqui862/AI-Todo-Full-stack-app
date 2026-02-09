# Todo Application Helm Chart

This Helm chart deploys the Todo full-stack application to Kubernetes.

## Chart Details

- **Name**: todo-app
- **Version**: 0.4.0
- **AppVersion**: 1.0.0

## Introduction

This chart deploys a full-stack Todo application consisting of:
- Frontend service (Next.js)
- Backend service (FastAPI)
- Chatbot service (OpenAI integration)

## Prerequisites

- Kubernetes 1.19+
- Helm 3.10+
- PV provisioner support in the underlying infrastructure (if persistence is required)

## Installing the Chart

To install the chart with the release name `my-release`:

```bash
helm install my-release . \
  --namespace todo-ns \
  --set frontend.image.tag=v1.0.0 \
  --set backend.image.tag=v1.0.0 \
  --set chatbot.image.tag=v1.0.0 \
  --set secrets.databaseUrl=<your-database-url> \
  --set secrets.openAiKey=<your-openai-key> \
  --set secrets.jwtSecret=<your-jwt-secret> \
  --set secrets.accessTokenExpireMinutes=<access-token-expire-minutes> \
  --set secrets.refreshTokenExpireDays=<refresh-token-expire-days> \
  --set secrets.googleRedirectUri=<google-redirect-uri>
```

## Uninstalling the Chart

To uninstall/delete the `my-release` deployment:

```bash
helm delete my-release -n todo-ns
```

## Configuration

The following table lists the configurable parameters of the todo-app chart and their default values.

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of pod replicas | `2` |

### Frontend Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.image.repository` | Frontend image repository | `todo-frontend` |
| `frontend.image.tag` | Frontend image tag | `latest` |
| `frontend.image.pullPolicy` | Frontend image pull policy | `IfNotPresent` |
| `frontend.port` | Frontend service port | `3000` |
| `frontend.resources.limits.cpu` | Frontend CPU limit | `200m` |
| `frontend.resources.limits.memory` | Frontend memory limit | `256Mi` |
| `frontend.resources.requests.cpu` | Frontend CPU request | `100m` |
| `frontend.resources.requests.memory` | Frontend memory request | `128Mi` |

### Backend Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backend.image.repository` | Backend image repository | `todo-backend` |
| `backend.image.tag` | Backend image tag | `latest` |
| `backend.image.pullPolicy` | Backend image pull policy | `IfNotPresent` |
| `backend.port` | Backend service port | `8000` |
| `backend.dbUrl` | Database connection URL | `""` |
| `backend.resources.limits.cpu` | Backend CPU limit | `200m` |
| `backend.resources.limits.memory` | Backend memory limit | `256Mi` |
| `backend.resources.requests.cpu` | Backend CPU request | `100m` |
| `backend.resources.requests.memory` | Backend memory request | `128Mi` |

### Chatbot Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `chatbot.enabled` | Enable the chatbot service | `true` |
| `chatbot.image.repository` | Chatbot image repository | `todo-chatbot` |
| `chatbot.image.tag` | Chatbot image tag | `latest` |
| `chatbot.image.pullPolicy` | Chatbot image pull policy | `IfNotPresent` |
| `chatbot.port` | Chatbot service port | `8001` |
| `chatbot.resources.limits.cpu` | Chatbot CPU limit | `200m` |
| `chatbot.resources.limits.memory` | Chatbot memory limit | `256Mi` |
| `chatbot.resources.requests.cpu` | Chatbot CPU request | `100m` |
| `chatbot.resources.requests.memory` | Chatbot memory request | `128Mi` |

### Ingress Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class name | `""` |
| `ingress.hosts[0].host` | Ingress host | `todo.local` |
| `ingress.hosts[0].paths[0].path` | Root path mapping | `/` |
| `ingress.hosts[0].paths[0].pathType` | Root path type | `Prefix` |
| `ingress.hosts[0].paths[1].path` | API path mapping | `/api` |
| `ingress.hosts[0].paths[1].pathType` | API path type | `Prefix` |
| `ingress.hosts[0].paths[2].path` | Chat path mapping | `/chat` |
| `ingress.hosts[0].paths[2].pathType` | Chat path type | `Prefix` |

### Secrets Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `secrets.databaseUrl` | Database URL (base64 encoded) | `""` |
| `secrets.geminiApiKey` | Gemini API key (base64 encoded) | `""` |
| `secrets.jwtSecret` | JWT secret (base64 encoded) | `""` |
| `secrets.betterAuthSecret` | Better Auth secret (base64 encoded) | `""` |
| `secrets.googleClientId` | Google OAuth client ID (base64 encoded) | `""` |
| `secrets.googleClientSecret` | Google OAuth client secret (base64 encoded) | `""` |
| `secrets.accessTokenExpireMinutes` | Access token expiration in minutes (base64 encoded) | `""` |
| `secrets.refreshTokenExpireDays` | Refresh token expiration in days (base64 encoded) | `""` |
| `secrets.googleRedirectUri` | Google OAuth redirect URI (base64 encoded) | `""` |

## Example Usage

Here's an example of how to customize the deployment:

```yaml
# custom-values.yaml
replicaCount: 3

frontend:
  image:
    tag: v1.2.0
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 200m
      memory: 256Mi

backend:
  image:
    tag: v1.2.0
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 200m
      memory: 256Mi

ingress:
  hosts:
    - host: my-todo-app.example.com
      paths:
        - path: /
          pathType: Prefix
        - path: /api
          pathType: Prefix
        - path: /chat
          pathType: Prefix

secrets:
  databaseUrl: <base64-encoded-database-url>
  geminiApiKey: <base64-encoded-gemini-api-key>
  jwtSecret: <base64-encoded-jwt-secret>
  accessTokenExpireMinutes: <base64-encoded-access-token-expire-minutes>
  refreshTokenExpireDays: <base64-encoded-refresh-token-expire-days>
  googleRedirectUri: <base64-encoded-google-redirect-uri>
```

Then install with:

```bash
helm install my-release . -f custom-values.yaml
```

## Architecture

The chart deploys the following components:

- Deployments for frontend, backend, and chatbot services
- Services to expose the deployments internally
- Ingress to route external traffic to the appropriate services
- Secrets to store sensitive information
- Horizontal Pod Autoscalers for automatic scaling based on CPU usage

## Scaling

The chart includes Horizontal Pod Autoscalers (HPA) for each service. By default, pods will scale up when CPU usage exceeds 70% and scale down when it drops below 30%.

## Troubleshooting

If the application is not accessible:

1. Check if all pods are running:
   ```bash
   kubectl get pods -n todo-ns
   ```

2. Check if services are properly exposed:
   ```bash
   kubectl get services -n todo-ns
   ```

3. Check if ingress is configured correctly:
   ```bash
   kubectl get ingress -n todo-ns
   ```

4. Check pod logs for errors:
   ```bash
   kubectl logs -l app=backend -n todo-ns
   ```