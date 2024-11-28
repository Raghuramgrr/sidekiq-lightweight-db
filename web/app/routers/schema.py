from fastapi import APIRouter, HTTPException
from ..db import get_connection

router = APIRouter()

@router.get("/")
async def get_tables():
    try:
        conn = await get_connection()
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        tables = await conn.fetch(query)
        await conn.close()
        return {"tables": [table["table_name"] for table in tables]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
