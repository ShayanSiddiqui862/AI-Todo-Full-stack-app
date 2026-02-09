# Kubernetes Deployment Guide for FocusFlow Todo Application

This guide provides step-by-step instructions to deploy the FocusFlow Todo application to a local Kubernetes cluster using Minikube, Helm, and other tools.

## Prerequisites

Before starting the deployment, ensure you have the following tools installed:

- Docker (v20.10+)
- Minikube (v1.30+)
- kubectl (v1.25+)
- Helm (v3.10+)
- Git

## Step 1: Clone the Repository

```cmd
git clone https://github.com/your-username/Todo-Full-stack.git
cd Todo-Full-stack
```

## Step 2: Start Minikube Cluster

Start Minikube with the recommended resources for this application:

```cmd
# Start Minikube with 4 CPUs and 8GB memory
minikube start --driver=docker --cpus=4 --memory=4096mb

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify cluster status
kubectl cluster-info
kubectl get nodes
```

## Step 3: Build Docker Images

Build the Docker images for the frontend and backend services:

```cmd
# Build backend image
cd backend
docker build -t todo-backend:latest .
cd ..

# Build frontend image
cd frontend
docker build -t todo-frontend:latest .
cd ..

# If you have a chatbot service, build it as well
# docker build -t todo-chatbot:latest . -f chatbot/Dockerfile
```

## Step 4: Load Images into Minikube

Load the built images into the Minikube cluster:

```cmd
# Load backend image
minikube image load todo-backend:latest

# Load frontend image
minikube image load todo-frontend:latest

# If you have a chatbot service
# minikube image load todo-chatbot:latest
```

## Step 5: Prepare Secrets

Prepare your secrets file with the required environment variables:

For Windows Command Prompt:

```cmd
# Create a secrets.env file with your environment variables
echo DATABASE_URL=your_database_connection_string > secrets.env
echo GEMINI_API_KEY=your_gemini_api_key >> secrets.env
echo JWT_SECRET=your_jwt_secret >> secrets.env
echo BETTER_AUTH_SECRET=your_better_auth_secret >> secrets.env
echo GOOGLE_CLIENT_ID=your_google_client_id >> secrets.env
echo GOOGLE_CLIENT_SECRET=your_google_client_secret >> secrets.env
echo ACCESS_TOKEN_EXPIRE_MINUTES=1440 >> secrets.env
echo REFRESH_TOKEN_EXPIRE_DAYS=7 >> secrets.env
echo GOOGLE_REDIRECT_URI=http://localhost:3000/api/auth/google/callback >> secrets.env
```

Encode the secrets in base64 format using PowerShell (run from Command Prompt):

```cmd
# Run PowerShell commands to encode secrets in base64
powershell -Command "$DATABASE_URL_B64 = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes('your_database_connection_string')); Set-Item -Path Env:DATABASE_URL_B64 -Value $DATABASE_URL_B64"
powershell -Command "$GEMINI_API_KEY_B64 = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes('your_gemini_api_key')); Set-Item -Path Env:GEMINI_API_KEY_B64 -Value $GEMINI_API_KEY_B64"
powershell -Command "$JWT_SECRET_B64 = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes('your_jwt_secret')); Set-Item -Path Env:JWT_SECRET_B64 -Value $JWT_SECRET_B64"
powershell -Command "$BETTER_AUTH_SECRET_B64 = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes('your_better_auth_secret')); Set-Item -Path Env:BETTER_AUTH_SECRET_B64 -Value $BETTER_AUTH_SECRET_B64"
powershell -Command "$GOOGLE_CLIENT_ID_B64 = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes('your_google_client_id')); Set-Item -Path Env:GOOGLE_CLIENT_ID_B64 -Value $GOOGLE_CLIENT_ID_B64"
powershell -Command "$GOOGLE_CLIENT_SECRET_B64 = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes('your_google_client_secret')); Set-Item -Path Env:GOOGLE_CLIENT_SECRET_B64 -Value $GOOGLE_CLIENT_SECRET_B64"
powershell -Command "$ACCESS_TOKEN_EXPIRE_MINUTES_B64 = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes('1440')); Set-Item -Path Env:ACCESS_TOKEN_EXPIRE_MINUTES_B64 -Value $ACCESS_TOKEN_EXPIRE_MINUTES_B64"
powershell -Command "$REFRESH_TOKEN_EXPIRE_DAYS_B64 = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes('7')); Set-Item -Path Env:REFRESH_TOKEN_EXPIRE_DAYS_B64 -Value $REFRESH_TOKEN_EXPIRE_DAYS_B64"
powershell -Command "$GOOGLE_REDIRECT_URI_B64 = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes('http://localhost:3000/api/auth/google/callback')); Set-Item -Path Env:GOOGLE_REDIRECT_URI_B64 -Value $GOOGLE_REDIRECT_URI_B64"
```

Alternatively, you can set the environment variables directly in Command Prompt:

```cmd
set DATABASE_URL_B64=base64_encoded_database_url
set GEMINI_API_KEY_B64=base64_encoded_gemini_api_key
set JWT_SECRET_B64=base64_encoded_jwt_secret
set BETTER_AUTH_SECRET_B64=base64_encoded_better_auth_secret
set GOOGLE_CLIENT_ID_B64=base64_encoded_google_client_id
set GOOGLE_CLIENT_SECRET_B64=base64_encoded_google_client_secret
set ACCESS_TOKEN_EXPIRE_MINUTES_B64=base64_encoded_access_token_expire_minutes
set REFRESH_TOKEN_EXPIRE_DAYS_B64=base64_encoded_refresh_token_expire_days
set GOOGLE_REDIRECT_URI_B64=base64_encoded_google_redirect_uri
```

## Step 6: Create Namespace

Create the namespace for the application:

```cmd
kubectl create namespace todo-ns
```

## Step 7: Deploy Using Helm

Navigate to the charts directory and install the Helm chart:

```cmd
# Navigate to the charts directory
cd charts/todo-app
```

For Windows Command Prompt:

```cmd
# Install the application using Helm with your secrets
helm install focusflow-release . ^
  --namespace todo-ns ^
  --set secrets.databaseUrl=%DATABASE_URL_B64% ^
  --set secrets.geminiApiKey=%GEMINI_API_KEY_B64% ^
  --set secrets.jwtSecret=%JWT_SECRET_B64% ^
  --set secrets.betterAuthSecret=%BETTER_AUTH_SECRET_B64% ^
  --set secrets.googleClientId=%GOOGLE_CLIENT_ID_B64% ^
  --set secrets.googleClientSecret=%GOOGLE_CLIENT_SECRET_B64% ^
  --set secrets.accessTokenExpireMinutes=%ACCESS_TOKEN_EXPIRE_MINUTES_B64% ^
  --set secrets.refreshTokenExpireDays=%REFRESH_TOKEN_EXPIRE_DAYS_B64% ^
  --set secrets.googleRedirectUri=%GOOGLE_REDIRECT_URI_B64% ^
  --set frontend.image.tag=latest ^
  --set backend.image.tag=latest ^
  --set ingress.hosts[0].host=focusflow.local
```

## Step 8: Verify Deployment

Check that all pods are running and ready:

```cmd
# Check pod status
kubectl get pods -n todo-ns

# Check services
kubectl get services -n todo-ns

# Check ingress
kubectl get ingress -n todo-ns
```

## Step 9: Configure Local DNS

Add an entry to your hosts file to access the application:

In Windows Command Prompt (run as Administrator):

```cmd
for /f %i in ('minikube ip') do echo %i focusflow.local >> C:\Windows\System32\drivers\etc\hosts
```

## Step 10: Access the Application

Access the application in your browser:

- Frontend: http://focusflow.local
- Backend API: http://focusflow.local/api
- Chat Interface: http://focusflow.local/chat

## Step 11: Deploy AI Operations Tools (Optional)

If you want to deploy the kagent for monitoring and auto-scaling:

```cmd
# Apply the kagent configuration
kubectl apply -f ../../../aops/kagent-agent.yaml

# Verify kagent is running
kubectl get pods -n kube-system
```

## Step 12: Monitor the Application

Monitor the application's resources and logs:

```cmd
# View pod logs
kubectl logs -l app=todo-frontend -n todo-ns
kubectl logs -l app=todo-backend -n todo-ns

# Monitor resources
kubectl top pods -n todo-ns
kubectl top nodes

# Check Horizontal Pod Autoscalers
kubectl get hpa -n todo-ns
```

## Step 13: Scaling the Application

Scale the application based on demand:

```cmd
# Check current replica counts
kubectl get deployments -n todo-ns

# Scale frontend service
kubectl scale deployment todo-app-frontend -n todo-ns --replicas=3

# Scale backend service
kubectl scale deployment todo-app-backend -n todo-ns --replicas=3
```

## Troubleshooting

### Common Issues:

1. **Images not found**: Ensure images are built and loaded into Minikube
   For Windows:

   ```cmd
   # Verify images are loaded
   minikube ssh "docker images | grep todo"
   ```

2. **Ingress not accessible**: Check if ingress controller is running

   ```cmd
   kubectl get pods -n ingress-nginx
   ```

3. **Database connection issues**: Verify Neon DB connection string in secrets

   ```cmd
   kubectl describe secret todo-app-secrets -n todo-ns
   ```

4. **Insufficient resources**: Increase Minikube resources
   ```cmd
   minikube stop
   minikube start --driver=docker --cpus=6 --memory=12288mb
   ```

## Cleanup

To remove the application from your cluster:

```cmd
# Uninstall Helm release
helm uninstall focusflow-release -n todo-ns

# Delete namespace
kubectl delete namespace todo-ns

# Stop Minikube
minikube stop
```

## Additional Commands

### Useful kubectl commands:

```cmd
# Get all resources in the todo-ns namespace
kubectl get all -n todo-ns

# Describe a specific pod for troubleshooting
kubectl describe pod <pod-name> -n todo-ns

# Execute commands inside a pod
kubectl exec -it <pod-name> -n todo-ns -- /bin/sh

# Port forward to access services locally
kubectl port-forward -n todo-ns svc/todo-app-frontend 3000:80
kubectl port-forward -n todo-ns svc/todo-app-backend 8000:80
```

### Useful Helm commands:

```cmd
# List releases
helm list -n todo-ns

# Upgrade the release with new values
helm upgrade focusflow-release . -n todo-ns -f values.yaml

# Rollback to previous version
helm rollback focusflow-release 1 -n todo-ns

# Get status of release
helm status focusflow-release -n todo-ns
```

### Useful Minikube commands:

```cmd
# Get Minikube IP
minikube ip

# Open dashboard
minikube dashboard

# SSH into Minikube
minikube ssh

# Get Minikube status
minikube status
```

This guide provides a complete walkthrough of deploying the FocusFlow Todo application to a local Kubernetes cluster using Minikube and Helm. The application includes frontend, backend, and optional chatbot services with proper configuration for authentication, database connections, and AI integration.
