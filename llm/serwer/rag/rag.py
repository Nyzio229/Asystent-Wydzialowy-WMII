from llama_cpp import Llama

from sentence_transformers import SentenceTransformer

from llama_index.core.query_engine import RetrieverQueryEngine

from rag.retriever import VectorDBRetriever

def rag(
    llm: Llama,
    embedder: SentenceTransformer,
    query: str
) -> str:
    retriever = VectorDBRetriever(
        embedder=embedder,
        query_mode="default",
        similarity_top_k=2
    )

    # @TODO: jak zrobić dopasowywanie argumentów tak jak w create_chat_completion? I w ogóle uwzględnienie całej konwersacji?
    query_engine = RetrieverQueryEngine.from_args(retriever, llm)

    response = query_engine.query(query)
    response = str(response)

    return response
