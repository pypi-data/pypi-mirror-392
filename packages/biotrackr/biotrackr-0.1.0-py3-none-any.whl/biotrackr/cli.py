"""
fetch_papers(cfg["keywords"])
fetch_bioconductor_release()
fetch_github_releases(cfg["github_repos"], token=None)  # Add GH token if rate-limited
generate_digest()
"""

import argparse
from pathlib import Path
from .config import load_config
from .database import get_db_path, init_db, get_session
from .core import *

def main():
    parser = argparse.ArgumentParser(prog="biotrackr", description="BioTrackr CLI")
    parser.add_argument("--config", type=str, help="Path to a custom config file")
    parser.add_argument("--since_days", type=int, help="Number of days back for fetching papers")
    parser.add_argument("-o", "--output", type=str, help="Output HTML file for the digest")
    parser.add_argument("--no-fetch", action="store_true", help="Skip fetching and just generate the digest")
    args = parser.parse_args()

    # Load config
    config = load_config(Path(args.config) if args.config else None)

    # Setup DB
    db_path = get_db_path(config)
    engine = init_db(db_path)
    session = get_session(engine)

    # Determine since_days (argument overrides config, default 7)
    since_days = args.since_days or config.get("since_days", 7)

    if not args.no_fetch:
        fetch_bioconductor_release(session)

        keywords = config.get("keywords", [])
        if keywords:
            fetch_papers(session, keywords, since_days=since_days)

        github_repos = config.get("github_repos", [])
        if github_repos:
            fetch_github(session, github_repos)

    # Determine output file (default: report.html)
    output_file = args.output or config.get("output_file") or "report.html"
    generate_digest(session, output_file=output_file)

if __name__ == "__main__":
    main()

