from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text, ForeignKey, text, Float
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base, relationship, backref, Session
from app.core.config import settings

# Engine setup
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

Base = declarative_base()
Base.query = db_session.query_property()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Flask-SQLAlchemy compatibility bridge for untouched models
class DBBridge:
    Model = Base
    Column = Column
    String = String
    Integer = Integer
    Boolean = Boolean
    DateTime = DateTime
    Text = Text
    Float = Float
    ForeignKey = ForeignKey
    backref = backref
    text = text

    @staticmethod
    def relationship(*args, **kwargs):
        if "lazy" in kwargs and kwargs["lazy"] is True:
            kwargs["lazy"] = "select"
        elif "lazy" in kwargs and kwargs["lazy"] is False:
            kwargs["lazy"] = "joined"
        return relationship(*args, **kwargs)

    @property
    def session(self):
        return db_session

    def create_all(self):
        Base.metadata.create_all(bind=engine)

db = DBBridge()
