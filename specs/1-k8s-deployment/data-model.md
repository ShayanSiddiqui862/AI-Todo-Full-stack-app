# Data Model: Cloud-Native Todo Application Deployment

## Key Entities

### 1. Frontend Service (Next.js application)
- **Name**: frontend-service
- **Fields**:
  - image: Docker image identifier
  - port: Port number for service exposure (default: 3000)
  - replicas: Number of pod replicas (default: 2)
  - resources: CPU and memory limits/requests
  - health_check_path: Health check endpoint path
- **Relationships**: 
  - Depends on: backend-service (for API calls)
  - Exposes via: ingress-controller
- **Validation rules**: 
  - Image must be a valid Docker image reference
  - Port must be between 1-65535
  - Replicas must be >= 1

### 2. Backend Service (FastAPI application)
- **Name**: backend-service
- **Fields**:
  - image: Docker image identifier
  - port: Port number for service exposure (default: 8000)
  - replicas: Number of pod replicas (default: 2)
  - resources: CPU and memory limits/requests
  - db_url: Database connection string
  - health_check_path: Health check endpoint path
- **Relationships**:
  - Connects to: neon-database
  - Accessed by: frontend-service, external clients
- **Validation rules**:
  - Image must be a valid Docker image reference
  - Port must be between 1-65535
  - Replicas must be >= 1
  - db_url must be a valid database connection string

### 3. Chatbot Service (OpenAI Agents integration)
- **Name**: chatbot-service
- **Fields**:
  - image: Docker image identifier
  - port: Port number for service exposure (default: 8001)
  - replicas: Number of pod replicas (default: 1)
  - resources: CPU and memory limits/requests
  - openai_api_key: OpenAI API key
  - health_check_path: Health check endpoint path
- **Relationships**:
  - Communicates with: OpenAI API
  - Accessed by: frontend-service, external clients
- **Validation rules**:
  - Image must be a valid Docker image reference
  - Port must be between 1-65535
  - Replicas must be >= 1
  - openai_api_key must be a valid API key format

### 4. Neon Database (external PostgreSQL database)
- **Name**: neon-database
- **Fields**:
  - connection_url: Full database connection URL
  - ssl_required: Boolean indicating if SSL is required
  - pool_size: Connection pool size
- **Relationships**:
  - Connected by: backend-service
- **Validation rules**:
  - connection_url must be a valid PostgreSQL connection string
  - ssl_required must be boolean
  - pool_size must be between 1-100

### 5. Kubernetes Cluster (Minikube)
- **Name**: k8s-cluster
- **Fields**:
  - driver: Virtualization driver (default: docker)
  - cpus: Number of CPU cores (minimum: 4)
  - memory: Memory allocation in MB (minimum: 8192)
  - addons: Enabled Kubernetes addons (ingress, metrics-server)
  - namespace: Dedicated namespace for the application (default: todo-ns)
- **Validation rules**:
  - cpus must be >= 4
  - memory must be >= 8192MB
  - addons must be valid Kubernetes addon names

### 6. Helm Chart (deployment configuration)
- **Name**: helm-chart
- **Fields**:
  - name: Chart name (default: todo-app)
  - version: Chart version (default: 0.4.0)
  - values: Configuration values map
  - templates: List of Kubernetes manifest templates
- **Relationships**:
  - Deploys: frontend-service, backend-service, chatbot-service
  - Configures: ingress, services, deployments
- **Validation rules**:
  - name must be a valid Helm chart name
  - version must follow semantic versioning
  - templates must generate valid Kubernetes manifests

### 7. Ingress Configuration
- **Name**: ingress-config
- **Fields**:
  - enabled: Boolean to enable/disable ingress (default: true)
  - host: Hostname for the ingress (default: todo.local)
  - paths: Map of URL paths to services
    - "/": routes to frontend-service
    - "/api": routes to backend-service
    - "/chat": routes to chatbot-service
- **Relationships**:
  - Routes to: frontend-service, backend-service, chatbot-service
  - Managed by: ingress-controller
- **Validation rules**:
  - host must be a valid hostname or IP address
  - paths must be valid URL paths
  - Services referenced in paths must exist

### 8. Secrets Management
- **Name**: k8s-secrets
- **Fields**:
  - db_url_secret: Encrypted database connection string
  - openai_api_key_secret: Encrypted OpenAI API key
  - jwt_secret: Encrypted JWT signing key
- **Relationships**:
  - Used by: backend-service, chatbot-service
  - Stored in: Kubernetes secrets
- **Validation rules**:
  - Values must be base64 encoded
  - Access must be restricted via RBAC

## State Transitions

### Deployment Lifecycle
1. **Pending**: Helm chart prepared but not yet deployed
2. **Installing**: Helm install command executed, resources being created
3. **Running**: All services are deployed and healthy
4. **Updating**: Helm upgrade command executed, resources being updated
5. **Scaling**: Pod replicas being adjusted based on load
6. **Terminating**: Helm uninstall command executed, resources being deleted

### Pod Lifecycle
1. **Pending**: Pod scheduled but not all containers created
2. **Running**: Pod bound to node and all containers running
3. **Succeeded**: All containers terminated successfully
4. **Failed**: At least one container terminated with failure
5. **Unknown**: Status cannot be determined


