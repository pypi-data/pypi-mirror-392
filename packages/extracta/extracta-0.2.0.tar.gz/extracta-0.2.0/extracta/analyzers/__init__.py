def get_analyzer_for_content(content_type: str):
    """Get appropriate analyzer for content type"""
    if content_type == "text":
        from .text_analyzer import TextAnalyzer

        return TextAnalyzer()
    elif content_type == "image":
        from .image_analyzer import ImageAnalyzer

        return ImageAnalyzer()

    # TODO: Add more analyzers (code, etc.)
    return None


def get_citation_analyzer():
    """Get citation analyzer for academic integrity checking"""
    from .citation_analyzer import CitationAnalyzer

    return CitationAnalyzer()


def get_reference_analyzer():
    """Get reference analyzer for bibliography validation"""
    from .reference_analyzer import ReferenceAnalyzer

    return ReferenceAnalyzer()


def get_url_analyzer():
    """Get URL analyzer for web reference validation"""
    from .url_analyzer import URLAnalyzer

    return URLAnalyzer()


def get_conversation_analyzer():
    """Get conversation analyzer for AI conversation cognitive intent classification"""
    from .conversation_analyzer import ConversationAnalyzer

    return ConversationAnalyzer()
