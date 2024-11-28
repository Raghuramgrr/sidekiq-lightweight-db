import os

# Directory and file structure
PROJECT_STRUCTURE = {
    "web": {
        "app": {
            "routers": ["__init__.py", "schema.py", "query.py"],
            "files": ["main.py", "db.py"]
        },
        "files": ["Dockerfile", "requirements.txt"]
    },
    "files": ["docker-compose.yml"]
}

BOILERPLATES = {
    "docker-compose.yml": """\
version: "3.9"

services:
  postgres:
    image: postgres:15
    container_name: postgres_db
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123
      POSTGRES_DB: mydb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build:
      context: ./web
    container_name: web_dashboard
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: mydb
      DB_USER: admin
      DB_PASSWORD: admin123
    ports:
      - "8000:8000"
    depends_on:
      - postgres

volumes:
  postgres_data:
""",
    "Dockerfile": """\
FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    "requirements.txt": "fastapi\nuvicorn\nasyncpg\n",
    "__init__.py": "",
    "main.py": """\
from fastapi import FastAPI
from .routers import schema, query

app = FastAPI()

app.include_router(schema.router, prefix="/schema", tags=["Schema"])
app.include_router(query.router, prefix="/query", tags=["Query"])
""",
    "db.py": """\
import asyncpg
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "mydb")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")

async def get_connection():
    return await asyncpg.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
""",
    "schema.py": """\
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
""",
    "query.py": """\
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
"""
}

def generate_project(base_path="."):
    for root, content in PROJECT_STRUCTURE.items():
        root_path = os.path.join(base_path, root)
        if isinstance(content, dict):  # Subdirectories
            os.makedirs(root_path, exist_ok=True)
            for subfolder, files in content.items():
                sub_path = os.path.join(root_path, subfolder)
                os.makedirs(sub_path, exist_ok=True)
                for file_name in files:
                    if file_name in BOILERPLATES:
                        with open(os.path.join(sub_path, file_name), "w") as f:
                            f.write(BOILERPLATES[file_name])
        elif isinstance(content, list):  # Files
            os.makedirs(root_path, exist_ok=True)
            for file_name in content:
                if file_name in BOILERPLATES:
                    with open(os.path.join(root_path, file_name), "w") as f:
                        f.write(BOILERPLATES[file_name])

if __name__ == "__main__":
    generate_project()
    print("Project structure generated successfully.")
