"""Default example rubrics for common content types."""

from .rubric_manager import Rubric, RubricBuilder


def create_academic_content_rubric() -> Rubric:
    """Create a rubric for academic content (essays, papers)."""
    builder = RubricBuilder(
        name="Academic Content",
        description="Evaluate academic content such as essays, research papers, and assignments",
    )

    # Content Category
    content = builder.add_category(
        name="Content Quality",
        description="Evaluation of content depth and accuracy",
        weight=2.0,
    )
    content.add_criterion(
        name="Research Depth",
        description="Demonstrates thorough understanding and research",
        weight=1.5,
        scoring_guide="1=Superficial, 3=Adequate, 5=Comprehensive and insightful",
    )
    content.add_criterion(
        name="Clear Thesis/Purpose",
        description="Main argument or purpose is clearly stated",
        weight=1.5,
        scoring_guide="1=Unclear, 3=Moderately clear, 5=Crystal clear",
    )
    content.add_criterion(
        name="Supporting Evidence",
        description="Uses relevant data, citations, and examples",
        weight=1.0,
        scoring_guide="1=Minimal, 3=Adequate citations, 5=Excellent sourcing",
    )

    # Writing Category
    writing = builder.add_category(
        name="Writing Quality",
        description="Evaluation of writing mechanics and style",
        weight=1.5,
    )
    writing.add_criterion(
        name="Clarity",
        description="Writing is clear and easy to understand",
        weight=1.0,
        scoring_guide="1=Confusing, 3=Generally clear, 5=Very clear",
    )
    writing.add_criterion(
        name="Organization",
        description="Ideas presented in logical sequence",
        weight=1.0,
        scoring_guide="1=Disorganized, 3=Generally logical, 5=Excellent flow",
    )
    writing.add_criterion(
        name="Grammar & Mechanics",
        description="Free of grammatical errors and typos",
        weight=0.5,
        scoring_guide="1=Many errors, 3=Few errors, 5=Error-free",
    )

    # Analysis Category
    analysis = builder.add_category(
        name="Analysis & Critical Thinking",
        description="Depth of analysis and critical thinking",
        weight=1.5,
    )
    analysis.add_criterion(
        name="Critical Analysis",
        description="Demonstrates critical thinking and analysis",
        weight=1.0,
        scoring_guide="1=Descriptive only, 3=Some analysis, 5=Deep critical analysis",
    )
    analysis.add_criterion(
        name="Original Insights",
        description="Provides original insights or perspectives",
        weight=1.0,
        scoring_guide="1=Repetitive, 3=Some originality, 5=Highly original",
    )

    # Set custom scoring scale
    builder.set_scoring_scale(
        min_score=1,
        max_score=5,
        labels={
            1: "Poor - Needs significant improvement",
            2: "Below Average - Notable deficiencies",
            3: "Average - Meets basic expectations",
            4: "Good - Exceeds expectations",
            5: "Excellent - Outstanding work",
        },
    )

    return builder.build(is_template=True, tags=["academic", "writing", "research"])


def create_business_content_rubric() -> Rubric:
    """Create a rubric for business content (reports, proposals)."""
    builder = RubricBuilder(
        name="Business Content",
        description="Evaluate business content such as reports, proposals, and communications",
    )

    # Business Logic Category
    business = builder.add_category(
        name="Business Logic",
        description="Clarity of business reasoning and strategy",
        weight=2.0,
    )
    business.add_criterion(
        name="Clear Objectives",
        description="Business objectives and goals are clearly stated",
        weight=1.0,
        scoring_guide="1=Vague, 3=Clear, 5=Very clear and measurable",
    )
    business.add_criterion(
        name="Strategic Thinking",
        description="Demonstrates strategic thinking and planning",
        weight=1.5,
        scoring_guide="1=Tactical only, 3=Some strategy, 5=Strong strategic approach",
    )
    business.add_criterion(
        name="Market Understanding",
        description="Shows understanding of market and competitive landscape",
        weight=1.0,
        scoring_guide="1=No market analysis, 3=Basic market data, 5=In-depth market insights",
    )

    # Communication Category
    comm = builder.add_category(
        name="Communication",
        description="Effectiveness of communication and presentation",
        weight=1.5,
    )
    comm.add_criterion(
        name="Clarity",
        description="Information is presented clearly and concisely",
        weight=1.0,
        scoring_guide="1=Confusing, 3=Generally clear, 5=Very clear and concise",
    )
    comm.add_criterion(
        name="Professional Tone",
        description="Appropriate professional tone and language",
        weight=0.75,
        scoring_guide="1=Unprofessional, 3=Professional, 5=Highly professional",
    )
    comm.add_criterion(
        name="Persuasiveness",
        description="Effectively persuades and influences the audience",
        weight=0.75,
        scoring_guide="1=Unconvincing, 3=Moderately persuasive, 5=Highly compelling",
    )

    # Practicality Category
    practical = builder.add_category(
        name="Practicality",
        description="Feasibility and practicality of recommendations",
        weight=1.0,
    )
    practical.add_criterion(
        name="Feasibility",
        description="Recommendations are realistic and feasible",
        weight=1.0,
        scoring_guide="1=Not feasible, 3=Somewhat feasible, 5=Highly feasible",
    )

    builder.set_scoring_scale(
        min_score=1,
        max_score=5,
        labels={
            1: "Poor - Not business-ready",
            2: "Below Average - Significant concerns",
            3: "Average - Meets basic business standards",
            4: "Good - Strong business content",
            5: "Excellent - Ready for executive presentation",
        },
    )

    return builder.build(
        is_template=True, tags=["business", "professional", "communication"]
    )


def create_creative_content_rubric() -> Rubric:
    """Create a rubric for creative content (stories, designs, media)."""
    builder = RubricBuilder(
        name="Creative Content",
        description="Evaluate creative content such as stories, designs, and multimedia",
    )

    # Creativity Category
    creativity = builder.add_category(
        name="Creativity & Originality",
        description="Originality and creative approach",
        weight=2.0,
    )
    creativity.add_criterion(
        name="Originality",
        description="Content shows original thinking and ideas",
        weight=1.5,
        scoring_guide="1=Derivative, 3=Some originality, 5=Highly original",
    )
    creativity.add_criterion(
        name="Innovation",
        description="Introduces new concepts or approaches",
        weight=1.0,
        scoring_guide="1=Conventional, 3=Some innovation, 5=Breakthrough innovation",
    )
    creativity.add_criterion(
        name="Risk Taking",
        description="Appropriately takes creative risks",
        weight=0.5,
        scoring_guide="1=Safe/conservative, 3=Moderate risk, 5=Bold and appropriate risks",
    )

    # Execution Category
    execution = builder.add_category(
        name="Execution & Craftsmanship",
        description="Quality of execution and technical skill",
        weight=1.5,
    )
    execution.add_criterion(
        name="Technical Skill",
        description="Demonstrates technical proficiency and skill",
        weight=1.0,
        scoring_guide="1=Poor technique, 3=Adequate skill, 5=Masterful technique",
    )
    execution.add_criterion(
        name="Polish",
        description="Content is refined and polished",
        weight=1.0,
        scoring_guide="1=Rough, 3=Some polish, 5=Highly polished",
    )

    # Impact Category
    impact = builder.add_category(
        name="Impact & Engagement",
        description="Ability to engage and impact the audience",
        weight=1.5,
    )
    impact.add_criterion(
        name="Emotional Impact",
        description="Creates emotional connection with audience",
        weight=1.0,
        scoring_guide="1=No emotional connection, 3=Some connection, 5=Powerful emotional impact",
    )
    impact.add_criterion(
        name="Memorability",
        description="Content is memorable and sticks with audience",
        weight=1.0,
        scoring_guide="1=Forgettable, 3=Somewhat memorable, 5=Highly memorable",
    )

    builder.set_scoring_scale(
        min_score=1,
        max_score=5,
        labels={
            1: "Poor - Lacks creativity",
            2: "Below Average - Limited creativity",
            3: "Average - Shows some creative potential",
            4: "Good - Creative and engaging",
            5: "Excellent - Outstanding creative work",
        },
    )

    return builder.build(is_template=True, tags=["creative", "artistic", "design"])


def create_general_content_rubric() -> Rubric:
    """Create a general-purpose rubric for any type of content."""
    builder = RubricBuilder(
        name="General Content",
        description="Evaluate any type of content on core quality criteria",
    )

    # Quality Category
    quality = builder.add_category(
        name="Content Quality",
        description="Overall quality and value of content",
        weight=1.5,
    )
    quality.add_criterion(
        name="Relevance",
        description="Content is relevant and appropriate",
        weight=1.0,
        scoring_guide="1=Irrelevant, 3=Somewhat relevant, 5=Highly relevant",
    )
    quality.add_criterion(
        name="Accuracy",
        description="Information presented is accurate",
        weight=1.0,
        scoring_guide="1=Multiple errors, 3=Mostly accurate, 5=Completely accurate",
    )
    quality.add_criterion(
        name="Completeness",
        description="Content is comprehensive and thorough",
        weight=1.0,
        scoring_guide="1=Incomplete, 3=Adequate coverage, 5=Thorough coverage",
    )

    # Presentation Category
    presentation = builder.add_category(
        name="Presentation",
        description="How well the content is presented",
        weight=1.5,
    )
    presentation.add_criterion(
        name="Clarity",
        description="Content is clear and easy to understand",
        weight=1.0,
        scoring_guide="1=Confusing, 3=Generally clear, 5=Very clear",
    )
    presentation.add_criterion(
        name="Organization",
        description="Content is well-organized and logical",
        weight=1.0,
        scoring_guide="1=Disorganized, 3=Generally organized, 5=Excellent organization",
    )

    # Impact Category
    impact = builder.add_category(
        name="Impact",
        description="Effectiveness and impact of the content",
        weight=1.0,
    )
    impact.add_criterion(
        name="Effectiveness",
        description="Content achieves its intended purpose",
        weight=1.0,
        scoring_guide="1=Ineffective, 3=Somewhat effective, 5=Highly effective",
    )

    builder.set_scoring_scale(
        min_score=1,
        max_score=5,
        labels={
            1: "Poor",
            2: "Below Average",
            3: "Average",
            4: "Good",
            5: "Excellent",
        },
    )

    return builder.build(is_template=True, tags=["general", "content"])


def get_default_rubric(rubric_type: str) -> Rubric | None:
    """Get a default rubric by type.

    Args:
        rubric_type: Type of rubric (academic, business, creative, general)

    Returns:
        Rubric object or None if type not found
    """
    rubrics = {
        "academic": create_academic_content_rubric,
        "business": create_business_content_rubric,
        "creative": create_creative_content_rubric,
        "general": create_general_content_rubric,
    }

    builder = rubrics.get(rubric_type.lower())
    return builder() if builder else None


def list_default_rubrics() -> list[str]:
    """List all available default rubric types."""
    return ["academic", "business", "creative", "general"]
