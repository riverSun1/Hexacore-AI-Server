from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crawling.Engine.CrawlingEngine import CrawlingEngine
from app.data.adapter.input.web.request.create_data_request import (
    CreateDataListRequest,
    CrawlingIngestRequest,
)
from app.data.adapter.input.web.response.data_response import DataResponse
from app.data.application.use_case.create_data_list import CreateDataList
from app.data.application.use_case.get_data_list import GetDataList
from app.data.infrastructure.repository.data_repository_impl import DataRepositoryImpl
from app.keywords.infrastructure.repository.keyword_repository_impl import (
    KeywordRepositoryImpl,
)
from config.database.session import get_db

data_router = APIRouter()


def _create_data_items(items: list[dict], db: Session) -> list[DataResponse]:
    try:
        keyword_repository = KeywordRepositoryImpl(db)
        data_repository = DataRepositoryImpl(db, keyword_repository)

        use_case = CreateDataList(data_repository)

        created_data_list = use_case.execute(items)

        db.commit()

        response_list = []
        for data in created_data_list:
            response_list.append(
                DataResponse(
                    id=data.id,
                    title=data.title,
                    content=data.content,
                    keywords=data.keywords,
                    published_at=data.published_at,
                )
            )

        return response_list

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데이터 생성 중 오류가 발생했습니다: {str(e)}",
        ) from e


@data_router.get("/", response_model=List[DataResponse])
def get_data(limit: int = 20, db: Session = Depends(get_db)):
    """
    최근 데이터 목록 조회
    """
    keyword_repository = KeywordRepositoryImpl(db)
    repository = DataRepositoryImpl(db, keyword_repository)
    use_case = GetDataList(repository)
    data_list = use_case.execute(limit=limit)

    return [
        DataResponse(
            id=data.id,
            title=data.title,
            content=data.content,
            keywords=data.keywords,
            published_at=data.published_at,
        )
        for data in data_list
    ]
@data_router.post("/dailylist", response_model=List[DataResponse])
async def daily_listup(limit: int = 20, db: Session = Depends(get_db)):

    keyword_repository = KeywordRepositoryImpl(db)
    data_repository = DataRepositoryImpl(db, keyword_repository)

    use_case = CreateDataList(data_repository)
    engine = CrawlingEngine()

    # 1) DB에서 가장 최신 published_at 가져오기
    recent = data_repository.get_recent(limit=limit)
    latest_date = None

    if recent:
        published_str = recent[0].published_at
        if published_str:
            try:
                latest_date = datetime.fromisoformat(published_str)
            except ValueError:
                latest_date = None  # 혹시 잘못된 포맷이면 비교 못 하므로 무시

    # 2) 크롤링 실행
    items = await engine.article_analysis(page_count=5)

    # 3) 최신 데이터만 필터링
    filtered_items = []
    for item in items:
        # item.published_at 은 datetime 형식이어야 비교 가능
        if latest_date is None or item.published_at > latest_date:
            filtered_items.append({
                "title": item.title,
                "content": item.content,
                "keywords": item.keywords,
                "published_at": item.published_at,
            })

    # 4) 저장할 데이터 없으면 바로 반환
    if not filtered_items:
        return []

    # 5) DB 저장
    created_data_list = use_case.execute(filtered_items) #주석 살리면 filtered_items 로 변환
    db.commit()

    # 6) 저장된 결과 리턴
    return [
        DataResponse(
            id=data.id,
            title=data.title,
            content=data.content,
            keywords=data.keywords,
            published_at=data.published_at,
        )
        for data in created_data_list
    ]


# TODO: /data/top-keywords, /data/keywords 등 통계용 엔드포인트는
# 추후 datas.keywords 컬럼을 기반으로 재구현할 수 있습니다.


@data_router.post(
    "/",
    response_model=List[DataResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_data_from_crawling(
    request: CrawlingIngestRequest, db: Session = Depends(get_db)
):
    """
    크롤링/분석 API 결과에 포함된 analysis 내용을 DB에 저장
    """
    items_to_save: List[dict] = []
    for article in request.articles:
        analysis = article.analysis
        title = analysis.title.strip()
        content = analysis.content.strip()
        keywords = [
            keyword.strip()
            for keyword in analysis.keywords
            if isinstance(keyword, str) and keyword.strip()
        ]

        if not title or not content:
            continue

        # published_at이 필수 필드이므로, 없으면 빈 문자열로 처리
        published_at = ""
        if hasattr(analysis, 'published_at') and analysis.published_at:
            published_at = analysis.published_at
        
        items_to_save.append(
            {
                "title": title,
                "content": content,
                "keywords": keywords,
                "published_at": published_at,
            }
        )

    if not items_to_save:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="저장 가능한 분석 데이터가 없습니다.",
        )

    return _create_data_items(items_to_save, db)

