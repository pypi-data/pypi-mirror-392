import datetime
import requests
from biotrackr.models import Paper, Keyword
from sqlalchemy import insert, select, func
import random

def random_dark_color():
    """Return a hex color string that is dark enough for white text."""
    r = random.randint(0, 150)
    g = random.randint(0, 150)
    b = random.randint(0, 150)
    return f"#{r:02x}{g:02x}{b:02x}"

def fetch_papers(session, keywords, since_days=7):
    """Fetch new papers from Europe PMC based on keywords and store them in the database."""
    if not keywords:
        return
    base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    since_date = (datetime.date.today() - datetime.timedelta(days=since_days)).isoformat()
    before = session.scalar(select(func.count()).select_from(Paper))

    for kw in keywords:
        query = f"({kw}) AND FIRST_PDATE:[{since_date} TO *]"
        params = {"query": query, "format": "json", "pageSize": 25}
        resp = requests.get(base_url, params=params)
        resp.raise_for_status()
        results = resp.json().get("resultList", {}).get("result", [])
            
        # Get or create keyword
        keyword_obj = session.query(Keyword).filter_by(name=kw).first()
        if not keyword_obj:
            keyword_obj = Keyword(name=kw, color=random_dark_color())  # optionally assign random color
            session.add(keyword_obj)
            session.commit()

        for r in results:
            pub_date_str = r.get("firstPublicationDate")
            try:
                pub_date = datetime.datetime.strptime(pub_date_str, "%Y-%m-%d").date()
            except Exception:
                pub_date = None

            # check if paper exists
            paper = session.query(Paper).filter_by(doi=r.get("doi")).first()
            if paper:
                # update relationship if new keyword
                if keyword_obj not in paper.keywords:
                    paper.keywords.append(keyword_obj)
                    session.commit()
            else:
                # create new paper with keyword
                paper = Paper(
                        pmid= r["id"],
                        title=r["title"],
                        doi=r.get("doi"),
                        url=f"https://pubmed.ncbi.nlm.nih.gov/{r.get('pmid')}",
                        published_on=pub_date,
                        keywords=[keyword_obj],
                )
                session.add(paper)
                session.commit()

    after = session.scalar(select(func.count()).select_from(Paper))
    added = after - before
    print(f"📖 Added {added} new papers (ignored duplicates).")
