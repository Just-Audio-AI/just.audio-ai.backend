# Chat Endpoint Examples

## Send a chat message to a file

```bash
curl -X POST "http://localhost:8000/chat/123" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "Проанализируй основные темы в этой аудиозаписи"
  }'
```

### Response

```json
{
  "message": "Основываясь на транскрипции аудиозаписи, могу выделить следующие основные темы: ..."
}
```

## Running the migration

To create the necessary database tables, run:

```bash
alembic upgrade head
```

## Environment Variables

Make sure to set the following environment variables for OpenAI integration:

```
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4-turbo etc.
```

## Implementation Details

The chat feature allows users to have conversations with an AI assistant about their audio files. The implementation:

1. Creates a chat session for each file when a user first sends a message
2. Stores all messages in the database for persistence
3. Sends the file's transcription as context to OpenAI
4. Maintains conversation history
5. Authenticates users and ensures they can only interact with their own files 