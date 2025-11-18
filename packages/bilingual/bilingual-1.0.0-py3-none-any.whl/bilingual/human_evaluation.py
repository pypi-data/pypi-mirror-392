#!/usr/bin/env python3
"""
Human-in-the-loop evaluation for child-appropriate content.

This module provides tools for human reviewers to evaluate generated content
for appropriateness, safety, and educational value for children.
"""

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ContentRating(Enum):
    """Rating categories for content evaluation."""

    VERY_APPROPRIATE = "very_appropriate"  # 5 stars - Perfect for children
    APPROPRIATE = "appropriate"  # 4 stars - Good for children
    NEUTRAL = "neutral"  # 3 stars - Acceptable
    INAPPROPRIATE = "inappropriate"  # 2 stars - Not suitable
    VERY_INAPPROPRIATE = "very_inappropriate"  # 1 star - Harmful


class SafetyCategory(Enum):
    """Safety categories for content classification."""

    VIOLENCE = "violence"
    HATE_SPEECH = "hate_speech"
    SEXUAL_CONTENT = "sexual_content"
    PROFANITY = "profanity"
    DRUGS_ALCOHOL = "drugs_alcohol"
    MENTAL_HEALTH = "mental_health"
    PERSONAL_INFO = "personal_info"
    OTHER = "other"


@dataclass
class ContentEvaluation:
    """Data class for storing content evaluation results."""

    evaluation_id: str
    content_id: str
    content_text: str
    evaluator_id: str
    timestamp: str
    overall_rating: ContentRating
    safety_flags: List[SafetyCategory]
    age_appropriateness: Dict[str, bool]  # e.g., {"6-8": True, "9-12": True}
    educational_value: int  # 1-5 scale
    engagement_score: int  # 1-5 scale
    comments: str
    suggested_improvements: str
    metadata: Dict[str, Any]


class HumanEvaluator:
    """
    Human-in-the-loop evaluation system for child-appropriate content.
    """

    def __init__(self, storage_path: str = "data/evaluations/"):
        """
        Initialize the human evaluator.

        Args:
            storage_path: Path to store evaluation results
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Evaluation history
        self.evaluations_file = self.storage_path / "evaluations.jsonl"
        self.metrics_file = self.storage_path / "metrics.json"

        # Load existing evaluations
        self.evaluations = self._load_evaluations()

    def _load_evaluations(self) -> List[ContentEvaluation]:
        """Load existing evaluations from storage."""
        evaluations = []

        if self.evaluations_file.exists():
            try:
                with open(self.evaluations_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            evaluations.append(self._dict_to_evaluation(data))
            except Exception as e:
                print(f"Warning: Could not load evaluations: {e}")

        return evaluations

    def _dict_to_evaluation(self, data: Dict[str, Any]) -> ContentEvaluation:
        """Convert dictionary to ContentEvaluation object."""
        return ContentEvaluation(
            evaluation_id=data["evaluation_id"],
            content_id=data["content_id"],
            content_text=data["content_text"],
            evaluator_id=data["evaluator_id"],
            timestamp=data["timestamp"],
            overall_rating=ContentRating(data["overall_rating"]),
            safety_flags=[SafetyCategory(flag) for flag in data["safety_flags"]],
            age_appropriateness=data["age_appropriateness"],
            educational_value=data["educational_value"],
            engagement_score=data["engagement_score"],
            comments=data["comments"],
            suggested_improvements=data["suggested_improvements"],
            metadata=data.get("metadata", {}),
        )

    def _evaluation_to_dict(self, evaluation: ContentEvaluation) -> Dict[str, Any]:
        """Convert ContentEvaluation object to dictionary."""
        return {
            "evaluation_id": evaluation.evaluation_id,
            "content_id": evaluation.content_id,
            "content_text": evaluation.content_text,
            "evaluator_id": evaluation.evaluator_id,
            "timestamp": evaluation.timestamp,
            "overall_rating": evaluation.overall_rating.value,
            "safety_flags": [flag.value for flag in evaluation.safety_flags],
            "age_appropriateness": evaluation.age_appropriateness,
            "educational_value": evaluation.educational_value,
            "engagement_score": evaluation.engagement_score,
            "comments": evaluation.comments,
            "suggested_improvements": evaluation.suggested_improvements,
            "metadata": evaluation.metadata,
        }

    def submit_evaluation(
        self,
        content_id: str,
        content_text: str,
        evaluator_id: str,
        overall_rating: ContentRating,
        safety_flags: List[SafetyCategory],
        age_appropriateness: Dict[str, bool],
        educational_value: int,
        engagement_score: int,
        comments: str = "",
        suggested_improvements: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Submit a human evaluation for content.

        Args:
            content_id: Unique identifier for the content
            content_text: The content being evaluated
            evaluator_id: ID of the human evaluator
            overall_rating: Overall appropriateness rating
            safety_flags: Any safety concerns identified
            age_appropriateness: Appropriateness for different age groups
            educational_value: Educational value rating (1-5)
            engagement_score: Engagement score (1-5)
            comments: Additional comments
            suggested_improvements: Suggestions for improvement
            metadata: Additional metadata

        Returns:
            Evaluation ID
        """
        evaluation_id = str(uuid.uuid4())

        evaluation = ContentEvaluation(
            evaluation_id=evaluation_id,
            content_id=content_id,
            content_text=content_text,
            evaluator_id=evaluator_id,
            timestamp=datetime.now().isoformat(),
            overall_rating=overall_rating,
            safety_flags=safety_flags,
            age_appropriateness=age_appropriateness,
            educational_value=educational_value,
            engagement_score=engagement_score,
            comments=comments,
            suggested_improvements=suggested_improvements,
            metadata=metadata or {},
        )

        # Add to evaluations list
        self.evaluations.append(evaluation)

        # Save to file
        with open(self.evaluations_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(self._evaluation_to_dict(evaluation), ensure_ascii=False) + "\n")

        print(f"✅ Evaluation submitted: {evaluation_id}")
        return evaluation_id

    def get_content_evaluations(self, content_id: str) -> List[ContentEvaluation]:
        """Get all evaluations for a specific content."""
        return [eval for eval in self.evaluations if eval.content_id == content_id]

    def get_evaluator_evaluations(self, evaluator_id: str) -> List[ContentEvaluation]:
        """Get all evaluations by a specific evaluator."""
        return [eval for eval in self.evaluations if eval.evaluator_id == evaluator_id]

    def calculate_content_safety_score(self, content_id: str) -> Dict[str, Any]:
        """
        Calculate safety score for content based on human evaluations.

        Args:
            content_id: Content identifier

        Returns:
            Safety metrics
        """
        evaluations = self.get_content_evaluations(content_id)

        if not evaluations:
            return {"error": "No evaluations found for this content"}

        # Calculate metrics
        total_evaluations = len(evaluations)

        # Overall rating distribution
        rating_counts = {}
        for rating in ContentRating:
            rating_counts[rating.value] = sum(
                1 for eval in evaluations if eval.overall_rating == rating
            )

        # Safety flags
        all_safety_flags = []
        for eval in evaluations:
            all_safety_flags.extend(eval.safety_flags)

        safety_flag_counts = {}
        for flag in SafetyCategory:
            safety_flag_counts[flag.value] = sum(1 for f in all_safety_flags if f == flag)

        # Average scores
        avg_educational_value = (
            sum(eval.educational_value for eval in evaluations) / total_evaluations
        )
        avg_engagement_score = (
            sum(eval.engagement_score for eval in evaluations) / total_evaluations
        )

        # Age appropriateness
        age_appropriateness = {}
        for age_group in ["6-8", "9-12", "13-15", "16+"]:
            age_appropriateness[age_group] = (
                sum(1 for eval in evaluations if eval.age_appropriateness.get(age_group, False))
                / total_evaluations
            )

        # Overall safety score (0-100)
        # Higher is safer - penalize inappropriate ratings and safety flags
        inappropriate_penalty = (
            rating_counts.get("inappropriate", 0) * 20
            + rating_counts.get("very_inappropriate", 0) * 40
        ) / total_evaluations

        safety_flag_penalty = sum(safety_flag_counts.values()) * 5 / total_evaluations

        educational_bonus = avg_educational_value * 5
        engagement_bonus = avg_engagement_score * 3

        safety_score = max(
            0,
            min(
                100,
                80
                - inappropriate_penalty
                - safety_flag_penalty
                + educational_bonus
                + engagement_bonus,
            ),
        )

        return {
            "content_id": content_id,
            "total_evaluations": total_evaluations,
            "safety_score": safety_score,
            "rating_distribution": rating_counts,
            "safety_flags": safety_flag_counts,
            "average_educational_value": avg_educational_value,
            "average_engagement_score": avg_engagement_score,
            "age_appropriateness": age_appropriateness,
            "recommendations": self._generate_safety_recommendations(
                safety_score, safety_flag_counts
            ),
        }

    def _generate_safety_recommendations(
        self, safety_score: float, safety_flags: Dict[str, int]
    ) -> List[str]:
        """Generate recommendations based on safety analysis."""
        recommendations = []

        if safety_score < 60:
            recommendations.append(
                "Content requires significant review and modification before use with children"
            )

        if safety_score < 40:
            recommendations.append(
                "Content should not be used with children until major safety concerns are addressed"
            )

        if safety_flags.get("violence", 0) > 0:
            recommendations.append("Remove or significantly reduce violent content")

        if safety_flags.get("hate_speech", 0) > 0:
            recommendations.append("Eliminate all hate speech and discriminatory content")

        if safety_flags.get("sexual_content", 0) > 0:
            recommendations.append("Remove all sexual content and innuendo")

        if safety_flags.get("profanity", 0) > 0:
            recommendations.append("Replace profanity with child-appropriate language")

        if safety_flags.get("drugs_alcohol", 0) > 0:
            recommendations.append("Remove references to drugs and alcohol")

        if not recommendations:
            recommendations.append("Content appears appropriate for children")

        return recommendations

    def generate_evaluation_report(
        self, output_path: str = "data/evaluations/report.json"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive evaluation report.

        Args:
            output_path: Path to save the report

        Returns:
            Report data
        """
        if not self.evaluations:
            return {"error": "No evaluations available"}

        # Calculate overall metrics
        total_evaluations = len(self.evaluations)
        unique_contents = len(set(eval.content_id for eval in self.evaluations))
        unique_evaluators = len(set(eval.evaluator_id for eval in self.evaluations))

        # Safety score distribution
        safety_scores = []
        for content_id in set(eval.content_id for eval in self.evaluations):
            content_metrics = self.calculate_content_safety_score(content_id)
            if "safety_score" in content_metrics:
                safety_scores.append(content_metrics["safety_score"])

        # Average safety score
        avg_safety_score = sum(safety_scores) / len(safety_scores) if safety_scores else 0

        # Content categories
        safe_content = sum(1 for score in safety_scores if score >= 80)
        moderate_content = sum(1 for score in safety_scores if 60 <= score < 80)
        unsafe_content = sum(1 for score in safety_scores if score < 60)

        # Common safety flags
        all_safety_flags = []
        for eval in self.evaluations:
            all_safety_flags.extend([flag.value for flag in eval.safety_flags])

        flag_distribution = {}
        for flag in SafetyCategory:
            flag_distribution[flag.value] = all_safety_flags.count(flag.value)

        # Age appropriateness
        age_stats = {"6-8": 0, "9-12": 0, "13-15": 0, "16+": 0}
        for eval in self.evaluations:
            for age_group, appropriate in eval.age_appropriateness.items():
                if appropriate:
                    age_stats[age_group] += 1

        # Generate report
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_evaluations": total_evaluations,
                "unique_contents": unique_contents,
                "unique_evaluators": unique_evaluators,
                "average_safety_score": avg_safety_score,
            },
            "content_safety": {
                "safe_content": safe_content,
                "moderate_content": moderate_content,
                "unsafe_content": unsafe_content,
                "safety_score_distribution": {
                    "excellent": sum(1 for score in safety_scores if score >= 90),
                    "good": sum(1 for score in safety_scores if 80 <= score < 90),
                    "moderate": sum(1 for score in safety_scores if 60 <= score < 80),
                    "poor": sum(1 for score in safety_scores if score < 60),
                },
            },
            "common_safety_flags": flag_distribution,
            "age_appropriateness": age_stats,
            "recommendations": [
                "Continue regular content evaluation to maintain safety standards",
                "Focus additional review on content with safety flags",
                "Consider age-specific content guidelines for better targeting",
                "Encourage evaluator training for consistent ratings",
            ],
        }

        # Save report
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f" Evaluation report saved to: {output_path}")
        return report

    def create_evaluation_interface(self, content_id: str, content_text: str) -> str:
        """
        Generate HTML interface for human evaluation.

        Args:
            content_id: Content identifier
            content_text: Content text
        """
        # Escape content for HTML
        escaped_content = content_text.replace('"', "&quot;").replace("'", "&#39;")

        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Content Safety Evaluation</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .content-box {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .rating {{ margin: 10px 0; }}
                .comments {{ width: 100%; height: 100px; margin: 10px 0; }}
                .safety-checkbox {{ margin: 5px; }}
                .submit-btn {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <h1>Content Safety Evaluation</h1>

            <div class="content-box">
                <h3>Content to Evaluate:</h3>
                <p>{escaped_content}</p>
            </div>

            <form id="evaluationForm">
                <input type="hidden" name="content_id" value="{content_id}">
                <input type="hidden" name="content_text" value="{escaped_content}">

                <div class="rating">
                    <label><strong>Overall Appropriateness:</strong></label><br>
                    <input type="radio" name="overall_rating" value="very_appropriate" required> Very Appropriate (5 stars)<br>
                    <input type="radio" name="overall_rating" value="appropriate"> Appropriate (4 stars)<br>
                    <input type="radio" name="overall_rating" value="neutral"> Neutral (3 stars)<br>
                    <input type="radio" name="overall_rating" value="inappropriate"> Inappropriate (2 stars)<br>
                    <input type="radio" name="overall_rating" value="very_inappropriate"> Very Inappropriate (1 star)
                </div>

                <div class="rating">
                    <label><strong>Safety Concerns (check all that apply):</strong></label><br>
                    <input type="checkbox" class="safety-checkbox" name="safety_flags" value="violence"> Violence<br>
                    <input type="checkbox" class="safety-checkbox" name="safety_flags" value="hate_speech"> Hate Speech<br>
                    <input type="checkbox" class="safety-checkbox" name="safety_flags" value="sexual_content"> Sexual Content<br>
                    <input type="checkbox" class="safety-checkbox" name="safety_flags" value="profanity"> Profanity<br>
                    <input type="checkbox" class="safety-checkbox" name="safety_flags" value="drugs_alcohol"> Drugs/Alcohol<br>
                    <input type="checkbox" class="safety-checkbox" name="safety_flags" value="mental_health"> Mental Health Concerns<br>
                    <input type="checkbox" class="safety-checkbox" name="safety_flags" value="personal_info"> Personal Information<br>
                    <input type="checkbox" class="safety-checkbox" name="safety_flags" value="other"> Other
                </div>

                <div class="rating">
                    <label><strong>Age Appropriateness:</strong></label><br>
                    <input type="checkbox" name="age_groups" value="6-8"> Ages 6-8<br>
                    <input type="checkbox" name="age_groups" value="9-12"> Ages 9-12<br>
                    <input type="checkbox" name="age_groups" value="13-15"> Ages 13-15<br>
                    <input type="checkbox" name="age_groups" value="16+"> Ages 16+
                </div>

                <div class="rating">
                    <label><strong>Educational Value (1-5):</strong></label><br>
                    <input type="range" name="educational_value" min="1" max="5" value="3">
                </div>

                <div class="rating">
                    <label><strong>Engagement Score (1-5):</strong></label><br>
                    <input type="range" name="engagement_score" min="1" max="5" value="3">
                </div>

                <div class="rating">
                    <label><strong>Comments:</strong></label><br>
                    <textarea class="comments" name="comments" placeholder="Additional comments about the content..."></textarea>
                </div>

                <div class="rating">
                    <label><strong>Suggested Improvements:</strong></label><br>
                    <textarea class="comments" name="suggested_improvements" placeholder="How can this content be improved?"></textarea>
                </div>

                <button type="submit" class="submit-btn">Submit Evaluation</button>
            </form>

            <script>
                document.getElementById('evaluationForm').addEventListener('submit', function(e) {{
                    e.preventDefault();

                    // Collect form data
                    const formData = new FormData(e.target);
                    const data = {{
                        content_id: formData.get('content_id'),
                        content_text: formData.get('content_text'),
                        evaluator_id: 'human_evaluator_' + Date.now(), // In practice, this would be logged in user
                        overall_rating: formData.get('overall_rating'),
                        safety_flags: formData.getAll('safety_flags'),
                        age_appropriateness: {{
                            '6-8': formData.getAll('age_groups').includes('6-8'),
                            '9-12': formData.getAll('age_groups').includes('9-12'),
                            '13-15': formData.getAll('age_groups').includes('13-15'),
                            '16+': formData.getAll('age_groups').includes('16+')
                        }},
                        educational_value: parseInt(formData.get('educational_value')),
                        engagement_score: parseInt(formData.get('engagement_score')),
                        comments: formData.get('comments'),
                        suggested_improvements: formData.get('suggested_improvements')
                    }};

                    // Send to evaluation API (in practice)
                    console.log('Evaluation data:', data);
                    alert('Evaluation submitted successfully!');

                    // Reset form
                    e.target.reset();
                }});
            </script>
        </body>
        </html>
        """

        return html_template


# Global human evaluator instance
_human_evaluator = None


def get_human_evaluator(storage_path: str = "data/evaluations/") -> HumanEvaluator:
    """Get or create the global human evaluator instance."""
    global _human_evaluator
    if _human_evaluator is None:
        _human_evaluator = HumanEvaluator(storage_path)
    return _human_evaluator


def submit_evaluation(
    content_id: str,
    content_text: str,
    evaluator_id: str,
    overall_rating: str,
    safety_flags: List[str],
    age_appropriateness: Dict[str, bool],
    educational_value: int,
    engagement_score: int,
    comments: str = "",
    suggested_improvements: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Convenience function to submit content evaluation.

    Args:
        content_id: Content identifier
        content_text: Content to evaluate
        evaluator_id: Evaluator identifier
        overall_rating: Overall rating ('very_appropriate', 'appropriate', etc.)
        safety_flags: List of safety flags
        age_appropriateness: Age group appropriateness
        educational_value: Educational value score (1-5)
        engagement_score: Engagement score (1-5)
        comments: Additional comments
        suggested_improvements: Improvement suggestions
        metadata: Additional metadata

    Returns:
        Evaluation ID
    """
    evaluator = get_human_evaluator()

    # Convert string rating to enum
    rating_enum = ContentRating(overall_rating)

    # Convert string flags to enums
    flag_enums = [SafetyCategory(flag) for flag in safety_flags]

    return evaluator.submit_evaluation(
        content_id,
        content_text,
        evaluator_id,
        rating_enum,
        flag_enums,
        age_appropriateness,
        educational_value,
        engagement_score,
        comments,
        suggested_improvements,
        metadata,
    )


def calculate_content_safety_score(content_id: str) -> Dict[str, Any]:
    """Convenience function to calculate content safety score."""
    return get_human_evaluator().calculate_content_safety_score(content_id)


def generate_evaluation_report(output_path: str = "data/evaluations/report.json") -> Dict[str, Any]:
    """Convenience function to generate evaluation report."""
    return get_human_evaluator().generate_evaluation_report(output_path)


def create_evaluation_interface(content_id: str, content_text: str) -> str:
    """Convenience function to create evaluation interface."""
    return get_human_evaluator().create_evaluation_interface(content_id, content_text)
