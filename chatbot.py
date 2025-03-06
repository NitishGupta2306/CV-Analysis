import json
import os
import spacy
from collections import defaultdict

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load all responses from JSON files
def load_responses():
    responses = []
    for file_name in os.listdir():
        if file_name.startswith("Response") and file_name.endswith(".json"):
            with open(file_name, "r", encoding="utf-8") as f:
                data = json.load(f)
                responses.append(data["response"])
    return responses

# Function to search for a specific keyword in the response
def search_data(query, response):
    query = query.lower()
    if "personal information" in query:
        return response.get("Personal Information", "Not Provided")
    elif "education history" in query:
        return response.get("Education History", "Not Provided")
    elif "work experience" in query:
        return response.get("Work Experience", "Not Provided")
    elif "skills" in query:
        return response.get("Skills", "Not Provided")
    elif "projects" in query:
        return response.get("Projects", "Not Provided")
    elif "certifications" in query:
        return response.get("Certifications", "Not Provided")
    else:
        return "Sorry, I couldn't find information related to your query."

# Function to analyze and understand user queries (NLU)
def analyze_query(query):
    # Process the query with spaCy
    doc = nlp(query)
    
    # Identify entities (like skills, job roles, industries)
    entities = {}
    for ent in doc.ents:
        if ent.label_ == "ORG":
            entities["organization"] = ent.text
        elif ent.label_ == "GPE":
            entities["location"] = ent.text
        elif ent.label_ == "WORK_OF_ART":
            entities["project"] = ent.text
    
    return entities, doc

# Context management to remember previous queries
class ContextManager:
    def __init__(self):
        self.context = defaultdict(str)  # Store context of user

    def update_context(self, key, value):
        self.context[key] = value
    
    def get_context(self, key):
        return self.context.get(key, None)

# Function to handle skills search
def find_candidates_with_skills(query, responses):
    skills = []
    for response in responses:
        skills_info = response.get("Skills", "Not Provided")
        if query.lower() in skills_info.lower():
            skills.append(skills_info)
    
    if skills:
        return "Candidates with the required skills:\n" + "\n".join(skills)
    else:
        return "No candidates found with those skills."

# Function to compare education levels
def compare_education_levels(query, responses):
    education_level = None
    for response in responses:
        education_info = response.get("Education History", "Not Provided")
        if query.lower() in education_info.lower():
            education_level = education_info
            break
    
    if education_level:
        return f"Education level: {education_level}"
    else:
        return "No information on the requested education level."

# Function to search for experience in specific industries
def search_experience_in_industry(query, responses):
    experience = []
    for response in responses:
        work_experience = response.get("Work Experience", "Not Provided")
        if query.lower() in work_experience.lower():
            experience.append(work_experience)
    
    if experience:
        return "Candidates with the required experience:\n" + "\n".join(experience)
    else:
        return "No candidates found with experience in this industry."

# Function to identify matching candidates based on job requirements
def identify_matching_candidates(query, responses):
    matching_candidates = []
    for response in responses:
        # Assuming job requirements contain key words like "experience", "skills", etc.
        skills = response.get("Skills", "Not Provided")
        education = response.get("Education History", "Not Provided")
        work_experience = response.get("Work Experience", "Not Provided")
        
        if any(skill.lower() in query.lower() for skill in skills.split(", ")) or \
           any(exp.lower() in query.lower() for exp in work_experience.split(", ")):
            matching_candidates.append(response)
    
    if matching_candidates:
        return f"Found {len(matching_candidates)} matching candidate(s)."
    else:
        return "No candidates match the given job requirements."

# Main function to handle chatbot interaction
def chatbot_interface():
    responses = load_responses()
    context_manager = ContextManager()

    print("Welcome to the Advanced Resume Chatbot!")
    print("You can ask about skills, education, work experience, or find candidates based on job requirements.")
    print("Type 'exit' to end the conversation.\n")

    while True:
        query = input("You: ").strip()

        if query.lower() == "exit":
            print("Goodbye!")
            break
        
        # Analyze the query to understand entities (like skills, industries, etc.)
        entities, doc = analyze_query(query)
        
        # Handle the different types of queries
        if "skills" in query.lower():
            result = find_candidates_with_skills(query, responses)
        elif "education" in query.lower():
            result = compare_education_levels(query, responses)
        elif "experience" in query.lower():
            result = search_experience_in_industry(query, responses)
        elif "job requirement" in query.lower():
            result = identify_matching_candidates(query, responses)
        else:
            result = "Sorry, I couldn't understand your query. Please ask about skills, education, or experience."

        print(f"Bot: {result}")

if __name__ == "__main__":
    chatbot_interface()
