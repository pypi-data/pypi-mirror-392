"""Conversation analyzer for classifying cognitive intent in AI conversations."""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..base_analyzer import BaseAnalyzer


class ConversationAnalyzer(BaseAnalyzer):
    """Analyzer for classifying cognitive intent in AI conversations using LLM."""

    def __init__(
        self, api_key: Optional[str] = None, system_prompt_path: Optional[str] = None
    ):
        """Initialize the conversation analyzer.

        Args:
            api_key: LLM API key (defaults to GEMINI_API_KEY env var)
            system_prompt_path: Path to system prompt file
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable must be set")

        # Load system prompt
        self.system_prompt = self._load_system_prompt(system_prompt_path)

        # Initialize LLM client (lazy loading)
        self._llm_client = None

    def _load_system_prompt(self, prompt_path: Optional[str] = None) -> str:
        """Load the system prompt from file or use default."""
        if prompt_path:
            path = Path(prompt_path)
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return f.read().strip()

        # Default system prompt based on specification
        return """You are an expert educational analyst. Your sole function is to classify a student's prompt to an AI tutor based on its cognitive intent. You must determine if the student is trying to learn (Scaffolding) or just get the answer (Delegation).

You MUST respond ONLY with a single, minified JSON object matching this exact schema:
{"intent_category": "string", "intent_subcategory": "string", "confidence": float, "rationale": "string"}

Use the following taxonomy for "intent_category" and "intent_subcategory":

1. **"intent_category": "Delegation"** (The user is offloading work to the AI)
    * **"intent_subcategory": "Solution"**: Asks for the complete answer or solution. (e.g., "Write the code for me," "What is the answer?")
    * **"intent_subcategory": "Completion"**: Asks the AI to finish an incomplete task. (e.g., "Complete this function")
    * **"intent_subcategory": "Direct_Fix"**: Asks the AI to fix their code without any user effort. (e.g., "Fix this," "This is broken, correct it")

2. **"intent_category": "Scaffolding"** (The user is trying to learn or get help)
    * **"intent_subcategory": "Explanation"**: Asks for an explanation of a concept, code, or error. (e.g., "Why does this error happen?" "Explain what this function does")
    * **"intent_subcategory": "Ideation"**: Asks for ideas, approaches, or how to start. (e.g., "How should I begin?" "What are some ways to solve this?")
    * **"intent_subcategory": "Debugging"**: Provides their own work and asks for help finding a problem. (e.g., "My code isn't working, can you spot the bug?" "I get this error, what did I do wrong?")
    * **"intent_subcategory": "Refinement"**: Has a working solution and wants to improve it. (e.g., "How can I make this code better?" "Is there a more efficient way?")

3. **"intent_category": "Other"**
    * **"intent_subcategory": "Social"**: Non-task-related chat. (e.g., "Hello," "Thanks!")
    * **"intent_subcategory": "Unclear"**: Gibberish or too vague to classify.

Provide a "confidence" score between 0.0 and 1.0.
Provide a brief "rationale" (1 sentence) for your classification."""

    def _initialize_llm_client(self):
        """Initialize the LLM client (lazy loading)."""
        if self._llm_client is None:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self._llm_client = genai.GenerativeModel("gemini-pro")
            except ImportError:
                raise ImportError(
                    "google-generativeai package is required for conversation analysis"
                )

    def analyze(self, content: str, mode: str = "assessment") -> Dict[str, Any]:
        """Analyze conversation data for cognitive intent patterns.

        Args:
            content: Conversation data (JSON string or dict)
            mode: Analysis mode ('research' or 'assessment')

        Returns:
            Dictionary containing conversation analysis results
        """
        try:
            # Parse conversation data
            if isinstance(content, str):
                try:
                    conversation_data = json.loads(content)
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Invalid JSON conversation data",
                        "analysis": {},
                    }
            else:
                conversation_data = content

            # Extract user prompts from conversation
            user_prompts = self._extract_user_prompts(conversation_data)

            if not user_prompts:
                return {
                    "success": False,
                    "error": "No user prompts found in conversation",
                    "analysis": {},
                }

            # Classify each prompt
            classified_prompts = []
            for prompt in user_prompts:
                classification = self.classify_prompt(prompt)
                if classification:
                    classified_prompts.append(
                        {"prompt": prompt, "classification": classification}
                    )

            # Analyze session-level metrics
            session_analysis = self.analyze_session(classified_prompts)

            return {
                "conversation_analysis": {
                    "total_prompts": len(user_prompts),
                    "classified_prompts": len(classified_prompts),
                    "session_metrics": session_analysis,
                    "detailed_classifications": classified_prompts,
                    "learning_assessment": self._assess_learning_quality(
                        session_analysis
                    ),
                }
            }

        except Exception as e:
            return {"success": False, "error": str(e), "analysis": {}}

    def classify_prompt(self, prompt_text: str) -> Optional[Dict[str, Any]]:
        """Classify a single user prompt using LLM.

        Args:
            prompt_text: The raw text of the user's prompt

        Returns:
            Classification dictionary or None if classification fails
        """
        try:
            self._initialize_llm_client()

            # Prepare the prompt for the LLM
            full_prompt = f'{self.system_prompt}\n\n---\nSTUDENT PROMPT TO CLASSIFY:\n"{prompt_text}"'

            # Configure for JSON output
            generation_config = {
                "temperature": 0.1,  # Low temperature for consistent classification
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 200,
            }

            # Make the API call
            response = self._llm_client.generate_content(
                full_prompt, generation_config=generation_config
            )

            # Parse JSON response
            response_text = response.text.strip()

            # Clean up response (remove markdown code blocks if present)
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            try:
                classification = json.loads(response_text)

                # Validate required fields
                required_fields = [
                    "intent_category",
                    "intent_subcategory",
                    "confidence",
                    "rationale",
                ]
                if all(field in classification for field in required_fields):
                    return classification
                else:
                    print(
                        f"Missing required fields in classification: {classification}"
                    )
                    return None

            except json.JSONDecodeError as e:
                print(f"Failed to parse LLM response as JSON: {response_text}")
                print(f"JSON Error: {e}")
                return None

        except Exception as e:
            print(f"Error classifying prompt: {e}")
            return None

    def analyze_session(
        self, classified_prompts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze a list of classified prompts and return session-level metrics.

        Args:
            classified_prompts: List of dictionaries with prompt and classification

        Returns:
            Dictionary containing session-level metrics
        """
        if not classified_prompts:
            return {
                "total_prompts": 0,
                "intent_counts": {"Delegation": 0, "Scaffolding": 0, "Other": 0},
                "scaffolding_ratio": 0.0,
                "intent_sequence": [],
            }

        # Count intents
        intent_counts = {"Delegation": 0, "Scaffolding": 0, "Other": 0}
        intent_sequence = []

        for item in classified_prompts:
            classification = item.get("classification", {})
            intent_category = classification.get("intent_category", "Other")

            if intent_category in intent_counts:
                intent_counts[intent_category] += 1
            else:
                intent_counts["Other"] += 1

            intent_sequence.append(intent_category)

        # Calculate scaffolding ratio
        delegation_total = intent_counts["Delegation"] + intent_counts["Scaffolding"]
        scaffolding_ratio = (
            intent_counts["Scaffolding"] / delegation_total
            if delegation_total > 0
            else 0.0
        )

        # Calculate subcategory breakdown
        subcategory_counts = {}
        for item in classified_prompts:
            classification = item.get("classification", {})
            subcategory = classification.get("intent_subcategory", "Unknown")
            subcategory_counts[subcategory] = subcategory_counts.get(subcategory, 0) + 1

        # Calculate average confidence
        confidences = [
            item.get("classification", {}).get("confidence", 0.0)
            for item in classified_prompts
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return {
            "total_prompts": len(classified_prompts),
            "intent_counts": intent_counts,
            "scaffolding_ratio": round(scaffolding_ratio, 3),
            "intent_sequence": intent_sequence,
            "subcategory_breakdown": subcategory_counts,
            "average_confidence": round(avg_confidence, 3),
            "learning_patterns": self._analyze_learning_patterns(intent_sequence),
        }

    def _extract_user_prompts(self, conversation_data: Dict[str, Any]) -> List[str]:
        """Extract user prompts from conversation data."""
        messages = conversation_data.get("messages", [])
        user_prompts = []

        for message in messages:
            if isinstance(message, dict) and message.get("role") == "user":
                content = message.get("content", "").strip()
                if content:
                    user_prompts.append(content)

        return user_prompts

    def _analyze_learning_patterns(self, intent_sequence: List[str]) -> Dict[str, Any]:
        """Analyze patterns in the learning sequence."""
        patterns = {
            "consistent_scaffolding": False,
            "delegation_spikes": [],
            "learning_progression": "unknown",
            "engagement_quality": "unknown",
        }

        if not intent_sequence:
            return patterns

        # Check for consistent scaffolding (good learning behavior)
        scaffolding_count = intent_sequence.count("Scaffolding")
        total_count = len(intent_sequence)
        patterns["consistent_scaffolding"] = (scaffolding_count / total_count) > 0.7

        # Find delegation spikes (potential learning moments)
        for i, intent in enumerate(intent_sequence):
            if intent == "Delegation" and i > 0:
                # Check if followed by scaffolding (indicates learning)
                if (
                    i < len(intent_sequence) - 1
                    and intent_sequence[i + 1] == "Scaffolding"
                ):
                    patterns["delegation_spikes"].append(
                        {"position": i, "followed_by_learning": True}
                    )

        # Assess learning progression
        if patterns["consistent_scaffolding"]:
            patterns["learning_progression"] = "strong"
            patterns["engagement_quality"] = "excellent"
        elif scaffolding_count / total_count > 0.4:
            patterns["learning_progression"] = "moderate"
            patterns["engagement_quality"] = "good"
        else:
            patterns["learning_progression"] = "limited"
            patterns["engagement_quality"] = "needs_improvement"

        return patterns

    def _assess_learning_quality(
        self, session_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess overall learning quality from session metrics."""
        scaffolding_ratio = session_metrics.get("scaffolding_ratio", 0.0)
        avg_confidence = session_metrics.get("average_confidence", 0.0)
        patterns = session_metrics.get("learning_patterns", {})

        # Calculate learning quality score (0-100)
        quality_score = 0

        # Scaffolding ratio (40% weight)
        quality_score += scaffolding_ratio * 40

        # Confidence in classifications (30% weight)
        quality_score += avg_confidence * 30

        # Learning patterns (30% weight)
        if patterns.get("consistent_scaffolding"):
            quality_score += 30
        elif patterns.get("learning_progression") == "moderate":
            quality_score += 20
        elif patterns.get("learning_progression") == "strong":
            quality_score += 30

        # Determine learning level
        if quality_score >= 80:
            level = "Excellent"
            description = "Strong evidence of active learning and scaffolding behaviors"
        elif quality_score >= 60:
            level = "Good"
            description = (
                "Moderate evidence of learning engagement with room for improvement"
            )
        elif quality_score >= 40:
            level = "Fair"
            description = "Some learning behaviors present but inconsistent"
        else:
            level = "Needs Improvement"
            description = "Limited evidence of active learning, mostly delegation"

        return {
            "learning_quality_score": round(quality_score, 1),
            "learning_level": level,
            "description": description,
            "recommendations": self._generate_learning_recommendations(session_metrics),
        }

    def _generate_learning_recommendations(
        self, session_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate learning recommendations based on session metrics."""
        recommendations = []
        scaffolding_ratio = session_metrics.get("scaffolding_ratio", 0.0)
        intent_counts = session_metrics.get("intent_counts", {})

        if scaffolding_ratio < 0.3:
            recommendations.append(
                "Encourage more questions that explore concepts rather than asking for complete solutions"
            )
            recommendations.append(
                "Practice explaining your understanding before asking for help"
            )

        if intent_counts.get("Delegation", 0) > intent_counts.get("Scaffolding", 0) * 2:
            recommendations.append(
                "Try breaking down problems into smaller parts and solving them step by step"
            )
            recommendations.append(
                "When stuck, first try to identify what specifically you don't understand"
            )

        if not session_metrics.get("learning_patterns", {}).get(
            "consistent_scaffolding"
        ):
            recommendations.append(
                "Focus on understanding the 'why' behind solutions, not just the 'how'"
            )
            recommendations.append(
                "After getting help, try to explain the solution in your own words"
            )

        if len(recommendations) == 0:
            recommendations.append("Great job maintaining active learning behaviors!")

        return recommendations
