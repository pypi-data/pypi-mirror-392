"""
Decay Scoring Core Module
Implements time-based decay for search results
"""

import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class DecayScorer:
    """
    Manages time-based decay calculations for search results.

    Uses exponential decay formula: score = base_score * e^(-λ * time_factor)
    where λ (lambda) controls the decay rate.
    """

    # Preset decay rates
    DECAY_RATES = {
        "very_slow": 0.01,  # Items stay relevant for ~100 days
        "slow": 0.05,  # Items stay relevant for ~20 days
        "medium": 0.1,  # Items stay relevant for ~10 days
        "fast": 0.2,  # Items stay relevant for ~5 days
        "very_fast": 0.5,  # Items stay relevant for ~2 days
    }

    def __init__(self, lambda_value: float = 0.05, time_mode: str = "combined"):
        """
        Initialize decay scorer.

        Args:
            lambda_value: Decay rate (0.01-0.5). Higher = faster decay
            time_mode: How to calculate time factor
                - 'creation': Time since creation
                - 'access': Time since last access
                - 'combined': Weighted average (default)
        """
        self.lambda_value = lambda_value
        self.time_mode = time_mode

        # Weights for combined mode
        self.creation_weight = 0.3
        self.access_weight = 0.7

    @classmethod
    def from_preset(cls, preset: str = "slow", time_mode: str = "combined"):
        """
        Create decay scorer with preset decay rate.

        Args:
            preset: One of 'very_slow', 'slow', 'medium', 'fast', 'very_fast'
            time_mode: Time calculation mode

        Returns:
            DecayScorer instance
        """
        lambda_value = cls.DECAY_RATES.get(preset, 0.05)
        return cls(lambda_value=lambda_value, time_mode=time_mode)

    def calculate_time_factor(
        self,
        created_at: datetime,
        last_accessed: Optional[datetime] = None,
        current_time: Optional[datetime] = None,
    ) -> float:
        """
        Calculate time factor based on timestamps.

        Args:
            created_at: When item was created
            last_accessed: When item was last accessed (None = never accessed)
            current_time: Current time (None = now)

        Returns:
            Time factor in days
        """
        if current_time is None:
            current_time = datetime.now()

        days_since_creation = (current_time - created_at).total_seconds() / 86400.0

        if self.time_mode == "creation":
            return days_since_creation

        elif self.time_mode == "access":
            if last_accessed is None:
                return days_since_creation
            days_since_access = (current_time - last_accessed).total_seconds() / 86400.0
            return days_since_access

        elif self.time_mode == "combined":
            if last_accessed is None:
                return days_since_creation

            days_since_access = (current_time - last_accessed).total_seconds() / 86400.0

            # Weighted average
            time_factor = (
                self.creation_weight * days_since_creation
                + self.access_weight * days_since_access
            )
            return time_factor

        else:
            raise ValueError(f"Invalid time_mode: {self.time_mode}")

    def calculate_score(
        self,
        base_score: float,
        created_at: datetime,
        last_accessed: Optional[datetime] = None,
        current_time: Optional[datetime] = None,
    ) -> Tuple[float, float]:
        """
        Calculate decayed score.

        Args:
            base_score: Original score
            created_at: When item was created
            last_accessed: When item was last accessed
            current_time: Current time

        Returns:
            Tuple of (decayed_score, decay_multiplier)
        """
        time_factor = self.calculate_time_factor(
            created_at, last_accessed, current_time
        )

        # Exponential decay: e^(-λ * t)
        decay_multiplier = math.exp(-self.lambda_value * time_factor)

        decayed_score = base_score * decay_multiplier

        return decayed_score, decay_multiplier

    def apply_decay(
        self,
        results: List[Dict],
        score_key: str = "final_score",
        current_time: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Apply decay to a list of search results.

        Args:
            results: List of result dictionaries
            score_key: Key containing the score to decay
            current_time: Current time

        Returns:
            Results with decay applied and sorted by decayed score
        """
        if current_time is None:
            current_time = datetime.now()

        for result in results:
            # Get timestamps from metadata
            metadata = result.get("metadata", {})

            # Parse timestamps
            created_at = self._parse_timestamp(
                metadata.get("created_at"), default=current_time
            )

            last_accessed = self._parse_timestamp(
                metadata.get("last_accessed"), default=None
            )

            # Ensure created_at is not None (should always have a value due to default)
            if created_at is None:
                created_at = current_time

            # Calculate decay
            base_score = result.get(score_key, 0.0)
            decayed_score, decay_multiplier = self.calculate_score(
                base_score, created_at, last_accessed, current_time
            )

            # Update result
            result["decayed_score"] = decayed_score
            result["decay_multiplier"] = decay_multiplier
            result["base_score"] = base_score

        # Re-sort by decayed score
        results.sort(key=lambda x: x.get("decayed_score", 0), reverse=True)

        return results

    def should_cleanup(
        self,
        created_at: datetime,
        last_accessed: Optional[datetime] = None,
        threshold: float = 0.01,
        current_time: Optional[datetime] = None,
    ) -> bool:
        """
        Determine if item should be cleaned up based on decay.

        Args:
            created_at: When item was created
            last_accessed: When item was last accessed
            threshold: Cleanup threshold (default 0.01 = 1%)
            current_time: Current time

        Returns:
            True if item decay is below threshold
        """
        _, decay_multiplier = self.calculate_score(
            1.0, created_at, last_accessed, current_time
        )
        return decay_multiplier < threshold

    def get_half_life(self) -> float:
        """
        Calculate half-life (time for decay to reach 0.5).

        Returns:
            Half-life in days
        """
        return math.log(2) / self.lambda_value

    @staticmethod
    def _parse_timestamp(value, default=None) -> Optional[datetime]:
        """Parse timestamp from various formats"""
        if value is None:
            return default

        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except Exception:
                return default

        return default
