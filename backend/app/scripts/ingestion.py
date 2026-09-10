import json
from pathlib import Path
from app.core.config import settings
from pinecone import Pinecone
from pinecone import ServerlessSpec
from app.core.logger import logger

VECTORS_DIR = Path("app/assets/vectors")

def seed_pinecone(batch_size: int):
    logger.info("[pinecone] starting seeding...")
    
    pc = Pinecone(host=settings.PINECONE_HOST, api_key=settings.PINECONE_API_KEY)
    if settings.PINECONE_INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=settings.PINECONE_INDEX_NAME,
            dimension=512,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        logger.info("[pinecone] index created")
        
    index = pc.Index(name=settings.PINECONE_INDEX_NAME, host=settings.PINECONE_INDEX_HOST)
    
    batch = []
    total = 0
    with open(VECTORS_DIR / "pinecone_vectors_2.jsonl") as f:
        for line in f:
            try:
                item = json.loads(line)

                batch.append({
                    "id": item["id"],
                    "values": item["values"],
                    "metadata": item.get("metadata", {})
                })

                if len(batch) >= batch_size:
                    index.upsert(vectors=batch, namespace="10k")
                    total += len(batch)
                    batch = []
                    
            except Exception as e:
                logger.warning(f"[pinecone] skipping bad line: {e}")
                
        if batch:
            index.upsert(vectors=batch, namespace="10k")
            total += len(batch)

    logger.info(f"[pinecone] done. total vectors: {total}")
    
def seed_users():
    from app.model.user import User
    from app.shared.db import SessionLocal
    from app.core.security import hash_password

    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            admin_user = User(username="admin", password=hash_password("admin"))
            db.add(admin_user)
            db.commit()
            logger.info("[db] seeded admin user")
        else:
            logger.info("[db] admin user already exists, skipping seeding")
    finally:
        db.close()
        
def seed_all():
    seed_users()
    seed_pinecone(batch_size=100)
            
if __name__ == "__main__":
    seed_all()