"""
JPEG to Markdown converter using Vision AI (Claude/GPT-4) with OCR fallback.

This converter prioritizes Vision AI models (Claude 3.5 Sonnet, GPT-4 Vision)
for high-accuracy extraction of handwritten notes, complex layouts, and mixed content.
Falls back to enhanced Tesseract OCR if no API keys are available.
"""

import sys
import os
from io import BytesIO
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.exceptions import ConversionError, DependencyError

try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError as e:
    raise DependencyError(
        "Pillow is required for image processing",
        missing_dependency="pillow"
    ) from e

# Lazy import pytesseract (optional fallback)
pytesseract = None
try:
    import pytesseract as _pytesseract
    pytesseract = _pytesseract
except ImportError:
    pass

# Import vision AI utilities
from utils.vision_ai import VisionAIConverter


class Jpeg2MdConverter:
    """Convert JPEG to Markdown using Vision AI with OCR fallback."""

    def __init__(self):
        """Initialize the converter with vision AI support."""
        self.vision_converter = VisionAIConverter()
        self.has_anthropic = bool(self.vision_converter.anthropic_api_key)
        self.has_openai = bool(self.vision_converter.openai_api_key)
        self.has_tesseract = pytesseract is not None

    def parse_jpeg2ast(self, input_path: str):
        """Parse JPEG to AST representation (placeholder)."""
        return None

    def ast2md(self, ast_root, output_path: str):
        """Convert AST to Markdown (placeholder)."""
        pass

    def _convert_with_vision_ai(self, input_path: str) -> Optional[dict]:
        """Try Vision AI conversion (Claude then OpenAI).

        Returns:
            dict with 'text' and 'method', or None if failed
        """
        # Try Claude first (best for handwriting)
        if self.has_anthropic:
            try:
                print("🔍 Using Anthropic Claude Vision (best for handwriting)...")
                text = self.vision_converter.convert_with_anthropic(input_path)
                return {
                    'text': text,
                    'method': 'Anthropic Claude 3.5 Sonnet'
                }
            except Exception as e:
                print(f"⚠️  Claude Vision failed: {e}")

        # Try OpenAI GPT-4 Vision
        if self.has_openai:
            try:
                print("🔍 Using OpenAI GPT-4 Vision...")
                text = self.vision_converter.convert_with_openai(input_path)
                return {
                    'text': text,
                    'method': 'OpenAI GPT-4 Vision'
                }
            except Exception as e:
                print(f"⚠️  GPT-4 Vision failed: {e}")

        return None

    def _convert_with_tesseract(self, input_path: str) -> dict:
        """Enhanced Tesseract OCR with preprocessing.

        Returns:
            dict with 'text' and 'method'
        """
        if not self.has_tesseract:
            raise ConversionError(
                "No OCR engine available. Please install Tesseract OCR or set ANTHROPIC_API_KEY/OPENAI_API_KEY",
                source_format="jpeg",
                target_format="md",
                suggestions=[
                    "Option 1: Install Tesseract - brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)",
                    "Option 2: Set ANTHROPIC_API_KEY for Claude Vision (best for handwriting)",
                    "Option 3: Set OPENAI_API_KEY for GPT-4 Vision"
                ]
            )

        print("🔍 Using Tesseract OCR with advanced preprocessing...")

        img = Image.open(input_path)

        # Preprocessing for better OCR
        # 1. Convert to grayscale
        if img.mode not in ('L',):
            img = img.convert('L')

        # 2. Increase contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)

        # 3. Sharpen
        img = img.filter(ImageFilter.SHARPEN)

        # Try multiple PSM modes and pick the best result
        best_result = None
        best_length = 0

        psm_modes = [3, 4, 6, 11, 12]  # Various page segmentation modes
        for psm in psm_modes:
            config = f'--oem 3 --psm {psm}'
            try:
                text = pytesseract.image_to_string(img, config=config)
                if len(text.strip()) > best_length:
                    best_length = len(text.strip())
                    best_result = text
            except:
                continue

        if not best_result or not best_result.strip():
            return {
                'text': f"![Image]({os.path.basename(input_path)})\n\n*No text detected in this image*",
                'method': 'Tesseract OCR (no text detected)'
            }

        return {
            'text': best_result.strip(),
            'method': 'Tesseract OCR (enhanced preprocessing)'
        }

    def convert(self, input_path: str, output_path: str, force_tesseract: bool = False) -> None:
        """Convert PNG image to Markdown using Vision AI or OCR.

        Conversion strategy:
        1. Try Anthropic Claude Vision (best for handwriting)
        2. Try OpenAI GPT-4 Vision
        3. Fallback to enhanced Tesseract OCR

        Args:
            input_path: Path to input PNG file
            output_path: Path to output Markdown file
            force_tesseract: Skip Vision AI and use Tesseract directly
        """

        if not os.path.exists(input_path):
            raise ConversionError(f"Input file not found: {input_path}")

        if not output_path.lower().endswith(".md"):
            output_path += ".md"

        try:
            print(f"🖼️  Converting JPEG to Markdown: {input_path}")

            # Strategy 1: Try Vision AI (unless forced to use Tesseract)
            result = None
            if not force_tesseract:
                result = self._convert_with_vision_ai(input_path)

            # Strategy 2: Fallback to Tesseract
            if result is None:
                if not force_tesseract:
                    print("📋 No Vision AI available, falling back to Tesseract OCR...")
                result = self._convert_with_tesseract(input_path)

            # Create Markdown content
            markdown_content = f"""# Image to Markdown Conversion

**Source:** {os.path.basename(input_path)}
**Method:** {result['method']}

---

{result['text']}

---

*Converted using Docuvert*
"""

            # Write to output file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            print(f"✅ Successfully converted '{input_path}' to '{output_path}'")
            print(f"   Method used: {result['method']}")

        except Exception as e:
            if isinstance(e, ConversionError):
                raise
            raise ConversionError(
                f"PNG to Markdown conversion failed: {e}",
                source_format="jpeg",
                target_format="md",
                suggestions=[
                    "For handwritten notes: Set ANTHROPIC_API_KEY or OPENAI_API_KEY",
                    "For typed text: Install Tesseract OCR",
                    "Ensure image is not corrupted"
                ]
            )
