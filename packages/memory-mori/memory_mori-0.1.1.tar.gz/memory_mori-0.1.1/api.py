"""
Memory Mori Main API
Clean interface for intelligent memory storage and retrieval
"""

from typing import List, Dict, Optional, Any, cast
from datetime import datetime

from config import Memory, MemoryConfig
from core.search import HybridSearch
from core.entities import EntityExtractor
from core.profile import ProfileManager
from core.decay import DecayScorer
from stores.vector_store import VectorStore
from stores.profile_store import ProfileStore


class MemoryMori:
    """
    Main interface for the Memory Mori system.

    Combines hybrid search, entity extraction, profile learning, and time-based decay
    for intelligent memory storage and retrieval.
    """

    def __init__(self, config: Optional[MemoryConfig] = None):
        """
        Initialize Memory Mori.

        Args:
            config: Configuration object (uses defaults if None)
        """
        self.config = config or MemoryConfig()

        print("Initializing Memory Mori...")
        print("="*60)

        # Initialize vector store
        print(f"Loading vector store ({self.config.collection_name})...")
        self.vector_store = VectorStore(
            collection_name=self.config.collection_name,
            persist_directory=self.config.persist_directory
        )

        # Initialize hybrid search
        print(f"Loading embedding model ({self.config.embedding_model}) on device '{self.config.device}'...")
        self.hybrid_search = HybridSearch(
            embedding_model_name=self.config.embedding_model,
            alpha=self.config.alpha,
            device=self.config.device
        )

        # Initialize entity extractor if enabled
        self.entity_extractor = None
        if self.config.enable_entities:
            print(f"Loading entity model ({self.config.entity_model}) on device '{self.config.device}'...")
            self.entity_extractor = EntityExtractor(
                model_name=self.config.entity_model,
                device=self.config.device
            )

        # Initialize profile store and manager if enabled
        self.profile_store = None
        self.profile_manager = None
        if self.config.enable_profile:
            print("Initializing profile store...")
            self.profile_store = ProfileStore(
                db_path=self.config.profile_db_path
            )
            self.profile_manager = ProfileManager()

        # Initialize decay scorer
        print(f"Initializing decay scorer (λ={self.config.lambda_decay})...")
        self.decay_scorer = DecayScorer(
            lambda_value=self.config.lambda_decay,
            time_mode=self.config.decay_mode
        )

        print("="*60)
        print("Memory Mori ready!")
        print()

    def store(self, text: str, metadata: Optional[Dict] = None) -> str:
        """
        Store a memory (document).

        Args:
            text: Text content to store
            metadata: Optional metadata dictionary

        Returns:
            ID of the stored memory
        """
        if metadata is None:
            metadata = {}

        # Generate ID
        memory_id = f"mem_{datetime.now().timestamp()}_{hash(text) % 10000}"

        # Add timestamp if not present
        if 'created_at' not in metadata:
            metadata['created_at'] = datetime.now().isoformat()
        if 'last_accessed' not in metadata:
            metadata['last_accessed'] = metadata['created_at']

        # Extract and add entities if enabled
        if self.entity_extractor:
            entity_metadata = self.entity_extractor.format_for_metadata(text)
            metadata.update(entity_metadata)

        # Generate embedding
        embedding = self.hybrid_search.embed_text(text)

        # Store in vector store
        self.vector_store.add(
            ids=[memory_id],
            texts=[text],
            embeddings=[embedding],
            metadatas=[metadata]
        )

        # Index for BM25
        self.hybrid_search.index_documents([text], [memory_id])

        return memory_id

    def retrieve(
        self,
        query: str,
        filters: Optional[Dict] = None,
        max_items: int = 3,
        min_score: float = 0.3
    ) -> List[Memory]:
        """
        Retrieve relevant memories.

        Args:
            query: Search query
            filters: Optional filters (entity_type, min_confidence, etc.)
            max_items: Maximum number of items to return (default: 3)
            min_score: Minimum score threshold for results (default: 0.3)

        Returns:
            List of Memory objects
        """
        if filters is None:
            filters = {}

        # Extract entity filter if specified
        entity_filter = filters.get('entity_type')
        apply_decay = filters.get('apply_decay', True)
        min_confidence = filters.get('min_confidence', 0.0)

        # Generate query embedding
        query_embedding = self.hybrid_search.embed_text(query)

        # Get semantic results from vector store
        vector_results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=max_items * self.config.top_k_multiplier
        )

        semantic_results = self.hybrid_search.search_semantic(
            query_embedding,
            cast(Dict[str, Any], vector_results),
            top_k=max_items * self.config.top_k_multiplier
        )

        # Get keyword results
        keyword_results = self.hybrid_search.search_keyword(
            query,
            top_k=max_items * self.config.top_k_multiplier
        )

        # Combine results
        combined_results = self.hybrid_search.combine_results(
            semantic_results,
            keyword_results
        )

        # Filter by entity type if specified
        if entity_filter and self.entity_extractor:
            combined_results = [
                r for r in combined_results
                if self.entity_extractor.filter_by_entity(r['text'], entity_filter)
            ]

        # Apply decay if requested
        if apply_decay:
            combined_results = self.decay_scorer.apply_decay(
                combined_results,
                score_key='final_score'
            )
            # Use decayed score as final score
            for r in combined_results:
                r['final_score'] = r['decayed_score']

        # Filter by minimum confidence (from filters) or min_score parameter
        threshold = max(min_confidence, min_score)
        if threshold > 0:
            combined_results = [r for r in combined_results if r['final_score'] >= threshold]

        # Convert to Memory objects
        memories = []
        for result in combined_results[:max_items]:
            # Extract entities from metadata
            entities_json = result['metadata'].get('entities_json', '[]')
            try:
                import json
                entities = json.loads(entities_json)
            except Exception:
                entities = []

            # Parse timestamp
            timestamp_str = result['metadata'].get('created_at')
            timestamp = None
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                except Exception:
                    pass

            memory = Memory(
                id=result['id'],
                text=result['text'],
                score=result['final_score'],
                entities=entities,
                timestamp=timestamp,
                metadata=result.get('metadata', {})
            )
            memories.append(memory)

        return memories

    def get_context(
        self,
        query: str,
        max_items: int = 3,
        include_profile: bool = True
    ) -> str:
        """
        Get formatted context for LLM prompts.

        Args:
            query: Search query
            max_items: Maximum number of memory items to include (default: 3)
            include_profile: Whether to include user profile context

        Returns:
            Formatted context string
        """
        context_parts = []

        # Add profile context if enabled
        if include_profile and self.profile_store and self.profile_manager:
            facts = self.profile_store.get_all(min_confidence=0.5)
            profile_context = self.profile_manager.format_context(facts)
            if profile_context:
                context_parts.append(profile_context)

        # Add relevant memories
        memories = self.retrieve(query, max_items=max_items)
        if memories:
            context_parts.append("\nRelevant Information:")
            for i, memory in enumerate(memories, 1):
                context_parts.append(f"{i}. [{memory.score:.2f}] {memory.text}")

        # Add user query
        context_parts.append(f"\nUser Query: {query}")

        return "\n".join(context_parts)

    def update_profile(self, facts: Dict):
        """
        Manually update profile facts.

        Args:
            facts: Dictionary mapping keys to (value, category, confidence) tuples
                   Example: {"job_title": ("Software Engineer", "role", 0.9)}
        """
        if not self.profile_store:
            raise RuntimeError("Profile store is not enabled in configuration")

        for key, (value, category, confidence) in facts.items():
            self.profile_store.set(key, value, category, confidence)

    def get_profile(self, category: Optional[str] = None) -> Dict:
        """
        Get profile facts.

        Args:
            category: Optional category filter

        Returns:
            Dictionary of profile facts
        """
        if not self.profile_store:
            return {}

        facts = self.profile_store.get_all(category=category)

        # Convert to simple dictionary
        result = {}
        for fact in facts:
            result[fact['key']] = {
                'value': fact['value'],
                'category': fact['category'],
                'confidence': fact['confidence']
            }

        return result

    def cleanup(self, threshold: float = 0.01) -> int:
        """
        Clean up stale memories based on decay.

        Args:
            threshold: Decay threshold below which memories are removed

        Returns:
            Number of memories cleaned up
        """
        all_data = self.vector_store.get_all()
        ids_to_delete = []

        # Ensure metadatas exists
        metadatas = all_data.get('metadatas')
        if not metadatas:
            return 0

        for i, doc_id in enumerate(all_data['ids']):
            metadata = metadatas[i] if i < len(metadatas) else {}

            # Parse timestamps
            created_at_str = metadata.get('created_at')
            last_accessed_str = metadata.get('last_accessed')

            if not created_at_str or not isinstance(created_at_str, str):
                continue

            try:
                created_at = datetime.fromisoformat(created_at_str)
                last_accessed = datetime.fromisoformat(last_accessed_str) if last_accessed_str and isinstance(last_accessed_str, str) else None

                # Check if should be cleaned up
                if self.decay_scorer.should_cleanup(created_at, last_accessed, threshold):
                    ids_to_delete.append(doc_id)
            except Exception:
                continue

        # Delete stale memories
        if ids_to_delete:
            self.vector_store.delete(ids_to_delete)

        return len(ids_to_delete)
