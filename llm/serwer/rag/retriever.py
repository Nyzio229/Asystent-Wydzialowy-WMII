from llama_index.core import QueryBundle
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import BaseNode, NodeWithScore
from llama_index.core.vector_stores import VectorStoreQuery

from sentence_transformers import SentenceTransformer

from embed import embed

from common import common

from config import config

from vector_store import get_vector_store

class VectorDBRetriever(BaseRetriever):
    def __init__(
        self,
        embedder: SentenceTransformer,
        query_mode: str = "default",
        similarity_top_k: int = 2
    ) -> None:
        super().__init__()

        self._embedder = embedder
        self._query_mode = query_mode
        self._similarity_top_k = similarity_top_k

        collection_name = config["vector_store"]["collection_name"]
        self._vector_store = get_vector_store(common.qdrant_client, collection_name)

    def _retrieve(
        self,
        query_bundle: QueryBundle
    ) -> list[NodeWithScore]:
        query_embedding = embed(self._embedder, query_bundle.query_str)

        vector_store_query = VectorStoreQuery(
            query_embedding=query_embedding,
            similarity_top_k=self._similarity_top_k,
            mode=self._query_mode,
        )

        query_result = self._vector_store.query(vector_store_query)

        def _create_node_with_score(idx: int, node: BaseNode) -> NodeWithScore:
            score = None if query_result.similarities is None else query_result.similarities[idx]
            node = NodeWithScore(node=node, score=score)

            return node

        nodes = list(map(lambda args: _create_node_with_score(*args), enumerate(query_result.nodes)))

        return nodes
