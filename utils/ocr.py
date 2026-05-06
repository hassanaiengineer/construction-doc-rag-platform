# import os
# import io
# import json
# import logging
# from pdf2image import convert_from_path
# from google.cloud import vision

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# class OCRProcessor:
#     def __init__(self, upload_dir='Uploads', pages_dir='Pages', sample_text_dir='Sample Text', structured_text_dir='Structured Text'):
#         """Initialize OCR processor with directory paths."""
#         self.upload_dir = upload_dir
#         self.pages_dir = pages_dir
#         self.sample_text_dir = sample_text_dir
#         self.structured_text_dir = structured_text_dir
        
#         # Path for Google Vision API credentials file
#         self.google_vision_json_path = 'google-vision-credentials.json'

#         # Create directories if they don't exist
#         for directory in [upload_dir, pages_dir, sample_text_dir, structured_text_dir]:
#             os.makedirs(directory, exist_ok=True)
        
#         # Initialize the Google Vision API client
#         try:
#             self.client = vision.ImageAnnotatorClient.from_service_account_json(self.google_vision_json_path)
#             logger.info("Google Vision API client initialized successfully")
#         except Exception as e:
#             logger.error(f"Error initializing Google Vision API client: {e}")
#             raise


#     def convert_pdf_to_images(self, pdf_path, dpi=200):
#         """
#         Convert PDF to images and save them to the pages directory.
        
#         Args:
#             pdf_path: Path to the PDF file
#             dpi: DPI for the converted images
            
#         Returns:
#             List of image paths
#         """
#         logger.info(f"Converting PDF: {pdf_path} to images...")
        
#         # Create base filename from original PDF name
#         base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        
#         # Convert PDF to images
#         images = convert_from_path(pdf_path, dpi=dpi)
#         image_paths = []
        
#         # Save each image
#         for i, image in enumerate(images):
#             image_path = os.path.join(self.pages_dir, f"{base_filename}_page_{i + 1}.png")
#             image.save(image_path, 'PNG')
#             image_paths.append(image_path)
            
#         logger.info(f"Generated {len(image_paths)} images from PDF")
#         return image_paths

#     def extract_text_from_image(self, image_path):
#         """
#         Extract text from an image using Google Vision API.
        
#         Args:
#             image_path: Path to the image file
            
#         Returns:
#             Extracted text as a string
#         """
#         with io.open(image_path, 'rb') as image_file:
#             content = image_file.read()
            
#         image = vision.Image(content=content)
#         response = self.client.document_text_detection(image=image)
        
#         if response.error.message:
#             logger.error(f"Error in OCR for {image_path}: {response.error.message}")
#             raise Exception(f"Error in OCR: {response.error.message}")
            
#         return response.full_text_annotation.text

#     def process_pdf(self, pdf_path):
#         """
#         Process a PDF file with OCR and save the results.
        
#         Args:
#             pdf_path: Path to the PDF file
            
#         Returns:
#             Tuple of (json_path, txt_path) with paths to the output files
#         """
#         # Get base filename for output files
#         base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        
#         # Define output paths
#         json_path = os.path.join(self.structured_text_dir, f"{base_filename}.json")
#         txt_path = os.path.join(self.sample_text_dir, f"{base_filename}.txt")
        
#         # Convert PDF to images
#         image_paths = self.convert_pdf_to_images(pdf_path)
        
#         # Extract text from all images
#         simplified_json = {}
#         all_text = ""
        
#         logger.info("Processing images with OCR...")
#         for i, image_path in enumerate(image_paths):
#             logger.info(f"Processing page {i+1}...")
#             page_text = self.extract_text_from_image(image_path)
#             simplified_json[f"page_{i+1}"] = page_text
#             all_text += f"\n\n=== PAGE {i+1} ===\n\n" + page_text
        
#         # Save the simplified JSON
#         with open(json_path, 'w', encoding='utf-8') as json_file:
#             json.dump(simplified_json, json_file, indent=2, ensure_ascii=False)
        
#         # Save the full text
#         with open(txt_path, 'w', encoding='utf-8') as text_file:
#             text_file.write(all_text)
        
#         logger.info(f"OCR processing complete: JSON saved to {json_path}, text saved to {txt_path}")
#         return json_path, txt_path

# import os
# import io
# import json
# import logging
# from pdf2image import convert_from_path
# from google.cloud import vision

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# class OCRProcessor:
#     def __init__(self, upload_dir='Uploads', pages_dir='Pages', sample_text_dir='Sample Text', structured_text_dir='Structured Text'):
#         """Initialize OCR processor with directory paths."""
#         self.upload_dir = upload_dir
#         self.pages_dir = pages_dir
#         self.sample_text_dir = sample_text_dir
#         self.structured_text_dir = structured_text_dir
        
#         # Path for Google Vision API credentials file
#         self.google_vision_json_path = 'google-vision-credentials.json'

#         # Create directories if they don't exist
#         for directory in [upload_dir, pages_dir, sample_text_dir, structured_text_dir]:
#             os.makedirs(directory, exist_ok=True)
        
#         # Initialize the Google Vision API client
#         try:
#             self.client = vision.ImageAnnotatorClient.from_service_account_json(self.google_vision_json_path)
#             logger.info("Google Vision API client initialized successfully")
#         except Exception as e:
#             logger.error(f"Error initializing Google Vision API client: {e}")
#             raise

#     def convert_pdf_to_images(self, pdf_path, dpi=200):
#         """
#         Convert PDF to images and save them to the pages directory.

#         Args:
#             pdf_path: Path to the PDF file
#             dpi: DPI for the converted images

#         Returns:
#             List of image paths
#         """
#         logger.info(f"Converting PDF: {pdf_path} to images...")
        
#         base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        
#         try:
#             images = convert_from_path(pdf_path, dpi=dpi)
#         except Exception as e:
#             logger.error(f"Failed to convert PDF to images: {e}")
#             raise Exception(f"PDF to image conversion failed: {e}")

#         image_paths = []

#         for i, image in enumerate(images):
#             image_path = os.path.join(self.pages_dir, f"{base_filename}_page_{i + 1}.png")
#             image.save(image_path, 'PNG')
#             image_paths.append(image_path)
            
#         logger.info(f"Generated {len(image_paths)} images from PDF")
#         return image_paths

#     def extract_text_from_image(self, image_path):
#         """
#         Extract text from an image using Google Vision API.

#         Args:
#             image_path: Path to the image file

#         Returns:
#             Extracted text as a string
#         """
#         with io.open(image_path, 'rb') as image_file:
#             content = image_file.read()

#         image = vision.Image(content=content)
#         response = self.client.document_text_detection(image=image)

#         if response.error.message:
#             logger.error(f"Error in OCR for {image_path}: {response.error.message}")
#             raise Exception(f"OCR error: {response.error.message}")

#         return response.full_text_annotation.text

#     def process_pdf(self, pdf_path):
#         """
#         Process a PDF file with OCR and save the results.

#         Args:
#             pdf_path: Path to the PDF file

#         Returns:
#             Tuple of (json_path, txt_path) with paths to the output files
#         """
#         base_filename = os.path.splitext(os.path.basename(pdf_path))[0]

#         json_path = os.path.join(self.structured_text_dir, f"{base_filename}.json")
#         txt_path = os.path.join(self.sample_text_dir, f"{base_filename}.txt")

#         image_paths = self.convert_pdf_to_images(pdf_path)

#         simplified_json = {}
#         all_text = ""

#         logger.info("Processing images with OCR...")
#         for i, image_path in enumerate(image_paths):
#             logger.info(f"Processing page {i + 1}...")
#             try:
#                 page_text = self.extract_text_from_image(image_path)
#                 simplified_json[f"page_{i + 1}"] = {
#                     "text": page_text,
#                     "page_number": i + 1
#                 }
#                 all_text += f"\n\n=== PAGE {i + 1} ===\n\n{page_text}"
#             except Exception as e:
#                 logger.error(f"Failed OCR extraction on page {i + 1}: {e}")
#                 simplified_json[f"page_{i + 1}"] = {
#                     "text": "",
#                     "page_number": i + 1,
#                     "error": str(e)
#                 }

#         with open(json_path, 'w', encoding='utf-8') as json_file:
#             json.dump(simplified_json, json_file, indent=2, ensure_ascii=False)

#         with open(txt_path, 'w', encoding='utf-8') as text_file:
#             text_file.write(all_text)

#         logger.info(f"OCR processing complete: JSON saved to {json_path}, text saved to {txt_path}")
#         return json_path, txt_path

import os
import io
import json
import logging
from pdf2image import convert_from_path
from google.cloud import vision

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OCRProcessor:
    def __init__(self, upload_dir='Uploads', pages_dir='Pages', sample_text_dir='Sample Text', structured_text_dir='Structured Text'):
        """Initialize OCR processor with directory paths."""
        self.upload_dir = upload_dir
        self.pages_dir = pages_dir
        self.sample_text_dir = sample_text_dir
        self.structured_text_dir = structured_text_dir
        
        # Path for Google Vision API credentials file
        self.google_vision_json_path = 'google-vision-credentials.json'

        # Create directories if they don't exist
        for directory in [upload_dir, pages_dir, sample_text_dir, structured_text_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Initialize the Google Vision API client
        try:
            self.client = vision.ImageAnnotatorClient.from_service_account_json(self.google_vision_json_path)
            logger.info("Google Vision API client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Google Vision API client: {e}")
            raise

    def convert_pdf_to_images(self, pdf_path, dpi=200):
        """
        Convert PDF to images and save them to the pages directory.

        Args:
            pdf_path: Path to the PDF file
            dpi: DPI for the converted images

        Returns:
            List of image paths
        """
        logger.info(f"Converting PDF: {pdf_path} to images...")
        
        base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # Check if images already exist
        existing_images = [f for f in os.listdir(self.pages_dir) if f.startswith(f"{base_filename}_page_")]
        if existing_images:
            logger.info(f"Found {len(existing_images)} existing images for {base_filename}, reusing them")
            return [os.path.join(self.pages_dir, img) for img in sorted(existing_images)]
        
        try:
            images = convert_from_path(pdf_path, dpi=dpi)
        except Exception as e:
            logger.error(f"Failed to convert PDF to images: {e}")
            raise Exception(f"PDF to image conversion failed: {e}")

        image_paths = []

        for i, image in enumerate(images):
            image_path = os.path.join(self.pages_dir, f"{base_filename}_page_{i + 1}.png")
            image.save(image_path, 'PNG')
            image_paths.append(image_path)
            
        logger.info(f"Generated {len(image_paths)} images from PDF")
        return image_paths

    def extract_text_from_image(self, image_path):
        """
        Extract text from an image using Google Vision API.

        Args:
            image_path: Path to the image file

        Returns:
            Extracted text as a string
        """
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = self.client.document_text_detection(image=image)

        if response.error.message:
            logger.error(f"Error in OCR for {image_path}: {response.error.message}")
            raise Exception(f"OCR error: {response.error.message}")

        return response.full_text_annotation.text

    def process_pdf(self, pdf_path):
        """
        Process a PDF file with OCR and save the results.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Tuple of (json_path, txt_path) with paths to the output files
        """
        base_filename = os.path.splitext(os.path.basename(pdf_path))[0]

        json_path = os.path.join(self.structured_text_dir, f"{base_filename}.json")
        txt_path = os.path.join(self.sample_text_dir, f"{base_filename}.txt")
        
        # Check if the output files already exist
        if os.path.exists(json_path) and os.path.exists(txt_path):
            logger.info(f"Output files already exist for {base_filename}, reusing them")
            return json_path, txt_path

        image_paths = self.convert_pdf_to_images(pdf_path)

        simplified_json = {}
        all_text = ""

        logger.info("Processing images with OCR...")
        for i, image_path in enumerate(image_paths):
            logger.info(f"Processing page {i + 1}...")
            try:
                page_text = self.extract_text_from_image(image_path)
                simplified_json[f"page_{i + 1}"] = {
                    "text": page_text,
                    "page_number": i + 1
                }
                all_text += f"\n\n=== PAGE {i + 1} ===\n\n{page_text}"
            except Exception as e:
                logger.error(f"Failed OCR extraction on page {i + 1}: {e}")
                simplified_json[f"page_{i + 1}"] = {
                    "text": "",
                    "page_number": i + 1,
                    "error": str(e)
                }

        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(simplified_json, json_file, indent=2, ensure_ascii=False)

        with open(txt_path, 'w', encoding='utf-8') as text_file:
            text_file.write(all_text)

        logger.info(f"OCR processing complete: JSON saved to {json_path}, text saved to {txt_path}")
        return json_path, txt_path