import pytesseract
import fitz
import docx
from pdf2image import convert_from_path
import re
import json
import os

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

# Regex patterns to match personal info (email, phone, name)
def extract_personal_information(text):
    personal_info = {
        "Name": "",
        "Email": "",
        "Phone": ""
    }

    # Extract name (looking for first and last name style)
    name_search = re.search(r"([A-Z][a-z]+ [A-Z][a-z]+)", text)
    if name_search:
        personal_info["Name"] = clean_text(name_search.group(1))

    # Extract email
    email_search = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+[a-zA-Z]{2,}", text)
    if email_search:
        personal_info["Email"] = clean_text(email_search.group(0))

    # Extract phone number (simple pattern for US phone numbers)
    phone_search = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    if phone_search:
        personal_info["Phone"] = clean_text(phone_search.group(0))

    return personal_info

# Function to extract sections
def extract_sections(text):
    sections = {
        "Personal Information": {},
        "Education History": "",
        "Work Experience": "",
        "Skills": "",
        "Projects": "",
        "Certifications": ""
    }

    # Extract Personal Information
    personal_info = extract_personal_information(text)
    sections["Personal Information"] = personal_info

    # Extract Education History (look for degree type and university)
    education_search = re.search(r"(Education|@)\s*(Bachelor|Master|Doctorate|Ph\.?D)[\w\s]+(?:in\s[\w\s]+)?\s*(University|College|Institute)[\w\s]+(?:\s\d{4})?", text, re.DOTALL)
    if education_search:
        sections["Education History"] = education_search.group(1)

    # Extract Work Experience (looking for "Work Experience" keyword)
    work_experience_search = re.search(r"(Work Experience.*?)(Skills|Projects|Certifications|$)", text, re.DOTALL)
    if work_experience_search:
        sections["Work Experience"] = work_experience_search.group(1)

    # Extract Skills section (looking for "Skills" keyword)
    skills_search = re.search(r"(Skills.*?)(Summary|Work Experience|Projects|Certifications|$)", text, re.DOTALL)
    if skills_search:
        sections["Skills"] = skills_search.group(1)

    # Extract Projects section
    projects_search = re.search(r"(Projects.*?)(Certifications|$)", text, re.DOTALL)
    if projects_search:
        sections["Projects"] = projects_search.group(1)

    # Extract Certifications section
    certifications_search = re.search(r"(Certifications.*?)(References|$)", text, re.DOTALL)
    if certifications_search:
        sections["Certifications"] = certifications_search.group(1)

    return sections

# Main function to process PDF or DOCX file
def process_resume(file_path):
    if file_path.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Only PDF and DOCX files are supported")
    
    #sections = extract_sections(text)
    
    # Save the extracted data into a JSON file
    json_file_path = file_path.split('.')[0] + '_extracted_data.json'
    with open(json_file_path, 'w') as json_file:
        json.dump(text, json_file, indent=4)

    return json_file_path  # Return the path to the saved JSON file

# Processing all files
for files in os.listdir("CVs"):
    if files.endswith(".pdf") or files.endswith(".docx"):
        json_output_path = process_resume(f"CVs/{files}")
        print(f"Processed {files} and saved extracted data to {json_output_path}")