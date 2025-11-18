"""
PNG to Markdown converter using advanced open-source OCR engines.

Uses (in priority order):
1. PaddleOCR - Best for handwriting (Apache 2.0)
2. EasyOCR - Deep learning-based (Apache 2.0)
3. Tesseract - Fallback for printed text (Apache 2.0)

NO API KEYS REQUIRED - 100% local, open-source processing.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.exceptions import ConversionError, DependencyError
from utils.advanced_ocr import AdvancedOCR

try:
    from PIL import Image
except ImportError as e:
    raise DependencyError(
        "Pillow is required for image processing",
        missing_dependency="pillow"
    ) from e


class Png2MdConverter:
    """Convert PNG to Markdown using advanced multi-engine OCR."""

    def __init__(self):
        """Initialize the converter with advanced OCR engines."""
        self.ocr = AdvancedOCR()

    def parse_png2ast(self, input_path: str):
        """Parse PNG to AST representation (placeholder)."""
        return None

    def ast2md(self, ast_root, output_path: str):
        """Convert AST to Markdown (placeholder)."""
        pass

    def _extract_text_with_ocr(self, input_path: str) -> dict:
        """Extract text using best available OCR engine.

        Uses multi-engine approach:
        1. PaddleOCR (best for handwriting)
        2. EasyOCR (deep learning)
        3. Tesseract (printed text fallback)

        Args:
            input_path: Path to image file

        Returns:
            dict with 'text' and 'method'
        """
        # Check if any engines are available
        engines = self.ocr.get_available_engines()

        if not engines:
            raise ConversionError(
                "No OCR engines available. Install at least one OCR engine.",
                source_format="png",
                target_format="md",
                suggestions=[
                    "Recommended: pip install paddleocr (best for handwriting)",
                    "Alternative: pip install easyocr (deep learning-based)",
                    "Fallback: brew install tesseract && pip install pytesseract"
                ]
            )

        print(f"🔍 Available OCR engines: {', '.join(engines)}")

        # Use automatic engine selection with fallback
        result = self.ocr.extract_text_auto(input_path)

        if not result['text'].strip() or 'No text detected' in result['text']:
            return {
                'text': f"![Image]({os.path.basename(input_path)})\n\n*No text detected in this image*\n\nEngines tried: {', '.join(engines)}",
                'method': result['method']
            }

        return result

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert PNG image to Markdown using advanced OCR engines.

        Args:
            input_path: Path to input PNG file
            output_path: Path to output Markdown file
        """
        if not os.path.exists(input_path):
            raise ConversionError(f"Input file not found: {input_path}")

        if not output_path.lower().endswith(".md"):
            output_path += ".md"

        try:
            print(f"🖼️  Converting PNG to Markdown: {input_path}")

            # Extract text with best available OCR engine
            result = self._extract_text_with_ocr(input_path)

            # Create Markdown content
            markdown_content = f"""# Image to Markdown Conversion

**Source:** {os.path.basename(input_path)}
**Method:** {result['method']}

---

{result['text']}

---

*Converted using Docuvert (local open-source OCR)*
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
                source_format="png",
                target_format="md",
                suggestions=[
                    "Recommended: pip install paddleocr (best for handwriting)",
                    "Alternative: pip install easyocr (deep learning)",
                    "Fallback: brew install tesseract && pip install pytesseract",
                    "Ensure image is not corrupted",
                    "Try a higher resolution image for better results"
                ]
            )
