from typing import List

from app.data.application.port.data_repository_port import DataRepositoryPort
from app.data.domain.data import Data


class CreateDataList:
    def __init__(
        self,
        data_repository: DataRepositoryPort,
    ):
        self.data_repository = data_repository

    def execute(
        self,
        items: List[dict],
    ) -> List[Data]:
        """
        여러 데이터를 한 번에 생성
        items: [{"title": str, "content": str, "keywords": List[str]}, ...]
        """
        created_data_list: List[Data] = []

        for item in items:
            # published_at이 필수 필드이므로, 없으면 빈 문자열로 처리
            published_at = item.get("published_at", "")
            if not published_at:
                published_at = ""
            
            data = Data(
                title=item["title"],
                content=item["content"],
                keywords=[
                    k.strip() for k in item.get("keywords", []) if k and k.strip()
                ],
                published_at=published_at,
            )
            saved_data = self.data_repository.save(data)
            created_data_list.append(saved_data)

        return created_data_list

