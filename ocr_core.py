try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from pytesseract import Output

def ocr_core(filename):
    """
    This function will handle the core OCR processing of images.
    """
    text = pytesseract.image_to_string(Image.open(filename))  # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
    return text

def ocr_hocr(filename):
    """
    This function will handle the core OCR processing of images and return hocr content in dictionary.
    """
    data = pytesseract.image_to_data(Image.open(filename), output_type=Output.DICT, lang='eng', config="--psm 4 -c tessedit_create_hocr=1")
    return data

#print(ocr_core('/home/shrinivas/Nitin.Desai/ocr/app/demo_images/demo5.jpg'))

