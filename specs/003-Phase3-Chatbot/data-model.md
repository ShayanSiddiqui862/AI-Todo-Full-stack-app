# Data Model: AI-Powered Todo Chatbot

## Entity: Conversation

Represents a user's chat session with the AI, including message history and context.

```python
class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Foreign key to User, indexed for performance
    title: Optional[str] = Field(default=None, max_length=200)  # Optional title for the conversation
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")
```

**Validation rules**:
- `user_id` must correspond to an existing user
- `title` must not exceed 200 characters if provided
- Automatically sets `created_at` and `updated_at` timestamps

## Entity: Message

Individual exchanges between user and AI, with timestamps and sender identification.

```python
class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)  # Foreign key to Conversation
    role: str = Field(regex="^(user|assistant)$")  # Either "user" or "assistant"
    content: str = Field(min_length=1, max_length=10000)  # The message content
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to conversation
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

**Validation rules**:
- `conversation_id` must correspond to an existing conversation
- `role` must be either "user" or "assistant"
- `content` must be between 1 and 10,000 characters
- Automatically sets `created_at` timestamp

## Relationships

- One User → Many Conversations (via `user_id` foreign key)
- One Conversation → Many Messages (via `conversation_id` foreign key)
- One Message → One Conversation (via relationship)

## State Transitions

Messages have no state transitions - they are immutable once created. Conversations can be updated to change their title or metadata, but the core message history remains immutable.

## Indexes

- `user_id` on Conversation table (for efficient user-specific queries)
- `conversation_id` on Message table (for efficient conversation history retrieval)
- `created_at` on both tables (for chronological ordering)