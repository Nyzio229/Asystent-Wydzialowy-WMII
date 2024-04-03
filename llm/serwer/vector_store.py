from qdrant_client import QdrantClient

from llama_index.vector_stores.qdrant import QdrantVectorStore 

def get_vector_store(
    client: QdrantClient,
    collection_name: str
) -> QdrantVectorStore:
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection_name
    )

    return vector_store
