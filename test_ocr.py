
from cv.ocr import extract_text_from_image

from cv.parser import (
    clean_ocr_dimension_text,
    parse_tolerances_from_text,
    print_extracted_dimensions,
)

image_path = "data/test_image.jpg"

# ---------------------------------------------------
# OCR EXTRACTION
# ---------------------------------------------------
raw_text = extract_text_from_image(image_path)

print("\n================ RAW OCR TEXT ================\n")
print(raw_text)

# ---------------------------------------------------
# CLEAN OCR TEXT
# ---------------------------------------------------
cleaned_text = clean_ocr_dimension_text(raw_text)

print("\n================ CLEANED OCR TEXT ================\n")
print(cleaned_text)

# ---------------------------------------------------
# STRUCTURED EXTRACTION
# ---------------------------------------------------
df = parse_tolerances_from_text(
    cleaned_text,
    default_tolerance=0.1,
)

# ---------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------
print_extracted_dimensions(df)
