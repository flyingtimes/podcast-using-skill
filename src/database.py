import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Essay(Base):
    __tablename__ = "essays"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    subtitle = Column(Text, nullable=True)
    author = Column(String(200), nullable=True)
    url = Column(Text, unique=True, nullable=False, index=True)
    content = Column(Text, nullable=True)
    entry_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self, database_url: str = None):
        if database_url is None:
            # 使用绝对路径确保数据库文件能被找到
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            db_path = os.path.join(parent_dir, "local_db", "essays.db")
            database_url = f"sqlite:///{db_path}"

        self.engine = create_engine(database_url, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.create_tables()

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        return self.SessionLocal()

    def essay_exists(self, url: str) -> bool:
        session = self.get_session()
        try:
            return session.query(Essay).filter(Essay.url == url).first() is not None
        finally:
            session.close()

    def add_essay(self, title: str, url: str, subtitle: str = None, author: str = None, content: str = None, entry_time: datetime = None) -> bool:
        if self.essay_exists(url):
            return False

        session = self.get_session()
        try:
            essay = Essay(
                title=title,
                subtitle=subtitle,
                author=author,
                url=url,
                content=content,
                entry_time=entry_time
            )
            session.add(essay)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_essay_content(self, url: str, content: str) -> bool:
        """更新文章内容"""
        session = self.get_session()
        try:
            essay = session.query(Essay).filter(Essay.url == url).first()
            if essay:
                essay.content = content
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_essay_by_url(self, url: str):
        """根据URL获取文章"""
        session = self.get_session()
        try:
            return session.query(Essay).filter(Essay.url == url).first()
        finally:
            session.close()