"""
PDF to Markdown converter using local OCR (Tesseract).

This converter uses PyMuPDF for text extraction and Tesseract OCR for scanned PDFs.
NO API KEYS REQUIRED - 100% local processing.
"""

import sys
import os
from io import BytesIO
from typing import Optional, List, Dict
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.ast import ASTNode
from core.exceptions import ConversionError, DependencyError
from utils.ocr_utils import OCRExtractor

try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    Image = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import pytesseract
except ImportError:
    pytesseract = None


class Pdf2MdConverter:
    """
    Converts a PDF file to a Markdown file using only local tools.

    Strategies (in order):
    1. PyMuPDF text extraction with structure analysis (fast, for text-based PDFs)
    2. Enhanced Tesseract OCR (for scanned PDFs)
    3. Layout detection and markdown formatting
    """

    def __init__(self):
        """Initialize converter."""
        self.has_tesseract = pytesseract is not None

    def parse_pdf2ast(self, input_path: str) -> ASTNode:
        """
        Parses a PDF file and converts it to an AST.

        Args:
            input_path (str): The path to the input PDF file.

        Returns:
            ASTNode: The root of the generated AST.
        """
        # TODO: Implement the logic to parse the PDF and build an AST.
        print(f"Parsing PDF at {input_path} and converting to AST.")
        return ASTNode(type="root")

    def ast2md(self, ast_root: ASTNode, output_path: str):
        """
        Converts an AST to a Markdown file.

        Args:
            ast_root (ASTNode): The root of the AST.
            output_path (str): The path to the output Markdown file.
        """
        # TODO: Implement the logic to convert the AST to a Markdown document.
        print(f"Converting AST to Markdown at {output_path}")

    def _extract_text_with_structure(self, input_path: str) -> str:
        """Extract text from PDF with structure preservation using PyMuPDF.

        Args:
            input_path: Path to PDF file

        Returns:
            Extracted text with markdown formatting
        """
        if not fitz:
            raise ConversionError(
                "PyMuPDF is required for PDF text extraction",
                source_format="pdf",
                target_format="markdown",
                suggestions=["Install PyMuPDF: pip install PyMuPDF"]
            )

        pdf_doc = fitz.open(input_path)
        all_text = []

        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]

            # Try text extraction first
            text = page.get_text("text")

            if text.strip():
                all_text.append(f"## Page {page_num + 1}\n\n{text}")
            else:
                # Page is likely scanned/image-based, will need OCR
                all_text.append(f"## Page {page_num + 1}\n\n[Scanned page - OCR needed]")

        pdf_doc.close()
        return "\n\n---\n\n".join(all_text) if all_text else ""

    def _ocr_pdf_with_tesseract(self, input_path: str) -> str:
        """OCR PDF pages using Tesseract with enhanced preprocessing.

        Args:
            input_path: Path to PDF file

        Returns:
            Extracted text with markdown formatting
        """
        if not self.has_tesseract:
            return ""

        if not fitz or not Image:
            return ""

        print("🔍 Using Tesseract OCR on PDF pages...")

        pdf_doc = fitz.open(input_path)
        all_text = []

        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]

            # Render page at high resolution for better OCR
            mat = fitz.Matrix(3.0, 3.0)  # 3x zoom for better accuracy
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(BytesIO(img_data))

            # Preprocess image for better OCR
            if img.mode not in ('L',):
                img = img.convert('L')

            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)

            # Sharpen
            img = img.filter(ImageFilter.SHARPEN)

            # Try multiple PSM modes and pick the best result
            best_result = None
            best_length = 0

            psm_modes = [1, 3, 4, 6, 11]  # Various page segmentation modes
            for psm in psm_modes:
                config = f'--oem 3 --psm {psm}'
                try:
                    text = pytesseract.image_to_string(img, config=config)
                    if len(text.strip()) > best_length:
                        best_length = len(text.strip())
                        best_result = text
                except:
                    continue

            if best_result and best_result.strip():
                all_text.append(f"## Page {page_num + 1}\n\n{best_result.strip()}")
                print(f"   ✅ OCR extracted text from page {page_num + 1}")
            else:
                all_text.append(f"## Page {page_num + 1}\n\n*[No text detected on this page]*")
                print(f"   ⚠️  No text found on page {page_num + 1}")

        pdf_doc.close()
        return "\n\n---\n\n".join(all_text) if all_text else ""

    def convert(self, input_path: str, output_path: str):
        """
        Converts a PDF file to a Markdown file using local tools only (no APIs).

        Strategy:
        1. Try PyMuPDF text extraction (fast, for text-based PDFs)
        2. Fallback to Tesseract OCR (for scanned/image PDFs)

        Args:
            input_path (str): The path to the input PDF file.
            output_path (str): The path to the output Markdown file.
        """
        if not os.path.exists(input_path):
            raise ConversionError(f"Input file not found: {input_path}")

        try:
            print(f"🔄 Converting PDF to Markdown: {input_path}")

            # Strategy 1: Try direct text extraction
            print("📄 Attempting direct text extraction...")
            text = self._extract_text_with_structure(input_path)

            method = "PyMuPDF text extraction"

            # Strategy 2: If no text found or minimal text, automatically try OCR
            if not text.strip() or len(text.strip()) < 100 or "[Scanned page - OCR needed]" in text:
                if self.has_tesseract:
                    print("📋 Document appears to be scanned/image-based, using OCR...")
                    ocr_text = self._ocr_pdf_with_tesseract(input_path)

                    if ocr_text and len(ocr_text.strip()) > len(text.strip()):
                        text = ocr_text
                        method = "Tesseract OCR with enhanced preprocessing"
                    elif text.strip() and "[Scanned page" not in text:
                        method = "PyMuPDF text extraction"
                    else:
                        text = ocr_text if ocr_text else "No text could be extracted from this PDF."
                        method = "Tesseract OCR (attempted)"
                else:
                    print("⚠️  Document appears scanned but Tesseract is not installed")
                    if not text.strip() or "[Scanned page" in text:
                        text = "This PDF contains scanned/image pages. Install Tesseract OCR to extract text:\n\n  macOS: brew install tesseract\n  Linux: sudo apt-get install tesseract-ocr"
                        method = "PyMuPDF text extraction (OCR required but not available)"

            # Format as markdown
            markdown_content = self._format_as_markdown(text, method)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            print(f"✅ Successfully converted '{input_path}' to '{output_path}'")
            print(f"   Method used: {method}")

        except Exception as e:
            if isinstance(e, ConversionError):
                raise
            raise ConversionError(
                f"PDF to Markdown conversion failed: {e}",
                source_format="pdf",
                target_format="markdown",
                suggestions=[
                    "For scanned PDFs: Install Tesseract OCR (brew install tesseract)",
                    "Ensure PDF is not corrupted or password-protected",
                    "Check that PyMuPDF is installed (pip install PyMuPDF)"
                ]
            )

    def _format_as_markdown(self, text: str, method: str = "Unknown") -> str:
        """Format extracted text as markdown with basic structure."""
        markdown_content = f"""# PDF to Markdown Conversion

**Method:** {method}

---

{text}

---

*Converted using Docuvert*
"""
        return markdown_content
