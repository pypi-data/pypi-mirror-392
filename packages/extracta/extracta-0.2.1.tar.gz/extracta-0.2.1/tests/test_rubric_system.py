"""Tests for rubric system (migrated from video-lens)."""

import tempfile
from pathlib import Path

import pytest

from extracta.grading.rubric_manager import (
    Rubric,
    RubricAssessment,
    RubricBuilder,
    RubricCategory,
    RubricCriterion,
    RubricRepository,
    RubricScorer,
    ScoringScale,
)


class TestRubricCriterion:
    """Tests for RubricCriterion model."""

    def test_create_criterion(self):
        """Test creating a rubric criterion."""
        criterion = RubricCriterion(
            name="Clear Thesis",
            description="Student clearly states main argument",
            weight=2.0,
        )
        assert criterion.name == "Clear Thesis"
        assert criterion.description == "Student clearly states main argument"
        assert criterion.weight == 2.0

    def test_criterion_with_scoring_guide(self):
        """Test criterion with scoring guide."""
        criterion = RubricCriterion(
            name="Organization",
            scoring_guide="5: Excellent flow; 3: Adequate structure; 1: Disorganized",
            level_descriptions={1: "Disorganized", 3: "Adequate", 5: "Excellent"},
        )
        assert criterion.scoring_guide is not None
        assert len(criterion.level_descriptions) == 3

    def test_criterion_default_weight(self):
        """Test criterion defaults to weight of 1.0."""
        criterion = RubricCriterion(name="Test Criterion")
        assert criterion.weight == 1.0


class TestRubricCategory:
    """Tests for RubricCategory model."""

    def test_create_category(self):
        """Test creating a rubric category."""
        category = RubricCategory(
            name="Content Quality",
            description="Evaluation of content",
            weight=2.0,
        )
        assert category.name == "Content Quality"
        assert category.description == "Evaluation of content"
        assert category.weight == 2.0
        assert len(category.criteria) == 0

    def test_category_with_criteria(self):
        """Test category with criteria."""
        criterion1 = RubricCriterion(name="Clarity", weight=1.0)
        criterion2 = RubricCriterion(name="Accuracy", weight=1.5)

        category = RubricCategory(
            name="Content",
            criteria=[criterion1, criterion2],
        )
        assert len(category.criteria) == 2
        assert category.criteria[0].name == "Clarity"
        assert category.criteria[1].weight == 1.5

    def test_category_validation_requires_criteria(self):
        """Test that category must have at least one criterion."""
        with pytest.raises(
            ValueError, match="Category must have at least one criterion"
        ):
            RubricCategory(name="Empty Category", criteria=[])


class TestScoringScale:
    """Tests for ScoringScale model."""

    def test_create_scale(self):
        """Test creating a scoring scale."""
        scale = ScoringScale(
            name="1-5 Scale",
            min_score=1,
            max_score=5,
            labels={1: "Poor", 5: "Excellent"},
        )
        assert scale.name == "1-5 Scale"
        assert scale.min_score == 1
        assert scale.max_score == 5
        assert scale.labels[1] == "Poor"
        assert scale.labels[5] == "Excellent"

    def test_scale_validation_max_greater_than_min(self):
        """Test that max_score must be greater than min_score."""
        with pytest.raises(
            ValueError, match="max_score must be greater than min_score"
        ):
            ScoringScale(
                name="Invalid Scale",
                min_score=5,
                max_score=3,
            )


class TestRubric:
    """Tests for Rubric model."""

    def test_create_rubric(self):
        """Test creating a complete rubric."""
        criterion1 = RubricCriterion(name="Clarity", weight=1.0)
        criterion2 = RubricCriterion(name="Accuracy", weight=1.5)

        category = RubricCategory(
            name="Content Quality",
            description="Content evaluation",
            criteria=[criterion1, criterion2],
        )

        scale = ScoringScale(
            name="1-5 Scale",
            min_score=1,
            max_score=5,
        )

        rubric = Rubric(
            name="Test Rubric",
            description="A test rubric",
            categories=[category],
            scoring_scale=scale,
        )

        assert rubric.name == "Test Rubric"
        assert rubric.description == "A test rubric"
        assert len(rubric.categories) == 1
        assert rubric.categories[0].name == "Content Quality"
        assert rubric.is_template is False
        assert rubric.version == 1

    def test_rubric_serialization(self):
        """Test rubric to/from dict serialization."""
        # Create a simple rubric
        builder = RubricBuilder("Test Rubric")
        category = builder.add_category("Content")
        category.add_criterion("Clarity")

        rubric = builder.build()

        # Serialize to dict
        data = rubric.to_dict()
        assert isinstance(data, dict)
        assert data["name"] == "Test Rubric"

        # Deserialize from dict
        restored = Rubric.from_dict(data)
        assert restored.name == "Test Rubric"
        assert len(restored.categories) == 1


class TestRubricBuilder:
    """Tests for RubricBuilder helper."""

    def test_builder_basic(self):
        """Test basic rubric building."""
        builder = RubricBuilder("Test Rubric", "A test rubric")

        category = builder.add_category("Content", "Content quality", 2.0)
        category.add_criterion("Clarity", "Clear writing", 1.0)
        category.add_criterion("Accuracy", "Accurate information", 1.0)

        rubric = builder.build()

        assert rubric.name == "Test Rubric"
        assert rubric.description == "A test rubric"
        assert len(rubric.categories) == 1
        assert rubric.categories[0].weight == 2.0
        assert len(rubric.categories[0].criteria) == 2

    def test_builder_custom_scale(self):
        """Test builder with custom scoring scale."""
        builder = RubricBuilder("Custom Scale Rubric")
        builder.set_scoring_scale(0, 10, {0: "Fail", 10: "Perfect"})

        # Add a category since rubric requires at least one
        builder.add_category("Test Category").add_criterion("Test Criterion")

        rubric = builder.build()

        assert rubric.scoring_scale.min_score == 0
        assert rubric.scoring_scale.max_score == 10
        assert rubric.scoring_scale.labels[0] == "Fail"
        assert rubric.scoring_scale.labels[10] == "Perfect"


class TestRubricRepository:
    """Tests for RubricRepository."""

    def test_repository_operations(self):
        """Test basic repository operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = RubricRepository(Path(temp_dir))

            # Create and save a rubric
            builder = RubricBuilder("Repository Test")
            category = builder.add_category("Test Category")
            category.add_criterion("Test Criterion")

            rubric = builder.build()
            repo.save(rubric)

            # Load the rubric
            loaded = repo.load(rubric.id)
            assert loaded is not None
            assert loaded.name == "Repository Test"

            # List rubrics
            rubrics = repo.list_rubrics()
            assert len(rubrics) == 1

            # Delete rubric
            assert repo.delete(rubric.id) is True
            assert repo.load(rubric.id) is None


class TestRubricScorer:
    """Tests for RubricScorer."""

    def test_score_category(self):
        """Test scoring a single category."""
        # Create a rubric with one category and two criteria
        criterion1 = RubricCriterion(name="Clarity", weight=1.0)
        criterion2 = RubricCriterion(name="Accuracy", weight=1.0)

        category = RubricCategory(
            name="Content",
            criteria=[criterion1, criterion2],
        )

        scale = ScoringScale(name="1-5", min_score=1, max_score=5)
        rubric = Rubric(
            name="Test",
            categories=[category],
            scoring_scale=scale,
        )

        scorer = RubricScorer(rubric)

        # Score the category
        scores = {criterion1.id: 4, criterion2.id: 3}
        result = scorer.score_category(category.id, scores)

        assert result is not None
        assert result.category_name == "Content"
        assert result.category_total == 3.5  # Average of 4 and 3
        assert len(result.criterion_scores) == 2

    def test_score_all_categories(self):
        """Test scoring all categories in a rubric."""
        # Create rubric with two categories
        cat1 = RubricCategory(
            name="Content",
            criteria=[RubricCriterion(name="Clarity")],
        )
        cat2 = RubricCategory(
            name="Delivery",
            criteria=[RubricCriterion(name="Speaking")],
        )

        rubric = Rubric(
            name="Test Rubric",
            categories=[cat1, cat2],
            scoring_scale=ScoringScale(name="1-5", min_score=1, max_score=5),
        )

        scorer = RubricScorer(rubric)

        # Score all categories
        all_scores = {
            cat1.id: {cat1.criteria[0].id: 4},
            cat2.id: {cat2.criteria[0].id: 3},
        }

        assessment = scorer.score_all_categories(all_scores)

        assert assessment.rubric_name == "Test Rubric"
        assert len(assessment.category_scores) == 2
        assert assessment.overall_score == 3.5  # Average of category scores
