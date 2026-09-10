from pinecone import Pinecone
from app.core.config import settings

pc = Pinecone(host=settings.PINECONE_HOST, api_key=settings.PINECONE_API_KEY)
index = pc.Index(name=settings.PINECONE_INDEX_NAME, host=settings.PINECONE_INDEX_HOST)