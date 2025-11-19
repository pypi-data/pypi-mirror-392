"""
PPT to PDF converter (legacy PowerPoint format).
"""

import sys
import os
import subprocess
import shutil
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.exceptions import ConversionError
from core.ast import ASTNode


class Ppt2PdfConverter:
    """Convert PPT (legacy PowerPoint) to PDF format."""

    def parse_ppt2ast(self, input_path: str) -> ASTNode:
        """Parse PPT to AST representation (placeholder)."""
        return ASTNode(type="root")

    def ast2pdf(self, ast_root: ASTNode, output_path: str):
        """Convert AST to PDF (placeholder)."""
        pass

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert PPT to PDF.

        For legacy .ppt files, we first convert to .pptx then to PDF.

        Args:
            input_path: Path to input PPT file
            output_path: Path to output PDF file
        """
        if not os.path.exists(input_path):
            raise ConversionError(f"Input file not found: {input_path}")

        if not output_path.lower().endswith(".pdf"):
            output_path += ".pdf"

        errors = []

        # Method 1: LibreOffice direct conversion (best)
        if shutil.which("soffice") or shutil.which("libreoffice"):
            try:
                soffice_cmd = "soffice" if shutil.which("soffice") else "libreoffice"

                # Get output directory
                output_dir = os.path.dirname(os.path.abspath(output_path))
                if not output_dir:
                    output_dir = os.getcwd()

                # LibreOffice converts to PDF in the same directory
                result = subprocess.run([
                    soffice_cmd,
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", output_dir,
                    input_path
                ], capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    # LibreOffice creates PDF with same basename
                    input_basename = os.path.splitext(os.path.basename(input_path))[0]
                    expected_pdf = os.path.join(output_dir, f"{input_basename}.pdf")

                    # Move to desired output path if different
                    if os.path.exists(expected_pdf):
                        if expected_pdf != output_path:
                            shutil.move(expected_pdf, output_path)
                        print(f"Successfully converted '{input_path}' to '{output_path}' via LibreOffice")
                        return

                errors.append(f"LibreOffice failed: {result.stderr.strip()}")
            except subprocess.TimeoutExpired:
                errors.append("LibreOffice conversion timed out")
            except Exception as e:
                errors.append(f"LibreOffice error: {e}")

        # Method 2: Convert PPT -> PPTX -> PDF (two-stage conversion)
        try:
            from docuvert.utils.legacy_converter import LegacyFormatConverter

            # First convert PPT to PPTX
            with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp_pptx:
                tmp_pptx_path = tmp_pptx.name

            try:
                # Convert PPT to PPTX
                temp_pptx = LegacyFormatConverter.convert_ppt_to_pptx(input_path)
                if not temp_pptx:
                    errors.append("Failed to convert PPT to PPTX")
                else:
                    # Now convert PPTX to PDF
                    from docuvert.converters.pptx2pdf import Pptx2PdfConverter
                    pptx_converter = Pptx2PdfConverter()
                    pptx_converter.convert(temp_pptx, output_path)

                    # Clean up temporary PPTX
                    if os.path.exists(temp_pptx):
                        os.unlink(temp_pptx)

                    print(f"Successfully converted '{input_path}' to '{output_path}' via PPT->PPTX->PDF")
                    return
            finally:
                # Clean up temp files
                if os.path.exists(tmp_pptx_path):
                    os.unlink(tmp_pptx_path)

        except ImportError:
            errors.append("Legacy converter not available")
        except Exception as e:
            errors.append(f"Two-stage conversion failed: {e}")

        # Method 3: unoconv
        if shutil.which("unoconv"):
            try:
                result = subprocess.run([
                    "unoconv",
                    "-f", "pdf",
                    "-o", output_path,
                    input_path
                ], capture_output=True, text=True, timeout=60)

                if result.returncode == 0 and os.path.exists(output_path):
                    print(f"Successfully converted '{input_path}' to '{output_path}' via unoconv")
                    return

                errors.append(f"unoconv failed: {result.stderr.strip()}")
            except subprocess.TimeoutExpired:
                errors.append("unoconv conversion timed out")
            except Exception as e:
                errors.append(f"unoconv error: {e}")

        # If we reach here, all conversion methods failed
        raise ConversionError(
            f"PPT to PDF conversion failed with all methods.\n" +
            "Errors: " + " | ".join(errors),
            source_format="ppt",
            target_format="pdf",
            suggestions=[
                "Install LibreOffice: brew install libreoffice (macOS) or apt-get install libreoffice (Linux)",
                "Install unoconv: pip install unoconv",
                "Convert PPT to PPTX first using a newer version of PowerPoint",
                "Ensure PowerPoint file is not corrupted"
            ]
        )
