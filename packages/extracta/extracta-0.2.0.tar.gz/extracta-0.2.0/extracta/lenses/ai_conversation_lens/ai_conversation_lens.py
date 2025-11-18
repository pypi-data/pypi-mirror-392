"""AI Conversation lens for extracting conversation data from various formats."""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_lens import BaseLens


class AIConversationLens(BaseLens):
    """Lens for extracting AI conversation data from various formats."""

    SUPPORTED_EXTENSIONS = {
        ".json",  # ChatGPT exports, Claude exports, etc.
        ".txt",  # Plain text conversation logs
        ".md",  # Markdown conversation logs
        ".html",  # Web-based conversation exports
    }

    # Common AI platform patterns
    PLATFORM_PATTERNS = {
        "chatgpt": {
            "user_pattern": r"^\*\*User:\*\*\s*(.+)$",
            "assistant_pattern": r"^\*\*Assistant:\*\*\s*(.+)$",
            "timestamp_pattern": r"^\*\*Timestamp:\*\*\s*(.+)$",
        },
        "claude": {
            "user_pattern": r"^Human:\s*(.+)$",
            "assistant_pattern": r"^Assistant:\s*(.+)$",
        },
        "bard": {
            "user_pattern": r"^You:\s*(.+)$",
            "assistant_pattern": r"^(Bard|Assistant):\s*(.+)$",
        },
        "generic": {
            "user_pattern": r"^(User|Human|You):\s*(.+)$",
            "assistant_pattern": r"^(Assistant|AI|Bot):\s*(.+)$",
        },
    }

    def __init__(self):
        pass

    def extract(self, file_path: Path) -> Dict[str, Any]:
        """Extract conversation data from file."""
        try:
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "data": {},
                }

            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {file_path.suffix}",
                    "data": {},
                }

            # Read file content
            content = self._read_file_content(file_path)

            # Detect format and extract conversation
            if file_path.suffix.lower() == ".json":
                conversation_data = self._extract_from_json(content, file_path)
            else:
                conversation_data = self._extract_from_text(content, file_path)

            if not conversation_data.get("messages"):
                return {
                    "success": False,
                    "error": "No conversation messages found in file",
                    "data": {},
                }

            # Add metadata
            conversation_data.update(
                {
                    "file_path": str(file_path),
                    "file_size": file_path.stat().st_size,
                    "extraction_timestamp": datetime.now().isoformat(),
                }
            )

            return {
                "success": True,
                "data": conversation_data,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "data": {}}

    def _read_file_content(self, file_path: Path) -> str:
        """Read file content with encoding detection."""
        encodings = ["utf-8", "utf-16", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        # Last resort
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except:
            return ""

    def _extract_from_json(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Extract conversation from JSON format."""
        try:
            data = json.loads(content)

            # Handle different JSON formats
            if self._is_chatgpt_format(data):
                return self._extract_chatgpt_json(data)
            elif self._is_claude_format(data):
                return self._extract_claude_json(data)
            else:
                return self._extract_generic_json(data)

        except json.JSONDecodeError:
            # Not valid JSON, treat as text
            return self._extract_from_text(content, file_path)

    def _is_chatgpt_format(self, data: Dict) -> bool:
        """Check if data is in ChatGPT export format."""
        if not isinstance(data, list):
            return False
        # ChatGPT exports are usually arrays of conversation objects
        return len(data) > 0 and isinstance(data[0], dict) and "message" in data[0]

    def _is_claude_format(self, data: Dict) -> bool:
        """Check if data is in Claude export format."""
        # Claude exports might have different structure
        return isinstance(data, dict) and "chat_messages" in data

    def _extract_chatgpt_json(self, data: List[Dict]) -> Dict[str, Any]:
        """Extract from ChatGPT JSON export."""
        messages = []
        conversation_title = "ChatGPT Conversation"

        for item in data:
            if isinstance(item, dict) and "message" in item:
                message_data = item["message"]
                if isinstance(message_data, dict):
                    role = message_data.get("author", {}).get("role", "")
                    content = message_data.get("content", {}).get("parts", [""])[0]

                    if role in ["user", "assistant"] and content:
                        messages.append(
                            {
                                "role": role,
                                "content": content,
                                "timestamp": item.get("create_time"),
                            }
                        )

        return {
            "platform": "chatgpt",
            "title": conversation_title,
            "messages": messages,
            "message_count": len(messages),
        }

    def _extract_claude_json(self, data: Dict) -> Dict[str, Any]:
        """Extract from Claude JSON export."""
        messages = []
        chat_messages = data.get("chat_messages", [])

        for msg in chat_messages:
            if isinstance(msg, dict):
                role = "user" if msg.get("sender") == "human" else "assistant"
                content = msg.get("text", "")

                if content:
                    messages.append(
                        {
                            "role": role,
                            "content": content,
                            "timestamp": msg.get("created_at"),
                        }
                    )

        return {
            "platform": "claude",
            "title": data.get("name", "Claude Conversation"),
            "messages": messages,
            "message_count": len(messages),
        }

    def _extract_generic_json(self, data: Dict) -> Dict[str, Any]:
        """Extract from generic JSON conversation format."""
        messages = []

        # Try common JSON structures
        possible_message_keys = ["messages", "conversation", "chat", "turns"]

        for key in possible_message_keys:
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    if isinstance(item, dict):
                        # Try to identify role and content
                        role = (
                            item.get("role") or item.get("sender") or item.get("author")
                        )
                        content = (
                            item.get("content")
                            or item.get("text")
                            or item.get("message")
                        )

                        if role and content:
                            messages.append(
                                {
                                    "role": role
                                    if role in ["user", "assistant"]
                                    else "user",
                                    "content": content,
                                    "timestamp": item.get("timestamp")
                                    or item.get("time"),
                                }
                            )

        return {
            "platform": "generic_json",
            "title": "JSON Conversation",
            "messages": messages,
            "message_count": len(messages),
        }

    def _extract_from_text(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Extract conversation from text/markdown/HTML formats."""
        lines = content.split("\n")
        messages = []
        current_message = None
        platform = "generic_text"

        # Try to detect platform from content
        content_lower = content.lower()
        if "chatgpt" in content_lower or "**user:**" in content_lower:
            platform = "chatgpt"
        elif "claude" in content_lower or "human:" in content_lower:
            platform = "claude"
        elif "bard" in content_lower:
            platform = "bard"

        patterns = self.PLATFORM_PATTERNS.get(
            platform, self.PLATFORM_PATTERNS["generic"]
        )

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for user messages
            user_match = re.match(patterns["user_pattern"], line, re.IGNORECASE)
            if user_match:
                if current_message:
                    messages.append(current_message)
                current_message = {
                    "role": "user",
                    "content": user_match.group(1)
                    if len(user_match.groups()) > 0
                    else user_match.group(0),
                    "timestamp": None,
                }
                continue

            # Check for assistant messages
            assistant_match = re.match(
                patterns["assistant_pattern"], line, re.IGNORECASE
            )
            if assistant_match:
                if current_message:
                    messages.append(current_message)
                current_message = {
                    "role": "assistant",
                    "content": assistant_match.group(1)
                    if len(assistant_match.groups()) > 0
                    else assistant_match.group(0),
                    "timestamp": None,
                }
                continue

            # Check for timestamps
            timestamp_match = re.match(
                patterns.get("timestamp_pattern", r"^\d{4}-\d{2}-\d{2}"), line
            )
            if timestamp_match and current_message:
                current_message["timestamp"] = timestamp_match.group(0)

            # If we have a current message and this line doesn't match patterns,
            # it might be continuation of the message
            elif (
                current_message
                and not line.startswith("#")
                and not line.startswith("---")
            ):
                current_message["content"] += "\n" + line

        # Add final message
        if current_message:
            messages.append(current_message)

        # Extract title from first heading or filename
        title = self._extract_title(content, file_path)

        return {
            "platform": platform,
            "title": title,
            "messages": messages,
            "message_count": len(messages),
        }

    def _extract_title(self, content: str, file_path: Path) -> str:
        """Extract conversation title from content or filename."""
        # Try to find title in content
        lines = content.split("\n")
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line.startswith("# "):  # Markdown heading
                return line[2:].strip()
            elif line.startswith("Title:") or line.startswith("Subject:"):
                return line.split(":", 1)[1].strip()

        # Fallback to filename
        return file_path.stem.replace("_", " ").replace("-", " ").title()
