import pytesseract
import fitz
import docx
from pdf2image import convert_from_path
import re
import json
import os

data = []

# Clean up the text by removing unwanted spaces and newlines
def clean_text(text):
    # Replace special characters
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s\n.@]', '', text)
    
    # Replace multiple spaces with a single space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    return cleaned_text

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    
    if not text.strip():
        images = convert_from_path(pdf_path)
        for img in images:
            text += pytesseract.image_to_string(img)
    
    return clean_text(text)

# Function to extract text from DOCX
def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return clean_text(text)

# Main function to process PDF or DOCX file
def process_resume(file_path):
    if file_path.endswith('.pdf'):
        data.append(extract_text_from_pdf(file_path))
    elif file_path.endswith('.docx'):
        data.append(extract_text_from_docx(file_path))
    else:
        raise ValueError("Only PDF and DOCX files are supported")

# Processing all files
for files in os.listdir("CVs"):
    if files.endswith(".pdf") or files.endswith(".docx"):
        json_output_path = process_resume(f"CVs/{files}")