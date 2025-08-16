# app/api/routes/chat.py
from typing import Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.encoders import jsonable_encoder


from app.api.deps import get_optional_customer
from app.schemas.chat import ChatRequest
from app.services.llm_services.llm_client import build_llm_client
from app.db.models import Customer

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/")
async def chat(
    payload: ChatRequest,
    request: Request,
    current_user: Optional[Customer] = Depends(get_optional_customer),
):
    llm_client = build_llm_client()

    # return StreamingResponse(
    #     llm_client.astream_answer(
    #         message=payload.message,
    #         user=current_user,
    #         language=payload.language or "ky",
    #     ),
    #     media_type="text/event-stream",
    # )
    result = await llm_client.respond(
        message=payload.message,
        user=current_user,
        language=payload.language
    )
    return JSONResponse(content=jsonable_encoder(result))
