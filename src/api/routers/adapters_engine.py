from fastapi import APIRouter, Depends
from src.clients.engine import engine_client
from src.api.deps import get_api_key
from pydantic import BaseModel

router = APIRouter()


class TransformPayload(BaseModel):
    classPath: str


@router.post(
    "/adapters/engine/transform/{schema_type}", dependencies=[Depends(get_api_key)]
)
async def transform(schema_type: str, payload: TransformPayload):
    """Transform a Legend class to a schema (JSON Schema, Avro, etc.)."""
    return await engine_client.transform(schema_type, payload.classPath)
