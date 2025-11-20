import asyncio

from langchain_core.embeddings import Embeddings
from openai import AzureOpenAI


class AzureOpenAIEmbeddings(Embeddings):
    """Azure OpenAI embeddings implementation."""

    def __init__(
        self,
        azure_endpoint: str,
        api_key: str,
        api_version: str,
        embedding_deployment_name: str,
        batch_size: int = 50,
        vector_size: int | None = None,
    ) -> None:
        """Initialize AzureOpenAIEmbeddings.

        Args:
            azure_endpoint: Azure OpenAI endpoint URL
            api_key: API key for authentication
            api_version: API version (e.g., "2024-02-15-preview")
            embedding_deployment_name: Deployment name for the embedding model
            batch_size: Batch size for embedding documents
            vector_size: Vector size for embeddings (auto-detected if None)
        """
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version,
        )
        self.deployment_name = embedding_deployment_name
        self.__batch_size = batch_size
        self.vector_size = vector_size or self.set_vector_size()

    def set_vector_size(self) -> int:
        """Auto-detect vector size by embedding a test string."""
        text = "test"
        response = self.client.embeddings.create(
            model=self.deployment_name,
            input=[text],
        )
        return len(response.data[0].embedding)

    def embed_documents(
        self, texts: list[str], batch_size: int | None = None
    ) -> list[list[float]]:
        """Embed a list of documents.

        Args:
            texts: List of texts to embed
            batch_size: Batch size (uses default if None)

        Returns:
            List of embeddings
        """
        all_embeddings: list[list[float]] = []
        batch_size = batch_size or self.__batch_size
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                response = self.client.embeddings.create(
                    model=self.deployment_name,
                    input=batch,
                )
            except Exception as e:
                raise Exception(f"Failed to embed documents: {batch}") from e
            embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(embeddings)
        return all_embeddings

    async def aembed_documents(
        self, texts: list[str], batch_size: int | None = None
    ) -> list[list[float]]:
        """Async version of embed_documents."""
        return await asyncio.to_thread(self.embed_documents, texts, batch_size)

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        response = self.client.embeddings.create(
            model=self.deployment_name,
            input=[text],
        )
        return response.data[0].embedding

    async def aembed_query(self, text: str) -> list[float]:
        """Async version of embed_query."""
        return await asyncio.to_thread(self.embed_query, text)
