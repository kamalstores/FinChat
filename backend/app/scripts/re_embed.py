import json
import re
from pathlib import Path
import hashlib
import unicodedata

from collections import defaultdict

from app.agent.provider.gemini import embeddings_model
from app.core.logger import logger

VECTOR_PATH = Path("app/assets/vectors/pinecone_vectors.jsonl")
OUTPUT_PATH = Path("app/assets/vectors/pinecone_vectors_2.jsonl")


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)

    replacements = {
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬀ": "ff",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove common PDF artifacts
    text = re.sub(
        r"file:///\S+|\b\d+\s*/\s*\d+\b|[-_=]{3,}",
        " ",
        text,
    )

    return re.sub(r"\s+", " ", text).strip()


def load_documents():

    docs = defaultdict(list)

    with open(VECTOR_PATH, "r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)

            metadata = row.get("metadata", {})

            source = metadata.get("source")
            source = source.split("/")[-1]
            company = source.split("_")[0]
            page = metadata.get("page")
            page_label = metadata.get("page_label")

            text = metadata.get("text")

            if text:
                docs[source].append(
                    {
                        "text": text,
                        "page": page,
                        "page_label": page_label,
                        "company": company,
                    }
                )

    total_chunks = sum(len(chunks) for chunks in docs.values())
    logger.info(f"Loaded {total_chunks} chunks from {VECTOR_PATH}.")

    return [{"source": source, "chunks": chunks} for source, chunks in docs.items()]


def build_vectors():
    logger.info("Starting re-embedding process...")
    docs = load_documents()
    total_chunks = sum(len(doc["chunks"]) for doc in docs)
    logger.info(f"Loaded {total_chunks} chunks for re-embedding.")

    seen = set()

    texts = []
    metas = []

    total_chunks = 0
    count = 0
    fgp = 0

    for doc in docs:
        source = doc["source"]

        for item in doc["chunks"]:
            cleaned = clean_text(item["text"])
            text = cleaned.strip()

            if len(text) < 50:
                count += 1
                continue

            fingerprint = hashlib.md5(text.encode()).hexdigest()

            if fingerprint in seen:
                fgp += 1
                continue

            seen.add(fingerprint)

            texts.append(text)
            metas.append(
                {
                    "source": source,
                    "page": item.get("page"),
                    "page_label": item.get("page_label"),
                    "fingerprint": fingerprint,
                    "company": item.get("company"),
                }
            )

    logger.info(f"Removed {count} bad chunks after cleaning.")
    logger.info(f"Removed {fgp} duplicate chunks after fingerprinting.")
    logger.info(f"Embedding {len(texts)} chunks in batch...")

    batch_size = 100
    batch_output = []

    for i in range(0, len(texts), batch_size):
        text_batch = texts[i : i + batch_size]
        meta_batch = metas[i : i + batch_size]

        vectors = embeddings_model.embed_documents(text_batch)

        for text, meta, vector in zip(text_batch, meta_batch, vectors):
            vector_id = f"{meta['source']}-{meta['page']}-{meta['fingerprint'][:8]}"

            batch_output.append(
                {
                    "id": vector_id,
                    "values": vector,
                    "metadata": {
                        "source": meta["source"],
                        "company": meta["company"],
                        "page": meta["page"],
                        "page_label": meta["page_label"],
                        "text": text,
                    },
                }
            )

            total_chunks += 1

        logger.info(f"Processed batch {i} → {i + len(text_batch)}")

    save_to_file(batch_output)

    logger.info(f"done: {total_chunks} chunks indexed")


def save_to_file(batch: list[dict]):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for vector in batch:
            f.write(json.dumps(vector) + "\n")


if __name__ == "__main__":
    build_vectors()
