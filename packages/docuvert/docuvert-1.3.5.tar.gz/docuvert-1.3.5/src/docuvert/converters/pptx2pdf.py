"""
PPTX to PDF converter with multiple conversion methods.
"""

import sys
import os
import subprocess
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.exceptions import ConversionError, DependencyError
from core.ast import ASTNode

try:
    from pptx import Presentation
except ImportError as e:
    raise DependencyError(
        "python-pptx is required for PowerPoint processing",
        missing_dependency="python-pptx"
    ) from e


class Pptx2PdfConverter:
    """Convert PPTX to PDF format using multiple fallback methods."""

    def parse_pptx2ast(self, input_path: str) -> ASTNode:
        """Parse PPTX to AST representation (placeholder)."""
        return ASTNode(type="root")

    def ast2pdf(self, ast_root: ASTNode, output_path: str):
        """Convert AST to PDF (placeholder)."""
        pass

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert PPTX to PDF.

        Args:
            input_path: Path to input PPTX file
            output_path: Path to output PDF file
        """
        if not os.path.exists(input_path):
            raise ConversionError(f"Input file not found: {input_path}")

        if not output_path.lower().endswith(".pdf"):
            output_path += ".pdf"

        errors = []

        # Method 1: LibreOffice (best quality)
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

        # Method 2: unoconv (alternative LibreOffice interface)
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

        # Method 3: pypandoc (requires pandoc)
        try:
            import pypandoc

            pypandoc.convert_file(
                input_path,
                'pdf',
                outputfile=output_path,
                extra_args=['--pdf-engine=xelatex']
            )

            if os.path.exists(output_path):
                print(f"Successfully converted '{input_path}' to '{output_path}' via pypandoc")
                return

            errors.append("pypandoc did not create output file")
        except ImportError:
            errors.append("pypandoc not available")
        except Exception as e:
            errors.append(f"pypandoc failed: {e}")

        # Method 4: Convert via images (fallback - lower quality)
        try:
            from PIL import Image
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter

            # Load presentation
            prs = Presentation(input_path)

            # Create temporary directory for slide images
            with tempfile.TemporaryDirectory() as tmpdir:
                slide_images = []

                # Export slides would require additional tools
                # This is a placeholder - actual implementation would need
                # a tool like ImageMagick or LibreOffice to export slides
                errors.append("Image-based conversion requires LibreOffice or ImageMagick")

        except ImportError as e:
            errors.append(f"Image conversion dependencies missing: {e}")
        except Exception as e:
            errors.append(f"Image conversion failed: {e}")

        # If we reach here, all conversion methods failed
        raise ConversionError(
            f"PPTX to PDF conversion failed with all methods.\n" +
            "Errors: " + " | ".join(errors),
            source_format="pptx",
            target_format="pdf",
            suggestions=[
                "Install LibreOffice: brew install libreoffice (macOS) or apt-get install libreoffice (Linux)",
                "Install unoconv: pip install unoconv",
                "Install pypandoc: pip install pypandoc",
                "Ensure PowerPoint file is not corrupted"
            ]
        )
