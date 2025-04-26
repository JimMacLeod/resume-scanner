import os
import fitz  # PyMuPDF
import docx
import re
import json

# Extract text from PDF
def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as pdf:
        for page_number, page in enumerate(pdf):
            page_text = page.get_text()
            text += page_text
    return text

# Extract text from DOCX
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Extract contact info (name, email, phone)
def extract_contact_info(text):
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    phone_match = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    lines = text.splitlines()
    possible_name = next((line.strip() for line in lines if line.strip() and "@" not in line), "Not found")

    return {
        "Name": possible_name,
        "Email": email_match.group(0) if email_match else "Not found",
        "Phone": phone_match.group(0) if phone_match else "Not found"
    }

# Extract skills
def extract_skills(text):
    skill_keywords = [
        "Python", "Java", "JavaScript", "HTML", "CSS", "SQL", "Excel",
        "Canva", "Photoshop", "Illustrator", "Figma", "PowerPoint",
        "Marketing", "SEO", "Content", "CRM", "Analytics", "Google Analytics",
        "Project Management", "WordPress", "AI", "ChatGPT", "Copywriting"
    ]
    found_skills = set()
    for skill in skill_keywords:
        if skill.lower() in text.lower():
            found_skills.add(skill)
    return sorted(found_skills)

# Extract experience entries
import re

# Updated: Extract experience entries
def extract_experience_entries(text):
    lines = text.splitlines()
    experience = []
    date_pattern = re.compile(r"(\d{2}/\d{2}|\w+\s\d{4}|\d{4})\s*[–-]\s*(\d{2}/\d{2}|\w+\s\d{4}|Present|\d{4})", re.IGNORECASE)

    for i in range(len(lines)):
        line = lines[i].strip()
        if date_pattern.search(line):
            # Try to get previous 1-2 lines for Title and Company
            title = lines[i-2].strip() if i >= 2 else ""
            company = lines[i-1].strip() if i >= 1 else ""

            # Simple filters to avoid nonsense (empty strings, random bullets)
            if title and len(title) < 100 and not title.startswith("•"):
                experience.append({
                    "Title": title,
                    "Company": company,
                    "Dates": line
                })

    return experience

# Updated: Extract education entries
def extract_education_entries(text):
    lines = text.splitlines()
    education = []
    capturing = False

    education_keywords = ["education", "academic", "university", "college", "school", "degree", "bachelor", "master", "phd", "mba", "certificate", "certification", "associates"]
    stop_keywords = ["experience", "skills", "projects", "certifications", "summary", "work history"]

    for line in lines:
        line_lower = line.lower().strip()

        if any(keyword in line_lower for keyword in education_keywords):
            capturing = True
            continue  # Skip the actual header line

        if capturing:
            if any(stop_keyword in line_lower for stop_keyword in stop_keywords):
                break  # Stop capturing if a stop word is found
            if line.strip():  # Only add non-empty lines
                education.append(line.strip())

    return education


# Main parser
def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
def parse_resume(file_path):
    if not os.path.exists(file_path):
        return None

    if file_path.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        text = extract_text_from_docx(file_path)
    elif file_path.lower().endswith(".txt"):
        text = extract_text_from_txt(file_path)
    else:
        return None

    return {
        "contact": extract_contact_info(text),
        "skills": extract_skills(text),
        "experience": extract_experience_entries(text),
        "education": extract_education_entries(text),
    }    

# Render resume data to HTML
def render_html_from_parsed_data(data):
    html = ""
    html += "<h3>Contact Info</h3><ul>"
    for label, value in data["contact"].items():
        html += f"<li><strong>{label}:</strong> {value}</li>"
    html += "</ul>"

    html += "<h3>Skills</h3><ul>"
    for skill in data["skills"]:
        html += f"<li>{skill}</li>"
    html += "</ul>"

    html += "<h3>Experience</h3><ul>"
    for exp in data["experience"]:
        html += f"<li>{exp['Title']} at {exp['Company']} ({exp['Dates']})</li>"
    html += "</ul>"

    html += "<h3>Education</h3><ul>"
    for edu in data["education"]:
        html += f"<li>{edu['Degree']} at {edu['School']} ({edu['Extra']})</li>"
    html += "</ul>"

    return html
