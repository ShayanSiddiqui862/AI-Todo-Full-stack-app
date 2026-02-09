# Research: AI-Powered Todo Chatbot

## Decision: OpenAI ChatKit Integration Approach
**Rationale**: Based on the feature requirements (FR-001 to FR-006), we need to integrate with OpenAI ChatKit UI according to the official documentation. ChatKit requires a NEXT_PUBLIC_OPENAI_DOMAIN_KEY and needs to communicate with our backend chat endpoint.
**Alternatives considered**: Alternative chat UI libraries like react-simple-chatbot or custom-built solutions, but ChatKit provides the best integration with OpenAI's ecosystem.

## Decision: OpenAI Agents SDK Implementation
**Rationale**: The feature requires using the OpenAI Agents SDK for AI decision-making and intent recognition (FR-007). This SDK provides the best integration with MCP tools and natural language processing capabilities.
**Alternatives considered**: Using OpenAI's older Assistants API or other LLM providers like Anthropic Claude, but the Agents SDK is specifically designed for tool usage and MCP integration.

## Decision: MCP Server Architecture
**Rationale**: The feature requires implementing an MCP (Model Context Protocol) server using the Official MCP SDK (FR-008). MCP provides a standardized way to expose our todo operations as tools for the AI agent.
**Alternatives considered**: Direct API calls from the agent to our backend, but MCP provides better tool discovery and standardization.

## Decision: Stateless Request Cycle Design
**Rationale**: The backend must implement a stateless request cycle where all conversation state is persisted to the database rather than held in server memory (FR-011, FR-012). This ensures scalability and reliability.
**Alternatives considered**: Storing conversation state in server memory or Redis cache, but this violates the stateless requirement and reduces reliability.

## Decision: Database Schema for Conversations
**Rationale**: To support conversation continuity (User Story 3) and FR-012, we need to implement Conversation and Message entities in our database with proper relationships to users.
**Alternatives considered**: Storing conversation history in a separate NoSQL database, but keeping it in our existing PostgreSQL with SQLModel maintains consistency.

## Decision: Authentication Integration
**Rationale**: The system must pass authentication tokens from Better Auth to ChatKit provider for authenticated requests (FR-005) and ensure users can only access their own tasks (FR-013).
**Alternatives considered**: Implementing a separate authentication mechanism for the chatbot, but reusing the existing JWT system maintains consistency and security.