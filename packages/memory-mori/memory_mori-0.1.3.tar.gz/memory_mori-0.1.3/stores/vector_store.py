"""
Vector Store Abstraction
Provides a clean interface to ChromaDB for vector storage and retrieval
"""

from typing import List, Dict, Optional, Any, cast
import numpy as np
import chromadb
from chromadb.config import Settings
from chromadb.api.types import QueryResult, GetResult, Metadata


class VectorStore:
    """
    Vector storage using ChromaDB.

    Handles document storage, embedding storage, and vector similarity search.
    """

    def __init__(
        self,
        collection_name: str,
        persist_directory: str = "./memory_mori_data"
    ):
        """
        Initialize the vector store.

        Args:
            collection_name: Name of the collection
            persist_directory: Directory for data persistence
        """
        self.collection_name = collection_name

        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Memory Mori vector storage"}
        )

    def add(
        self,
        ids: List[str],
        texts: List[str],
        embeddings: List[np.ndarray],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Add documents to the vector store.

        Args:
            ids: List of document IDs
            texts: List of document texts
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dictionaries
        """
        if metadatas is None:
            metadatas = [{} for _ in ids]

        # Convert numpy arrays to lists for ChromaDB
        embeddings_list = [emb.tolist() if isinstance(emb, np.ndarray) else emb for emb in embeddings]

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings_list,
            metadatas=cast(List[Metadata], metadatas)
        )

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10
    ) -> QueryResult:
        """
        Search for similar documents using vector similarity.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return

        Returns:
            QueryResult with ids, documents, distances, and metadatas
        """
        # Convert numpy array to list for ChromaDB
        query_list = query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding

        results = self.collection.query(
            query_embeddings=[query_list],
            n_results=top_k
        )

        return results

    def update_metadata(
        self,
        ids: List[str],
        metadatas: List[Dict[str, Any]]
    ):
        """
        Update metadata for documents.

        Args:
            ids: List of document IDs to update
            metadatas: List of metadata dictionaries
        """
        self.collection.update(
            ids=ids,
            metadatas=cast(List[Metadata], metadatas)
        )

    def delete(self, ids: List[str]):
        """
        Delete documents from the store.

        Args:
            ids: List of document IDs to delete
        """
        self.collection.delete(ids=ids)

    def get_all(self) -> GetResult:
        """
        Get all documents in the collection.

        Returns:
            GetResult with all documents and metadata
        """
        return self.collection.get(include=['documents', 'metadatas', 'embeddings'])

    def count(self) -> int:
        """
        Get the number of documents in the collection.

        Returns:
            Document count
        """
        return len(self.collection.get()['ids'])
