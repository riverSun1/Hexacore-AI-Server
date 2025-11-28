from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from config.database.session import Base


class DataORM(Base):
    __tablename__ = "datas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    # keywords = Column(Text, nullable=True)  # JSON 문자열로 키워드 목록 저장
    published_at = Column(DateTime, nullable=True)  # 발행일시

