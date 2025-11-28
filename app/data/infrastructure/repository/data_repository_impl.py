from typing import List
from datetime import datetime

import json
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.data.application.port.data_repository_port import DataRepositoryPort
from app.data.domain.data import Data
from app.data.infrastructure.orm.data_orm import DataORM
from app.keywords.application.port.keyword_repository_port import KeywordRepositoryPort


class DataRepositoryImpl(DataRepositoryPort):
    def __init__(self, db_session: Session, keyword_repository: KeywordRepositoryPort):
        self.db = db_session
        self.keyword_repository = keyword_repository

    def get_recent(self, limit: int) -> List[Data]:
        query = (
            self.db.query(DataORM)
            .order_by(desc(DataORM.id))
            .limit(limit)
        )
        data_rows = query.all()

        results: List[Data] = []
        for row in data_rows:
            if row.keywords:
                try:
                    raw_keywords = json.loads(row.keywords)
                except json.JSONDecodeError:
                    raw_keywords = []
            else:
                raw_keywords = []

            resolved_keywords: List[str] = []
            for item in raw_keywords:
                if isinstance(item, int):
                    # id -> name 매핑
                    try:
                        keyword = self.keyword_repository.find_by_id(item)
                        resolved_keywords.append(keyword.name)
                    except ValueError:
                        # 존재하지 않는 id는 무시
                        continue
                elif isinstance(item, str):
                    # 예전 데이터(직접 이름 저장)는 그대로 사용
                    name = item.strip()
                    if name:
                        resolved_keywords.append(name)

            # published_at을 문자열로 변환 (datetime이면 ISO 형식으로)
            # published_at이 필수 필드이므로, NULL인 경우 빈 문자열로 처리
            if row.published_at:
                if isinstance(row.published_at, datetime):
                    published_at_str = row.published_at.isoformat()
                else:
                    published_at_str = str(row.published_at)
            else:
                # DB에 published_at이 NULL인 경우 기본값 제공
                published_at_str = ""

            data = Data(
                title=row.title,
                content=row.content,
                keywords=resolved_keywords,
                published_at=published_at_str,
            )
            data.id = row.id
            results.append(data)

        return results

    def save(self, data: Data) -> Data:
        keyword_ids: List[int] = []
        for name in data.keywords or []:
            name = name.strip()
            if not name:
                continue

            keyword = self.keyword_repository.get_or_create(name)
            if keyword.id is not None:
                keyword_ids.append(keyword.id)

        keywords_json = json.dumps(keyword_ids, ensure_ascii=False)

        # published_at 문자열을 datetime으로 변환
        published_at_dt = None
        if data.published_at:
            try:
                if isinstance(data.published_at, datetime):
                    published_at_dt = data.published_at
                elif isinstance(data.published_at, str):
                    # ISO 형식 문자열을 datetime으로 파싱
                    # 'Z'를 '+00:00'으로 변환
                    date_str = data.published_at.replace('Z', '+00:00')
                    # fromisoformat은 Python 3.7+에서 사용 가능
                    published_at_dt = datetime.fromisoformat(date_str)
            except (ValueError, AttributeError, TypeError):
                # 파싱 실패 시 None으로 저장
                published_at_dt = None

        orm_data = DataORM(
            title=data.title,
            content=data.content,
            keywords=keywords_json,
            published_at=published_at_dt,
        )
        self.db.add(orm_data)
        self.db.flush()  # ID를 얻기 위해 flush

        data.id = orm_data.id
        return data

