"""
Advanced OCR utilities using multiple open-source engines.

Supports (in order of preference for handwriting):
1. PaddleOCR - Best for handwriting, 80+ languages, Apache 2.0
2. EasyOCR - Good for handwriting, GPU-accelerated
3. TrOCR - Transformer-based, excellent for handwriting
4. Tesseract - Fallback for printed text

NO API KEYS REQUIRED - 100% local processing.
"""

import os
import cv2
import numpy as np
from typing import Optional, Dict, List
from PIL import Image, ImageEnhance, ImageFilter

# Try to import advanced OCR engines
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    PaddleOCR = None

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    easyocr = None

try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    import torch
    TROCR_AVAILABLE = True
except ImportError:
    TROCR_AVAILABLE = False
    TrOCRProcessor = None
    VisionEncoderDecoderModel = None
    torch = None

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    pytesseract = None


class AdvancedOCR:
    """Multi-engine OCR with automatic fallback for best results."""

    def __init__(self):
        """Initialize OCR engines (lazy loading)."""
        self._paddle_ocr = None
        self._easyocr_reader = None
        self._trocr_processor = None
        self._trocr_model = None
        self.has_paddle = PADDLE_AVAILABLE
        self.has_easyocr = EASYOCR_AVAILABLE
        self.has_trocr = TROCR_AVAILABLE
        self.has_tesseract = TESSERACT_AVAILABLE

    def preprocess_image_advanced(self, image_path: str, output_path: str = None) -> str:
        """Apply advanced preprocessing to improve OCR accuracy.

        Techniques:
        - Remove blue/colored tint
        - Adaptive thresholding
        - Noise reduction
        - Contrast enhancement
        - Deskewing

        Args:
            image_path: Path to input image
            output_path: Optional path to save preprocessed image

        Returns:
            Path to preprocessed image
        """
        # Read image with OpenCV
        img = cv2.imread(image_path)

        if img is None:
            return image_path  # Return original if can't read

        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Remove blue tint by enhancing contrast in each channel
        lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)

        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)

        # Merge channels
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)

        # Convert to grayscale
        gray = cv2.cvtColor(enhanced, cv2.COLOR_RGB2GRAY)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        # Adaptive thresholding to handle varying lighting
        binary = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        # Save preprocessed image
        if output_path is None:
            output_path = image_path.replace('.png', '_preprocessed.png').replace('.jpg', '_preprocessed.jpg')

        cv2.imwrite(output_path, cleaned)
        print(f"   📸 Preprocessed image saved to: {output_path}")

        return output_path

    def _get_paddle_ocr(self):
        """Lazy initialize PaddleOCR."""
        if not self.has_paddle:
            return None

        if self._paddle_ocr is None:
            print("   🔧 Initializing PaddleOCR (first time only)...")
            # Minimal initialization - PaddleOCR will use defaults
            # lang='en' for English (supports 80+ languages)
            self._paddle_ocr = PaddleOCR(lang='en')
        return self._paddle_ocr

    def _get_easyocr_reader(self):
        """Lazy initialize EasyOCR."""
        if not self.has_easyocr:
            return None

        if self._easyocr_reader is None:
            print("   🔧 Initializing EasyOCR (first time only)...")
            self._easyocr_reader = easyocr.Reader(
                ['en'],  # English
                gpu=False  # Set to True if GPU available
            )
        return self._easyocr_reader

    def _get_trocr_models(self):
        """Lazy initialize TrOCR processor and model."""
        if not self.has_trocr:
            return None, None

        if self._trocr_processor is None or self._trocr_model is None:
            print("   🔧 Initializing TrOCR (downloading models, first time only)...")
            # Use handwritten model for better handwriting recognition
            model_name = "microsoft/trocr-base-handwritten"
            self._trocr_processor = TrOCRProcessor.from_pretrained(model_name)
            self._trocr_model = VisionEncoderDecoderModel.from_pretrained(model_name)

        return self._trocr_processor, self._trocr_model

    def extract_text_paddle(self, image_path: str) -> Optional[Dict]:
        """Extract text using PaddleOCR.

        Args:
            image_path: Path to image file

        Returns:
            dict with 'text' and 'method', or None if failed
        """
        ocr = self._get_paddle_ocr()
        if not ocr:
            return None

        try:
            print("   🔍 Using PaddleOCR (best for handwriting)...")
            result = ocr.ocr(image_path, cls=True)

            if not result or not result[0]:
                return None

            # Extract text from results
            texts = []
            for line in result[0]:
                if line and len(line) > 1:
                    text = line[1][0]  # line[1] is (text, confidence)
                    texts.append(text)

            extracted_text = '\n'.join(texts)

            if extracted_text.strip():
                return {
                    'text': extracted_text.strip(),
                    'method': f'PaddleOCR v3.0 (handwriting-optimized, {len(texts)} lines)'
                }

        except Exception as e:
            print(f"   ⚠️  PaddleOCR failed: {e}")

        return None

    def extract_text_trocr(self, image_path: str) -> Optional[Dict]:
        """Extract text using TrOCR (transformer-based, best for handwriting).

        Args:
            image_path: Path to image file

        Returns:
            dict with 'text' and 'method', or None if failed
        """
        processor, model = self._get_trocr_models()
        if not processor or not model:
            return None

        try:
            print("   🔍 Using TrOCR (transformer-based, best for handwriting)...")

            # Open image
            img = Image.open(image_path).convert('RGB')

            # For full page, we need to process it as a whole
            # TrOCR works best on single lines, but we'll try full page first
            pixel_values = processor(img, return_tensors="pt").pixel_values
            generated_ids = model.generate(pixel_values)
            text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

            if text.strip():
                return {
                    'text': text.strip(),
                    'method': f'TrOCR (transformer handwriting model)'
                }

        except Exception as e:
            print(f"   ⚠️  TrOCR failed: {e}")

        return None

    def extract_text_easyocr(self, image_path: str) -> Optional[Dict]:
        """Extract text using EasyOCR.

        Args:
            image_path: Path to image file

        Returns:
            dict with 'text' and 'method', or None if failed
        """
        reader = self._get_easyocr_reader()
        if not reader:
            return None

        try:
            print("   🔍 Using EasyOCR (deep learning-based)...")
            result = reader.readtext(image_path)

            if not result:
                return None

            # Extract text from results
            texts = [text for (bbox, text, conf) in result if text.strip()]
            extracted_text = '\n'.join(texts)

            if extracted_text.strip():
                return {
                    'text': extracted_text.strip(),
                    'method': f'EasyOCR (deep learning, {len(texts)} lines)'
                }

        except Exception as e:
            print(f"   ⚠️  EasyOCR failed: {e}")

        return None

    def extract_text_tesseract(self, image_path: str) -> Optional[Dict]:
        """Extract text using Tesseract OCR (fallback).

        Args:
            image_path: Path to image file

        Returns:
            dict with 'text' and 'method', or None if failed
        """
        if not self.has_tesseract:
            return None

        try:
            print("   🔍 Using Tesseract OCR (printed text)...")

            from PIL import ImageEnhance, ImageFilter

            img = Image.open(image_path)

            # Preprocess
            if img.mode not in ('L',):
                img = img.convert('L')

            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
            img = img.filter(ImageFilter.SHARPEN)

            # Try multiple PSM modes
            best_result = None
            best_length = 0

            for psm in [1, 3, 4, 6, 11]:
                config = f'--oem 3 --psm {psm}'
                try:
                    text = pytesseract.image_to_string(img, config=config)
                    if len(text.strip()) > best_length:
                        best_length = len(text.strip())
                        best_result = text
                except:
                    continue

            if best_result and best_result.strip():
                return {
                    'text': best_result.strip(),
                    'method': f'Tesseract OCR (printed text, {best_length} chars)'
                }

        except Exception as e:
            print(f"   ⚠️  Tesseract failed: {e}")

        return None

    def extract_text_auto(self, image_path: str, use_preprocessing: bool = False) -> Dict:
        """Extract text using best available engine with automatic fallback.

        Strategy:
        1. Try TrOCR (transformer, best for handwriting) - line by line
        2. Try EasyOCR (deep learning, good results)
        3. Try PaddleOCR (if working)
        4. Try Tesseract (fallback for printed text)

        Args:
            image_path: Path to image file
            use_preprocessing: Apply advanced preprocessing (disabled by default, made things worse)

        Returns:
            dict with 'text' and 'method'
        """
        # Try TrOCR first (best for handwriting, but slower)
        result = self.extract_text_trocr(image_path)
        if result and len(result['text']) > 20:  # Lower threshold for TrOCR
            return result

        # Try EasyOCR (currently best full-page OCR for handwriting)
        result = self.extract_text_easyocr(image_path)
        if result and len(result['text']) > 50:
            return result

        # Try PaddleOCR (if API compatible)
        result = self.extract_text_paddle(image_path)
        if result and len(result['text']) > 50:
            return result

        # Try Tesseract as fallback
        result = self.extract_text_tesseract(image_path)
        if result:
            return result

        # If nothing worked, return error message
        engines_tried = []
        if self.has_trocr:
            engines_tried.append("TrOCR")
        if self.has_easyocr:
            engines_tried.append("EasyOCR")
        if self.has_paddle:
            engines_tried.append("PaddleOCR")
        if self.has_tesseract:
            engines_tried.append("Tesseract")

        if not engines_tried:
            return {
                'text': f"![Image]({os.path.basename(image_path)})\n\n*No OCR engines available. Install TrOCR, EasyOCR, PaddleOCR, or Tesseract.*",
                'method': 'No OCR engines available'
            }

        return {
            'text': f"![Image]({os.path.basename(image_path)})\n\n*No text detected. Engines tried: {', '.join(engines_tried)}*",
            'method': f'Failed ({", ".join(engines_tried)} attempted)'
        }

    def get_available_engines(self) -> List[str]:
        """Get list of available OCR engines."""
        engines = []
        if self.has_trocr:
            engines.append("TrOCR (transformer handwriting)")
        if self.has_easyocr:
            engines.append("EasyOCR (deep learning)")
        if self.has_paddle:
            engines.append("PaddleOCR (handwriting)")
        if self.has_tesseract:
            engines.append("Tesseract (printed)")
        return engines

    def get_installation_instructions(self) -> str:
        """Get installation instructions for missing engines."""
        instructions = []

        if not self.has_paddle:
            instructions.append("""
**Install PaddleOCR (recommended for handwriting):**
```bash
pip install paddleocr
```
""")

        if not self.has_easyocr:
            instructions.append("""
**Install EasyOCR (good alternative):**
```bash
pip install easyocr
```
""")

        if not self.has_tesseract:
            instructions.append("""
**Install Tesseract (fallback for printed text):**
```bash
# macOS
brew install tesseract
pip install pytesseract

# Linux
sudo apt-get install tesseract-ocr
pip install pytesseract
```
""")

        return '\n'.join(instructions) if instructions else "All OCR engines are installed!"
