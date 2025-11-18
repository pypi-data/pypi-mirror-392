# Extracta: Modular Content Analysis Platform & Development Guide

## Vision

Build a **modular content analysis platform** where diverse content formats (videos, documents, images, audio, code, websites) are intelligently ingested, standardized textual representations are extracted, and consistent analysis workflows are applied.

Core principle: **Extract once, analyze many ways**
- Each content format has a dedicated **ingestion lens** that extracts standardized textual descriptions
- Extracted descriptions flow to appropriate **content analyzers** for insights and metrics
- All analyses feed into **grading and assessment** workflows

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Orchestration Layer (CLI, API, future assessment-bench)
│  - Route content by file type
│  - Aggregate analysis results
│  - Manage workflows
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Content Ingestion Layer (LENSES)
│  - Extract standardized textual descriptions from files
│  - Convert raw content to analyzable text representations
│  - May compose/delegate to other lenses for complex formats
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Content Analysis Layer (ANALYZERS)
│  - Analyze textual descriptions and metadata
│  - Generate metrics, insights, quality scores
│  - Reusable across multiple content types
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Assessment & Feedback Layer
│  - rubric_manager: Apply custom rubrics to analysis results
│  - feedback_generator: Generate detailed feedback
│  - accessibility considerations
└─────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Content Ingestion Lenses

### Currently Implemented Lenses

#### video-lens
**Status:** ✅ Implemented (basic)

- **Input:** Video files (mp4, mov, avi, webm, mkv, flv, wmv, m4v)
- **Extraction:**
  - Video validation and metadata
  - Key frame extraction
  - Audio extraction from video
  - Placeholder for speech-to-text transcription
  - Placeholder for visual scene descriptions
- **Output:**
  ```json
  {
    "content_type": "video",
    "duration": 120.5,
    "resolution": "1920x1080",
    "fps": 30,
    "frames_extracted": 10,
    "transcript": "Textual transcription placeholder...",
    "frame_descriptions": [
      "Presentation slide with title and bullet points",
      "Speaker presenting to camera with good eye contact"
    ],
    "visual_summary": "Video content showing presentation slides and speaker delivery",
    "audio_quality": "Clear audio with good volume levels",
    "scene_changes": 8
  }
  ```
- **Delegate to:**
  - `text_analyzer` on transcript and descriptions

---

#### audio-lens
**Status:** ✅ Implemented (basic)

- **Input:** Audio files (mp3, wav, flac, aac, ogg, m4a, wma)
- **Extraction:**
  - Audio validation and metadata
  - Placeholder for speech-to-text transcription
  - Audio format conversion preparation
- **Output:**
  ```json
  {
    "content_type": "audio",
    "duration": 180.5,
    "sample_rate": 44100,
    "channels": 2,
    "format": "mp3",
    "transcript": "Textual transcription placeholder...",
    "audio_quality": "Good quality stereo audio"
  }
  ```
- **Delegate to:**
  - `text_analyzer` on transcript

---

#### image-lens
**Status:** ✅ Implemented (basic)

- **Input:** Image files (jpg, jpeg, png, gif, bmp, tiff, webp)
- **Extraction:**
  - Image validation and metadata
  - OCR text extraction
  - Basic visual quality assessment
- **Output:**
  ```json
  {
    "content_type": "image",
    "width": 1920,
    "height": 1080,
    "format": "JPEG",
    "extracted_text": "OCR text content from image...",
    "visual_quality": "High quality image",
    "accessibility": {
      "has_alt_text": false,
      "suggested_alt": "Image description placeholder"
    }
  }
  ```
- **Delegate to:**
  - `text_analyzer` on extracted_text
  - `image_analyzer` on visual metrics

---

#### document-lens
**Status:** ✅ Implemented (basic)

- **Input:** Document files (txt, md, rst)
- **Extraction:**
  - Text extraction
  - Basic structure analysis
- **Output:**
  ```json
  {
    "content_type": "document",
    "text": "Full extracted text content...",
    "word_count": 1250,
    "structure": {
      "headings": ["Introduction", "Methods", "Results"],
      "paragraphs": 15
    },
    "metadata": {
      "encoding": "utf-8",
      "format": "markdown"
    }
  }
  ```
- **Delegate to:**
  - `text_analyzer` on extracted text

---

### Future Lens Implementations

#### code-lens
**Status:** ✅ Implemented (basic)

- **Input:** Code files (.py, .js, .java, .rb, .sql, etc.) or Jupyter notebooks (.ipynb)
- **Extraction:**
  - Source code as structured AST (Python)
  - Comments and docstrings
  - Function/class definitions
  - Code metrics (complexity, lines of code)
  - SQL statement parsing and analysis
  - For notebooks: cells, outputs, visualizations
- **Output:**
  ```json
  {
    "code": "Full source code",
    "language": "python",
    "structure": {
      "functions": [{"name": "analyze_data", "complexity": 5}],
      "classes": [{"name": "Analyzer", "methods": 8}],
      "imports": ["numpy", "pandas"]
    },
    "metrics": {
      "lines_of_code": 245,
      "cyclomatic_complexity": 8,
      "maintainability_index": 75
    },
    "documentation": {
      "docstrings": 85,
      "comments": 120
    }
  }
  ```
- **SQL Analysis Output:**
  ```json
  {
    "language": "sql",
    "statements": [
      {
        "type": "select",
        "tables": ["users", "posts"],
        "columns": ["id", "name", "title"],
        "joins": ["posts"],
        "conditions": ["active = 1"]
      }
    ],
    "statement_types": {"select": 2, "insert": 1, "create_table": 1},
    "tables": ["users", "posts", "orders"],
    "columns": ["id", "name", "email", "active"],
    "complexity_metrics": {
      "total_statements": 4,
      "unique_tables": 3,
      "join_count": 1
    }
  }
  ```
- **Delegate to:**
  - `code_analyzer` on structure and metrics
  - `text_analyzer` on docstrings and comments

---

#### slide-lens
**Status:** ❌ Planned

- **Input:** Slide presentation files (pptx, odp, pdf with slides)
- **Extraction:**
  - Per-slide text extraction
  - Slide layout analysis
  - Embedded images and media
- **Output:**
  ```json
  {
    "slides": [
      {
        "number": 1,
        "title": "Introduction",
        "text": "Full text content on slide",
        "layout": "title_and_content",
        "images": [{"description": "Chart showing data"}]
      }
    ],
    "metadata": {
      "title": "Presentation Title",
      "slide_count": 20
    }
  }
  ```
- **Delegate to:**
  - `text_analyzer` on all extracted text
  - `image_analyzer` on slide images

---

#### web-lens
**Status:** ❌ Planned

- **Input:** Web projects (HTML/CSS/JS, React, WordPress, etc.)
- **Extraction:**
  - Source code analysis
  - Rendered content screenshots
  - Accessibility analysis
  - Performance metrics
- **Output:**
  ```json
  {
    "source_analysis": {
      "languages": ["javascript", "html", "css"],
      "framework": "react",
      "components": 15
    },
    "rendered_content": {
      "screenshots": ["homepage.png", "contact.png"],
      "pages": 5
    },
    "accessibility": {
      "wcag_score": 0.85,
      "issues": ["Missing alt text on 2 images"]
    },
    "performance": {
      "load_time": 1.2,
      "bundle_size": 245000
    }
  }
  ```
- **Delegate to:**
  - `code_lens` on source files
  - `image_analyzer` on screenshots
  - `text_analyzer` on extracted content

---

#### repo-lens
**Status:** ❌ Planned

- **Input:** GitHub repository URLs or local repo directories
- **Process:**
  1. Clone/download repository
  2. Scan file types
  3. Route files to appropriate lenses
- **Output:**
  ```json
  {
    "repository_metadata": {
      "language": "python",
      "languages": ["python", "javascript"],
      "files": 45
    },
    "analysis_by_type": {
      "code_files": {...},
      "documentation": {...},
      "images": {...}
    },
    "aggregated_metrics": {
      "total_lines_of_code": 5000,
      "test_coverage": 0.75
    }
  }
  ```
- **Delegate to:** Multiple lenses in sequence

---

#### ai-conversation-lens
**Status:** ✅ Implemented

- **Input:** AI conversation files (JSON exports, text logs, markdown)
- **Extraction:**
  - ChatGPT, Claude, Bard, and generic conversation format support
  - Message role detection (user/assistant)
  - Conversation structure parsing
  - Metadata extraction (platform, title, timestamps)
- **Output:**
  ```json
  {
    "platform": "chatgpt",
    "title": "Python Debugging Session",
    "messages": [
      {
        "role": "user",
        "content": "Why does my Python code give a NameError?",
        "timestamp": "2024-01-15T10:30:00Z"
      },
      {
        "role": "assistant",
        "content": "The NameError occurs when you try to use a variable that hasn't been defined...",
        "timestamp": "2024-01-15T10:30:05Z"
      }
    ],
    "message_count": 12,
    "file_path": "/path/to/conversation.json",
    "extraction_timestamp": "2024-01-15T11:00:00Z"
  }
  ```
- **Delegate to:**
  - `conversation_analyzer` for cognitive intent classification

---

## Layer 2: Content Analyzers

### Currently Implemented Analyzers

#### text-analyzer
**Status:** ✅ Implemented

**Input:** Any textual content (transcripts, extracted text, descriptions)

**Analysis:**
- Readability metrics (Flesch-Kincaid, SMOG)
- Vocabulary richness and diversity
- Sentiment analysis
- Grammar and style checking
- Content structure analysis

**Output:**
```json
{
  "readability": {
    "flesch_reading_ease": 65.5,
    "grade_level": 8.5,
    "reading_time_minutes": 3
  },
  "vocabulary": {
    "unique_words": 450,
    "vocabulary_richness": 0.78,
    "hapax_legomena": 120
  },
  "sentiment": {
    "positive_words": 45,
    "negative_words": 12,
    "sentiment_score": 0.25
  },
  "quality": {
    "grammar_issues": ["Double space found"],
    "clarity_score": 0.85
  }
}
```

---

#### image-analyzer
**Status:** ✅ Implemented (basic)

**Input:** Image data and metadata

**Analysis:**
- Basic quality metrics
- Format validation
- Accessibility considerations

**Output:**
```json
{
  "dimensions": {"width": 1920, "height": 1080},
  "quality": {"format": "JPEG", "size_mb": 2.1},
  "accessibility": {"has_alt_text": false}
}
```

---

#### citation-analyzer
**Status:** ✅ Implemented

**Input:** Any textual content (documents, papers, essays)

**Analysis:**
- Citation-reference relationship validation
- Bibliography padding detection
- Citation stuffing identification
- Academic integrity scoring
- Multiple citation style support (APA, MLA, Chicago, Harvard)

**Output:**
```json
{
  "citation_analysis": {
    "total_citations": 15,
    "unique_citations": 12,
    "citation_styles_detected": ["apa", "mla"],
    "total_references": 18,
    "reference_validation": {
      "citations_without_references": ["(Smith, 2020)"],
      "references_without_citations": ["Johnson, A. (2019). Title..."],
      "citation_coverage": 0.85,
      "reference_utilization": 0.75
    },
    "suspicious_patterns": {
      "citation_stuffing": {"detected": false, "instances": []},
      "bibliography_padding": {"detected": true, "count": 3},
      "future_dates": {"detected": false, "instances": []}
    },
    "academic_integrity_score": 78
  }
}
```

---

#### reference-analyzer
**Status:** ✅ Implemented

**Input:** Any textual content with bibliography/references

**Analysis:**
- DOI validation and format checking
- CrossRef API integration for reference verification
- URL extraction and accessibility testing
- Academic domain classification
- Reference completeness assessment

**Output:**
```json
{
  "reference_analysis": {
    "total_references": 18,
    "format_validation": {
      "valid_references": 15,
      "invalid_references": 3,
      "completeness_score": 83.3
    },
    "doi_analysis": {
      "total_dois": 12,
      "valid_dois": 10,
      "dois": [...]
    },
    "url_analysis": {
      "total_urls": 8,
      "academic_urls": 6,
      "accessible_urls": 7,
      "broken_urls": 1
    },
    "crossref_validation": {
      "checked_dois": 5,
      "valid_dois": 4,
      "resolved_metadata": [...]
    },
    "reference_quality_score": 82
  }
}
```

---

#### url-analyzer
**Status:** ✅ Implemented

**Input:** Any textual content with URLs

**Analysis:**
- HTTP status code validation (404 detection)
- Response time analysis
- Robots.txt compliance checking
- Domain reputation assessment
- Academic vs. commercial domain classification

**Output:**
```json
{
  "url_analysis": {
    "total_urls": 8,
    "validation_results": {
      "accessible_urls": 7,
      "broken_urls": 1,
      "timeout_urls": 0
    },
    "robots_compliance": {
      "compliant_sites": 5,
      "blocked_sites": 0
    },
    "domain_analysis": {
      "academic_domains": 6,
      "commercial_domains": 1,
      "suspicious_domains": 0
    },
    "accessibility_report": {
      "overall_accessibility": 87.5,
      "error_rate": 12.5,
      "recommendations": [...]
    },
    "url_quality_score": 84
  }
}
```

---

#### conversation-analyzer
**Status:** ✅ Implemented

**Input:** AI conversation data (extracted by ai-conversation-lens)

**Analysis:**
- Cognitive intent classification using Gemini LLM
- Delegation vs. Scaffolding behavior detection
- Session-level learning pattern analysis
- Academic integrity assessment for AI-assisted work

**Output:**
```json
{
  "conversation_analysis": {
    "total_prompts": 15,
    "classified_prompts": 15,
    "session_metrics": {
      "total_prompts": 15,
      "intent_counts": {"Delegation": 5, "Scaffolding": 8, "Other": 2},
      "scaffolding_ratio": 0.615,
      "intent_sequence": ["Scaffolding", "Delegation", ...],
      "subcategory_breakdown": {"Explanation": 4, "Ideation": 3, ...},
      "average_confidence": 0.87,
      "learning_patterns": {
        "consistent_scaffolding": true,
        "learning_progression": "strong"
      }
    },
    "learning_assessment": {
      "learning_quality_score": 82.3,
      "learning_level": "Good",
      "description": "Moderate evidence of learning engagement",
      "recommendations": [...]
    }
  }
}
```

---

### Future Analyzer Implementations

#### code-analyzer
**Status:** ❌ Planned

**Input:** Code structure and metrics from code-lens

**Analysis:**
- Code quality metrics (complexity, maintainability)
- Best practices adherence
- Documentation quality
- Security issues

**Output:**
```json
{
  "quality_metrics": {
    "maintainability_index": 75,
    "cyclomatic_complexity": 8,
    "code_duplication_ratio": 0.08
  },
  "best_practices": {
    "naming_conventions": 0.90,
    "documentation_completeness": 0.75
  },
  "issues": {
    "potential_bugs": [],
    "security_concerns": []
  }
}
```

---

#### accessibility-analyzer
**Status:** ❌ Planned

**Input:** Content from any lens (text, images, structure)

**Analysis:** WCAG 2.1 compliance
- Color contrast ratios
- Alt text quality
- Heading hierarchy
- Keyboard navigation

**Output:**
```json
{
  "wcag_level": "AA",
  "score": 0.85,
  "issues": [
    {
      "level": "error",
      "criterion": "1.4.3 Contrast (Minimum)",
      "suggestion": "Increase contrast ratio"
    }
  ]
}
```

---

## Layer 3: Assessment & Feedback

### Shared Assessment Infrastructure

#### rubric_manager (Shared)
**Status:** ✅ Implemented

- Core rubric system shared across all content types
- Custom rubric creation and management
- Scoring scale configuration
- Assessment result calculation
- Repository for storing rubrics

#### feedback_generator (Shared)
**Status:** ✅ Implemented (basic)

- Template-based feedback generation
- Audience-specific messaging
- Integration with analysis results

### Content-Specific Assessment

#### Lens-Specific Rubrics
**Status:** ✅ Implemented (video_lens example)

Each lens package can include content-specific rubrics and assessment helpers:

```python
# video_lens/rubrics.py
from ..rubric_manager import Rubric, RubricBuilder

def create_video_presentation_rubric() -> Rubric:
    # Video-specific rubric with delivery, content, technical criteria

def assess_video_content(analysis_results, rubric):
    # Video-specific assessment logic that knows how to map
    # analysis results to rubric criteria
```

**Benefits:**
- Content-specific rubric templates
- Lens packages are more self-contained
- Specialized assessment logic per content type
- Shared core rubric infrastructure

#### default_rubrics (Shared + Lens-Specific)
**Status:** ✅ Implemented

- **Shared:** Academic, business, creative, general rubrics
- **Lens-specific:** Video presentation, audio quality, image design, etc.

---

## Current Implementation Status

| Component | Status | Implementation Level |
|-----------|--------|---------------------|
| `video_lens` | ✅ | Basic extraction + textual descriptions |
| `audio_lens` | ✅ | Basic extraction + transcription prep |
| `image_lens` | ✅ | Basic extraction + OCR |
| `document_lens` | ✅ | Basic text extraction + Office docs |
| `text_analyzer` | ✅ | Full readability, sentiment, vocabulary analysis |
| `image_analyzer` | ✅ | Basic quality metrics |
| `citation_analyzer` | ✅ | Citation-reference validation + academic integrity |
| `reference_analyzer` | ✅ | Bibliography quality + DOI/CrossRef validation |
| `url_analyzer` | ✅ | URL accessibility + domain reputation analysis |
| `conversation_analyzer` | ✅ | AI conversation cognitive intent classification |
| `security` | ✅ | Input sanitization, URL validation, content filtering |
| `rubric_manager` | ✅ | Complete rubric system |
| `feedback_generator` | ✅ | Template-based feedback |
| `ai_conversation_lens` | ✅ | AI conversation file extraction |
| `code_lens` | ✅ | Multi-language code analysis + SQL support |
| `slide_lens` | ❌ | Not implemented |
| `web_lens` | ❌ | Not implemented |
| `repo_lens` | ❌ | Not implemented |
| `code_analyzer` | ❌ | Not implemented |
| `accessibility_analyzer` | ❌ | Not implemented |

## Technology Stack (Current)

### Core Dependencies
- **Python:** 3.10+
- **Build:** uv, hatchling
- **Linting:** ruff
- **Testing:** pytest
- **Types:** mypy

### Lens Implementations
- **video_lens:** ffmpeg-python, pydantic
- **audio_lens:** ffmpeg-python
- **image_lens:** Pillow, pytesseract
- **document_lens:** Built-in text processing
- **CLI:** Click
- **API:** FastAPI, Uvicorn

### Future Additions
- **code_lens:** AST parsing, tree-sitter, radon
- **web_lens:** Selenium/Playwright, BeautifulSoup
- **repo_lens:** GitPython, GitHub API
- **ML/AI:** faster-whisper (audio), vision models (images)

### Analyzers
- **text_analyzer:** Built-in algorithms (expand to spaCy, NLTK)
- **image_analyzer:** Pillow (expand to OpenCV, scikit-image)
- **citation_analyzer:** Regex patterns, CrossRef API, academic integrity scoring
- **reference_analyzer:** DOI validation, URL checking, bibliography quality assessment
- **url_analyzer:** HTTP validation, domain reputation, robots.txt compliance
- **conversation_analyzer:** Gemini LLM API, cognitive intent classification
- **code_analyzer:** radon, pylint, flake8 (planned)
- **accessibility_analyzer:** axe-core, webaim (planned)

---

## Development Roadmap

### Phase 1: Core Content Types ✅ (Current)
**Completed:**
- Video, audio, image, document ingestion
- Text analysis with comprehensive metrics
- Citation & reference validation system
- Academic integrity assessment tools
- Basic rubric-based assessment
- CLI and API interfaces
- Published to PyPI

**Deliverable:** Functional content analysis for basic use cases with academic integrity checking

### Phase 2: Enhanced Analysis (Next)
**Goals:**
- Improve existing analyzers with ML models
- Add code analysis capabilities
- Enhanced feedback generation
- Better OCR and transcription
- Academic integrity enhancements (screenshots, Wayback Machine, OCR analysis)

**Timeline:** 1-2 months

### Phase 3: Extended Content Types
**Add:**
- `code_lens` and `code_analyzer`
- `slide_lens` for presentations
- `web_lens` for web projects
- `repo_lens` for repositories

**Timeline:** 2-3 months

### Phase 4: Advanced Features
**Add:**
- `accessibility_analyzer`
- Multi-artifact portfolio assessment
- Parallel processing optimization
- Plugin architecture

**Timeline:** 3-4 months

### Phase 5: Integration & Scale
**Add:**
- LMS integrations (Canvas, Blackboard)
- GitHub Classroom integration
- Distributed processing
- Advanced ML models

**Timeline:** 4-6 months

---

## 📦 Package Structure & Implementation Plan

### **Core Principle**: Python Package → Multiple Interfaces

Build `extracta` as pure Python package first, add UI layers later.

### **Package Structure (Python First)**

```
extracta/
├── extracta/
│   ├── __init__.py
│   ├── lenses/              # Content extraction
│   │   ├── __init__.py
│   │   ├── audio_lens/      # From deep-talk
│   │   ├── video_lens/      # Audio + visual
│   │   ├── code_lens/       # From existing code-lens
│   │   ├── document_lens/    # New implementation
│   │   └── base_lens.py     # Common interface
│   ├── analyzers/           # Content analysis
│   │   ├── __init__.py
│   │   ├── text_analyzer/    # New - critical
│   │   ├── image_analyzer/   # New - critical
│   │   ├── citation_analyzer/ # Academic integrity
│   │   ├── reference_analyzer/ # Bibliography validation
│   │   ├── url_analyzer/     # URL validation
│   │   ├── code_analyzer/    # Extract from code-lens
│   │   └── base_analyzer.py  # Common interface
│   ├── grading/             # Rubrics & scoring
│   │   ├── __init__.py
│   │   ├── grading_lens/     # New implementation
│   │   ├── rubric_manager/   # New implementation
│   │   └── feedback_generator.py
│   ├── orchestration/       # Workflow management
│   │   ├── __init__.py
│   │   ├── workflow_engine.py
│   │   └── content_router.py
│   └── shared/              # Common utilities
│       ├── __init__.py
│       ├── interfaces.py     # Base interfaces
│       ├── schemas.py       # Data models
│       ├── config.py        # Configuration
│       └── utils.py         # Helper functions
├── tests/                   # Test suite
├── docs/                    # Documentation
├── examples/                # Usage examples
├── pyproject.toml           # Package configuration
└── README.md               # Package documentation
```

### **Detailed Implementation Phases**

#### **Phase 1: Core Python Package (Weeks 1-12)**

##### **Weeks 1-2: Foundation**
```bash
# Create package structure
mkdir extracta
cd extracta
mkdir -p extracta/{lenses,analyzers,grading,orchestration,shared}
mkdir -p tests docs examples

# Create pyproject.toml
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "extracta"
version = "0.1.0"
description = "Modular content analysis and insight generation"
authors = [{name = "Extracta Team"}]
license = {text = "MIT"}
requires-python = ">=3.10"
dependencies = [
    "click>=8.1.0",
    "pydantic>=2.5.0",
    "httpx>=0.25.0",
]

[project.optional-dependencies]
audio = ["faster-whisper>=1.0.0", "librosa>=0.10.0"]
video = ["opencv-python>=4.8.0", "ffmpeg-python>=0.2.0"]
text = ["spacy>=3.7.0", "nltk>=3.8.0", "textstat>=0.7.0"]
image = ["pillow>=10.0.0", "torch>=2.0.0"]
code = ["radon>=6.0.0", "ruff>=0.1.0", "ast>=3.8"]
citation = ["requests>=2.31.0", "beautifulsoup4>=4.12.0"]
all = ["extracta[audio,video,text,image,code,citation]"]

[project.scripts]
extracta = "extracta.cli:main"

[tool.ruff]
target-version = "py310"
line-length = 88
EOF
```

##### **Weeks 3-4: Migrate Existing Code**
```bash
# Migrate code-lens to extracta.lenses.code_lens
cp -r ../code-lens/codelens/* extracta/extracta/lenses/code_lens/

# Migrate deep-talk audio processing
cp -r ../deep-talk/src/services/* extracta/extracta/lenses/audio_lens/

# Update imports in migrated code
find extracta -name "*.py" -exec sed -i 's/from codelens/from extracta.lenses.code_lens/g' {} \;
find extracta -name "*.py" -exec sed -i 's/from services/from extracta.lenses.audio_lens/g' {} \;
```

##### **Weeks 5-8: Implement Missing Core**
```python
# extracta/extracta/analyzers/text_analyzer/__init__.py
from .analyzer import TextAnalyzer

# extracta/extracta/analyzers/text_analyzer/analyzer.py
class TextAnalyzer:
    """Research and assessment focused text analysis"""

    def analyze(self, text: str, mode: str = "assessment") -> dict:
        if mode == "research":
            return self._research_analysis(text)
        else:
            return self._assessment_analysis(text)

    def _research_analysis(self, text: str) -> dict:
        return {
            'themes': self._extract_themes(text),
            'discourse_patterns': self._analyze_discourse(text),
            'sentiment': self._analyze_sentiment(text),
            'linguistic_features': self._analyze_linguistics(text)
        }

    def _assessment_analysis(self, text: str) -> dict:
        return {
            'readability': self._analyze_readability(text),
            'writing_quality': self._analyze_quality(text),
            'vocabulary_richness': self._analyze_vocabulary(text),
            'grammar_issues': self._check_grammar(text)
        }
```

##### **Weeks 9-10: CLI Interface**
```python
# extracta/extracta/cli/__init__.py
from .main import main

# extracta/extracta/cli/main.py
import click
from pathlib import Path
from extracta.lenses import get_lens_for_file
from extracta.analyzers import get_analyzer_for_content

@click.group()
@click.version_option()
def main():
    """Extracta - Modular content analysis and insight generation"""
    pass

@main.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--mode', type=click.Choice(['research', 'assessment']), default='assessment')
@click.option('--output', '-o', type=click.Path())
def analyze(file_path, mode, output):
    """Analyze content from file"""
    file_path = Path(file_path)

    # Get appropriate lens
    lens = get_lens_for_file(file_path)
    if not lens:
        click.echo(f"No lens available for {file_path.suffix}", err=True)
        return

    click.echo(f"Analyzing {file_path.name}...")

    # Extract content
    result = lens.extract(file_path)
    if not result.success:
        click.echo(f"Error: {result.error}", err=True)
        return

    # Analyze content
    analyzer = get_analyzer_for_content(result.data['content_type'])
    if analyzer:
        analysis = analyzer.analyze(result.data['raw_content'], mode)
        result.data['analysis'] = analysis

    # Output results
    if output:
        import json
        with open(output, 'w') as f:
            json.dump(result.data, f, indent=2)
    else:
        click.echo(json.dumps(result.data, indent=2))
```

##### **Weeks 11-12: Testing & Documentation**
```python
# tests/test_text_analyzer.py
import pytest
from extracta.analyzers.text_analyzer import TextAnalyzer

class TestTextAnalyzer:
    def test_research_analysis(self):
        analyzer = TextAnalyzer()
        text = "This is a sample research interview transcript..."
        result = analyzer.analyze(text, mode="research")

        assert 'themes' in result
        assert 'discourse_patterns' in result
        assert 'sentiment' in result

    def test_assessment_analysis(self):
        analyzer = TextAnalyzer()
        text = "This is a student essay..."
        result = analyzer.analyze(text, mode="assessment")

        assert 'readability' in result
        assert 'writing_quality' in result
        assert 'vocabulary_richness' in result
```

#### **Phase 1.5: Academic Integrity Features (Weeks 13-16)**
- [x] Implement CitationAnalyzer (citation-reference validation)
- [x] Implement ReferenceAnalyzer (bibliography quality assessment)
- [x] Implement URLAnalyzer (web reference validation)
- [x] Add citation analysis CLI command
- [ ] **Future Enhancement**: Screenshot capture integration (requires Selenium/Playwright)
- [ ] **Future Enhancement**: Wayback Machine integration for broken URLs
- [ ] **Future Enhancement**: Google Scholar API integration (if available)
- [ ] **Future Enhancement**: OCR analysis of captured screenshots
- [ ] **Future Enhancement**: Content freshness analysis

#### **Phase 2: Add API Layer (Weeks 17-18)**

##### **Weeks 17-18: FastAPI Server**
```python
# extracta/extracta/api/__init__.py
from .main import create_app

# extracta/extracta/api/main.py
from fastapi import FastAPI, UploadFile, File
from extracta.lenses import get_lens_for_file
from extracta.analyzers import get_analyzer_for_content

def create_app() -> FastAPI:
    app = FastAPI(
        title="Extracta API",
        description="Modular content analysis and insight generation",
        version="0.1.0"
    )

    @app.post("/extract")
    async def extract_content(file: UploadFile = File(...)):
        """Extract content from uploaded file"""
        # Same logic as CLI but via HTTP
        pass

    @app.post("/analyze")
    async def analyze_content(request: dict):
        """Analyze extracted content"""
        # Same logic as CLI but via HTTP
        pass

    return app

# Add to pyproject.toml
[project.optional-dependencies]
api = ["fastapi>=0.104.0", "uvicorn[standard]>=0.24.0"]
```

#### **Phase 3: Add GUI Layer (Weeks 19-20)**

##### **Weeks 19-20: React Frontend (Optional)**
```bash
# Create GUI directory
mkdir extracta/gui
cd extracta/gui

# Initialize React app (similar to assessment-bench)
npm create vite@latest . --template react-ts
```

### **Implementation Checklist**

#### **Phase 1: Python Package (Weeks 1-12)**
- [x] Create package structure
- [x] Setup pyproject.toml
- [x] Migrate existing code (code-lens, deep-talk)
- [x] Implement text_analyzer (critical)
- [x] Implement image_analyzer (critical)
- [x] Implement citation_analyzer (academic integrity)
- [x] Implement reference_analyzer (bibliography validation)
- [x] Implement url_analyzer (URL validation)
- [x] Create CLI interface
- [x] Add comprehensive tests
- [x] Write documentation

#### **Phase 2: API Layer (Weeks 17-18)**
- [ ] Add FastAPI dependencies
- [ ] Create API endpoints
- [ ] Add authentication (optional)
- [ ] API documentation

#### **Phase 3: GUI Layer (Weeks 19-20)**
- [ ] Create React frontend
- [ ] Connect to Python API
- [ ] Add desktop packaging (optional)

### **Key Benefits of This Approach**

#### **1. Simplicity First**
- Focus on core Python functionality
- No UI complexity during initial development
- Clear testing and validation

#### **2. Progressive Enhancement**
- Core package works standalone
- Add interfaces as needed
- Each interface optional

#### **3. Multiple Consumption Patterns**
```bash
# CLI usage
extracta analyze interview.mp3 --mode research

# Python import
from extracta import TextAnalyzer
analyzer = TextAnalyzer()
result = analyzer.analyze(text, mode="research")

# API usage
curl -X POST "http://localhost:8000/extract" -F "file=@sample.mp3"

# GUI usage (later)
# React frontend calling same API
```

#### **4. Easy Distribution**
```bash
# Install and test
pip install -e .
extracta --help

# Upload to PyPI
pip install extracta
extracta analyze document.pdf --mode assessment
```

### **Getting Started**

#### **Immediate Actions**
```bash
# 1. Create package structure
mkdir extracta && cd extracta
# (See detailed setup commands above)

# 2. Migrate existing code
# (Copy from code-lens and deep-talk)

# 3. Install and test
pip install -e .
extracta --help

# 4. Start development
python -m extracta.cli analyze ../test-files/sample.mp3
```

---

## Key Design Principles

### 1. Lens Granularity
- **One lens per content type** (video_lens, audio_lens, etc.)
- **Textual output standardization** - all lenses produce analyzable text
- **Separation of concerns** - ingestion vs analysis

### 2. Analyzer Reusability
- **Format-agnostic analyzers** - text_analyzer works on any text source
- **Composable analysis** - combine multiple analyzers per content type
- **Extensible metrics** - easy to add new analysis dimensions

### 3. Configuration Management
- **Shared config system** - extracta/shared/config.py
- **Environment overrides** - customizable via env vars
- **Sensible defaults** - works out-of-the-box

### 4. Clean Architecture
- **Lens → Textual Description → Analyzer → Assessment**
- **No circular dependencies** - strict layer separation
- **Testable components** - each layer independently testable

### 5. Pragmatic Scope
- **In scope:** Content extraction, analysis, assessment
- **Out of scope:** UI, course management, advanced integrations
- **Future:** Integration with broader assessment platforms

---

## Future Considerations

### Scalability
- Parallel lens processing for batch analysis
- Caching of extracted content
- Cloud deployment options
- Distributed processing for heavy ML models

### Extensibility
- Plugin system for custom lenses/analyzers
- Domain-specific rubric templates
- Custom analysis metrics
- Third-party integrations

### ML Enhancements
- Fine-tuned models for educational content
- Multi-modal analysis (text + images + audio)
- Predictive feedback and suggestions
- Automated rubric generation

---

## 🚀 Future Enhancements

### Academic Integrity Enhancements

#### Citation & Reference Validation (Phase 2.5)

##### Screenshot Capture Integration
- **Purpose**: Visual assessment of web page validity for instructors
- **Implementation**: Selenium/Playwright integration for automated screenshots
- **Use Case**: Manual verification when automated analysis is insufficient
- **Status**: Requires additional dependencies, planned for Phase 2.5

##### Wayback Machine Integration
- **Purpose**: Check archived versions of broken or changed URLs
- **Implementation**: Wayback Machine API integration
- **Use Case**: Verify if URL was valid at time of citation submission
- **Status**: API research needed, planned for Phase 2.5

##### Google Scholar API Integration
- **Purpose**: Validate citation accuracy and completeness
- **Implementation**: Google Scholar API or scraping (if permitted)
- **Use Case**: Cross-reference cited works with actual publications
- **Status**: API availability assessment needed, planned for Phase 3

##### OCR Analysis of Screenshots
- **Purpose**: Extract text content from captured web page images
- **Implementation**: Tesseract OCR integration with screenshot preprocessing
- **Use Case**: Automated content verification when direct access fails
- **Status**: Depends on screenshot capture, planned for Phase 2.5

##### Content Freshness Analysis
- **Purpose**: Assess if cited web content is current and relevant
- **Implementation**: Date extraction, content change detection algorithms
- **Use Case**: Flag potentially outdated web references in academic work
- **Status**: Research needed, planned for Phase 2.5

##### URL-Based Conversation Analysis
- **Purpose**: Direct analysis of AI conversations from URLs without file downloads
- **Implementation**: Web scraping integration for ChatGPT share links, Claude conversation URLs
- **Use Case**: Real-time analysis of student AI interactions without requiring file exports
- **Status**: Web scraping research needed, planned for Phase 2.5

### Code Lens Advanced Features

#### ✅ Implemented Features
- **SQL Analysis**: Full statement parsing, table/column extraction, complexity metrics
- **Multi-language Support**: Python (AST), JavaScript, HTML, CSS, SQL
- **Jupyter Notebook Support**: Cell analysis, code/markdown separation

#### Immediate Additions
- **PHP Analysis**: For WordPress theme/plugin assessment
- **Advanced Python Metrics**: Using radon, pylint integration
- **LLM-Enhanced Analysis**: Compare static analysis with AI insights

#### Advanced Features
- **Sandbox Execution**: Safe code running with Docker
- **Similarity Analysis**: Code plagiarism detection
- **Dependency Analysis**: Import graph analysis
- **Performance Profiling**: Code execution timing

#### Web Integration
- **Screenshot Capture**: Configurable headless browser integration
- **DOM Analysis**: HTML structure assessment
- **Accessibility**: WCAG compliance checking
- **Performance**: Lighthouse-style metrics

### Video Content Processing Enhancements

#### URL-Based Video Analysis
Extracta will support direct analysis of videos hosted online, enabling comprehensive assessment of web-based video content:

- **Platform Support**: YouTube, Vimeo, TikTok, direct video URLs
- **Streaming Analysis**: Process videos without full download when possible
- **Metadata Extraction**: Title, description, tags, view counts, upload dates
- **Transcript Integration**: Leverage platform-provided captions/subtitles
- **Quality Assessment**: Video resolution, encoding quality, accessibility features

#### Embedded Video Processing
Advanced handling of videos embedded within other content formats:

- **PPTX Embedded Videos**: Extract and analyze videos embedded in PowerPoint presentations
  - Automatic detection of embedded media objects
  - Temporary extraction for analysis
  - Synchronization with slide timing and content
  - Assessment of video relevance to presentation context

- **Webpage Embedded Videos**: Process videos found in HTML content
  - iframe and video tag detection
  - Lazy-loading video handling
  - Cross-origin video analysis where permitted
  - Integration with web scraping capabilities

- **Document Embedded Videos**: Handle videos in PDF documents and other formats
  - Multimedia attachment processing
  - Video annotation and markup analysis
  - Contextual relevance assessment

#### Advanced Video Analysis Pipeline
Comprehensive processing for embedded and linked video content:

- **Multi-Format Support**: MP4, WebM, MOV, AVI, and platform-specific formats
- **Content Classification**: Educational vs. entertainment video detection
- **Presentation Context**: Analysis of video role within larger content (tutorials, demos, lectures)
- **Accessibility Assessment**: Caption availability, audio description, sign language
- **Quality Metrics**: Resolution, bitrate, compression artifacts, streaming performance

#### Integration with Existing Lenses
Seamless combination with current analysis capabilities:

- **Cascading Analysis**: Videos within documents trigger full video analysis pipeline
- **Cross-Reference**: Link video content back to embedding context
- **Unified Reporting**: Integrated results showing both container and embedded content analysis
- **Performance Optimization**: Smart caching and incremental processing for large presentations

#### Use Cases
- **Educational Assessment**: Analyze lecture videos embedded in course materials
- **Presentation Evaluation**: Assess video content within slide decks
- **Web Content Analysis**: Evaluate multimedia-rich web pages and articles
- **Content Curation**: Automated quality assessment of video resources

This enhancement will transform Extracta into a comprehensive multimedia content analysis platform, capable of understanding and assessing complex, multi-modal educational materials that combine text, images, and video content in various embedded and linked formats.

### Content Format Ecosystem Analysis

#### Overview
While Extracta currently handles ~80-90% of common educational submissions (text documents, presentations, images, videos), this section explores additional content formats that lecturers may request for analysis. This strategic analysis ensures the platform architecture can accommodate future expansion.

#### Data Analysis Formats
Structured data submissions requiring analytical assessment:

- **Spreadsheet Analysis** (Excel, Google Sheets, CSV)
  - Data validation and integrity checking
  - Formula correctness assessment
  - Chart and visualization quality evaluation
  - Statistical analysis of datasets
  - Data presentation and formatting standards

- **Database Exports** (SQL dumps, JSON, XML)
  - Schema design assessment
  - Data normalization evaluation
  - Query optimization analysis
  - Documentation quality review

- **Statistical Outputs** (R Markdown, Jupyter notebooks with data)
  - Methodology correctness
  - Statistical test appropriateness
  - Result interpretation accuracy
  - Reproducibility assessment

#### Visual Design Formats
Creative and design submissions requiring aesthetic and technical evaluation:

- **Art Portfolios** (series of images, PSD, AI files)
  - Composition and layout analysis
  - Color theory application
  - Technical execution quality
  - Conceptual development assessment
  - Series coherence evaluation

- **Comic Books/Graphic Novels** (CBR, CBZ, PDF)
  - Narrative structure analysis
  - Visual storytelling effectiveness
  - Panel layout and flow assessment
  - Character design consistency
  - Dialogue and text integration

- **Design Plans** (architectural drawings, CAD files, blueprints)
  - Technical accuracy assessment
  - Standard compliance checking
  - Scale and proportion analysis
  - Annotation clarity evaluation
  - Professional presentation standards

#### Specialized Academic Formats
Domain-specific content requiring expert analysis:

- **Mathematical Documents** (LaTeX, MathML, Mathematica notebooks)
  - Formula correctness verification
  - Proof structure assessment
  - Notation standards compliance
  - Solution methodology evaluation

- **Scientific Research** (lab notebooks, research papers with data)
  - Methodology documentation quality
  - Data collection and analysis rigor
  - Result interpretation accuracy
  - Research ethics compliance

- **Music Composition** (MIDI, MusicXML, sheet music PDFs)
  - Musical structure analysis
  - Harmonic progression assessment
  - Performance notation accuracy
  - Compositional originality evaluation

#### Interactive and Web Formats
Dynamic content requiring interaction analysis:

- **Web Applications** (HTML/CSS/JS, React apps, interactive websites)
  - User interface design assessment
  - Functionality testing and evaluation
  - Code quality and structure analysis
  - Accessibility compliance checking
  - Performance and usability metrics

- **Interactive PDFs** (forms, multimedia PDFs, e-books)
  - Interactive element functionality
  - Navigation design assessment
  - Multimedia integration quality
  - User experience evaluation

- **SCORM/Learning Packages** (e-learning modules, interactive courses)
  - Learning objective alignment
  - Interactive assessment quality
  - Navigation and flow assessment
  - Accessibility and standards compliance

#### Emerging Formats
Future-ready content types:

- **AR/VR Experiences** (3D models, interactive simulations)
  - User experience design assessment
  - Educational effectiveness evaluation
  - Technical implementation quality
  - Accessibility for diverse learners

- **Data Visualizations** (D3.js, Tableau, custom dashboards)
  - Data representation accuracy
  - Visual design effectiveness
  - Interactivity and usability
  - Information hierarchy assessment

- **Collaborative Documents** (Google Docs, Notion pages, Figma designs)
  - Collaboration quality assessment
  - Version control and iteration analysis
  - Contribution distribution evaluation
  - Final product quality assessment

#### Assessment Framework Considerations

##### Rubric Categories by Format Type
- **Technical Accuracy**: Code functionality, formula correctness, design precision
- **Presentation Quality**: Visual design, formatting, organization, clarity
- **Content Depth**: Research quality, analysis rigor, conceptual understanding
- **Innovation/Creativity**: Original approaches, novel solutions, creative expression
- **Standards Compliance**: Format-specific conventions, accessibility, best practices
- **Educational Effectiveness**: Learning outcome achievement, instructional design quality

##### Cross-Format Analysis Capabilities
- **Multi-Modal Assessment**: Combining different formats in single submissions
- **Progressive Evaluation**: Assessing drafts vs. final products
- **Peer Assessment Integration**: Student evaluation of peer work across formats
- **Automated Feedback**: Format-specific guidance and improvement suggestions

##### Implementation Strategy
- **Modular Lens Architecture**: Each format type gets specialized lens
- **Shared Analysis Components**: Common assessment criteria across formats
- **Extensible Rubric System**: Format-specific rubric templates
- **Progressive Enhancement**: Core formats first, specialized formats added iteratively

This comprehensive format analysis ensures Extracta can evolve to meet diverse educational assessment needs while maintaining architectural flexibility and assessment quality standards.

### Cascading Analysis System

#### Overview
Extracta now supports **cascading analysis** where lenses automatically detect and analyze additional content types within extracted data. For example:

- **Document Lens**: Extracts text from PDFs/DOCX, detects code snippets, sends to code-lens
- **Image Lens**: OCR extracts text, detects code in images, sends to code-lens
- **Presentation Lens**: Extracts slide text, detects code in presentations, sends to code-lens

#### Code Detection Heuristics
- **Keyword Analysis**: Detects programming keywords (`def`, `function`, `class`, etc.)
- **Syntax Patterns**: Identifies operators, brackets, semicolons
- **File Extensions**: Recognizes file paths with code extensions
- **Indentation**: Detects structured indentation patterns
- **Multi-Indicator Scoring**: Requires multiple indicators for reliable detection

#### Supported Languages
- **Python**: `def`, `class`, `import` patterns
- **JavaScript/TypeScript**: `function`, `var`, `const` patterns
- **Java**: `public class`, `System.out` patterns
- **C/C++**: `#include`, `int main` patterns
- **HTML/CSS**: Tag and selector patterns
- **SQL**: `SELECT`, `FROM`, `WHERE` patterns
- **JSON**: Structure-based detection

#### Usage
```bash
# Enable cascading analysis (default: enabled)
extracta analyze document.pdf --cascade

# Disable cascading analysis
extracta analyze document.pdf --no-cascade

# Use semantic routing (videos treated as presentations)
extracta analyze screencast.mp4 --semantic

# Presentation lens accepts both slides and videos
extracta presentation analyze video_demo.mp4
```

#### Benefits
- **Comprehensive Analysis**: Automatically detects code in any document type
- **Rich Reporting**: Provides nested analysis results for different content types
- **Educational Value**: Helps instructors identify code quality in submissions
- **Student Feedback**: Enables students to improve code within documents

### Semantic Routing System

#### Overview
Extracta supports **semantic routing** to align with user mental models rather than strict technical formats. This provides flexibility for content that can be interpreted in multiple ways.

#### Presentation Lens Flexibility
The presentation lens accepts both traditional slide formats and video presentations:

- **Slide Presentations**: PPTX, PPT files (traditional presentations)
- **Video Presentations**: MP4, MOV, AVI, etc. (screencasts, recorded demos, video lectures)

When a video is processed through the presentation lens, it automatically routes to the video lens internally but adds presentation-specific analysis and context.

#### Usage Examples
```bash
# Technical routing (default)
extracta analyze video.mp4          # Uses video-lens
extracta presentation analyze video.mp4  # Uses presentation-lens (semantic)

# Semantic flag for main analyze command
extracta analyze screencast.mp4 --semantic  # Treats video as presentation
```

#### Benefits
- **User-Friendly**: Aligns with how users think about content types
- **Flexible Analysis**: Same video can be analyzed for different purposes
- **Context-Aware**: Presentation lens adds semantic context to video analysis
- **Backward Compatible**: Technical routing remains the default

#### Implementation
- **Technical Mode** (default): Strict format-to-lens mapping
- **Semantic Mode**: User-intuitive content interpretation
- **Automatic Routing**: Presentation lens routes videos to video-lens internally
- **Enhanced Context**: Adds presentation-specific metadata and analysis

---

## Design Decisions and Clarifications

### API Design & Architecture

**FastAPI Integration Strategy:**
- The FastAPI server mirrors all CLI functionality as REST endpoints
- Each CLI command becomes an API endpoint (e.g., `POST /analyze`, `POST /citation/analyze`)
- Request/response schemas follow the same structure as CLI inputs/outputs
- API serves as the backend for all UI implementations

**UI Distribution Strategy:**
- **Maximum Flexibility**: Support multiple UI approaches simultaneously
- **TUI/GUI**: Import Python modules directly for local desktop applications
- **Web UIs**: React, Gradio, or other frameworks calling API endpoints
- **Electron Apps**: Embed Python server in cross-platform desktop applications
- **Docker Deployment**: Containerized API server for local or remote hosting
- **VPS Hosting**: Web server versions behind proxies or on cloud instances

**Schema Design:**
- Request/response validation using Pydantic models
- Consistent with CLI parameter structures
- Future enhancement: Comprehensive OpenAPI documentation

### Data Persistence Strategy

**Privacy-First Approach:**
- **No Built-in Storage**: Core system does not persist data or results
- **Report Generation Only**: System ingests documents and generates analysis reports
- **User Control**: Output saved to user-specified locations (CLI) or handled by UI applications
- **UI Responsibility**: Advanced UIs can implement database storage, trend tracking, comparisons
- **Grading/Rubric**: Proof-of-concept only, not intended for production assessment systems

**Session Management:**
- **Stateless Design**: Each analysis is independent
- **No Server-Side Sessions**: All state managed by client applications
- **Batch Processing**: Multiple files processed in single CLI command or API call

### Multi-Language Support

**Current Scope:**
- **English-Only**: Designed for English-first academic environment
- **Language Detection**: Important to identify non-English content for instructor investigation
- **Future Enhancement**: Multi-language support as institutional needs evolve

**LLM Prompt Strategy:**
- **English Prompts**: All LLM interactions use English system prompts
- **Content Analysis**: LLMs can process non-English content but respond in English
- **Detection Only**: Flag non-English content rather than translate/analyze

### Extension Points & Plugin Architecture

**Custom Lenses & Analyzers:**
- **Plugin System**: Future enhancement to allow user-defined lenses and analyzers
- **Registration Mechanism**: Dynamic loading of custom components
- **Current Limitation**: Would require architectural redesign to make existing components pluggable

**Rubric Creation Workflow:**
- **Assignment Mapping**: Upload assignment specifications to auto-generate rubrics
- **Existing Rubric Import**: Parse and map external rubric formats to internal structure
- **Customization**: Edit generated rubrics to match institutional standards
- **Template-Based**: Start with defaults and modify for specific needs

**Proof-of-Concept Focus:**
- **Orchestration UIs**: Demonstrate capabilities without full production implementation
- **Privacy Considerations**: User retains full control over data and analysis results
- **Modular Design**: Easy to extend or replace components as needs evolve

---

## Design Decisions and Clarifications

### API Design & Architecture

**FastAPI Integration Strategy:**
- The FastAPI server mirrors all CLI functionality as REST endpoints
- Each CLI command becomes an API endpoint (e.g., `POST /analyze`, `POST /citation/analyze`)
- Request/response schemas follow the same structure as CLI inputs/outputs
- API serves as the backend for all UI implementations

**UI Distribution Strategy:**
- **Maximum Flexibility**: Support multiple UI approaches simultaneously
- **TUI/GUI**: Import Python modules directly for local desktop applications
- **Web UIs**: React, Gradio, or other frameworks calling API endpoints
- **Electron Apps**: Embed Python server in cross-platform desktop applications
- **Docker Deployment**: Containerized API server for local or remote hosting
- **VPS Hosting**: Web server versions behind proxies or on cloud instances

**Schema Design:**
- Request/response validation using Pydantic models
- Consistent with CLI parameter structures
- Future enhancement: Comprehensive OpenAPI documentation

### Data Persistence Strategy

**Privacy-First Approach:**
- **No Built-in Storage**: Core system does not persist data or results
- **Report Generation Only**: System ingests documents and generates analysis reports
- **User Control**: Output saved to user-specified locations (CLI) or handled by UI applications
- **UI Responsibility**: Advanced UIs can implement database storage, trend tracking, comparisons
- **Grading/Rubric**: Proof-of-concept only, not intended for production assessment systems

**Session Management:**
- **Stateless Design**: Each analysis is independent
- **No Server-Side Sessions**: All state managed by client applications
- **Batch Processing**: Multiple files processed in single CLI command or API call

### Multi-Language Support

**Current Scope:**
- **English-Only**: Designed for English-first academic environment
- **Language Detection**: Important to identify non-English content for instructor investigation
- **Future Enhancement**: Multi-language support as institutional needs evolve

**LLM Prompt Strategy:**
- **English Prompts**: All LLM interactions use English system prompts
- **Content Analysis**: LLMs can process non-English content but respond in English
- **Detection Only**: Flag non-English content rather than translate/analyze

### Extension Points & Plugin Architecture

**Custom Lenses & Analyzers:**
- **Plugin System**: Future enhancement to allow user-defined lenses and analyzers
- **Registration Mechanism**: Dynamic loading of custom components
- **Current Limitation**: Would require architectural redesign to make existing components pluggable

**Rubric Creation Workflow:**
- **Assignment Mapping**: Upload assignment specifications to auto-generate rubrics
- **Existing Rubric Import**: Parse and map external rubric formats to internal structure
- **Customization**: Edit generated rubrics to match institutional standards
- **Template-Based**: Start with defaults and modify for specific needs

**Proof-of-Concept Focus:**
- **Orchestration UIs**: Demonstrate capabilities without full production implementation
- **Privacy Considerations**: User retains full control over data and analysis results
- **Modular Design**: Easy to extend or replace components as needs evolve

### Security & Privacy Design

**Input Sanitization & Validation:**
- Content size limits (10MB text, 2KB URLs, 255 char filenames)
- Hidden character detection (control chars, zero-width spaces)
- LLM jailbreak pattern recognition
- Malicious content detection (steganography, encoding)
- Filename sanitization and path traversal prevention

**URL Security & SSRF Protection:**
- Academic domain whitelisting (scholar.google.com, nature.com, etc.)
- Private network blocking (localhost, 127.0.0.1, 192.168.x.x)
- Metadata service prevention (AWS/GCP metadata endpoints)
- Suspicious pattern detection (internal, secret, metadata)

**Privacy & Data Protection:**
- No built-in data persistence or storage
- Ephemeral processing with user-controlled output locations
- No analytics, tracking, or usage monitoring
- Local processing maintains user privacy
- Content hashing for integrity verification

**Error Handling & Information Leakage:**
- Structured error messages without system internals
- User-friendly error descriptions with actionable suggestions
- Comprehensive logging for debugging (user-controlled)
- Graceful degradation on failures
- Recovery mechanisms for transient errors

---

## Glossary

- **Lens:** Content ingestion component that extracts standardized textual descriptions
- **Analyzer:** Reusable analysis tool that processes textual descriptions into metrics
- **Rubric:** Structured scoring criteria with weights and scales
- **Assessment:** Application of rubrics to analysis results
- **Feedback:** Generated guidance based on assessment results
- **Extracta:** Modular content analysis platform for diverse formats