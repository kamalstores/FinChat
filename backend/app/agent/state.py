from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.core.config import settings
from app.agent.finance import create_finance_agent
from app.core.logger import logger

# https://medium.com/@devwithll/simple-langgraph-implementation-with-memory-asyncsqlitesaver-checkpointer-fastapi-54f4e4879a2e
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncPostgresSaver.from_conn_string(settings.POSTGRES_URL) as checkpointer:
        await checkpointer.setup()
        finance_agent = create_finance_agent(checkpointer)
        app.state.agent = finance_agent
        app.state.checkpointer = checkpointer
        logger.info("Agent initialized and stored in app state.")
        yield
        logger.info("Lifespan context manager exiting. Cleanup if necessary.")


