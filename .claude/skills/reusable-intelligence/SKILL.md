name: reusable-intelligence
description: Advanced skill for generating cloud-native blueprints, infrastructure automation, and multi-language support. Use this to maximize hackathon bonus points.


# Reusable Intelligence Skill

This skill represents the "Architectural Intelligence" layer of the project. It enables agents to move beyond simple application code into the realm of automated infrastructure and localized user experiences.

## 1. Cloud-Native Blueprints
- **Infrastructure as Code (IaC)**: When requested, generate standardized Dockerfiles and Kubernetes manifests (YAML) based on the Phase IV/V requirements.
- **Helm Charts**: Automate the creation of Helm templates for deploying the frontend and backend as a single unit.
- **Deployment Strategy**: Ensure blueprints include health checks (liveness/readiness probes) and resource limits (CPU/Memory).

## 2. Multi-Language & Urdu Support
- **Localization (i18n)**: Implement patterns for the chatbot to detect and respond in Urdu when prompted by the user.
- **Translation Handlers**: Use standardized dictionary files or AI-driven translation logic to ensure a seamless bilingual experience.
- **RTL Support**: Ensure the frontend layout logic accounts for Right-to-Left (RTL) text alignment for Urdu strings.

## 3. Advanced AI Capabilities
- **Voice Commands**: Provide logic for integrating voice-to-text APIs to allow users to manage their todo list via speech.
- **Intelligent Rescheduling**: Use natural language processing logic to handle complex user requests like "Move all my high-priority tasks to tomorrow."
- **Contextual Memory**: Leverage the conversation history in the database to provide personalized task suggestions.

## 4. Automation & AIOps
- **Cluster Analysis**: Provide instructions for using `kagent` or `kubectl-ai` to analyze cluster health and optimize resource allocation.
- **CI/CD Blueprints**: Generate GitHub Action workflows that automatically build, test, and deploy the application to DigitalOcean or Azure.

## 5. Implementation Rules
- **Blueprints First**: Always generate a "Blueprint" (template) before applying specific environment configurations.
- **Bonus Alignment**: Explicitly state when a generated feature contributes to the "Reusable Intelligence" (+200) or "Cloud-Native Blueprints" (+200) bonus categories.

## 6. Verification Checklist
- [ ] Does the blueprint allow for environment-swappable variables (e.g., using Dapr abstractions)?
- [ ] Is the Urdu translation logic non-blocking and integrated into the Chat API?
- [ ] Are Kubernetes manifests follow best practices for security (Non-root users, Secret management)?

## 7. Workflow Constraints
- **Spec-Driven Blueprints**: All infrastructure changes must be documented in a plan before implementation.
- **No Hardcoding**: Credentials and environment-specific endpoints must never be hardcoded into blueprints.