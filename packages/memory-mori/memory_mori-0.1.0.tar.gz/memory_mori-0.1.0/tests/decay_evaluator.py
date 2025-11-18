"""
Decay Behavior Evaluator
Tests time-based decay over simulated time periods
"""

from datetime import datetime, timedelta
from typing import Dict, List
from core.decay import DecayScorer


class DecayEvaluator:
    """
    Evaluate decay behavior over time.
    """

    def __init__(self, decay_scorer: DecayScorer = None):
        """
        Initialize decay evaluator.

        Args:
            decay_scorer: DecayScorer instance (creates default if None)
        """
        self.decay_scorer = decay_scorer or DecayScorer()

    def test_decay_curve(self, days: List[int] = None) -> Dict:
        """
        Test decay over specified time periods.

        Args:
            days: List of day counts to test (default: 0, 1, 7, 14, 30, 60, 90)

        Returns:
            Dictionary with decay values at each time point
        """
        if days is None:
            days = [0, 1, 7, 14, 30, 60, 90]

        now = datetime.now()
        base_score = 1.0
        results = []

        for day_count in days:
            created_at = now - timedelta(days=day_count)
            decayed_score, multiplier = self.decay_scorer.calculate_score(
                base_score, created_at, current_time=now
            )

            results.append({
                'days': day_count,
                'multiplier': multiplier,
                'decayed_score': decayed_score,
                'retention_percent': multiplier * 100
            })

        return {
            'lambda': self.decay_scorer.lambda_value,
            'half_life': self.decay_scorer.get_half_life(),
            'decay_curve': results
        }

    def test_time_modes(self) -> Dict:
        """
        Test different time calculation modes.

        Returns:
            Dictionary comparing different modes
        """
        now = datetime.now()
        created_at = now - timedelta(days=30)
        last_accessed = now - timedelta(days=5)

        modes = ['creation', 'access', 'combined']
        results = {}

        for mode in modes:
            scorer = DecayScorer(
                lambda_value=self.decay_scorer.lambda_value,
                time_mode=mode
            )

            decayed_score, multiplier = scorer.calculate_score(
                1.0, created_at, last_accessed, now
            )

            results[mode] = {
                'multiplier': multiplier,
                'decayed_score': decayed_score
            }

        return results

    def test_cleanup_threshold(self, thresholds: List[float] = None) -> Dict:
        """
        Test cleanup behavior at different thresholds.

        Args:
            thresholds: List of thresholds to test

        Returns:
            Dictionary with cleanup results
        """
        if thresholds is None:
            thresholds = [0.5, 0.1, 0.05, 0.01, 0.001]

        now = datetime.now()
        results = []

        # Test documents of various ages
        test_ages = [1, 7, 14, 30, 60, 90, 180]

        for threshold in thresholds:
            documents_to_cleanup = []

            for days in test_ages:
                created_at = now - timedelta(days=days)

                should_cleanup = self.decay_scorer.should_cleanup(
                    created_at, None, threshold, now
                )

                if should_cleanup:
                    documents_to_cleanup.append(days)

            results.append({
                'threshold': threshold,
                'documents_cleaned': len(documents_to_cleanup),
                'ages_cleaned': documents_to_cleanup
            })

        return {'threshold_tests': results}

    def validate_decay_formula(self) -> Dict:
        """
        Validate decay formula correctness.

        Returns:
            Dictionary with validation results
        """
        now = datetime.now()
        errors = []

        # Test 1: Score at t=0 should be ~1.0
        created_at = now
        score, multiplier = self.decay_scorer.calculate_score(1.0, created_at, current_time=now)
        if not (0.99 <= multiplier <= 1.0):
            errors.append(f"t=0 multiplier should be ~1.0, got {multiplier}")

        # Test 2: Score should decrease over time
        prev_multiplier = 1.0
        for days in [1, 7, 14, 30]:
            created_at = now - timedelta(days=days)
            _, multiplier = self.decay_scorer.calculate_score(1.0, created_at, current_time=now)

            if multiplier >= prev_multiplier:
                errors.append(f"Multiplier should decrease over time, {days} days: {multiplier} >= {prev_multiplier}")

            prev_multiplier = multiplier

        # Test 3: Half-life should be accurate
        half_life = self.decay_scorer.get_half_life()
        created_at = now - timedelta(days=half_life)
        _, multiplier = self.decay_scorer.calculate_score(1.0, created_at, current_time=now)

        if not (0.48 <= multiplier <= 0.52):
            errors.append(f"Half-life multiplier should be ~0.5, got {multiplier} at {half_life} days")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }


def run_decay_evaluation(verbose: bool = True) -> Dict:
    """
    Run complete decay behavior evaluation.

    Args:
        verbose: Print detailed output

    Returns:
        Evaluation results
    """
    if verbose:
        print("="*80)
        print("Decay Behavior Evaluation")
        print("="*80)

    evaluator = DecayEvaluator()

    # Test decay curve
    if verbose:
        print("\nDecay Curve Test:")
        print("-"*80)

    curve_results = evaluator.test_decay_curve()

    if verbose:
        print(f"Lambda: {curve_results['lambda']}")
        print(f"Half-life: {curve_results['half_life']:.2f} days\n")
        print("Days | Multiplier | Retention %")
        print("-"*40)
        for point in curve_results['decay_curve']:
            print(f"{point['days']:4d} | {point['multiplier']:10.4f} | {point['retention_percent']:6.1f}%")

    # Test time modes
    if verbose:
        print("\n" + "="*80)
        print("Time Mode Comparison:")
        print("-"*80)

    mode_results = evaluator.test_time_modes()

    if verbose:
        print("Mode      | Multiplier")
        print("-"*30)
        for mode, result in mode_results.items():
            print(f"{mode:10s} | {result['multiplier']:.4f}")

    # Validate formula
    if verbose:
        print("\n" + "="*80)
        print("Formula Validation:")
        print("-"*80)

    validation = evaluator.validate_decay_formula()

    if verbose:
        if validation['valid']:
            print("✓ All validation tests passed!")
        else:
            print("✗ Validation errors:")
            for error in validation['errors']:
                print(f"  - {error}")

    return {
        'decay_curve': curve_results,
        'time_modes': mode_results,
        'validation': validation
    }
