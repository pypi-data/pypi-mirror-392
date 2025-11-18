import re
from collections import Counter
from statistics import variance
from typing import List, Dict, Any

# Import optional libraries for enhanced analysis
try:
    import textstat
    from nltk import download as nltk_download
    from nltk.tokenize import sent_tokenize, word_tokenize

    # Download required NLTK data if available
    try:
        sent_tokenize("test")
    except LookupError:
        try:
            nltk_download("punkt")
        except Exception:
            pass

except ImportError:
    textstat = None
    sent_tokenize = None
    word_tokenize = None

try:
    import spacy
except ImportError:
    spacy = None

try:
    import nltk
    from nltk.corpus import stopwords
except ImportError:
    nltk = None
    stopwords = None


class TextAnalyzer:
    """Research and assessment focused text analysis with enhanced capabilities"""

    # Basic sentiment word lists
    POSITIVE_WORDS = {
        "good",
        "great",
        "excellent",
        "amazing",
        "wonderful",
        "fantastic",
        "love",
        "like",
        "enjoy",
        "happy",
        "pleased",
        "satisfied",
        "best",
        "better",
        "perfect",
        "awesome",
        "brilliant",
    }

    NEGATIVE_WORDS = {
        "bad",
        "terrible",
        "awful",
        "horrible",
        "hate",
        "dislike",
        "sad",
        "angry",
        "frustrated",
        "disappointed",
        "worst",
        "worse",
        "poor",
        "ugly",
        "stupid",
        "dumb",
        "annoying",
    }

    # Enhanced linguistic patterns
    PASSIVE_INDICATORS = [
        r"\bis\s+\w+ed\b",
        r"\bare\s+\w+ed\b",
        r"\bwas\s+\w+ed\b",
        r"\bwere\s+\w+ed\b",
        r"\bbeen\s+\w+ed\b",
        r"\bbeing\s+\w+ed\b",
        r"\bis\s+\w+en\b",
        r"\bare\s+\w+en\b",
        r"\bwas\s+\w+en\b",
        r"\bwere\s+\w+en\b",
        r"\bbeen\s+\w+en\b",
        r"\bbeing\s+\w+en\b",
    ]

    TRANSITION_WORDS = {
        "addition": [
            "furthermore",
            "moreover",
            "additionally",
            "also",
            "besides",
            "in addition",
        ],
        "contrast": [
            "however",
            "nevertheless",
            "nonetheless",
            "conversely",
            "on the contrary",
            "in contrast",
        ],
        "sequence": [
            "firstly",
            "secondly",
            "subsequently",
            "finally",
            "meanwhile",
            "then",
        ],
        "causation": [
            "therefore",
            "consequently",
            "thus",
            "hence",
            "as a result",
            "because",
        ],
        "example": ["for instance", "for example", "such as", "namely", "specifically"],
        "summary": [
            "in conclusion",
            "in summary",
            "to summarize",
            "overall",
            "ultimately",
        ],
    }

    HEDGING_PATTERNS = [
        r"\bmight\b",
        r"\bmay\b",
        r"\bcould\b",
        r"\bwould\b",
        r"\bshould\b",
        r"\bpossibly\b",
        r"\bprobably\b",
        r"\bperhaps\b",
        r"\blikely\b",
        r"\bappears?\b",
        r"\bseems?\b",
        r"\bsuggests?\b",
        r"\bindicates?\b",
        r"\btends? to\b",
        r"\bmainly\b",
        r"\bmostly\b",
        r"\bgenerally\b",
        r"\boften\b",
        r"\busually\b",
        r"\btypically\b",
        r"\bfrequently\b",
        r"\bsomewhat\b",
        r"\brather\b",
        r"\bquite\b",
        r"\brelatively\b",
        r"\bto some extent\b",
        r"\bto a certain degree\b",
        r"\bin some ways\b",
    ]

    ACADEMIC_INDICATORS = {
        "formal_verbs": [
            "demonstrate",
            "illustrate",
            "indicate",
            "suggest",
            "propose",
            "examine",
            "investigate",
            "analyze",
            "evaluate",
            "assess",
        ],
        "scholarly_phrases": [
            "according to",
            "research shows",
            "studies indicate",
            "it has been found that",
            "evidence suggests",
            "data reveal",
        ],
        "formal_connectors": [
            "furthermore",
            "moreover",
            "consequently",
            "therefore",
            "nonetheless",
            "nevertheless",
            "thus",
            "hence",
        ],
    }

    def analyze(self, text: str, mode: str = "assessment") -> dict:
        if mode == "research":
            return self._research_analysis(text)
        else:
            return self._assessment_analysis(text)

    def _research_analysis(self, text: str) -> dict:
        return {
            "themes": self._extract_themes(text),
            "discourse_patterns": self._analyze_discourse(text),
            "sentiment": self._analyze_sentiment(text),
            "linguistic_features": self._analyze_linguistics(text),
        }

    def _assessment_analysis(self, text: str) -> dict:
        return {
            "readability": self._analyze_readability(text),
            "writing_quality": self._analyze_quality(text),
            "vocabulary_richness": self._analyze_vocabulary(text),
            "grammar_issues": self._check_grammar(text),
        }

    def _extract_themes(self, text: str) -> List[str]:
        """Extract potential themes using keyword frequency"""
        words = re.findall(r"\b\w+\b", text.lower())
        # Remove common stop words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "shall",
        }
        filtered_words = [
            word for word in words if word not in stop_words and len(word) > 3
        ]
        word_counts = Counter(filtered_words)
        # Return top 10 most common words as themes
        return [word for word, _ in word_counts.most_common(10)]

    def _analyze_discourse(self, text: str) -> Dict[str, Any]:
        """Analyze discourse patterns"""
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        questions = len([s for s in sentences if s.endswith("?")])
        exclamations = len([s for s in sentences if s.endswith("!")])

        return {
            "sentence_count": len(sentences),
            "question_count": questions,
            "exclamation_count": exclamations,
            "average_sentence_length": sum(len(s.split()) for s in sentences)
            / len(sentences)
            if sentences
            else 0,
        }

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Basic sentiment analysis using word lists"""
        words = re.findall(r"\b\w+\b", text.lower())
        positive_count = sum(1 for word in words if word in self.POSITIVE_WORDS)
        negative_count = sum(1 for word in words if word in self.NEGATIVE_WORDS)

        total_words = len(words)
        sentiment_score = (
            (positive_count - negative_count) / total_words if total_words > 0 else 0
        )

        return {
            "positive_words": positive_count,
            "negative_words": negative_count,
            "sentiment_score": sentiment_score,  # -1 to 1
            "sentiment": "positive"
            if sentiment_score > 0.1
            else "negative"
            if sentiment_score < -0.1
            else "neutral",
        }

    def _analyze_linguistics(self, text: str) -> Dict[str, Any]:
        """Analyze comprehensive linguistic features including named entities"""
        if not text.strip():
            return self._empty_linguistics()

        words = self._get_words_enhanced(text)
        sentences = self._get_sentences_enhanced(text)

        total_words = len(words)
        unique_words = len(set(word.lower() for word in words))
        avg_word_length = (
            sum(len(word) for word in words) / total_words if total_words > 0 else 0
        )

        # Named Entity Recognition
        named_entities = self._extract_named_entities(text)

        # Enhanced linguistic metrics
        lexical_diversity = unique_words / total_words if total_words > 0 else 0

        # Sentence complexity analysis
        sentence_complexity = self._analyze_sentence_complexity(sentences)

        return {
            "word_count": total_words,
            "unique_words": unique_words,
            "sentence_count": len(sentences),
            "average_word_length": avg_word_length,
            "lexical_diversity": lexical_diversity,
            "named_entities": named_entities,
            "sentence_complexity": sentence_complexity,
        }

    def _empty_linguistics(self) -> Dict[str, Any]:
        """Return empty linguistic analysis"""
        return {
            "word_count": 0,
            "unique_words": 0,
            "sentence_count": 0,
            "average_word_length": 0.0,
            "lexical_diversity": 0.0,
            "named_entities": [],
            "sentence_complexity": {},
        }

    def _extract_named_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities using spaCy or fallback"""
        if not spacy:
            return []

        # Try to load spaCy model
        try:
            nlp = spacy.load("en_core_web_sm")
        except (OSError, ImportError):
            return []

        try:
            doc = nlp(text)
            entities = []

            for ent in doc.ents:
                entities.append(
                    {
                        "text": str(ent.text),
                        "label": str(ent.label_),
                        "start_char": int(ent.start_char),
                        "end_char": int(ent.end_char),
                        "confidence": getattr(
                            ent, "_.confidence", None
                        ),  # Some models provide confidence
                    }
                )

            return entities

        except Exception:
            return []

    def _analyze_sentence_complexity(self, sentences: List[str]) -> Dict[str, Any]:
        """Analyze sentence complexity patterns"""
        if not sentences:
            return {}

        complexities = []
        for sentence in sentences:
            words_in_sentence = self._get_words_enhanced(sentence)
            complexity_score = len(
                words_in_sentence
            )  # Simple complexity based on length

            # Add complexity for punctuation variety
            punctuation_marks = len(re.findall(r'[,:;()""' "-]", sentence))
            complexity_score += punctuation_marks * 0.5

            complexities.append(complexity_score)

        if not complexities:
            return {}

        avg_complexity = sum(complexities) / len(complexities)
        max_complexity = max(complexities)
        min_complexity = min(complexities)

        # Complexity distribution
        simple_sentences = sum(1 for c in complexities if c < 10)
        complex_sentences = sum(1 for c in complexities if c > 25)

        return {
            "average_complexity": round(avg_complexity, 1),
            "max_complexity": round(max_complexity, 1),
            "min_complexity": round(min_complexity, 1),
            "simple_sentences": simple_sentences,
            "complex_sentences": complex_sentences,
            "complexity_variety": round(max_complexity - min_complexity, 1),
        }

    def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Calculate comprehensive readability metrics using enhanced algorithms"""
        if not text.strip():
            return self._empty_readability()

        # Basic counts
        word_count = self._count_words_enhanced(text)
        sentence_count = self._count_sentences_enhanced(text)
        paragraph_count = self._count_paragraphs(text)

        avg_words_per_sentence = word_count / max(sentence_count, 1)

        # Enhanced readability scores
        if textstat:
            flesch_score = textstat.flesch_reading_ease(text)
            flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
        else:
            # Fallback implementation
            flesch_score = self._calculate_flesch_score(
                text, word_count, sentence_count
            )
            flesch_kincaid_grade = self._calculate_flesch_kincaid_grade(
                text, word_count, sentence_count
            )

        # Additional readability factors
        readability_factors = self._get_readability_factors(text)

        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_words_per_sentence": round(avg_words_per_sentence, 1),
            "paragraph_count": paragraph_count,
            "flesch_reading_ease": round(flesch_score, 1),
            "flesch_kincaid_grade": round(flesch_kincaid_grade, 1),
            "grade_level": self._flesch_to_grade(flesch_score),
            "readability_factors": readability_factors,
        }

    def _empty_readability(self) -> Dict[str, Any]:
        """Return empty readability analysis"""
        return {
            "word_count": 0,
            "sentence_count": 0,
            "avg_words_per_sentence": 0.0,
            "paragraph_count": 0,
            "flesch_reading_ease": 0.0,
            "flesch_kincaid_grade": 0.0,
            "grade_level": "Unknown",
            "readability_factors": {},
        }

    def _count_words_enhanced(self, text: str) -> int:
        """Count words using enhanced tokenization"""
        if nltk and word_tokenize:
            try:
                tokens = word_tokenize(text.lower())
                return len([token for token in tokens if token.isalpha()])
            except Exception:
                pass

        # Fallback regex-based counting
        words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
        return len(words)

    def _count_sentences_enhanced(self, text: str) -> int:
        """Count sentences using NLTK or fallback"""
        if textstat and sent_tokenize:
            try:
                sentences = sent_tokenize(text)
                return len(sentences)
            except Exception:
                pass

        # Fallback method
        sentences = re.split(r"[.!?]+", text)
        return len([s for s in sentences if s.strip()])

    def _count_paragraphs(self, text: str) -> int:
        """Count paragraphs in text"""
        paragraphs = text.split("\n\n")
        return len([p for p in paragraphs if p.strip()])

    def _calculate_flesch_score(
        self, text: str, word_count: int, sentence_count: int
    ) -> float:
        """Calculate Flesch Reading Ease score"""
        if word_count == 0 or sentence_count == 0:
            return 0.0

        # Count syllables
        words = re.findall(r"\b\w+\b", text.lower())
        total_syllables = sum(self._count_syllables(word) for word in words)

        if total_syllables == 0:
            return 0.0

        # Flesch Reading Ease formula
        return (
            206.835
            - 1.015 * (word_count / sentence_count)
            - 84.6 * (total_syllables / word_count)
        )

    def _calculate_flesch_kincaid_grade(
        self, text: str, word_count: int, sentence_count: int
    ) -> float:
        """Calculate Flesch-Kincaid Grade Level"""
        if word_count == 0 or sentence_count == 0:
            return 0.0

        # Count syllables
        words = re.findall(r"\b\w+\b", text.lower())
        total_syllables = sum(self._count_syllables(word) for word in words)

        if total_syllables == 0:
            return 0.0

        # Flesch-Kincaid Grade Level formula
        return (
            0.39 * (word_count / sentence_count)
            + 11.8 * (total_syllables / word_count)
            - 15.59
        )

    def _get_readability_factors(self, text: str) -> Dict[str, float]:
        """Get additional factors that affect readability"""
        sentences = self._get_sentences_enhanced(text)
        words = self._get_words_enhanced(text)

        if not sentences or not words:
            return {}

        # Average words per sentence
        avg_words_per_sentence = len(words) / len(sentences)

        # Complex word ratio (words > 6 characters)
        complex_words = [w for w in words if len(w) > 6]
        complex_word_ratio = len(complex_words) / len(words) if words else 0

        # Long sentence ratio (sentences > 20 words)
        long_sentences = 0
        for sentence in sentences:
            sentence_words = re.findall(r"\b\w+\b", sentence)
            if len(sentence_words) > 20:
                long_sentences += 1

        long_sentence_ratio = long_sentences / len(sentences) if sentences else 0

        return {
            "avg_words_per_sentence": round(avg_words_per_sentence, 1),
            "complex_word_ratio": round(complex_word_ratio * 100, 1),
            "long_sentence_ratio": round(long_sentence_ratio * 100, 1),
        }

    def _get_sentences_enhanced(self, text: str) -> List[str]:
        """Get sentences using NLTK or fallback"""
        if nltk and sent_tokenize:
            try:
                result = sent_tokenize(text)
                return [str(s) for s in result]
            except Exception:
                pass

        # Fallback sentence splitting
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _get_words_enhanced(self, text: str) -> List[str]:
        """Get words using NLTK or fallback"""
        if nltk and word_tokenize:
            try:
                tokens = word_tokenize(text.lower())
                return [token for token in tokens if token.isalpha()]
            except Exception:
                pass

        # Fallback word extraction
        return re.findall(r"\b[a-zA-Z]+\b", text.lower())

    def _analyze_quality(self, text: str) -> Dict[str, Any]:
        """Analyze comprehensive writing quality indicators"""
        if not text.strip():
            return self._empty_quality()

        # Basic text processing
        sentences = self._get_sentences_enhanced(text)
        words = self._get_words_enhanced(text)

        if not sentences or not words:
            return self._empty_quality()

        # Calculate enhanced metrics
        passive_voice_percentage = self._calculate_passive_voice(sentences)
        sentence_variety = self._calculate_sentence_variety(sentences)
        transition_words_score = self._calculate_transition_words(text)
        hedging_language = self._calculate_hedging_language(text, len(words))
        academic_tone = self._calculate_academic_tone(text)

        # Legacy metrics for backward compatibility
        total_words = len(words)
        total_sentences = len(sentences)
        avg_sentence_length = (
            total_words / total_sentences if total_sentences > 0 else 0
        )
        long_sentences = sum(1 for s in sentences if len(s.split()) > 25)
        short_sentences = sum(1 for s in sentences if len(s.split()) < 5)

        return {
            # Enhanced metrics
            "passive_voice_percentage": passive_voice_percentage,
            "sentence_variety": sentence_variety,
            "transition_words": transition_words_score,
            "hedging_language": hedging_language,
            "academic_tone": academic_tone,
            # Legacy metrics
            "average_sentence_length": avg_sentence_length,
            "long_sentences": long_sentences,
            "short_sentences": short_sentences,
            "sentence_variety_legacy": (long_sentences + short_sentences)
            / total_sentences
            if total_sentences > 0
            else 0,
        }

    def _empty_quality(self) -> Dict[str, Any]:
        """Return empty quality analysis"""
        return {
            "passive_voice_percentage": 0.0,
            "sentence_variety": 0.0,
            "transition_words": 0.0,
            "hedging_language": 0.0,
            "academic_tone": 0.0,
            "average_sentence_length": 0.0,
            "long_sentences": 0,
            "short_sentences": 0,
            "sentence_variety_legacy": 0.0,
        }

    def _calculate_passive_voice(self, sentences: List[str]) -> float:
        """Calculate percentage of sentences containing passive voice"""
        if not sentences:
            return 0.0

        passive_count = 0
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for pattern in self.PASSIVE_INDICATORS:
                if re.search(pattern, sentence_lower):
                    passive_count += 1
                    break

        return round((passive_count / len(sentences)) * 100, 1)

    def _calculate_sentence_variety(self, sentences: List[str]) -> float:
        """Calculate sentence variety based on length variation"""
        if len(sentences) < 2:
            return 0.0

        # Calculate word counts per sentence
        word_counts = []
        for sentence in sentences:
            words_in_sentence = re.findall(r"\b\w+\b", sentence)
            word_counts.append(len(words_in_sentence))

        if len(word_counts) < 2:
            return 0.0

        # Calculate coefficient of variation (normalized variance)
        try:
            mean_length = sum(word_counts) / len(word_counts)
            if mean_length == 0:
                return 0.0

            var = variance(word_counts)
            cv = (var**0.5) / mean_length

            # Convert to 0-100 scale (higher = more variety)
            # Typical good writing has CV around 0.3-0.6
            variety_score = min(100, cv * 200)
            return round(float(variety_score), 1)

        except (ZeroDivisionError, ValueError):
            return 0.0

    def _calculate_transition_words(self, text: str) -> float:
        """Calculate transition word usage score"""
        text_lower = text.lower()
        word_count = len(re.findall(r"\b\w+\b", text))

        if word_count == 0:
            return 0.0

        transition_count = 0
        for category in self.TRANSITION_WORDS.values():
            for phrase in category:
                # Count occurrences of each transition phrase
                transition_count += len(
                    re.findall(rf"\b{re.escape(phrase)}\b", text_lower)
                )

        # Calculate per 100 words and normalize to 0-100 scale
        transitions_per_100 = (transition_count / word_count) * 100

        # Good writing typically has 2-5 transition phrases per 100 words
        # Score based on optimal range
        if transitions_per_100 < 1:
            score = transitions_per_100 * 30  # Low usage
        elif transitions_per_100 <= 5:
            score = 30 + (transitions_per_100 - 1) * 17.5  # Optimal range
        else:
            score = max(0, 100 - (transitions_per_100 - 5) * 10)  # Overuse penalty

        return round(min(100, score), 1)

    def _calculate_hedging_language(self, text: str, word_count: int) -> float:
        """Calculate hedging language frequency"""
        if word_count == 0:
            return 0.0

        text_lower = text.lower()
        hedging_count = 0

        for pattern in self.HEDGING_PATTERNS:
            hedging_count += len(re.findall(pattern, text_lower))

        # Calculate per 100 words
        hedging_per_100 = (hedging_count / word_count) * 100

        # Convert to 0-100 scale
        # Academic writing typically has 3-8 hedging phrases per 100 words
        if hedging_per_100 <= 8:
            score = (hedging_per_100 / 8) * 100
        else:
            score = max(0, 100 - (hedging_per_100 - 8) * 5)  # Penalty for overuse

        return round(score, 1)

    def _calculate_academic_tone(self, text: str) -> float:
        """Calculate academic tone strength"""
        text_lower = text.lower()
        word_count = len(re.findall(r"\b\w+\b", text))

        if word_count == 0:
            return 0.0

        academic_score = 0.0

        # Check for formal verbs
        formal_verb_count = 0
        for verb in self.ACADEMIC_INDICATORS["formal_verbs"]:
            formal_verb_count += len(re.findall(rf"\b{verb}", text_lower))

        # Check for scholarly phrases
        scholarly_phrase_count = 0
        for phrase in self.ACADEMIC_INDICATORS["scholarly_phrases"]:
            scholarly_phrase_count += len(
                re.findall(rf"{re.escape(phrase)}", text_lower)
            )

        # Check for formal connectors
        formal_connector_count = 0
        for connector in self.ACADEMIC_INDICATORS["formal_connectors"]:
            formal_connector_count += len(re.findall(rf"\b{connector}\b", text_lower))

        # Calculate component scores
        verb_score = min(40, (formal_verb_count / word_count) * 1000 * 40)
        phrase_score = min(30, (scholarly_phrase_count / word_count) * 1000 * 30)
        connector_score = min(30, (formal_connector_count / word_count) * 1000 * 30)

        academic_score = verb_score + phrase_score + connector_score

        # Penalty for informal contractions
        contractions = len(re.findall(r"\b\w+'\w+\b", text))
        contraction_penalty = min(20, (contractions / word_count) * 100 * 20)

        final_score = max(0, academic_score - contraction_penalty)
        return round(final_score, 1)

    def _analyze_vocabulary(self, text: str) -> Dict[str, Any]:
        """Analyze comprehensive vocabulary richness and word patterns"""
        if not text.strip():
            return self._empty_vocabulary()

        # Enhanced word tokenization
        words = self._get_words_enhanced(text)
        if not words:
            return self._empty_vocabulary()

        total_words = len(words)
        unique_words = len(set(words))

        # Hapax legomena (words appearing once)
        word_counts = Counter(words)
        hapax = sum(1 for count in word_counts.values() if count == 1)

        # Get stop words for meaningful analysis
        stop_words = self._get_stop_words()

        # Filter out stop words and short words for meaningful analysis
        meaningful_words = [
            word for word in words if len(word) > 2 and word not in stop_words
        ]

        meaningful_unique = len(set(meaningful_words))
        meaningful_total = len(meaningful_words)

        # Calculate enhanced vocabulary metrics
        type_token_ratio = unique_words / total_words if total_words > 0 else 0
        lexical_diversity = (unique_words / total_words) * 100 if total_words > 0 else 0
        avg_word_length = sum(len(word) for word in words) / total_words

        # Most frequent words (excluding stop words)
        meaningful_word_freq = Counter(meaningful_words)
        most_frequent = meaningful_word_freq.most_common(20)

        # Extract meaningful phrases (bigrams and trigrams)
        unique_phrases = self._extract_phrases(text, stop_words)

        return {
            # Basic metrics
            "total_words": total_words,
            "unique_words": unique_words,
            "vocabulary_richness": unique_words / total_words if total_words > 0 else 0,
            "hapax_legomena": hapax,
            "hapax_percentage": hapax / total_words if total_words > 0 else 0,
            # Enhanced metrics
            "meaningful_words": meaningful_total,
            "meaningful_unique": meaningful_unique,
            "type_token_ratio": round(type_token_ratio, 3),
            "lexical_diversity": round(lexical_diversity, 1),
            "average_word_length": round(avg_word_length, 1),
            "most_frequent_words": most_frequent[:10],  # Top 10 for API response size
            "unique_phrases": unique_phrases[:10],  # Top 10 phrases
        }

    def _empty_vocabulary(self) -> Dict[str, Any]:
        """Return empty vocabulary analysis"""
        return {
            "total_words": 0,
            "unique_words": 0,
            "vocabulary_richness": 0.0,
            "hapax_legomena": 0,
            "hapax_percentage": 0.0,
            "meaningful_words": 0,
            "meaningful_unique": 0,
            "type_token_ratio": 0.0,
            "lexical_diversity": 0.0,
            "average_word_length": 0.0,
            "most_frequent_words": [],
            "unique_phrases": [],
        }

    def _get_stop_words(self) -> set[str]:
        """Get stop words, with fallback if NLTK is not available"""
        if nltk and stopwords:
            try:
                return set(stopwords.words("english"))
            except Exception:
                pass

        # Fallback stop words
        return {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "for",
            "from",
            "has",
            "he",
            "in",
            "is",
            "it",
            "its",
            "of",
            "on",
            "that",
            "the",
            "to",
            "was",
            "will",
            "with",
            "would",
            "i",
            "you",
            "we",
            "they",
            "this",
            "these",
            "those",
            "or",
            "but",
            "not",
            "have",
            "had",
            "do",
            "does",
            "did",
            "can",
            "could",
            "should",
            "may",
            "might",
            "must",
        }

    def _extract_phrases(
        self, text: str, stop_words: set[str], limit: int = 15
    ) -> List[Dict[str, Any]]:
        """Extract meaningful phrases (n-grams) from text"""
        words = self._get_words_enhanced(text)

        # Extract bigrams (2-word phrases)
        bigrams = self._extract_ngrams(words, 2, stop_words)
        phrases = [
            {"phrase": phrase, "count": count, "type": "bigram"}
            for phrase, count in bigrams.most_common(limit // 2)
        ]

        # Extract trigrams (3-word phrases)
        trigrams = self._extract_ngrams(words, 3, stop_words)
        phrases.extend(
            [
                {"phrase": phrase, "count": count, "type": "trigram"}
                for phrase, count in trigrams.most_common(limit // 2)
            ]
        )

        # Sort by frequency and return top phrases
        phrases.sort(key=lambda x: x["count"], reverse=True)
        return phrases[:limit]

    def _extract_ngrams(
        self, words: List[str], n: int, stop_words: set[str]
    ) -> Counter[str]:
        """Extract n-grams from words, filtering out stop words and common patterns"""
        if len(words) < n:
            return Counter()

        # Generate n-grams
        if nltk and hasattr(nltk.util, "ngrams"):
            try:
                phrase_list = list(nltk.ngrams(words, n))
            except Exception:
                # Fallback to manual n-gram generation
                phrase_list = [
                    tuple(words[i : i + n]) for i in range(len(words) - n + 1)
                ]
        else:
            # Manual n-gram generation
            phrase_list = [tuple(words[i : i + n]) for i in range(len(words) - n + 1)]

        # Filter meaningful phrases
        meaningful_phrases = []
        for phrase_tuple in phrase_list:
            # Skip phrases with stop words
            if any(word in stop_words for word in phrase_tuple):
                continue

            # Skip phrases with very short words
            if any(len(word) < 3 for word in phrase_tuple):
                continue

            # Join into string
            phrase = " ".join(phrase_tuple)

            # Skip phrases with repeated words
            if len(set(phrase_tuple)) < len(phrase_tuple):
                continue

            meaningful_phrases.append(phrase)

        return Counter(meaningful_phrases)

    def _check_grammar(self, text: str) -> List[str]:
        """Basic grammar and style checks"""
        issues = []

        # Check for double spaces
        if "  " in text:
            issues.append("Contains double spaces")

        # Check for multiple consecutive punctuation
        if re.search(r"[.!?]{2,}", text):
            issues.append("Multiple consecutive punctuation marks")

        # Check for sentences starting with lowercase
        sentences = re.split(r"[.!?]+", text)
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence[0].islower():
                issues.append("Sentence starts with lowercase letter")
                break  # Only report once

        # Check for missing spaces after punctuation
        if re.search(r"[.!?][A-Z]", text):
            issues.append("Missing space after punctuation")

        return issues

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (basic implementation)"""
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith("e"):
            count -= 1
        if count == 0:
            count += 1
        return count

    def _flesch_to_grade(self, score: float) -> str:
        """Convert Flesch score to grade level"""
        if score >= 90:
            return "5th grade"
        elif score >= 80:
            return "6th grade"
        elif score >= 70:
            return "7th grade"
        elif score >= 60:
            return "8th-9th grade"
        elif score >= 50:
            return "10th-12th grade"
        elif score >= 30:
            return "College"
        else:
            return "College Graduate"
