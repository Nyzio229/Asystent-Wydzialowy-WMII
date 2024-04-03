from sentence_transformers import SentenceTransformer

def embed(
    embedder: SentenceTransformer,
    text: str | list[str]
) -> list[float] | list[list[float]]:
    embedding = embedder.encode(text)
    embedding = embedding.tolist()

    return embedding
