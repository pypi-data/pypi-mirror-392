"""
Test Dataset for Evaluation
Contains ground truth data for testing retrieval quality
"""

from typing import List, Dict, Tuple


class TestDataset:
    """
    Test dataset with documents and ground truth query-document pairs.
    """

    def __init__(self):
        """Initialize the test dataset."""
        self.documents = self._create_documents()
        self.queries = self._create_queries()
        self.ground_truth = self._create_ground_truth()

    def _create_documents(self) -> List[Dict]:
        """
        Create test documents with IDs and metadata.

        Returns:
            List of document dictionaries
        """
        return [
            {
                "id": "doc_1",
                "text": "Python is a high-level programming language known for its simplicity and readability",
                "category": "programming",
                "entities": ["Python"]
            },
            {
                "id": "doc_2",
                "text": "JavaScript is essential for modern web development and runs in browsers",
                "category": "programming",
                "entities": ["JavaScript"]
            },
            {
                "id": "doc_3",
                "text": "Machine learning with PyTorch enables building neural networks efficiently",
                "category": "ml",
                "entities": ["PyTorch"]
            },
            {
                "id": "doc_4",
                "text": "React is a JavaScript library for building user interfaces",
                "category": "frontend",
                "entities": ["React", "JavaScript"]
            },
            {
                "id": "doc_5",
                "text": "Docker containers provide isolated environments for application deployment",
                "category": "devops",
                "entities": ["Docker"]
            },
            {
                "id": "doc_6",
                "text": "TensorFlow is Google's machine learning framework for deep learning",
                "category": "ml",
                "entities": ["TensorFlow", "Google"]
            },
            {
                "id": "doc_7",
                "text": "FastAPI is a modern Python web framework with automatic API documentation",
                "category": "web",
                "entities": ["FastAPI", "Python"]
            },
            {
                "id": "doc_8",
                "text": "Kubernetes orchestrates containerized applications across clusters",
                "category": "devops",
                "entities": ["Kubernetes"]
            },
            {
                "id": "doc_9",
                "text": "TypeScript adds static typing to JavaScript for better developer experience",
                "category": "programming",
                "entities": ["TypeScript", "JavaScript"]
            },
            {
                "id": "doc_10",
                "text": "Natural language processing with spaCy enables entity extraction",
                "category": "ml",
                "entities": ["spaCy"]
            },
        ]

    def _create_queries(self) -> List[Dict]:
        """
        Create test queries.

        Returns:
            List of query dictionaries
        """
        return [
            {
                "id": "q_1",
                "text": "Python programming language",
                "intent": "Find Python-related content"
            },
            {
                "id": "q_2",
                "text": "web development frameworks",
                "intent": "Find web development tools"
            },
            {
                "id": "q_3",
                "text": "machine learning libraries",
                "intent": "Find ML frameworks"
            },
            {
                "id": "q_4",
                "text": "container orchestration",
                "intent": "Find containerization tools"
            },
            {
                "id": "q_5",
                "text": "JavaScript frameworks",
                "intent": "Find JavaScript-related tools"
            },
            {
                "id": "q_6",
                "text": "deep learning with neural networks",
                "intent": "Find deep learning frameworks"
            },
            {
                "id": "q_7",
                "text": "Python web APIs",
                "intent": "Find Python web frameworks"
            },
            {
                "id": "q_8",
                "text": "entity extraction NLP",
                "intent": "Find NLP tools"
            },
        ]

    def _create_ground_truth(self) -> Dict[str, List[str]]:
        """
        Create ground truth mappings: query_id -> list of relevant doc_ids.

        Returns:
            Dictionary mapping query IDs to lists of relevant document IDs
        """
        return {
            "q_1": ["doc_1", "doc_7"],  # Python programming
            "q_2": ["doc_2", "doc_4", "doc_7"],  # Web development
            "q_3": ["doc_3", "doc_6", "doc_10"],  # Machine learning
            "q_4": ["doc_5", "doc_8"],  # Container orchestration
            "q_5": ["doc_2", "doc_4", "doc_9"],  # JavaScript
            "q_6": ["doc_3", "doc_6"],  # Deep learning
            "q_7": ["doc_7"],  # Python web APIs
            "q_8": ["doc_10"],  # NLP entity extraction
        }

    def get_document_by_id(self, doc_id: str) -> Dict:
        """Get document by ID."""
        for doc in self.documents:
            if doc["id"] == doc_id:
                return doc
        return None

    def get_query_by_id(self, query_id: str) -> Dict:
        """Get query by ID."""
        for query in self.queries:
            if query["id"] == query_id:
                return query
        return None

    def get_relevant_docs(self, query_id: str) -> List[str]:
        """Get list of relevant document IDs for a query."""
        return self.ground_truth.get(query_id, [])


class EntityTestDataset:
    """
    Test dataset for entity extraction evaluation.
    """

    def __init__(self):
        """Initialize entity test dataset."""
        self.test_cases = self._create_test_cases()

    def _create_test_cases(self) -> List[Dict]:
        """
        Create test cases with expected entities.

        Returns:
            List of test case dictionaries
        """
        return [
            {
                "text": "Microsoft released .NET 8 with new features",
                "expected_entities": [
                    {"text": "Microsoft", "type": "ORG"},
                    {"text": ".NET 8", "type": "PRODUCT"}
                ]
            },
            {
                "text": "Elon Musk founded SpaceX and Tesla Motors",
                "expected_entities": [
                    {"text": "Elon Musk", "type": "PERSON"},
                    {"text": "SpaceX", "type": "ORG"},
                    {"text": "Tesla Motors", "type": "ORG"}
                ]
            },
            {
                "text": "The World Cup 2026 will be held in the United States",
                "expected_entities": [
                    {"text": "World Cup 2026", "type": "EVENT"},
                    {"text": "2026", "type": "DATE"},
                    {"text": "United States", "type": "ORG"}
                ]
            },
            {
                "text": "Python 3.12 was released in October 2023",
                "expected_entities": [
                    {"text": "Python 3.12", "type": "PRODUCT"},
                    {"text": "October 2023", "type": "DATE"}
                ]
            },
            {
                "text": "Google announced Gemini AI model at Google I/O",
                "expected_entities": [
                    {"text": "Google", "type": "ORG"},
                    {"text": "Gemini", "type": "PRODUCT"},
                    {"text": "Google I/O", "type": "EVENT"}
                ]
            },
        ]


def get_test_dataset() -> TestDataset:
    """
    Get the standard test dataset.

    Returns:
        TestDataset instance
    """
    return TestDataset()


def get_entity_test_dataset() -> EntityTestDataset:
    """
    Get the entity test dataset.

    Returns:
        EntityTestDataset instance
    """
    return EntityTestDataset()
