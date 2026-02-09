---
id: 001
title: K8s Deployment Spec
stage: spec
date: 2026-02-08
surface: agent
model: Qwen
feature: 1-k8s-deployment
branch: 1-k8s-deployment
user: user1
command: /sp.specify
labels: [k8s, deployment, spec, todo-app]
links:
  spec: ../specs/1-k8s-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/1-k8s-deployment/spec.md
 - specs/1-k8s-deployment/checklists/requirements.md
tests:
 - null
---

## Prompt

```
Objective: Deploy the Todo full-stack web app (Next.js + FastAPI + Neon DB) with integrated AI chatbot (OpenAI Agents) as a cloud-native application on a local Kubernetes cluster using Minikube. Use Docker for containerization, Helm for orchestration, and AI tools (kubectl-ai, kagent) for operations. This phase establishes a blueprint for scalable, observable deployments. Key Features Containerize frontend, backend, and chatbot services. Deploy to Minikube with Helm charts. Integrate AIOps for automated troubleshooting and scaling. Ensure high availability (e.g., replicas) and persistence (e.g., DB connection). Architecture Diagram (Text-Based) text[User] --> Ingress/Nginx --> [Frontend Pod (Next.js)] | v [LoadBalancer] --> [Backend Pod (FastAPI + SQLModel)] --> [Neon DB (External)] | v [Chatbot Service (OpenAI Agents/MCP SDK)] <--> [Event Bus (Internal)] | v [Monitoring: kubectl-ai / kagent] --> Minikube Cluster Assumptions Minikube v1.30+ installed and running. Docker daemon accessible. Existing monorepo structure from Phase II/III (frontend/, backend/, specs/). Environment vars (e.g., Neon DB URL, OpenAI API key, JWT secret) managed via Kubernetes Secrets. 2. Requirements Breakdown 2.1 Containerization (Docker) Features: Build multi-stage Docker images for frontend (Node.js) and backend (Python). Separate image for chatbot if modular (integrate via Agents SDK). Optimize for size: Use distroless base images where possible. Specs: Dockerfile for Frontend (frontend/Dockerfile): Stage 1: Build Next.js app with npm run build. Stage 2: Serve with nginx:1.25-alpine, copy built assets. Expose port 3000. Health check: /api/health endpoint. Dockerfile for Backend (backend/Dockerfile): Use python:3.12-slim. Install deps via poetry/uv. Copy FastAPI app, run with uvicorn. Expose port 8000. Health check: curl http://localhost:8000/health. Multi-Service Compose (for local testing): Update docker-compose.yml to build/test before K8s. Validation: Images build and run locally via docker build and docker run. 2.2 Minikube Setup and Cluster Configuration Features: Provision local K8s cluster. Enable addons: ingress, metrics-server. Specs: Minikube Manifest (infra/minikube-setup.yaml): Command sequence: minikube start --driver=docker --cpus=4 --memory=8192mb. Enable: minikube addons enable ingress, minikube addons enable metrics-server. Persistent volume for any local state (e.g., if caching). Namespace: Create todo-ns for isolation. Validation: kubectl get nodes shows ready cluster; ingress accessible. 2.3 Helm Chart Deployment Features: Package services into a reusable Helm chart. Deploy frontend, backend, chatbot as Deployments with Services. Configurable values: Replicas (default 2), image tags, env vars. Specs: Helm Chart Structure (charts/todo-app/): Chart.yaml: Name todo-app, version 0.4.0, dependencies none. values.yaml:YAMLreplicas: 2 frontend: image: "your-repo/frontend:latest" port: 3000 backend: image: "your-repo/backend:latest" port: 8000 dbUrl: "{{ .Values.secrets.neonUrl }}" chatbot: enabled: true openAiKey: "{{ .Values.secrets.openAiKey }}" ingress: enabled: true host: "todo.local" templates/: deployment-frontend.yaml: Deployment with podTemplate (resources: cpu 100m, mem 256Mi). service-frontend.yaml: ClusterIP or LoadBalancer on port 3000. Similar for backend (port 8000) and chatbot. ingress.yaml: Nginx ingress routing / to frontend, /api to backend, /chat to chatbot. secrets.yaml: Base64-encoded secrets for DB, JWT, OpenAI. Hooks: Pre-install job to run DB migrations via backend init container. Deployment Command: helm install todo-release ./charts/todo-app -n todo-ns --set image.tag=phase4. Validation: helm ls shows release; kubectl port-forward svc/frontend 3000:3000 accesses app. 2.4 AIOps Integration (kubectl-ai, kagent) Features: Use kubectl-ai for AI-assisted kubectl commands (e.g., debug pods). Integrate kagent for agentic monitoring (e.g., auto-scale based on CPU). Specs: kubectl-ai Config (aops/kubectl-ai-setup.yaml): Install plugin: Assume pre-installed; spec for wrapper script. Example Usage: Generate spec for "kubectl-ai explain deployment todo-frontend" to auto-generate troubleshooting YAML. kagent Blueprint (aops/kagent-agent.yaml): Deploy as DaemonSet for cluster-wide monitoring. Skills: Query pod logs, suggest scaling (e.g., if >80% CPU, scale replicas). Integrate with Claude Code: Use as subagent for "generate scaling policy". Observability: Add Prometheus annotations for scraping; simple dashboard spec. Validation: Run kubectl-ai describe pod outputs natural language summary; kagent logs show agent actions. 2.5 Reusable Intelligence (Bonus: +200 points) Features: Create Cloud-Native Blueprints via Agent Skills. Specs: Agent Skill Blueprint (specs/blueprints/k8s-deployment-skill.md): Reusable YAML template generator: Input spec → Output Helm values. Subagent: "k8s-deployer" using Claude Code to refine manifests. Export as MCP SDK tool for Phase V reuse. 3. Implementation Workflow (Agentic Dev Stack) Write Spec: Refine this doc iteratively. Generate Plan: Prompt Claude Code: "Based on Phase IV spec, outline tasks for Docker + Helm." Break into Tasks: Sub-tasks: Dockerfile gen → Helm chart → Deployment. Implement via Claude Code: @specs/phase-iv-overview.md → Generate files in /infra/. Validate & Iterate: Test on Minikube; log in CLAUDE.md. 4. Deliverables Updated GitHub repo: /infra/ folder with Dockerfiles, Helm charts, AIOps scripts. README.md: Minikube setup + deployment instructions. Demo Video (<90s): Screen record minikube tunnel + app access + chatbot interaction. Submission: Via Google Form with repo link, Vercel (for web preview), video, WhatsApp. 5. Risks & Mitigations Risk: Minikube resource limits → Mitigation: Spec min 4CPU/8GB. Risk: Secret leakage → Mitigation: Use SealedSecrets or external vault spec. Risk: DB Connectivity → Mitigation: Init container for Neon migration.
```

## Response snapshot

I've successfully created the feature specification for your cloud-native Todo application deployment. Here's a summary of what was completed:

1. Created a new feature branch named "1-k8s-deployment"
2. Generated a comprehensive feature specification document at `specs/1-k8s-deployment/spec.md`
3. Created a quality checklist at `specs/1-k8s-deployment/checklists/requirements.md`

The specification covers all the key aspects you outlined:
- Containerization with Docker for frontend (Next.js), backend (FastAPI), and chatbot services
- Minikube cluster setup with proper resource allocation
- Helm chart deployment with configurable values
- AIOps integration with kubectl-ai and kagent
- Proper risk mitigation strategies
- Clear success criteria and acceptance criteria

The specification follows best practices by focusing on WHAT the system should do rather than HOW to implement it, making it suitable for both technical and non-technical stakeholders.

You can now proceed with the next phases:
1. `/sp.clarify` if you need to clarify any requirements
2. `/sp.plan` to create a technical implementation plan

The specification is ready for review and planning.

## Outcome

- ✅ Impact: Successfully created a comprehensive specification for deploying the Todo app on Kubernetes
- 🧪 Tests: N/A (specification phase)
- 📁 Files: Created spec.md and requirements.md in the feature directory
- 🔁 Next prompts: Ready for /sp.clarify or /sp.plan
- 🧠 Reflection: The specification addresses all major requirements from the original request

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed with technical planning