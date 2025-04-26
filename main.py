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
def extract_experience_entries(text):
    lines = text.splitlines()
    experience = []
    for i, line in enumerate(lines):
        date_match = re.search(r"(\d{2}/\d{2})\s+[\u2013–-]\s+(Present|\d{2}/\d{2})", line)
        if date_match:
            # Look at the 2-3 lines above for title and company
            title = ""
            company = ""
            search_back = 1
            while i - search_back >= 0 and not title:
                candidate = lines[i - search_back].strip()
                if candidate and not candidate.startswith(("•", "-", "*")):
                    title = candidate
                search_back += 1
            search_back += 1
            while i - search_back >= 0 and not company:
                candidate = lines[i - search_back].strip()
                if candidate and not candidate.startswith(("•", "-", "*")):
                    company = candidate
                search_back += 1

            experience.append({
                "Title": title,
                "Company": company,
                "Dates": date_match.group(0)
            })
    return experience

# Extract education entries
def extract_education_entries(text):
    lines = text.splitlines()
    education = []
    start_index = -1

    # Find the EDUCATION section
    for i, line in enumerate(lines):
        if "EDUCATION" in line.upper():
            start_index = i
            break
    if start_index == -1:
        return education

    # Start scanning after EDUCATION
    degree_keywords = ["BA", "BS", "MA", "MS", "MBA", "PhD", "Associate", "Bachelor", "Master", "Doctorate"]
    end_section_keywords = ["SKILLS", "CORE STRENGTHS", "EXPERIENCE", "PUBLICATIONS"]

    for i in range(start_index + 1, len(lines)):
        current = lines[i].strip()

        if not current:
            continue  # Skip blank lines

        if any(end in current.upper() for end in end_section_keywords):
            break  # Stop when hitting next major section

        if any(degree in current for degree in degree_keywords):
            # Assume degree + school = 2 lines
            degree = current
            school = lines[i - 1].strip() if i - 1 >= 0 else ""
            extra = lines[i + 1].strip() if i + 1 < len(lines) else ""
            education.append({
                "Degree": degree,
                "School": school,
                "Extra": extra
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
