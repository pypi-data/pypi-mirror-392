"""
Profile Management Core Module
Handles user profile storage and automatic fact extraction
"""

import re
from datetime import datetime
from typing import Dict, List, Optional


class ProfileManager:
    """
    Manages user profile facts extraction and context formatting.

    This is a lightweight profile manager that works with a profile store interface.
    The actual storage is handled by the ProfileStore in the stores module.
    """

    # Pattern types and their categories
    ROLE_PATTERNS = [
        (r"(?:I(?:'m| am) a |I work as )([a-z ]{3,30})", "job_title"),
        (r"(?:I(?:'m| am) an? )([a-z ]{3,30})(?: at| for| working)", "job_title"),
    ]

    PREFERENCE_PATTERNS = [
        (r"I (?:like|love|enjoy|prefer) (.{3,50})", "likes_"),
        (r"I (?:don't like|dislike|hate|avoid) (.{3,50})", "dislikes_"),
        (r"my favorite (.{3,30}) is (.{2,30})", "favorite_"),
    ]

    PROJECT_PATTERNS = [
        (r"(?:working on|building|developing|creating) (.{5,50})", "current_project"),
        (r"(?:my project|this project) (?:is|does|involves) (.{5,50})", "project_description"),
    ]

    SKILL_PATTERNS = [
        (r"(?:I know|I'm good at|I'm proficient in|my expertise is) (.{3,40})", "skill_"),
        (r"(?:experienced in|experience with|background in) (.{3,40})", "experience_"),
    ]

    # Trigger words that suggest profile information
    TRIGGER_WORDS = {
        "I'm", "I am", "my", "I like", "I prefer", "I work", "I know",
        "my favorite", "working on", "building", "creating"
    }

    def __init__(self):
        """Initialize the profile manager."""
        pass

    def should_extract(self, text: str) -> bool:
        """
        Check if text likely contains profile information.

        Args:
            text: Input text to check

        Returns:
            True if text likely contains profile information
        """
        text_lower = text.lower()
        return any(trigger.lower() in text_lower for trigger in self.TRIGGER_WORDS)

    def extract_facts(self, text: str) -> List[Dict]:
        """
        Extract profile facts from text.

        Args:
            text: Input text to extract from

        Returns:
            List of fact dictionaries with key, value, category, confidence
        """
        facts = []
        text_lower = text.lower()

        # Try each pattern category
        pattern_sets = [
            (self.ROLE_PATTERNS, 'role', 0.85),
            (self.PREFERENCE_PATTERNS, 'preference', 0.80),
            (self.PROJECT_PATTERNS, 'project', 0.75),
            (self.SKILL_PATTERNS, 'skill', 0.80),
        ]

        for patterns, category, confidence in pattern_sets:
            for pattern, key_prefix in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) == 1:
                        value = match.group(1).strip()
                        if len(value) > 2:  # Minimum length check
                            facts.append({
                                'key': key_prefix if key_prefix.endswith('_') else key_prefix,
                                'value': value[:50],  # Limit length
                                'category': category,
                                'confidence': confidence
                            })
                    elif len(match.groups()) == 2:
                        # For patterns with two capture groups (e.g., "my favorite X is Y")
                        sub_key = match.group(1).strip()
                        value = match.group(2).strip()
                        if len(value) > 1:
                            facts.append({
                                'key': f"{key_prefix}{sub_key}",
                                'value': value[:50],
                                'category': category,
                                'confidence': confidence
                            })

        return facts

    def format_context(
        self,
        facts: List[Dict],
        min_confidence: float = 0.5,
        max_facts: int = 20
    ) -> str:
        """
        Format profile facts as context for prompts.

        Args:
            facts: List of fact dictionaries
            min_confidence: Only include facts with confidence >= this
            max_facts: Maximum number of facts to include

        Returns:
            Formatted string suitable for prompt injection
        """
        # Filter by confidence
        facts = [f for f in facts if f['confidence'] >= min_confidence]

        # Limit to max_facts
        facts = facts[:max_facts]

        if not facts:
            return ""

        # Group by category
        by_category = {}
        for fact in facts:
            cat = fact['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(f"{fact['key']}: {fact['value']}")

        # Format as readable context
        context_parts = []
        category_labels = {
            'role': 'Role',
            'preference': 'Preferences',
            'project': 'Projects',
            'skill': 'Skills',
            'context': 'Context'
        }

        for cat in ['role', 'preference', 'project', 'skill', 'context']:
            if cat in by_category:
                label = category_labels.get(cat, cat.title())
                items = ', '.join(by_category[cat])
                context_parts.append(f"{label}: {items}")

        if context_parts:
            return "User Profile: " + " | ".join(context_parts)
        return ""
