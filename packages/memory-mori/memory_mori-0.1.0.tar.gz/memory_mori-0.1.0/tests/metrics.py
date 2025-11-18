"""
Evaluation Metrics
Calculates precision, recall, F1, and other retrieval metrics
"""

from typing import List, Set, Dict, Tuple


class RetrievalMetrics:
    """
    Calculate retrieval evaluation metrics.
    """

    @staticmethod
    def precision(retrieved: List[str], relevant: List[str]) -> float:
        """
        Calculate precision: |retrieved ∩ relevant| / |retrieved|

        Args:
            retrieved: List of retrieved document IDs
            relevant: List of relevant document IDs (ground truth)

        Returns:
            Precision score (0.0 to 1.0)
        """
        if not retrieved:
            return 0.0

        retrieved_set = set(retrieved)
        relevant_set = set(relevant)

        true_positives = len(retrieved_set & relevant_set)
        return true_positives / len(retrieved_set)

    @staticmethod
    def recall(retrieved: List[str], relevant: List[str]) -> float:
        """
        Calculate recall: |retrieved ∩ relevant| / |relevant|

        Args:
            retrieved: List of retrieved document IDs
            relevant: List of relevant document IDs (ground truth)

        Returns:
            Recall score (0.0 to 1.0)
        """
        if not relevant:
            return 0.0

        retrieved_set = set(retrieved)
        relevant_set = set(relevant)

        true_positives = len(retrieved_set & relevant_set)
        return true_positives / len(relevant_set)

    @staticmethod
    def f1_score(retrieved: List[str], relevant: List[str]) -> float:
        """
        Calculate F1 score: 2 * (precision * recall) / (precision + recall)

        Args:
            retrieved: List of retrieved document IDs
            relevant: List of relevant document IDs (ground truth)

        Returns:
            F1 score (0.0 to 1.0)
        """
        p = RetrievalMetrics.precision(retrieved, relevant)
        r = RetrievalMetrics.recall(retrieved, relevant)

        if p + r == 0:
            return 0.0

        return 2 * (p * r) / (p + r)

    @staticmethod
    def precision_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
        """
        Calculate precision at k (P@k).

        Args:
            retrieved: List of retrieved document IDs (ranked)
            relevant: List of relevant document IDs (ground truth)
            k: Cutoff position

        Returns:
            Precision@k score
        """
        return RetrievalMetrics.precision(retrieved[:k], relevant)

    @staticmethod
    def recall_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
        """
        Calculate recall at k (R@k).

        Args:
            retrieved: List of retrieved document IDs (ranked)
            relevant: List of relevant document IDs (ground truth)
            k: Cutoff position

        Returns:
            Recall@k score
        """
        return RetrievalMetrics.recall(retrieved[:k], relevant)

    @staticmethod
    def average_precision(retrieved: List[str], relevant: List[str]) -> float:
        """
        Calculate Average Precision (AP).

        Args:
            retrieved: List of retrieved document IDs (ranked)
            relevant: List of relevant document IDs (ground truth)

        Returns:
            Average Precision score
        """
        if not relevant:
            return 0.0

        relevant_set = set(relevant)
        score = 0.0
        num_hits = 0.0

        for i, doc_id in enumerate(retrieved):
            if doc_id in relevant_set:
                num_hits += 1.0
                score += num_hits / (i + 1.0)

        if num_hits == 0:
            return 0.0

        return score / len(relevant)

    @staticmethod
    def reciprocal_rank(retrieved: List[str], relevant: List[str]) -> float:
        """
        Calculate Reciprocal Rank (RR).

        Args:
            retrieved: List of retrieved document IDs (ranked)
            relevant: List of relevant document IDs (ground truth)

        Returns:
            Reciprocal Rank score
        """
        relevant_set = set(relevant)

        for i, doc_id in enumerate(retrieved):
            if doc_id in relevant_set:
                return 1.0 / (i + 1.0)

        return 0.0

    @staticmethod
    def ndcg_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain at k (NDCG@k).

        Args:
            retrieved: List of retrieved document IDs (ranked)
            relevant: List of relevant document IDs (ground truth)
            k: Cutoff position

        Returns:
            NDCG@k score
        """
        if not relevant:
            return 0.0

        relevant_set = set(relevant)

        # Calculate DCG@k
        dcg = 0.0
        for i, doc_id in enumerate(retrieved[:k]):
            if doc_id in relevant_set:
                # Binary relevance: 1 if relevant, 0 otherwise
                dcg += 1.0 / (i + 2.0)  # log2(i+2) approximation

        # Calculate IDCG@k (ideal DCG)
        idcg = 0.0
        for i in range(min(k, len(relevant))):
            idcg += 1.0 / (i + 2.0)

        if idcg == 0:
            return 0.0

        return dcg / idcg


class EntityMetrics:
    """
    Calculate entity extraction evaluation metrics.
    """

    @staticmethod
    def entity_precision(extracted: List[Dict], expected: List[Dict]) -> float:
        """
        Calculate precision for entity extraction.

        Args:
            extracted: List of extracted entities
            expected: List of expected entities

        Returns:
            Precision score
        """
        if not extracted:
            return 0.0

        # Convert to sets of (text, type) tuples for comparison
        extracted_set = {(e['text'].lower(), e['type']) for e in extracted}
        expected_set = {(e['text'].lower(), e['type']) for e in expected}

        true_positives = len(extracted_set & expected_set)
        return true_positives / len(extracted_set)

    @staticmethod
    def entity_recall(extracted: List[Dict], expected: List[Dict]) -> float:
        """
        Calculate recall for entity extraction.

        Args:
            extracted: List of extracted entities
            expected: List of expected entities

        Returns:
            Recall score
        """
        if not expected:
            return 0.0

        # Convert to sets of (text, type) tuples for comparison
        extracted_set = {(e['text'].lower(), e['type']) for e in extracted}
        expected_set = {(e['text'].lower(), e['type']) for e in expected}

        true_positives = len(extracted_set & expected_set)
        return true_positives / len(expected_set)

    @staticmethod
    def entity_f1(extracted: List[Dict], expected: List[Dict]) -> float:
        """
        Calculate F1 score for entity extraction.

        Args:
            extracted: List of extracted entities
            expected: List of expected entities

        Returns:
            F1 score
        """
        p = EntityMetrics.entity_precision(extracted, expected)
        r = EntityMetrics.entity_recall(extracted, expected)

        if p + r == 0:
            return 0.0

        return 2 * (p * r) / (p + r)


def calculate_all_metrics(retrieved: List[str], relevant: List[str]) -> Dict:
    """
    Calculate all retrieval metrics for a single query.

    Args:
        retrieved: List of retrieved document IDs
        relevant: List of relevant document IDs

    Returns:
        Dictionary with all metrics
    """
    metrics = RetrievalMetrics()

    return {
        'precision': metrics.precision(retrieved, relevant),
        'recall': metrics.recall(retrieved, relevant),
        'f1': metrics.f1_score(retrieved, relevant),
        'precision@3': metrics.precision_at_k(retrieved, relevant, 3),
        'precision@5': metrics.precision_at_k(retrieved, relevant, 5),
        'recall@3': metrics.recall_at_k(retrieved, relevant, 3),
        'recall@5': metrics.recall_at_k(retrieved, relevant, 5),
        'average_precision': metrics.average_precision(retrieved, relevant),
        'reciprocal_rank': metrics.reciprocal_rank(retrieved, relevant),
        'ndcg@3': metrics.ndcg_at_k(retrieved, relevant, 3),
        'ndcg@5': metrics.ndcg_at_k(retrieved, relevant, 5),
    }


def aggregate_metrics(metrics_list: List[Dict]) -> Dict:
    """
    Aggregate metrics across multiple queries.

    Args:
        metrics_list: List of metric dictionaries

    Returns:
        Dictionary with aggregated metrics
    """
    if not metrics_list:
        return {}

    # Calculate mean for each metric
    aggregated = {}
    metric_keys = metrics_list[0].keys()

    for key in metric_keys:
        values = [m[key] for m in metrics_list]
        aggregated[f'mean_{key}'] = sum(values) / len(values)

    # Add MAP (Mean Average Precision)
    if 'average_precision' in metrics_list[0]:
        aggregated['MAP'] = aggregated['mean_average_precision']

    # Add MRR (Mean Reciprocal Rank)
    if 'reciprocal_rank' in metrics_list[0]:
        aggregated['MRR'] = aggregated['mean_reciprocal_rank']

    return aggregated
