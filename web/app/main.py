from fastapi import FastAPI
from .routers import schema, query

app = FastAPI()

app.include_router(schema.router, prefix="/schema", tags=["Schema"])
app.include_router(query.router, prefix="/query", tags=["Query"])
