"""Video-specific rubrics and assessment helpers."""

from typing import Dict, Any, List
from ..rubric_manager import Rubric, RubricBuilder


def create_video_presentation_rubric() -> Rubric:
    """Create a rubric specifically for video presentations."""
    builder = RubricBuilder(
        name="Video Presentation Assessment",
        description="Evaluate video presentations on delivery, content, and technical quality",
    )

    # Delivery Category
    delivery = builder.add_category(
        name="Presentation Delivery",
        description="Speaker presence, clarity, and engagement",
        weight=2.0,
    )
    delivery.add_criterion(
        name="Speaking Clarity",
        description="Speech is clear, well-paced, and easy to understand",
        weight=1.0,
        scoring_guide="1=Poor audio/clarity, 3=Generally clear, 5=Excellent clarity and pacing",
    )
    delivery.add_criterion(
        name="Visual Engagement",
        description="Effective use of visuals, eye contact, and body language",
        weight=1.0,
        scoring_guide="1=No visual engagement, 3=Some visual aids, 5=Highly engaging visuals",
    )
    delivery.add_criterion(
        name="Professionalism",
        description="Professional appearance, confidence, and presence",
        weight=0.5,
        scoring_guide="1=Unprofessional, 3=Professional, 5=Highly polished",
    )

    # Content Category
    content = builder.add_category(
        name="Content Quality",
        description="Organization, accuracy, and depth of content",
        weight=2.0,
    )
    content.add_criterion(
        name="Content Organization",
        description="Clear structure, logical flow, and appropriate length",
        weight=1.0,
        scoring_guide="1=Disorganized, 3=Generally organized, 5=Excellent structure",
    )
    content.add_criterion(
        name="Content Accuracy",
        description="Information is accurate, well-researched, and properly cited",
        weight=1.0,
        scoring_guide="1=Inaccurate information, 3=Mostly accurate, 5=Highly accurate and well-supported",
    )

    # Technical Category
    technical = builder.add_category(
        name="Technical Quality",
        description="Audio, video, and production quality",
        weight=1.0,
    )
    technical.add_criterion(
        name="Audio Quality",
        description="Clear audio without distractions, appropriate volume",
        weight=0.5,
        scoring_guide="1=Poor audio, 3=Acceptable audio, 5=Professional audio quality",
    )
    technical.add_criterion(
        name="Video Quality",
        description="Clear video, good lighting, stable camera work",
        weight=0.5,
        scoring_guide="1=Poor video quality, 3=Acceptable quality, 5=Professional video production",
    )

    builder.set_scoring_scale(
        min_score=1,
        max_score=5,
        labels={
            1: "Poor - Major improvements needed",
            2: "Below Average - Significant issues",
            3: "Average - Meets basic requirements",
            4: "Good - Above average quality",
            5: "Excellent - Outstanding presentation",
        },
    )

    return builder.build(is_template=True, tags=["video", "presentation", "assessment"])


def assess_video_content(
    analysis_results: Dict[str, Any], rubric: Rubric
) -> Dict[str, Any]:
    """
    Video-specific assessment logic that knows how to interpret video analysis results.

    Args:
        analysis_results: Results from video analysis (transcript, frame descriptions, etc.)
        rubric: Rubric to apply

    Returns:
        Assessment results with video-specific insights
    """
    from ..rubric_manager import RubricScorer

    scorer = RubricScorer(rubric)

    # Extract relevant metrics from video analysis for rubric scoring
    scores = {}

    # Map transcript analysis to content criteria
    if "transcript_analysis" in analysis_results:
        transcript = analysis_results["transcript_analysis"]
        readability = transcript.get("readability", {})

        # Content organization based on readability and structure
        if readability.get("grade_level", 12) <= 10:
            scores["content_organization"] = 4  # Good readability = good organization
        elif readability.get("grade_level", 12) <= 12:
            scores["content_organization"] = 3
        else:
            scores["content_organization"] = 2

        # Content accuracy (placeholder - would need more sophisticated analysis)
        scores["content_accuracy"] = 3  # Default neutral score

    # Map frame analysis to visual engagement
    if "frame_analysis" in analysis_results:
        frame_analysis = analysis_results["frame_analysis"]
        readability = frame_analysis.get("readability", {})

        # Visual engagement based on frame description complexity
        if readability.get("vocabulary_richness", 0) > 0.7:
            scores["visual_engagement"] = 4  # Rich descriptions = good visuals
        elif readability.get("vocabulary_richness", 0) > 0.5:
            scores["visual_engagement"] = 3
        else:
            scores["visual_engagement"] = 2

    # Technical quality assessments (placeholder)
    scores["audio_quality"] = 3  # Would analyze actual audio metrics
    scores["video_quality"] = 3  # Would analyze actual video metrics
    scores["speaking_clarity"] = 3  # Would analyze transcript clarity
    scores["professionalism"] = 3  # Would analyze content professionalism

    # Apply rubric scoring
    assessment = scorer.score_all_categories({"delivery": scores})

    # Add video-specific insights
    assessment.feedback = _generate_video_feedback(assessment, analysis_results)

    return {
        "assessment": assessment,
        "video_insights": {
            "content_length": len(analysis_results.get("transcript", "")),
            "visual_complexity": len(analysis_results.get("frame_descriptions", [])),
            "technical_quality": "good",  # Would be calculated from actual metrics
        },
    }


def _generate_video_feedback(assessment, analysis_results: Dict[str, Any]) -> str:
    """Generate video-specific feedback based on assessment and analysis."""
    feedback_parts = []

    # Overall assessment
    if assessment.overall_percentage >= 80:
        feedback_parts.append(
            "Excellent video presentation with strong delivery and content quality."
        )
    elif assessment.overall_percentage >= 60:
        feedback_parts.append(
            "Good video presentation with room for improvement in some areas."
        )
    else:
        feedback_parts.append(
            "Video presentation needs significant improvement in delivery and content."
        )

    # Specific feedback based on analysis
    transcript_analysis = analysis_results.get("transcript_analysis", {})
    readability = transcript_analysis.get("readability", {})

    if readability.get("grade_level", 12) > 12:
        feedback_parts.append("Consider simplifying language to improve accessibility.")
    elif readability.get("grade_level", 12) < 8:
        feedback_parts.append(
            "Content is very accessible but could benefit from more depth."
        )

    # Technical feedback
    feedback_parts.append(
        "Ensure good lighting and clear audio for better viewer experience."
    )

    return " ".join(feedback_parts)


# Export video-specific rubrics
VIDEO_RUBRICS = {
    "presentation": create_video_presentation_rubric,
}
