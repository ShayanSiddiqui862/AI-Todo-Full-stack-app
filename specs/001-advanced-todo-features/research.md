# Research Summary: Advanced Todo Features with Event-Driven Architecture

## Decision: Dapr for Distributed Runtime
**Rationale**: Dapr provides a portable, event-driven runtime that abstracts away infrastructure concerns. It offers pub/sub messaging, state management, service invocation, and secret management with minimal code changes. This aligns with the requirement to avoid direct Kafka/DB calls in application code.

**Alternatives considered**:
- Direct Kafka integration: Would require Kafka client libraries in app code, violating the constraint
- Custom event system: Would reinvent existing solutions and increase complexity
- RabbitMQ: Less portable than Kafka, doesn't align with specified technology

## Decision: Redpanda for Local Kafka Development
**Rationale**: Redpanda is a drop-in Kafka replacement that's lighter weight and faster to set up locally. It maintains full Kafka API compatibility, allowing seamless transition to production Kafka clusters.

**Alternatives considered**:
- Apache Kafka directly: Heavier to run locally, more complex setup
- In-memory message queue: Doesn't provide durability or persistence guarantees
- Cloud Kafka service: Not suitable for local development

## Decision: PostgreSQL with JSONB for Tag Storage
**Rationale**: PostgreSQL's JSONB column type provides efficient storage and querying of tag arrays. Combined with GIN indexing, it enables fast tag-based searches. This maintains data locality while supporting flexible tag structures.

**Alternatives considered**:
- Separate tags table with junction: More normalized but requires joins, potentially impacting performance
- Comma-separated string: Harder to query and validate
- MongoDB: Would introduce additional database technology to the stack

## Decision: Dapr Jobs API for Scheduling
**Rationale**: Using Dapr's Jobs API abstracts away scheduling infrastructure while providing reliable, time-based triggers for reminders and recurring tasks. This fits the constraint of not having direct dependencies on scheduling libraries.

**Alternatives considered**:
- Celery: Would require Redis/RabbitMQ and introduces Python-specific dependencies
- Cron jobs: Not suitable for containerized environments, harder to scale
- Custom polling mechanism: Inefficient and doesn't meet exact-time trigger requirement

## Decision: MCP for Natural Language Parsing
**Rationale**: MCP (Model Context Protocol) tools are already integrated in the existing system and provide sophisticated natural language processing capabilities. Extending the existing MCP tools to extract priority, tags, due date, and recurrence patterns maintains consistency with the existing architecture.

**Alternatives considered**:
- Custom NLP: Would require significant development effort
- Third-party NLP services: Would introduce external dependencies and potential costs
- Rule-based parsing: Less flexible and robust than MCP