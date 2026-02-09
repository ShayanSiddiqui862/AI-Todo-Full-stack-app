# Quickstart Guide: Cloud-Native Todo Application Deployment

## Prerequisites

Before deploying the Todo application to Kubernetes, ensure you have the following tools installed:

- Docker (v20.10 or later)
- Minikube (v1.30 or later)
- kubectl (v1.25 or later)
- Helm (v3.10 or later)
- Git

## Setting Up Your Environment

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/Todo-Full-stack.git
cd Todo-Full-stack
```

### 2. Start Minikube Cluster
```bash
# Start Minikube with recommended resources for this application
minikube start --driver=docker --cpus=4 --memory=8192mb

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
```

### 3. Verify Cluster Status
```bash
kubectl cluster-info
kubectl get nodes
```

## Building Container Images

### 1. Build Backend Image
```bash
cd backend
docker build -t todo-backend:latest .
cd ..
```

### 2. Build Frontend Image
```bash
cd frontend
docker build -t todo-frontend:latest .
cd ..
```

### 3. (Optional) Build Chatbot Image
```bash
cd chatbot  # if separate service exists
docker build -t todo-chatbot:latest .
cd ..
```

## Deploying the Application

### 1. Create Namespace
```bash
kubectl create namespace todo-ns
```

### 2. Configure Secrets
```bash
# Create a secret file with your environment variables
cat <<EOF > secrets.env
DATABASE_URL=your_database_connection_string
OPENAI_API_KEY=your_openai_api_key
JWT_SECRET=your_jwt_secret
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
GOOGLE_REDIRECT_URI=http://localhost:3000/api/auth/google/callback
EOF

# Apply secrets to the cluster
kubectl create secret generic todo-secrets \
  --from-env-file=secrets.env \
  -n todo-ns
```

### 3. Deploy Using Helm
```bash
# Navigate to the charts directory
cd charts/todo-app

# Install the application using Helm
helm install todo-release . \
  --namespace todo-ns \
  --set frontend.image=todo-frontend:latest \
  --set backend.image=todo-backend:latest \
  --set chatbot.image=todo-chatbot:latest \
  --set ingress.hosts[0].host=todo.local \
  --set ingress.hosts[0].paths[0].path='/' \
  --set ingress.hosts[0].paths[0].pathType=Prefix
```

## Verifying the Deployment

### 1. Check Pod Status
```bash
kubectl get pods -n todo-ns
```

### 2. Check Services
```bash
kubectl get services -n todo-ns
```

### 3. Check Ingress
```bash
kubectl get ingress -n todo-ns
```

### 4. Access the Application
```bash
# Get the Minikube IP
minikube ip

# Add entry to hosts file (Windows)
echo "$(minikube ip) todo.local" | Out-File -Append -Encoding ASCII C:\Windows\System32\drivers\etc\hosts

# Or on Linux/Mac
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts

# Access the application in browser
# Frontend: http://todo.local
# Backend API: http://todo.local/api
```

## Scaling the Application

### 1. Check Current Replica Counts
```bash
kubectl get deployments -n todo-ns
```

### 2. Scale Frontend Service
```bash
kubectl scale deployment todo-frontend --replicas=3 -n todo-ns
```

### 3. Scale Backend Service
```bash
kubectl scale deployment todo-backend --replicas=3 -n todo-ns
```

## Monitoring and Observability

### 1. View Pod Logs
```bash
kubectl logs -l app=todo-frontend -n todo-ns
kubectl logs -l app=todo-backend -n todo-ns
```

### 2. Monitor Resources
```bash
kubectl top pods -n todo-ns
kubectl top nodes
```

### 3. Using AI Operations Tools
```bash
# If kubectl-ai is installed
kubectl-ai describe pod -l app=todo-frontend -n todo-ns

# Check kagent status if deployed
kubectl get pods -n kube-system | grep kagent
```

## Troubleshooting

### Common Issues:

1. **Images not found**: Ensure images are built and available to Minikube
   ```bash
   # Load images into Minikube
   minikube image load todo-frontend:latest
   minikube image load todo-backend:latest
   ```

2. **Ingress not accessible**: Check if ingress controller is running
   ```bash
   kubectl get pods -n ingress-nginx
   ```

3. **Database connection issues**: Verify Neon DB connection string in secrets
   ```bash
   kubectl describe secret todo-secrets -n todo-ns
   ```

4. **Insufficient resources**: Increase Minikube resources
   ```bash
   minikube stop
   minikube start --driver=docker --cpus=6 --memory=12288mb
   ```

## Cleanup

### 1. Uninstall Helm Release
```bash
helm uninstall todo-release -n todo-ns
```

### 2. Delete Namespace
```bash
kubectl delete namespace todo-ns
```

### 3. Stop Minikube
```bash
minikube stop
```

## Next Steps

1. Explore the Helm chart values to customize your deployment
2. Set up monitoring with Prometheus and Grafana
3. Implement CI/CD pipeline for automated deployments
4. Add health checks and readiness probes to your services
5. Configure horizontal pod autoscaling based on metrics