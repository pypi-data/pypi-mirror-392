"""
Retrieval Quality Evaluator
Tests retrieval performance against ground truth
"""

from typing import Dict, List
from api import MemoryMori
from config import MemoryConfig
from tests.test_dataset import get_test_dataset
from tests.metrics import calculate_all_metrics, aggregate_metrics


class RetrievalEvaluator:
    """
    Evaluate retrieval quality against ground truth.
    """

    def __init__(self, config: MemoryConfig = None):
        """
        Initialize retrieval evaluator.

        Args:
            config: MemoryConfig for testing (uses default if None)
        """
        self.config = config or MemoryConfig(
            collection_name="eval",
            persist_directory="./eval_data",
            profile_db_path="./eval_profile.db"
        )
        self.dataset = get_test_dataset()

    def setup(self):
        """Initialize MemoryMori and load test documents."""
        self.mm = MemoryMori(self.config)

        # Load test documents
        for doc in self.dataset.documents:
            self.mm.store(doc['text'], metadata={'doc_id': doc['id']})

    def evaluate_query(self, query_id: str, max_items: int = 5) -> Dict:
        """
        Evaluate a single query.

        Args:
            query_id: Query ID from test dataset
            max_items: Number of items to retrieve

        Returns:
            Dictionary with metrics and results
        """
        query = self.dataset.get_query_by_id(query_id)
        relevant_docs = self.dataset.get_relevant_docs(query_id)

        if not query:
            return {}

        # Retrieve memories
        results = self.mm.retrieve(query['text'], max_items=max_items)

        # Extract document IDs from metadata
        retrieved_ids = []
        for memory in results:
            doc_id = memory.metadata.get('doc_id')
            if doc_id:
                retrieved_ids.append(doc_id)

        # Calculate metrics
        metrics = calculate_all_metrics(retrieved_ids, relevant_docs)

        return {
            'query_id': query_id,
            'query_text': query['text'],
            'num_retrieved': len(retrieved_ids),
            'num_relevant': len(relevant_docs),
            'retrieved': retrieved_ids,
            'relevant': relevant_docs,
            'metrics': metrics
        }

    def evaluate_all(self, max_items: int = 5, verbose: bool = False) -> Dict:
        """
        Evaluate all queries in the test dataset.

        Args:
            max_items: Number of items to retrieve per query
            verbose: Print per-query results

        Returns:
            Dictionary with aggregated results
        """
        self.setup()

        results = []
        metrics_list = []

        for query in self.dataset.queries:
            result = self.evaluate_query(query['id'], max_items)

            if result:
                results.append(result)
                metrics_list.append(result['metrics'])

                if verbose:
                    print(f"\nQuery: {result['query_text']}")
                    print(f"Retrieved: {result['num_retrieved']}, Relevant: {result['num_relevant']}")
                    print(f"P: {result['metrics']['precision']:.3f}, "
                          f"R: {result['metrics']['recall']:.3f}, "
                          f"F1: {result['metrics']['f1']:.3f}")

        # Aggregate metrics across all queries
        aggregated = aggregate_metrics(metrics_list)

        return {
            'num_queries': len(results),
            'max_items': max_items,
            'aggregated_metrics': aggregated,
            'per_query_results': results
        }

    def compare_alpha_values(self, alpha_values: List[float] = None) -> Dict:
        """
        Compare retrieval performance at different alpha values.

        Args:
            alpha_values: List of alpha values to test

        Returns:
            Comparison results
        """
        if alpha_values is None:
            alpha_values = [0.0, 0.3, 0.5, 0.7, 0.9, 1.0]

        comparison_results = {}

        for alpha in alpha_values:
            # Create config with specific alpha
            config = MemoryConfig(
                collection_name=f"eval_alpha_{alpha}",
                persist_directory=f"./eval_alpha_{alpha}_data",
                profile_db_path=f"./eval_alpha_{alpha}.db",
                alpha=alpha
            )

            # Create evaluator with this config
            evaluator = RetrievalEvaluator(config)

            # Evaluate
            results = evaluator.evaluate_all(max_items=5)

            comparison_results[alpha] = {
                'aggregated_metrics': results['aggregated_metrics'],
                'mean_f1': results['aggregated_metrics']['mean_f1'],
                'MAP': results['aggregated_metrics']['MAP'],
                'MRR': results['aggregated_metrics']['MRR']
            }

        return comparison_results


def run_retrieval_evaluation(verbose: bool = True, max_items: int = 5) -> Dict:
    """
    Run complete retrieval evaluation.

    Args:
        verbose: Print detailed output
        max_items: Number of items to retrieve

    Returns:
        Evaluation results
    """
    if verbose:
        print("="*80)
        print("Retrieval Quality Evaluation")
        print("="*80)

    evaluator = RetrievalEvaluator()
    results = evaluator.evaluate_all(max_items=max_items, verbose=verbose)

    if verbose:
        print("\n" + "="*80)
        print("AGGREGATED METRICS")
        print("="*80)

        metrics = results['aggregated_metrics']
        print(f"Queries evaluated: {results['num_queries']}")
        print(f"Max items per query: {results['max_items']}")
        print()
        print(f"Mean Precision: {metrics['mean_precision']:.3f}")
        print(f"Mean Recall: {metrics['mean_recall']:.3f}")
        print(f"Mean F1: {metrics['mean_f1']:.3f}")
        print(f"P@3: {metrics['mean_precision@3']:.3f}")
        print(f"P@5: {metrics['mean_precision@5']:.3f}")
        print(f"MAP (Mean Average Precision): {metrics['MAP']:.3f}")
        print(f"MRR (Mean Reciprocal Rank): {metrics['MRR']:.3f}")
        print(f"NDCG@3: {metrics['mean_ndcg@3']:.3f}")
        print(f"NDCG@5: {metrics['mean_ndcg@5']:.3f}")

    return results
