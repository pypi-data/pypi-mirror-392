import json
import click
from pathlib import Path
from extracta.lenses import get_lens_for_file
from extracta.analyzers import get_analyzer_for_content


@click.group()
@click.version_option()
def main():
    """Extracta - Modular content analysis and insight generation"""
    pass


# Content-type specific subcommands
@main.group()
def video():
    """Video content analysis commands"""
    pass


@main.group()
def image():
    """Image content analysis commands"""
    pass


@main.group()
def text():
    """Text content analysis commands"""
    pass


@main.group()
def code():
    """Code content analysis commands"""
    pass


@main.group()
def presentation():
    """Presentation content analysis commands"""
    pass


@main.group()
def repo():
    """Repository analysis commands"""
    pass


@main.group()
def citation():
    """Citation and reference analysis commands"""
    pass


@main.group()
def rubric():
    """Rubric management commands"""
    pass


@citation.command("analyze")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--mode", type=click.Choice(["research", "assessment"]), default="assessment"
)
@click.option("--output", "-o", type=click.Path())
def citation_analyze(file_path, mode, output):
    """Analyze citations and references in academic documents"""
    from extracta.lenses import get_lens_for_file
    from extracta.analyzers.citation_analyzer import CitationAnalyzer
    from extracta.analyzers.reference_analyzer import ReferenceAnalyzer
    from extracta.analyzers.url_analyzer import URLAnalyzer

    file_path = Path(file_path)

    # Get appropriate lens
    lens = get_lens_for_file(file_path)
    if not lens:
        click.echo(f"No lens available for {file_path.suffix}", err=True)
        return

    click.echo(f"Analyzing citations in {file_path.name}...")

    # Extract content
    result = lens.extract(file_path)
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return

    # Get text content for analysis
    text_content = ""
    if "raw_content" in result["data"]:
        text_content = result["data"]["raw_content"]
    elif "content" in result["data"]:
        text_content = result["data"]["content"]
    else:
        click.echo("No text content found for citation analysis", err=True)
        return

    # Run citation analysis
    citation_analyzer = CitationAnalyzer()
    citation_result = citation_analyzer.analyze(text_content, mode)

    # Run reference analysis
    reference_analyzer = ReferenceAnalyzer()
    reference_result = reference_analyzer.analyze(text_content, mode)

    # Run URL analysis
    url_analyzer = URLAnalyzer()
    url_result = url_analyzer.analyze(text_content, mode)

    # Combine results
    combined_result = {
        "file_analysis": result["data"],
        "citation_analysis": citation_result["citation_analysis"],
        "reference_analysis": reference_result["reference_analysis"],
        "url_analysis": url_result["url_analysis"],
    }

    # Output results
    if output:
        with open(output, "w") as f:
            json.dump(combined_result, f, indent=2)
        click.echo(f"Results saved to {output}")
    else:
        click.echo(json.dumps(combined_result, indent=2))


@citation.command("conversation")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path())
@click.option("--api-key", envvar="GEMINI_API_KEY", help="Gemini API key")
@click.option(
    "--system-prompt", type=click.Path(), help="Path to custom system prompt file"
)
def conversation_analyze(file_path, output, api_key, system_prompt):
    """Analyze AI conversation for cognitive intent patterns"""
    from extracta.lenses.ai_conversation_lens import AIConversationLens
    from extracta.analyzers.conversation_analyzer import ConversationAnalyzer

    file_path = Path(file_path)

    # Extract conversation data
    lens = AIConversationLens()
    click.echo(f"Extracting conversation from {file_path.name}...")

    result = lens.extract(file_path)
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return

    # Analyze conversation
    try:
        analyzer = ConversationAnalyzer(
            api_key=api_key, system_prompt_path=system_prompt
        )
        click.echo("Analyzing cognitive intent patterns...")

        # Convert conversation data to JSON string for analyzer
        conversation_json = json.dumps(result["data"])
        analysis_result = analyzer.analyze(conversation_json)

        # Combine results
        combined_result = {
            "conversation_extraction": result["data"],
            "cognitive_analysis": analysis_result["conversation_analysis"],
        }

        # Output results
        if output:
            with open(output, "w") as f:
                json.dump(combined_result, f, indent=2)
            click.echo(f"Results saved to {output}")
        else:
            click.echo(json.dumps(combined_result, indent=2))

    except Exception as e:
        click.echo(f"Analysis error: {e}", err=True)
        if "GEMINI_API_KEY" not in str(e):
            click.echo("Make sure GEMINI_API_KEY environment variable is set", err=True)


@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--mode", type=click.Choice(["research", "assessment"]), default="assessment"
)
@click.option("--output", "-o", type=click.Path())
@click.option(
    "--cascade/--no-cascade",
    default=True,
    help="Enable cascading analysis for code detection",
)
@click.option(
    "--semantic",
    is_flag=True,
    help="Use semantic routing (videos can be treated as presentations)",
)
def analyze(file_path, mode, output, cascade, semantic):
    """Analyze content from file"""
    file_path = Path(file_path)

    # Get appropriate lens (with semantic routing option)
    semantic_mode = "semantic" if semantic else "technical"
    lens = get_lens_for_file(file_path, semantic_mode=semantic_mode)
    if not lens:
        click.echo(f"No lens available for {file_path.suffix}", err=True)
        return

    click.echo(f"Analyzing {file_path.name}...")

    # Extract content
    result = lens.extract(file_path)
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return

    # Apply cascading analysis if enabled
    if cascade:
        from extracta.lenses import analyze_extracted_content

        result["data"] = analyze_extracted_content(result["data"])

    # Analyze content
    if result["data"]["content_type"] == "video":
        # Video lens outputs textual descriptions - analyze them with text_analyzer
        from extracta.analyzers.text_analyzer import TextAnalyzer

        text_analyzer = TextAnalyzer()

        # Analyze transcript
        transcript_analysis = text_analyzer.analyze(result["data"]["transcript"], mode)

        # Analyze frame descriptions as combined text
        frame_text = " ".join(result["data"]["frame_descriptions"])
        frame_analysis = text_analyzer.analyze(frame_text, mode)

        # Analyze visual summary
        summary_analysis = text_analyzer.analyze(result["data"]["visual_summary"], mode)

        # Simple combined score (average of readability grades)
        combined_score = (
            transcript_analysis.get("readability", {}).get("grade_level", 8)
            + frame_analysis.get("readability", {}).get("grade_level", 8)
            + summary_analysis.get("readability", {}).get("grade_level", 8)
        ) / 3

        result["data"]["analysis"] = {
            "transcript_analysis": transcript_analysis,
            "frame_analysis": frame_analysis,
            "summary_analysis": summary_analysis,
            "combined_readability_grade": round(combined_score, 1),
        }
    else:
        analyzer = get_analyzer_for_content(result["data"]["content_type"])
        if analyzer:
            if result["data"]["content_type"] == "image":
                analysis = analyzer.analyze(result["data"]["file_path"], mode)
            else:
                analysis = analyzer.analyze(result["data"]["raw_content"], mode)
            result["data"]["analysis"] = analysis

    # Output results
    if output:
        with open(output, "w") as f:
            json.dump(result["data"], f, indent=2)
    else:
        click.echo(json.dumps(result["data"], indent=2))


@video.command("analyze")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--mode", type=click.Choice(["research", "assessment"]), default="assessment"
)
@click.option("--output", "-o", type=click.Path())
def video_analyze(file_path, mode, output):
    """Analyze video content"""
    file_path = Path(file_path)

    # Force video lens
    from extracta.lenses.video_lens import VideoLens

    lens = VideoLens()

    click.echo(f"Analyzing video {file_path.name}...")

    # Extract content
    result = lens.extract(file_path)
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return

    # Analyze content
    from extracta.analyzers.text_analyzer import TextAnalyzer

    text_analyzer = TextAnalyzer()

    # Analyze transcript
    transcript_analysis = text_analyzer.analyze(result["data"]["transcript"], mode)

    # Analyze frame descriptions
    frame_text = " ".join(result["data"]["frame_descriptions"])
    frame_analysis = text_analyzer.analyze(frame_text, mode)

    # Analyze visual summary
    summary_analysis = text_analyzer.analyze(result["data"]["visual_summary"], mode)

    # Simple combined score
    combined_score = (
        transcript_analysis.get("readability", {}).get("grade_level", 8)
        + frame_analysis.get("readability", {}).get("grade_level", 8)
        + summary_analysis.get("readability", {}).get("grade_level", 8)
    ) / 3

    result["data"]["analysis"] = {
        "transcript_analysis": transcript_analysis,
        "frame_analysis": frame_analysis,
        "summary_analysis": summary_analysis,
        "combined_readability_grade": round(combined_score, 1),
    }

    # Output results
    if output:
        with open(output, "w") as f:
            json.dump(result["data"], f, indent=2)
        click.echo(f"Results saved to {output}")
    else:
        click.echo(json.dumps(result["data"], indent=2))


@image.command("analyze")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--mode", type=click.Choice(["research", "assessment"]), default="assessment"
)
@click.option("--output", "-o", type=click.Path())
def image_analyze(file_path, mode, output):
    """Analyze image content"""
    file_path = Path(file_path)

    # Force image lens
    from extracta.lenses.image_lens import ImageLens

    lens = ImageLens()

    click.echo(f"Analyzing image {file_path.name}...")

    # Extract content
    result = lens.extract(file_path)
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return

    # Analyze content
    analyzer = get_analyzer_for_content(result["data"]["content_type"])
    if analyzer:
        analysis = analyzer.analyze(result["data"]["file_path"], mode)
        result["data"]["analysis"] = analysis

    # Output results
    if output:
        with open(output, "w") as f:
            json.dump(result["data"], f, indent=2)
        click.echo(f"Results saved to {output}")
    else:
        click.echo(json.dumps(result["data"], indent=2))


@text.command("analyze")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--mode", type=click.Choice(["research", "assessment"]), default="assessment"
)
@click.option("--output", "-o", type=click.Path())
def text_analyze(file_path, mode, output):
    """Analyze text content"""
    file_path = Path(file_path)

    # Force document lens
    from extracta.lenses.document_lens import DocumentLens

    lens = DocumentLens()

    click.echo(f"Analyzing text {file_path.name}...")

    # Extract content
    result = lens.extract(file_path)
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return

    # Analyze content
    analyzer = get_analyzer_for_content(result["data"]["content_type"])
    if analyzer:
        analysis = analyzer.analyze(result["data"]["raw_content"], mode)
        result["data"]["analysis"] = analysis

    # Output results
    if output:
        with open(output, "w") as f:
            json.dump(result["data"], f, indent=2)
        click.echo(f"Results saved to {output}")
    else:
        click.echo(json.dumps(result["data"], indent=2))


@rubric.command("list")
def rubric_list():
    """List available rubrics"""
    from extracta.grading import default_rubrics

    rubrics = []
    rubrics.extend(default_rubrics.list_default_rubrics())

    click.echo("Available rubrics:")
    for rubric_type in rubrics:
        click.echo(f"  - {rubric_type}")


@rubric.command("create")
@click.argument("name")
@code.command("analyze")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--mode", type=click.Choice(["research", "assessment"]), default="assessment"
)
@click.option("--output", "-o", type=click.Path())
def code_analyze(file_path, mode, output):
    """Analyze code content"""
    file_path = Path(file_path)

    # Force code lens
    from extracta.lenses.code_lens import CodeLens

    lens = CodeLens()

    click.echo(f"Analyzing code {file_path.name}...")

    # Extract content
    result = lens.extract(file_path)
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return

    # Analyze content
    from extracta.analyzers.text_analyzer import TextAnalyzer

    text_analyzer = TextAnalyzer()

    # For code, we analyze the extracted text content
    if "content" in result["data"]:
        analysis = text_analyzer.analyze(result["data"]["content"], mode)
        result["data"]["analysis"] = analysis

    # Output results
    if output:
        with open(output, "w") as f:
            json.dump(result["data"], f, indent=2)
        click.echo(f"Results saved to {output}")
    else:
        click.echo(json.dumps(result["data"], indent=2))


@presentation.command("analyze")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--mode", type=click.Choice(["research", "assessment"]), default="assessment"
)
@click.option("--output", "-o", type=click.Path())
@click.option("--extract-images", is_flag=True, help="Extract images from slides")
@click.option("--render-slides", is_flag=True, help="Render slides as images")
@click.option(
    "--cascade/--no-cascade",
    default=True,
    help="Enable cascading analysis for code detection",
)
def presentation_analyze(
    file_path, mode, output, extract_images, render_slides, cascade
):
    """Analyze presentation content"""
    file_path = Path(file_path)

    # Force presentation lens
    from extracta.lenses.presentation_lens import PresentationLens

    lens = PresentationLens(extract_images=extract_images, render_slides=render_slides)

    click.echo(f"Analyzing presentation {file_path.name}...")

    # Extract content
    result = lens.extract(file_path)
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return

    # Analyze slide text with text analyzer
    from extracta.analyzers.text_analyzer import TextAnalyzer

    text_analyzer = TextAnalyzer()

    # Analyze slide text
    if result["data"].get("slide_text"):
        slide_analysis = text_analyzer.analyze(result["data"]["slide_text"], mode)
        result["data"]["slide_analysis"] = slide_analysis

    # Apply cascading analysis if enabled
    if cascade:
        from extracta.lenses import analyze_extracted_content

        result["data"] = analyze_extracted_content(result["data"])

    # Analyze presenter notes separately
    if result["data"].get("presenter_notes"):
        notes_analysis = text_analyzer.analyze(result["data"]["presenter_notes"], mode)
        result["data"]["notes_analysis"] = notes_analysis

    # Add presentation structure analysis
    if hasattr(lens, "analyze_presentation_structure"):
        structure_analysis = lens.analyze_presentation_structure(
            result["data"]["slides_content"]
        )
        result["data"]["structure_analysis"] = structure_analysis

    # Output results
    if output:
        with open(output, "w") as f:
            json.dump(result["data"], f, indent=2)
        click.echo(f"Results saved to {output}")
    else:
        click.echo(json.dumps(result["data"], indent=2))


@click.option(
    "--type",
    "rubric_type",
    type=click.Choice(["academic", "business", "creative", "general"]),
    default="general",
)
@click.option("--output", "-o", type=click.Path())
def rubric_create(name, rubric_type, output):
    """Create a new rubric based on a template"""
    from extracta.grading import default_rubrics

    # Get template
    template = default_rubrics.get_default_rubric(rubric_type)
    if not template:
        click.echo(f"Unknown rubric type: {rubric_type}", err=True)
        return

    # Customize the template
    template.name = name

    if output:
        # Export to file
        import json

        with open(output, "w") as f:
            json.dump(template.to_dict(), f, indent=2)
        click.echo(f"Rubric saved to {output}")
    else:
        click.echo(f"Created rubric: {name} (based on {rubric_type} template)")
        click.echo("Use --output to save to file")


@main.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8000, type=int, help="Port to bind to")
def serve(host, port):
    """Start the FastAPI server"""
    try:
        from extracta.api import create_app
        import uvicorn

        app = create_app()
        click.echo(f"Starting server on http://{host}:{port}")
        click.echo("Press Ctrl+C to stop")
        uvicorn.run(app, host=host, port=port)

    except ImportError:
        click.echo(
            "API dependencies not installed. Install with: pip install extracta[api]",
            err=True,
        )
