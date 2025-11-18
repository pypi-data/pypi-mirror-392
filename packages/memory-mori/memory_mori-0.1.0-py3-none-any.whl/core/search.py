"""
Hybrid Search Core Module
Combines semantic search (embeddings) with keyword search (BM25)
"""

import numpy as np
from typing import List, Dict, Optional, Literal
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from .device import DeviceManager


class HybridSearch:
    """
    Hybrid search combining semantic and keyword-based search.

    Attributes:
        embedding_model: SentenceTransformer for semantic embeddings
        alpha: Weight for semantic search (1-alpha for keyword search)
        bm25: BM25 index for keyword search
        documents: List of documents for BM25 indexing
        doc_ids: List of document IDs
    """

    def __init__(
        self,
        embedding_model_name: str = "all-mpnet-base-v2",
        alpha: float = 0.7,
        device: Literal["auto", "cpu", "cuda"] = "auto"
    ):
        """
        Initialize the hybrid search component.

        Args:
            embedding_model_name: Name of the sentence-transformers model
            alpha: Weight for semantic search (0-1), keyword gets (1-alpha)
            device: Device to run embedding model on ("auto", "cpu", or "cuda")
        """
        # Initialize device manager
        self.device_manager = DeviceManager(device)

        # Initialize embedding model with device
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.embedding_model.to(self.device_manager.get_torch_device())

        self.alpha = alpha

        # BM25 will be initialized when documents are indexed
        self.bm25 = None
        self.documents = []
        self.doc_ids = []

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a text string.

        Args:
            text: Input text to embed

        Returns:
            Embedding vector
        """
        return self.embedding_model.encode(text, convert_to_numpy=True)

    def index_documents(
        self,
        texts: List[str],
        ids: List[str]
    ):
        """
        Index documents for BM25 keyword search.

        Args:
            texts: List of document texts
            ids: List of document IDs
        """
        self.documents.extend(texts)
        self.doc_ids.extend(ids)

        # Tokenize for BM25 (simple whitespace tokenization)
        tokenized_docs = [doc.lower().split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_docs)

    def search_semantic(
        self,
        query_embedding: np.ndarray,
        results: Dict,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Format semantic search results from vector store.

        Args:
            query_embedding: Query embedding (not used, for interface consistency)
            results: Raw results from vector store
            top_k: Number of results to return

        Returns:
            Formatted search results
        """
        formatted_results = []

        if not results or not results.get('ids'):
            return formatted_results

        for i in range(min(len(results['ids'][0]), top_k)):
            metadata = results['metadatas'][0][i] if results.get('metadatas') else {}

            formatted_results.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'score': 1 - results['distances'][0][i],  # Convert distance to similarity
                'metadata': metadata
            })

        return formatted_results

    def search_keyword(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Perform keyword search using BM25.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of results with scores
        """
        if self.bm25 is None:
            return []

        # Tokenize query
        tokenized_query = query.lower().split()

        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)

        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k]

        # Format results
        formatted_results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include documents with non-zero scores
                formatted_results.append({
                    'id': self.doc_ids[idx],
                    'text': self.documents[idx],
                    'score': float(scores[idx]),
                    'metadata': {}
                })

        return formatted_results

    @staticmethod
    def normalize_scores(results: List[Dict]) -> List[Dict]:
        """
        Normalize scores to [0, 1] range using min-max normalization.

        Args:
            results: List of results with scores

        Returns:
            Results with normalized scores
        """
        if not results:
            return results

        scores = [r['score'] for r in results]
        min_score = min(scores)
        max_score = max(scores)

        if max_score == min_score:
            # All scores are the same
            for r in results:
                r['normalized_score'] = 1.0
        else:
            for r in results:
                r['normalized_score'] = (r['score'] - min_score) / (max_score - min_score)

        return results

    def combine_results(
        self,
        semantic_results: List[Dict],
        keyword_results: List[Dict],
        alpha: Optional[float] = None
    ) -> List[Dict]:
        """
        Combine semantic and keyword search results.

        Args:
            semantic_results: Results from semantic search
            keyword_results: Results from keyword search
            alpha: Weight for semantic search (overrides instance alpha if provided)

        Returns:
            Combined and re-ranked results
        """
        if alpha is None:
            alpha = self.alpha

        # Normalize scores
        semantic_results = self.normalize_scores(semantic_results)
        keyword_results = self.normalize_scores(keyword_results)

        # Combine results
        combined_scores = {}

        # Add semantic scores
        for result in semantic_results:
            doc_id = result['id']
            combined_scores[doc_id] = {
                'text': result['text'],
                'metadata': result['metadata'],
                'semantic_score': result['normalized_score'],
                'keyword_score': 0.0
            }

        # Add keyword scores
        for result in keyword_results:
            doc_id = result['id']
            if doc_id in combined_scores:
                combined_scores[doc_id]['keyword_score'] = result['normalized_score']
            else:
                combined_scores[doc_id] = {
                    'text': result['text'],
                    'metadata': result['metadata'],
                    'semantic_score': 0.0,
                    'keyword_score': result['normalized_score']
                }

        # Calculate final scores
        final_results = []
        for doc_id, scores in combined_scores.items():
            final_score = (
                alpha * scores['semantic_score'] +
                (1 - alpha) * scores['keyword_score']
            )
            final_results.append({
                'id': doc_id,
                'text': scores['text'],
                'metadata': scores['metadata'],
                'final_score': final_score,
                'semantic_score': scores['semantic_score'],
                'keyword_score': scores['keyword_score']
            })

        # Sort by final score
        final_results.sort(key=lambda x: x['final_score'], reverse=True)

        return final_results
