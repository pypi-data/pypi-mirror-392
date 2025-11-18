"""
Entity Extraction Core Module
Uses spaCy for Named Entity Recognition (NER)
"""

import spacy
import json
import logging
from typing import List, Dict, Literal, cast
from spacy.pipeline import EntityRuler
from .device import check_spacy_gpu_support

logger = logging.getLogger(__name__)


class EntityExtractor:
    """
    Extract entities from text using spaCy NER with custom patterns for tech terms.

    Maps spaCy entity labels to a custom taxonomy suitable for search.
    """

    # Map spaCy labels to our taxonomy
    ENTITY_TYPE_MAPPING = {
        'PERSON': 'PERSON',
        'ORG': 'ORG',
        'GPE': 'ORG',  # Geopolitical entities often represent organizations in context
        'DATE': 'DATE',
        'TIME': 'DATE',
        'PRODUCT': 'PRODUCT',
        'EVENT': 'EVENT',
        'WORK_OF_ART': 'PRODUCT',  # Map work of art to product
        'LAW': 'PRODUCT',
        'LANGUAGE': 'PRODUCT',
        'FAC': 'ORG',  # Facilities
        'LOC': 'ORG',  # Locations
    }

    # Core entity types we care about
    CORE_TYPES = {'PERSON', 'ORG', 'DATE', 'PRODUCT', 'EVENT'}

    # Custom patterns for tech terms that spaCy often misses
    TECH_PATTERNS = [
        # Programming Languages
        {"label": "PRODUCT", "pattern": "Python"},
        {"label": "PRODUCT", "pattern": "JavaScript"},
        {"label": "PRODUCT", "pattern": "TypeScript"},
        {"label": "PRODUCT", "pattern": "Java"},
        {"label": "PRODUCT", "pattern": "C++"},
        {"label": "PRODUCT", "pattern": "C#"},
        {"label": "PRODUCT", "pattern": "Ruby"},
        {"label": "PRODUCT", "pattern": "Go"},
        {"label": "PRODUCT", "pattern": "Rust"},
        {"label": "PRODUCT", "pattern": "Swift"},
        {"label": "PRODUCT", "pattern": "Kotlin"},
        {"label": "PRODUCT", "pattern": "PHP"},

        # Frameworks & Libraries
        {"label": "PRODUCT", "pattern": "React"},
        {"label": "PRODUCT", "pattern": "Vue"},
        {"label": "PRODUCT", "pattern": "Angular"},
        {"label": "PRODUCT", "pattern": "Django"},
        {"label": "PRODUCT", "pattern": "Flask"},
        {"label": "PRODUCT", "pattern": "FastAPI"},
        {"label": "PRODUCT", "pattern": "Express"},
        {"label": "PRODUCT", "pattern": "Next.js"},
        {"label": "PRODUCT", "pattern": [{"LOWER": "next"}, {"LOWER": "."}, {"LOWER": "js"}]},
        {"label": "PRODUCT", "pattern": "TensorFlow"},
        {"label": "PRODUCT", "pattern": "PyTorch"},
        {"label": "PRODUCT", "pattern": "scikit-learn"},

        # Databases
        {"label": "PRODUCT", "pattern": "PostgreSQL"},
        {"label": "PRODUCT", "pattern": "MySQL"},
        {"label": "PRODUCT", "pattern": "MongoDB"},
        {"label": "PRODUCT", "pattern": "Redis"},
        {"label": "PRODUCT", "pattern": "Elasticsearch"},
        {"label": "PRODUCT", "pattern": "ChromaDB"},

        # Cloud & DevOps
        {"label": "PRODUCT", "pattern": "Docker"},
        {"label": "PRODUCT", "pattern": "Kubernetes"},
        {"label": "PRODUCT", "pattern": "AWS"},
        {"label": "PRODUCT", "pattern": "Azure"},
        {"label": "PRODUCT", "pattern": "GCP"},
        {"label": "PRODUCT", "pattern": [{"LOWER": "google"}, {"LOWER": "cloud"}]},
        {"label": "PRODUCT", "pattern": "Terraform"},
        {"label": "PRODUCT", "pattern": "Jenkins"},

        # AI/ML
        {"label": "PRODUCT", "pattern": "GPT"},
        {"label": "PRODUCT", "pattern": [{"TEXT": {"REGEX": "GPT-[0-9]+"}}]},
        {"label": "PRODUCT", "pattern": "Claude"},
        {"label": "PRODUCT", "pattern": "LLaMA"},
        {"label": "PRODUCT", "pattern": "BERT"},
        {"label": "PRODUCT", "pattern": "Gemini"},

        # Version patterns (e.g., .NET 8, Python 3.12)
        {"label": "PRODUCT", "pattern": [{"LOWER": "."}, {"LOWER": "net"}, {"IS_DIGIT": True}]},
        {"label": "PRODUCT", "pattern": [{"ORTH": "Python"}, {"IS_DIGIT": True, "OP": "+"}]},
    ]

    def __init__(
        self,
        model_name: str = "en_core_web_md",
        device: Literal["auto", "cpu", "cuda"] = "auto"
    ):
        """
        Initialize the entity extractor with custom tech patterns.

        Args:
            model_name: Name of the spaCy model to use
            device: Device to run model on ("auto", "cpu", or "cuda")
        """
        # Try to use GPU if requested and available
        self.device = device
        self.using_gpu = False

        if device in ["auto", "cuda"]:
            if check_spacy_gpu_support():
                try:
                    # Import prefer_gpu from spacy.util
                    from spacy.util import prefer_gpu  # type: ignore
                    prefer_gpu()
                    self.using_gpu = True
                    logger.info("spaCy using GPU for entity extraction")
                except Exception as e:
                    logger.warning(f"Failed to enable spaCy GPU: {e}. Using CPU.")
            elif device == "cuda":
                logger.warning("CUDA requested for spaCy but cupy not installed or GPU not available. Using CPU.")

        self.nlp = spacy.load(model_name)

        # Add entity ruler with custom patterns
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = cast(EntityRuler, self.nlp.add_pipe("entity_ruler", before="ner"))
            ruler.add_patterns(self.TECH_PATTERNS)

    def extract(self, text: str) -> List[Dict]:
        """
        Extract entities from text.

        Args:
            text: Input text to process

        Returns:
            List of entity dictionaries with text, type, start, and end positions
        """
        doc = self.nlp(text)

        entities = []
        for ent in doc.ents:
            # Map to our taxonomy
            entity_type = self.ENTITY_TYPE_MAPPING.get(ent.label_, None)

            # Only include entities that map to our core types
            if entity_type in self.CORE_TYPES:
                entities.append({
                    'text': ent.text,
                    'type': entity_type,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'original_label': ent.label_
                })

        return entities

    def extract_types(self, text: str) -> List[str]:
        """
        Extract just the entity types from text.

        Args:
            text: Input text to process

        Returns:
            List of unique entity types found in the text
        """
        entities = self.extract(text)
        return list(set([e['type'] for e in entities]))

    def filter_by_entity(self, text: str, entity_type: str) -> bool:
        """
        Check if text contains a specific entity type.

        Args:
            text: Input text to check
            entity_type: Type of entity to look for

        Returns:
            True if text contains the entity type, False otherwise
        """
        entities = self.extract(text)
        return any(e['type'] == entity_type for e in entities)

    def format_for_metadata(self, text: str) -> Dict:
        """
        Format extracted entities for storage in metadata.

        Note: ChromaDB only supports simple types (str, int, float, bool) in metadata.
        We store entities as a JSON string and entity_types as a comma-separated string.

        Args:
            text: Input text to process

        Returns:
            Dictionary with entities and entity_types ready for metadata storage
        """
        entities = self.extract(text)
        entity_types = list(set([e['type'] for e in entities]))

        return {
            'entities_json': json.dumps(entities),  # Store as JSON string
            'entity_types': ','.join(entity_types) if entity_types else ''  # Store as CSV string
        }
