import pytest
from extracta.analyzers.text_analyzer import TextAnalyzer


class TestTextAnalyzer:
    def test_research_analysis(self):
        analyzer = TextAnalyzer()
        text = "This is a sample research interview transcript about climate change. The interviewee discussed global warming, renewable energy, and sustainable practices. They emphasized the importance of reducing carbon emissions and transitioning to green technologies."
        result = analyzer.analyze(text, mode="research")

        assert "themes" in result
        assert "discourse_patterns" in result
        assert "sentiment" in result
        assert "linguistic_features" in result
        assert isinstance(result["themes"], list)
        assert isinstance(result["discourse_patterns"], dict)
        assert isinstance(result["sentiment"], dict)
        assert isinstance(result["linguistic_features"], dict)

    def test_assessment_analysis(self):
        analyzer = TextAnalyzer()
        text = "This is a student essay about environmental science. Climate change is a serious problem that affects our planet. We need to take action to protect the environment. Renewable energy sources like solar and wind power can help reduce pollution."
        result = analyzer.analyze(text, mode="assessment")

        assert "readability" in result
        assert "writing_quality" in result
        assert "vocabulary_richness" in result
        assert "grammar_issues" in result
        assert isinstance(result["readability"], dict)
        assert isinstance(result["writing_quality"], dict)
        assert isinstance(result["vocabulary_richness"], dict)
        assert isinstance(result["grammar_issues"], list)

    def test_theme_extraction(self):
        analyzer = TextAnalyzer()
        text = "The climate is changing rapidly. Global warming affects weather patterns. Renewable energy is essential for sustainability."
        themes = analyzer._extract_themes(text)
        assert isinstance(themes, list)
        assert len(themes) > 0
        assert (
            "climate" in themes or "energy" in themes
        )  # Should extract meaningful words

    def test_sentiment_analysis(self):
        analyzer = TextAnalyzer()
        positive_text = "I love this amazing product. It's fantastic and wonderful."
        negative_text = "This is terrible and awful. I hate it completely."

        pos_result = analyzer._analyze_sentiment(positive_text)
        neg_result = analyzer._analyze_sentiment(negative_text)

        assert pos_result["sentiment_score"] > 0
        assert neg_result["sentiment_score"] < 0
        assert pos_result["sentiment"] == "positive"
        assert neg_result["sentiment"] == "negative"

    def test_readability_analysis(self):
        analyzer = TextAnalyzer()
        simple_text = "The cat sat on the mat. It was happy."
        complex_text = "The multifaceted environmental challenges necessitate comprehensive interdisciplinary approaches to sustainable development paradigms."

        simple_result = analyzer._analyze_readability(simple_text)
        complex_result = analyzer._analyze_readability(complex_text)

        assert "flesch_reading_ease" in simple_result
        assert "grade_level" in simple_result
        assert isinstance(simple_result["flesch_reading_ease"], float)
        assert isinstance(complex_result["flesch_reading_ease"], float)

    def test_vocabulary_analysis(self):
        analyzer = TextAnalyzer()
        repetitive_text = "The cat is black. The dog is black. The bird is black."
        diverse_text = (
            "The cat is black. The dog is white. The bird is blue. The fish is red."
        )

        rep_result = analyzer._analyze_vocabulary(repetitive_text)
        div_result = analyzer._analyze_vocabulary(diverse_text)

        assert div_result["vocabulary_richness"] > rep_result["vocabulary_richness"]
        assert div_result["unique_words"] > rep_result["unique_words"]

    def test_grammar_check(self):
        analyzer = TextAnalyzer()
        good_text = "This is a good sentence. It has proper punctuation."
        bad_text = "This is bad  sentence.  It has double  spaces!!"

        good_issues = analyzer._check_grammar(good_text)
        bad_issues = analyzer._check_grammar(bad_text)

        assert len(good_issues) == 0
        assert len(bad_issues) > 0
        assert "double spaces" in " ".join(bad_issues).lower()

    def test_empty_text(self):
        analyzer = TextAnalyzer()
        result = analyzer.analyze("", mode="assessment")
        assert "readability" in result
        assert result["vocabulary_richness"]["total_words"] == 0

    def test_syllable_count(self):
        analyzer = TextAnalyzer()
        assert analyzer._count_syllables("cat") == 1
        assert analyzer._count_syllables("elephant") == 3
        assert (
            analyzer._count_syllables("syllable") == 2
        )  # Basic algorithm approximation
