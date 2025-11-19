# autoResumeX

autoResumeX is a Python library that automatically generates **ATS-friendly resumes** in **PDF** or **Markdown** format using Jinja2 templates.

Created and maintained by **Ganeshamoorthy**  
Email: **ganeshms1110@gmail.com**  
LinkedIn: **www.linkedin.com/in/ganeshamoorthy-s-8466b7332**

---

## 🚀 Features
- Auto-generate clean professional resumes
- ATS-friendly structure (simple HTML + text)
- Add unlimited skills, projects, experience, education
- Export:
  - ✅ PDF (via WeasyPrint)
  - ✅ Markdown
- Includes 2 resume templates:
  - `ats_basic`
  - `modern_clean`

---

## 📌 Installation

---

## 🧑‍💻 Usage Example
```python
from autoresumex import generate

profile = {
    "name": "Ganeshamoorthy",
    "contact": "ganeshms1110@gmail.com | www.linkedin.com/in/ganeshamoorthy-s-8466b7332",
    "skills": ["Python", "SQL", "Pandas"],
    "projects": [
        {"title": "autoResumeX", "description": "Resume generator library"},
        {"title": "Sales Dashboard", "description": "Automated dashboard using Python"}
    ]
}

generate(profile, template="ats_basic", save="resume.pdf")
