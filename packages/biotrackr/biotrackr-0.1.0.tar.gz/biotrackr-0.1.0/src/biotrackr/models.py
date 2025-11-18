from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Text, func, Table, ForeignKey, Column


class Base(DeclarativeBase):
    pass


class BiocRelease(Base):
    __tablename__ = "bioc_release"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[str] = mapped_column(String, nullable=False)
    release_date: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    added_on = mapped_column(DateTime, server_default=func.now(), nullable=False)
    notes_url: Mapped[str] = mapped_column(String, nullable=False)


class GithubRepo(Base):
    __tablename__ = "github"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    tag: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String, nullable=False)
    published_on: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    added_on = mapped_column(DateTime, server_default=func.now(), nullable=False)


paper_keywords = Table(
    "paper_keywords",
    Base.metadata,
    Column("paper_id", ForeignKey("papers.id"), primary_key=True),
    Column("keyword_id", ForeignKey("keywords.id"), primary_key=True),
)


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pmid: Mapped[str] = mapped_column(Text, unique=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    doi: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    published_on: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    added_on = mapped_column(DateTime, server_default=func.now(), nullable=False)

    keywords = relationship("Keyword", secondary=paper_keywords, back_populates="papers")


class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(20), nullable=True)  # hex or named color
    added_on = mapped_column(DateTime, server_default=func.now(), nullable=False)

    papers = relationship("Paper", secondary=paper_keywords, back_populates="keywords")

