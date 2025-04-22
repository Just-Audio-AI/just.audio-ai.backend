from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status

from src.dependency import get_chat_service, get_current_user_id
from src.schemas.chat import ChatMessageCreate, ChatResponse, ChatSessionResponse
from src.service.chat_service import ChatService

router = APIRouter(
    tags=["chat"],
    prefix="/chat",
)


@router.get(
    "/{file_id}",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_chat_history(
    file_id: Annotated[
        int, Path(..., title="The ID of the file to get chat history for")
    ],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    """
    Get the chat history for a specific file.

    Args:
        file_id: ID of the file to get chat history for
        current_user_id: ID of the current user
        chat_service: Chat service dependency

    Returns:
        Chat session with all messages

    Raises:
        HTTPException: If the file is not found or doesn't belong to the user
    """
    try:
        # Get user file and verify it exists and belongs to the user
        user_file = await chat_service.get_user_file(file_id)
        if not user_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File with id {file_id} not found",
            )

        # Verify the file belongs to the current user
        if user_file.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="File does not belong to the current user",
            )

        # Get chat session with messages
        chat_session = await chat_service.get_chat_history(file_id)

        return chat_session

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chat history: {str(e)}",
        )


@router.post(
    "/{file_id}",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
async def send_chat_message(
    file_id: Annotated[int, Path(..., title="The ID of the file to chat about")],
    message: ChatMessageCreate,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    """
    Send a message to the chat assistant for a specific file and get a response.

    Args:
        file_id: ID of the file to chat about
        message: User message content
        current_user_id: ID of the current user
        chat_service: Chat service dependency

    Returns:
        The assistant's response message

    Raises:
        HTTPException: If the file is not found or if there's an error processing the message
    """
    try:
        # Get user file and verify it exists and belongs to the user
        user_file = await chat_service.get_user_file(file_id)
        if not user_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File with id {file_id} not found",
            )

        # Verify the file belongs to the current user
        if user_file.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="File does not belong to the current user",
            )

        # Process the message and get a response
        response = await chat_service.process_message(
            file_id=file_id, message_content=message.message, user_id=current_user_id
        )

        # Если превышен лимит, возвращаем сообщение об ошибке, но с кодом 200
        # Так фронтенд сможет показать пользователю информацию о лимите
        return ChatResponse(
            message=response["message"],
            error=response.get("error", False),
            limit_exceeded=response.get("limit_exceeded", False),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}",
        )
