from pathlib import Path
from platformdirs import user_data_dir
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

APP_NAME = "biotrackr"

def get_db_path(config: dict) -> Path:
    db_path = config.get("database", {}).get("path")
    if db_path:
        return Path(db_path).expanduser()
    return Path(user_data_dir(APP_NAME)) / "biotrackr.db"

def init_db(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

