import pytesseract
import fitz
import docx
from pdf2image import convert_from_path
import re
import json
import os
import openai


# Set your OpenAI API key here
openai.api_key = "your_api_key"

# Data to store extracted text
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

# Function to send text to OpenAI's GPT model and extract structured information
def openai_request(text):
    """Sends a string text to OpenAI's GPT chat model and returns the response."""
    try:
        prompt = f"""
        I have a resume in text format. Please extract and organize the information into the following categories:
        
        Personal Information: Full Name, Email, Phone Number, LinkedIn, GitHub, or any other contact details
        Education History: Degree, Major, University, Years Attended
        Work Experience: Job Title, Company, Start & End Dates, Key Responsibilities & Achievements
        Skills: List of technical and soft skills mentioned
        Projects: Project Name, Description, Technologies Used
        Certifications: Name of Certification, Issuing Organization, Year
        
        If any category is missing from the resume, note it as 'Not Provided'.
        Ensure the extracted details are structured and concise. Format the response clearly.
        
        Here is the resume data:
        
        {text}
        """
        
        # Making the API request to OpenAI using GPT chat model (GPT-3.5 or GPT-4)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Switch to gpt-3.5-turbo or gpt-4 based on your access
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,  # Adjust max tokens depending on resume length
            temperature=0.5  # Adjust temperature for response randomness
        )
        
        return response['choices'][0]['message']['content'].strip()

    except Exception as e:
        print("Error:", e)
        return None

# Processing all files in the 'CVs' folder
for files in os.listdir("CVs"):
    if files.endswith(".pdf") or files.endswith(".docx"):
        process_resume(f"CVs/{files}")

# Call OpenAI's model for extracting structured information
response = openai_request(data[0])  # Assuming you have at least one resume in 'data'

# Save response to a file
if response:
    with open("Response0.json", "w", encoding="utf-8") as f:
        json.dump({"response": response}, f, ensure_ascii=False, indent=4)
    print("Response saved to Response0.json")
else:
    print("Failed to generate response.")
