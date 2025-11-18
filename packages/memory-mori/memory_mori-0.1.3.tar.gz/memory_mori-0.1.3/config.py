"""
Configuration and data classes for Memory Mori
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List, Any, Literal


@dataclass
class Memory:
    """
    Represents a retrieved memory from the system.
    """
    id: str
    text: str
    score: float
    entities: List[Dict[str, str]] = field(default_factory=list)
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"Memory(id={self.id}, score={self.score:.3f}, text={self.text[:50]}...)"


@dataclass
class MemoryConfig:
    """
    Configuration for the Memory Mori system.
    """
    # Search configuration
    alpha: float = 0.8  # Hybrid search weight (0=keyword, 1=semantic)
    embedding_model: str = "all-mpnet-base-v2"

    # Decay configuration
    lambda_decay: float = 0.05  # Decay rate (0.05 = slow)
    decay_mode: str = "combined"  # 'creation', 'access', or 'combined'

    # Entity extraction
    entity_model: str = "en_core_web_lg"  # Options: en_core_web_sm, en_core_web_md, en_core_web_lg
    enable_entities: bool = True

    # Profile store
    enable_profile: bool = True

    # Storage paths
    persist_directory: str = "./memory_mori_data"
    profile_db_path: str = "./memory_mori_profile.db"

    # Collection name
    collection_name: str = "memory_mori"

    # Performance
    top_k_multiplier: int = 2  # Retrieve 2x results before filtering

    # Device configuration
    device: Literal["auto", "cpu", "cuda"] = "auto"  # Device for models: auto (detect GPU), cpu, cuda

    def __post_init__(self):
        """Validate configuration values."""
        if not 0 <= self.alpha <= 1:
            raise ValueError(f"alpha must be between 0 and 1, got {self.alpha}")

        if self.lambda_decay < 0:
            raise ValueError(f"lambda_decay must be positive, got {self.lambda_decay}")

        if self.decay_mode not in ['creation', 'access', 'combined']:
            raise ValueError(f"decay_mode must be 'creation', 'access', or 'combined', got {self.decay_mode}")

        if self.device not in ['auto', 'cpu', 'cuda']:
            raise ValueError(f"device must be 'auto', 'cpu', or 'cuda', got {self.device}")

    @classmethod
    def from_preset(cls, preset: str) -> 'MemoryConfig':
        """
        Create configuration from preset.

        Args:
            preset: One of 'minimal', 'standard', 'full'

        Returns:
            MemoryConfig instance
        """
        presets = {
            'minimal': {
                'alpha': 0.8,
                'lambda_decay': 0.05,
                'enable_entities': False,
                'enable_profile': False,
            },
            'standard': {
                'alpha': 0.8,
                'lambda_decay': 0.05,
                'enable_entities': True,
                'enable_profile': True,
            },
            'full': {
                'alpha': 0.8,
                'lambda_decay': 0.05,
                'enable_entities': True,
                'enable_profile': True,
            },
            'high_accuracy': {
                'alpha': 0.8,
                'lambda_decay': 0.05,
                'enable_entities': True,
                'enable_profile': True,
                'entity_model': 'en_core_web_lg',  # Use larger model for better accuracy
            },
        }

        if preset not in presets:
            raise ValueError(f"Unknown preset '{preset}'. Choose from: {list(presets.keys())}")

        return cls(**presets[preset])
