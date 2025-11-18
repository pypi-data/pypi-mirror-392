import requests
import datetime
from sqlalchemy.exc import IntegrityError

from biotrackr.models import BiocRelease


def fetch_bioconductor_release(session):
    """Check if a new Bioconductor release has appeared since last check."""
    url = "https://bioconductor.org/config.yaml"
    r = requests.get(url)
    r.raise_for_status()
    lines = r.text.splitlines()

    # 1. Find current release version
    version = None
    for line in lines:
        if "release_version:" in line:
            version = line.split(":")[1].strip().strip("'\"")
            break
    if not version:
        print("⚠️ Could not find release_version in Bioconductor config.")
        return

    # 2. Insert into DB if not already present
    exists = session.query(BiocRelease).filter_by(version=version).first()
    if exists:
        print(f"✅ Bioconductor is still at {version}")
        session.close()
        return

    # 3. Extract release date from the `release_dates:` section
    release_date = None
    in_release_dates = False
    for line in lines:
        if line.strip().startswith("release_dates:"):
            in_release_dates = True
            continue
        if in_release_dates:
            # section ends when indentation ends or blank line
            if not line.startswith("  ") or not line.strip():
                break
            if line.strip().startswith(f'"{version}"'):
                release_date = line.split(":", 1)[1].strip().strip('"')
                break

    # 4. Normalize release_date
    try:
        release_date = datetime.datetime.strptime(release_date, "%m/%d/%Y").date()
    except Exception:
        release_date = datetime.date.today()

    # 5. Insert in db
    notes_url = f"https://bioconductor.org/news/bioc_{version.replace('.', '_')}_release.html"
    new_release = BiocRelease(
        version=version,
        release_date=release_date,
        notes_url=notes_url,
        added_on=datetime.datetime.now()
    )

    try:
        session.add(new_release)
        session.commit()
        print(f"🧬 New Bioconductor release detected: {version} ({release_date})")
    except IntegrityError:
        session.rollback()
        print(f"⚠️ Release {version} already exists (race condition?)")
    finally:
        session.close()

