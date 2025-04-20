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

# Extract name, email, and phone number
def extract_contact_info(text):
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    email = email_match.group(0) if email_match else "Not found"

    phone_match = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    phone = phone_match.group(0) if phone_match else "Not found"

    lines = text.splitlines()
    possible_name = next((line.strip() for line in lines if line.strip() and "@" not in line), "Not found")

    return {
        "Name": possible_name,
        "Email": email,
        "Phone": phone
    }

# Extract skills using keyword matching
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

# Experience extraction
def extract_experience_entries(text):
    lines = text.splitlines()
    experience = []

    date_pattern = re.compile(
        r"\d{2}/\d{2}\s*(?:–|-|to)\s*(\d{2}/\d{2}|Present|Current)", re.IGNORECASE
    )

    for i in range(len(lines)):
        line = lines[i].strip()
        match = date_pattern.search(line)

        if match:
            date_range = match.group(0)
            title = lines[i - 3].strip() if i - 3 >= 0 else ""
            company = lines[i - 2].strip() if i - 2 >= 0 else ""

            experience.append({
                "Title": title,
                "Company": company,
                "Dates": date_range
            })

    return experience

# Education extraction
def extract_education_entries(text):
    lines = text.splitlines()
    education = []

    degree_keywords = [
        "ba", "bs", "ma", "ms", "mba", "phd", "mfa", "bfa", "jd", "associate",
        "bachelor", "master", "doctor", "certificate", "diploma"
    ]

    def looks_like_degree(line):
        line_clean = line.strip().lower()
        return any(re.match(rf"^{keyword}\b", line_clean) for keyword in degree_keywords)

    education_index = next(
        (i for i, line in enumerate(lines) if line.strip().lower() == "education"),
        None
    )

    if education_index is not None:
        for i in range(education_index + 1, education_index + 11):
            if i >= len(lines):
                break
            line = lines[i].strip()

            if line.startswith("•"):
                continue

            if looks_like_degree(line):
                degree = line
                school = lines[i - 1].strip() if i - 1 >= 0 else ""
                extra = lines[i + 1].strip() if i + 1 < len(lines) else ""
                education.append({
                    "School": school,
                    "Degree": degree,
                    "Extra": extra
                })

    return education

# Resume parser returns structured data
def parse_resume(file_path):
    if not os.path.exists(file_path):
        print("File not found:", file_path)
        return

    if file_path.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        print("Unsupported file type.")
        return

    contact_info = extract_contact_info(text)
    skills = extract_skills(text)
    experience = extract_experience_entries(text)
    education = extract_education_entries(text)

    result_data = {
        "contact": contact_info,
        "skills": skills,
        "experience": experience,
        "education": education
    }

    return result_data

# Render HTML from parsed data
def render_html_from_parsed_data(data):
    html = ""

    html += "<h2>Contact Info</h2>\n<ul>"
    for label, value in data["contact"].items():
        html += f"<li><strong>{label}:</strong> {value}</li>"
    html += "</ul>\n"

    html += "<h2>Skills</h2>\n<ul>"
    for skill in data["skills"]:
        html += f"<li>{skill}</li>"
    html += "</ul>\n"

    html += "<h2>Experience</h2>\n<ul>"
    for entry in data["experience"]:
        html += f"<li><strong>{entry['Title']}</strong> at {entry['Company']} ({entry['Dates']})</li>"
    html += "</ul>\n"

    html += "<h2>Education</h2>\n<ul>"
    for entry in data["education"]:
        html += f"<li><strong>{entry['Degree']}</strong> at {entry['School']} ({entry['Extra']})</li>"
    html += "</ul>\n"

    return html

# === Run the parser ===
resume_file = "Jim-MacLeod-test.pdf"
print(f"Trying to parse: {resume_file}")
parsed_data = parse_resume(resume_file)

# Output as JSON
print("\n--- Parsed Resume (JSON Format) ---")
print(json.dumps(parsed_data, indent=2))

# Output as HTML
html_output = render_html_from_parsed_data(parsed_data)
print("\n--- Parsed Resume (HTML Format) ---")
print(html_output)