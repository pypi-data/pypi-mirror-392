import datetime
import requests
from sqlalchemy.exc import IntegrityError
from biotrackr.models import GithubRepo  # adjust import if needed


def fetch_github(session, repos, token=None, since_days=7):
    """
    Fetch recent GitHub releases for given repos and insert new ones into the DB.
    Works like fetch_bioconductor_release: checks existence before inserting.
    Returns the number of new releases added.
    """
    headers = {"Authorization": f"token {token}"} if token else {}
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=since_days)

    added_count = 0

    for repo in repos:
        url = f"https://api.github.com/repos/{repo}/releases"
        try:
            r = requests.get(url, headers=headers)
            r.raise_for_status()
        except Exception as e:
            print(f"⚠️ Failed to fetch {repo}: {e}")
            continue

        for rel in r.json():
            tag = rel.get("tag_name")
            if not tag:
                continue

            # Skip if already in DB
            exists = session.query(GithubRepo).filter_by(name=repo, tag=tag).first()
            if exists:
                continue

            # Published date
            published_at = rel.get("published_at")
            if not published_at:
                continue
            try:
                published = datetime.datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            except Exception:
                published = datetime.datetime.now(datetime.timezone.utc)

            if published < cutoff:
                continue

            # URL
            url_release = rel.get("html_url", "")

            # Insert
            new_release = GithubRepo(
                name=repo,
                tag=tag,
                published_on=published,
                url=url_release,
            )
            try:
                session.add(new_release)
                session.commit()
                added_count += 1
                print(f"🚀 New release: {repo} {tag} ({published.date()})")
            except IntegrityError:
                session.rollback()
                print(f"⚠️ Repo {repo} {tag} already exists (race condition?)")

    return added_count

