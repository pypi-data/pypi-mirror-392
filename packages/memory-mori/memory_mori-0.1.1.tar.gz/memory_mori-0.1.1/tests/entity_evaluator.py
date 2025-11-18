"""
Entity Extraction Evaluator
Tests entity extraction accuracy against ground truth
"""

from typing import List, Dict
from core.entities import EntityExtractor
from tests.metrics import EntityMetrics
from tests.test_dataset import get_entity_test_dataset


class EntityEvaluator:
    """
    Evaluate entity extraction performance.
    """

    def __init__(self, entity_extractor: EntityExtractor = None):
        """
        Initialize entity evaluator.

        Args:
            entity_extractor: EntityExtractor instance (creates new if None)
        """
        self.entity_extractor = entity_extractor or EntityExtractor()
        self.metrics = EntityMetrics()

    def evaluate_single(self, text: str, expected_entities: List[Dict]) -> Dict:
        """
        Evaluate entity extraction on a single text.

        Args:
            text: Input text
            expected_entities: List of expected entities

        Returns:
            Dictionary with metrics and details
        """
        # Extract entities
        extracted = self.entity_extractor.extract(text)

        # Calculate metrics
        precision = self.metrics.entity_precision(extracted, expected_entities)
        recall = self.metrics.entity_recall(extracted, expected_entities)
        f1 = self.metrics.entity_f1(extracted, expected_entities)

        return {
            'text': text,
            'extracted_count': len(extracted),
            'expected_count': len(expected_entities),
            'extracted': extracted,
            'expected': expected_entities,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }

    def evaluate_dataset(self, verbose: bool = False) -> Dict:
        """
        Evaluate on the full entity test dataset.

        Args:
            verbose: Print detailed results

        Returns:
            Dictionary with aggregated results
        """
        dataset = get_entity_test_dataset()
        results = []

        for test_case in dataset.test_cases:
            result = self.evaluate_single(
                test_case['text'],
                test_case['expected_entities']
            )
            results.append(result)

            if verbose:
                print(f"\nText: {result['text']}")
                print(f"Extracted: {result['extracted_count']}, Expected: {result['expected_count']}")
                print(f"P: {result['precision']:.3f}, R: {result['recall']:.3f}, F1: {result['f1']:.3f}")

        # Aggregate metrics
        avg_precision = sum(r['precision'] for r in results) / len(results)
        avg_recall = sum(r['recall'] for r in results) / len(results)
        avg_f1 = sum(r['f1'] for r in results) / len(results)

        return {
            'test_cases': len(results),
            'average_precision': avg_precision,
            'average_recall': avg_recall,
            'average_f1': avg_f1,
            'detailed_results': results
        }

    def analyze_errors(self) -> Dict:
        """
        Analyze common entity extraction errors.

        Returns:
            Dictionary with error analysis
        """
        dataset = get_entity_test_dataset()

        false_positives = []  # Extracted but not expected
        false_negatives = []  # Expected but not extracted

        for test_case in dataset.test_cases:
            extracted = self.entity_extractor.extract(test_case['text'])
            expected = test_case['expected_entities']

            # Convert to sets for comparison
            extracted_set = {(e['text'].lower(), e['type']) for e in extracted}
            expected_set = {(e['text'].lower(), e['type']) for e in expected}

            # Find false positives
            fp = extracted_set - expected_set
            if fp:
                false_positives.extend([(test_case['text'], item) for item in fp])

            # Find false negatives
            fn = expected_set - extracted_set
            if fn:
                false_negatives.extend([(test_case['text'], item) for item in fn])

        return {
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'fp_count': len(false_positives),
            'fn_count': len(false_negatives)
        }


def run_entity_evaluation(verbose: bool = True) -> Dict:
    """
    Run complete entity extraction evaluation.

    Args:
        verbose: Print detailed output

    Returns:
        Evaluation results
    """
    if verbose:
        print("="*80)
        print("Entity Extraction Evaluation")
        print("="*80)

    evaluator = EntityEvaluator()

    # Evaluate on test dataset
    results = evaluator.evaluate_dataset(verbose=verbose)

    if verbose:
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Test cases: {results['test_cases']}")
        print(f"Average Precision: {results['average_precision']:.3f}")
        print(f"Average Recall: {results['average_recall']:.3f}")
        print(f"Average F1: {results['average_f1']:.3f}")

        # Error analysis
        print("\n" + "="*80)
        print("ERROR ANALYSIS")
        print("="*80)
        errors = evaluator.analyze_errors()
        print(f"False Positives: {errors['fp_count']}")
        print(f"False Negatives: {errors['fn_count']}")

    return results
