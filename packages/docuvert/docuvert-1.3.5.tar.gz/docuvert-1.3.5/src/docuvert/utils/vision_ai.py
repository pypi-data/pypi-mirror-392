"""
Vision AI utilities for high-accuracy image and PDF to text conversion.
Supports OpenAI GPT-4 Vision and Anthropic Claude Vision APIs.
"""

import os
import base64
from typing import Optional, Dict, Any
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    Image = None


class VisionAIConverter:
    """Convert images and PDFs to Markdown using vision AI models."""

    def __init__(self):
        """Initialize the vision AI converter."""
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')

    def _encode_image_to_base64(self, image_path: str) -> str:
        """Encode image to base64 string.

        Args:
            image_path: Path to image file

        Returns:
            Base64 encoded image string
        """
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def _get_image_mime_type(self, image_path: str) -> str:
        """Get MIME type for image.

        Args:
            image_path: Path to image file

        Returns:
            MIME type string (e.g., 'image/png', 'image/jpeg')
        """
        ext = image_path.lower().split('.')[-1]
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        return mime_types.get(ext, 'image/png')

    def convert_with_openai(self, image_path: str, prompt: Optional[str] = None) -> str:
        """Convert image to markdown using OpenAI GPT-4 Vision.

        Args:
            image_path: Path to image file
            prompt: Optional custom prompt (default: transcribe to markdown)

        Returns:
            Markdown text extracted from image

        Raises:
            ImportError: If openai package is not installed
            ValueError: If API key is not set
        """
        try:
            import openai
        except ImportError:
            raise ImportError(
                "OpenAI package is required for GPT-4 Vision. "
                "Install with: pip install openai"
            )

        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Set it with: export OPENAI_API_KEY='your-api-key'"
            )

        # Set up OpenAI client
        client = openai.OpenAI(api_key=self.openai_api_key)

        # Default prompt for accurate transcription
        if prompt is None:
            prompt = """Please transcribe this image to Markdown format with maximum accuracy.

Rules:
1. Preserve all text exactly as written, including handwriting
2. Maintain the structure and layout using Markdown formatting
3. Use appropriate headers (##, ###), lists, code blocks, and emphasis
4. For mathematical notation, use LaTeX in $ or $$ blocks
5. For diagrams or drawings, describe them in [brackets]
6. If text is unclear, mark it as [unclear: possible_text]
7. Do not add commentary or explanations - just transcribe

Output only the transcribed Markdown, nothing else."""

        # Encode image
        base64_image = self._encode_image_to_base64(image_path)
        mime_type = self._get_image_mime_type(image_path)

        # Call GPT-4 Vision API
        response = client.chat.completions.create(
            model="gpt-4o",  # Latest GPT-4 with vision
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}",
                                "detail": "high"  # High detail for better accuracy
                            }
                        }
                    ]
                }
            ],
            max_tokens=4096,
            temperature=0  # Deterministic output for consistency
        )

        return response.choices[0].message.content.strip()

    def convert_with_anthropic(self, image_path: str, prompt: Optional[str] = None) -> str:
        """Convert image to markdown using Anthropic Claude Vision.

        Args:
            image_path: Path to image file
            prompt: Optional custom prompt (default: transcribe to markdown)

        Returns:
            Markdown text extracted from image

        Raises:
            ImportError: If anthropic package is not installed
            ValueError: If API key is not set
        """
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "Anthropic package is required for Claude Vision. "
                "Install with: pip install anthropic"
            )

        if not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Set it with: export ANTHROPIC_API_KEY='your-api-key'"
            )

        # Set up Anthropic client
        client = anthropic.Anthropic(api_key=self.anthropic_api_key)

        # Default prompt for accurate transcription
        if prompt is None:
            prompt = """Please transcribe this image to Markdown format with maximum accuracy.

Rules:
1. Preserve all text exactly as written, including handwriting
2. Maintain the structure and layout using Markdown formatting
3. Use appropriate headers (##, ###), lists, code blocks, and emphasis
4. For mathematical notation, use LaTeX in $ or $$ blocks
5. For diagrams or drawings, describe them in [brackets]
6. If text is unclear, mark it as [unclear: possible_text]
7. Do not add commentary or explanations - just transcribe

Output only the transcribed Markdown, nothing else."""

        # Encode image
        base64_image = self._encode_image_to_base64(image_path)
        mime_type = self._get_image_mime_type(image_path)

        # Call Claude Vision API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Latest Claude with vision
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )

        return response.content[0].text.strip()

    def convert_with_fallback(self, image_path: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        """Convert image to markdown with intelligent fallback.

        Tries multiple methods in order:
        1. Anthropic Claude Vision (best for handwriting and complex layouts)
        2. OpenAI GPT-4 Vision (excellent for typed text and diagrams)
        3. Tesseract OCR (fallback for simple typed text)

        Args:
            image_path: Path to image file
            prompt: Optional custom prompt for vision AI

        Returns:
            Dictionary with 'text' (markdown content) and 'method' (which method succeeded)
        """
        errors = []

        # Try Anthropic Claude first (best for handwriting)
        if self.anthropic_api_key:
            try:
                text = self.convert_with_anthropic(image_path, prompt)
                return {
                    'text': text,
                    'method': 'anthropic_claude',
                    'success': True
                }
            except Exception as e:
                errors.append(f"Anthropic Claude failed: {e}")

        # Try OpenAI GPT-4 Vision
        if self.openai_api_key:
            try:
                text = self.convert_with_openai(image_path, prompt)
                return {
                    'text': text,
                    'method': 'openai_gpt4',
                    'success': True
                }
            except Exception as e:
                errors.append(f"OpenAI GPT-4 failed: {e}")

        # Fallback to Tesseract OCR
        try:
            import pytesseract
            if Image:
                img = Image.open(image_path)
                text = pytesseract.image_to_string(img, config='--oem 3 --psm 6')
                return {
                    'text': text.strip(),
                    'method': 'tesseract_ocr',
                    'success': True,
                    'warning': 'Used basic OCR - may not be accurate for handwriting or complex layouts'
                }
        except Exception as e:
            errors.append(f"Tesseract OCR failed: {e}")

        # All methods failed
        error_msg = "\n".join(errors)
        return {
            'text': '',
            'method': 'none',
            'success': False,
            'error': f"All conversion methods failed:\n{error_msg}"
        }
