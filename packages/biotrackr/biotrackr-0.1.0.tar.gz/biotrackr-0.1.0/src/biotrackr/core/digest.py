import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import select, func
from biotrackr.models import Paper, GithubRepo, BiocRelease  # adjust imports
from sqlalchemy.orm import selectinload

def generate_digest(session, output_file="report.html"):
    """
    Generate a digest HTML report using only entries added today.
    """
    today = datetime.date.today()

    def fetch_table(model, columns):
        stmt = select(model).where(func.date(model.added_on) == today)

        # Special case for Paper to load keywords eagerly
        if model is Paper:
            stmt = stmt.options(selectinload(Paper.keywords))

        rows = session.execute(stmt).scalars().all()

        result = []
        for row in rows:
            row_dict = {col: getattr(row, col) for col in columns}

            # For papers, also add the keywords
            if model is Paper:
                row_dict['keywords'] = [
                    {"name": kw.name, "color": kw.color} for kw in row.keywords
                ]

            result.append(row_dict)
        return result

    data = {
        "date": today.isoformat(),
        "papers": fetch_table(Paper, ["title", "doi", "published_on", "url"]),
        "github_releases": fetch_table(GithubRepo, ["name", "tag", "url"]),
        "bioc_releases": fetch_table(BiocRelease, ["version", "release_date", "notes_url"]),
    }

    TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("report.html.j2")

    html = template.render(**data)

    report_path = Path(output_file)
    report_path.write_text(html, encoding="utf-8")
    print(f"✅ Digest generated: {report_path}")

