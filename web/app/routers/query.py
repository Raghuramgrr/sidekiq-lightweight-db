from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import get_connection

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/")
async def execute_query(request: QueryRequest):
    try:
        conn = await get_connection()
        async with conn.transaction():
            result = await conn.execute(request.query)
        await conn.close()
        return {"message": "Query executed successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
