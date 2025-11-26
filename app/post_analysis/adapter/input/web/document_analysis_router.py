import csv
import io
from typing import List

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile

from app.post_analysis.adapter.input.web.request.analyze_post_request import AnalyzePostRequest
from app.post_analysis.adapter.input.web.response.document_analysis_response import StockPostAnalysisResponse
from app.post_analysis.application.usecase.analyze_document import AnalyzeStockPostUseCase
from app.post_analysis.infrastructure.service.openai_service_impl import OpenAIServiceImpl
from config.settings import Settings, get_settings


post_analysis_router = APIRouter(tags=["post_analysis"])


@post_analysis_router.post("/analyze", response_model=StockPostAnalysisResponse)
async def analyze_post(
    request: AnalyzePostRequest,
    settings: Settings = Depends(get_settings)
):
    """
    POST /post-analysis/analyze - 주식 게시글 분석

    크롤링된 주식 게시글 텍스트를 분석하여 title, content, keywords를 추출합니다.

    Args:
        request: raw_text가 포함된 요청 모델 (크롤링된 원본 텍스트)
        settings: 애플리케이션 설정

    Returns:
        StockPostAnalysisResponse: 분석 결과 (title, content, keywords)
    """
    try:
        # 서비스 초기화
        openai_service = OpenAIServiceImpl(api_key=settings.OPENAI_API_KEY)

        # 유스케이스 실행
        use_case = AnalyzeStockPostUseCase(openai_service)
        result = await use_case.execute(
            request.raw_text,
            prompt_template=request.prompt_template
        )

        return StockPostAnalysisResponse(
            title=result.title,
            content=result.content,
            keywords=result.keywords
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")

@post_analysis_router.post("/analyze-csv", response_model=List[StockPostAnalysisResponse])
async def analyze_post_csv(
        file: UploadFile = File(...),
        settings: Settings = Depends(get_settings),
):
    """
    POST /post-analysis/analyze-csv - CSV 파일 기반 주식 게시글 분석

    - Postman 설정:
      * Method: POST
      * URL:    /post-analysis/analyze-csv  (main.py에서 prefix를 어떻게 붙였는지에 따라 다를 수 있음)
      * Body:   form-data
          - Key: file (타입: File)
          - Value: 분석할 CSV 파일

    CSV 예시 컬럼 (Kaggle reddit stocks 데이터 기준):
    - title, score, id, url, comms_num, created, body, timestamp
    여기서는 title + body를 합쳐 raw_text로 사용.
    """
    if file.content_type not in ["text/csv", "application/vnd.ms-excel"]:
        raise HTTPException(status_code=400, detail="CSV 파일만 업로드 가능합니다.")

    # 파일 내용 읽기
    content = await file.read()
    text_io = io.StringIO(content.decode("utf-8"))

    # 첫 줄을 header로 사용하는 CSV라고 가정
    reader = csv.DictReader(text_io)

    openai_service = OpenAIServiceImpl(api_key=settings.OPENAI_API_KEY)
    use_case = AnalyzeStockPostUseCase(openai_service)

    results: List[StockPostAnalysisResponse] = []

    for row in reader:
        # CSV 컬럼명에 맞게 raw_text 생성
        # title + 두 줄 띄우고 + body
        raw_text = f"{row.get('title', '')}\n\n{row.get('body', '')}"

        result = await use_case.execute(raw_text)

        results.append(
            StockPostAnalysisResponse(
                title=result.title,
                content=result.content,
                keywords=result.keywords,
            )
        )

    return results