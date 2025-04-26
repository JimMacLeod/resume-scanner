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
    start_index = -1

    # Find where EDUCATION section starts
    for i, line in enumerate(lines):
        if "EDUCATION" in line.upper():
            start_index = i
            break

    if start_index == -1:
        return education

    # Look for lines after EDUCATION
    stop_words = ["SKILLS", "EXPERIENCE", "PROFESSIONAL EXPERIENCE", "SUMMARY", "CERTIFICATIONS"]
    for i in range(start_index + 1, len(lines) - 2):
        line_upper = lines[i].strip().upper()

        # Stop if we hit a new major section
        if any(stop in line_upper for stop in stop_words):
            break

        degree_line = lines[i].strip()
        school_line = lines[i+1].strip()
        extra_line = lines[i+2].strip()

        if degree_line and school_line:
            # Match degrees based on keywords
            if re.search(r"(BA|BS|MS|MA|MBA|PHD|BACHELOR|MASTER|CERTIFICATE)", degree_line.upper()):
                education.append({
                    "Degree": degree_line,
                    "School": school_line,
                    "Extra": extra_line
                })

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
