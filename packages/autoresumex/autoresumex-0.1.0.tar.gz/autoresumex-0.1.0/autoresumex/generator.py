import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .utils import validate_profile, normalize_profile

try:
    from weasyprint import HTML
    WEASY = True
except Exception:
    WEASY = False

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"])
)

def _render_html(profile: dict, template_name: str) -> str:
    tpl = env.get_template(f"{template_name}.html")
    return tpl.render(profile=profile)

def _save_pdf(html: str, out_path: str):
    if not WEASY:
        raise RuntimeError("WeasyPrint not installed.")
    HTML(string=html).write_pdf(out_path)

def _save_md(profile: dict, out_path: str):
    lines = [
        f"# {profile['name']}",
        f"**Contact:** {profile['contact']}",
        "\n"
    ]

    if profile.get("skills"):
        lines.append("## Skills")
        for s in profile["skills"]:
            lines.append(f"- {s}")

    if profile.get("projects"):
        lines.append("\n## Projects")
        for p in profile["projects"]:
            lines.append(f"### {p['title']}")
            lines.append(p["description"])

    md = "\n".join(lines)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)

def generate(profile: dict, template: str = "ats_basic", save: str = "resume.pdf", export_md: bool = False):
    validate_profile(profile)
    profile = normalize_profile(profile)

    html = _render_html(profile, template)

    ext = os.path.splitext(save)[1].lower()
    if ext == ".pdf":
        _save_pdf(html, save)
    elif ext == ".html":
        with open(save, "w", encoding="utf-8") as f:
            f.write(html)
    else:
        _save_pdf(html, save)

    if export_md:
        md_path = os.path.splitext(save)[0] + ".md"
        _save_md(profile, md_path)

    return save
