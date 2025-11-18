"""
Evaluation and Metrics Package
Comprehensive testing framework for Memory Mori
"""

from tests.metrics import (
    RetrievalMetrics,
    EntityMetrics,
    calculate_all_metrics,
    aggregate_metrics
)
from tests.test_dataset import (
    TestDataset,
    EntityTestDataset,
    get_test_dataset,
    get_entity_test_dataset
)
from tests.retrieval_evaluator import (
    RetrievalEvaluator,
    run_retrieval_evaluation
)
from tests.entity_evaluator import (
    EntityEvaluator,
    run_entity_evaluation
)
from tests.decay_evaluator import (
    DecayEvaluator,
    run_decay_evaluation
)
from tests.benchmark import (
    Benchmark,
    run_benchmark
)

__all__ = [
    # Metrics
    'RetrievalMetrics',
    'EntityMetrics',
    'calculate_all_metrics',
    'aggregate_metrics',

    # Test Datasets
    'TestDataset',
    'EntityTestDataset',
    'get_test_dataset',
    'get_entity_test_dataset',

    # Evaluators
    'RetrievalEvaluator',
    'EntityEvaluator',
    'DecayEvaluator',
    'Benchmark',

    # Runner Functions
    'run_retrieval_evaluation',
    'run_entity_evaluation',
    'run_decay_evaluation',
    'run_benchmark',
]
