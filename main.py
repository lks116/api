from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

# CSV 데이터 로딩 (UTF-8 인코딩)
data = pd.read_csv("data.csv", encoding="utf-8")

# GPT 필드명 ↔ CSV 한글 열 이름 매핑
field_map = {
    "customer_name": "고객이름",
    "device_name": "장비명",
    "serial_number": "시리얼넘버",
    "region": "지역",
    "city": "시",
    "address": "주소",
    "install_date": "고객설치일",
    "warranty_expiry": "워런티종료일",
    "option_expiry": "옵타입종료일",
    "usage_years": "사용년",
    "device_count": "총장비수",
    "option_info": "옵션"
}

# 요청 바디 모델 정의 (GPT 함수 호출 시 매핑)
class Query(BaseModel):
    customer_name: str = None
    device_name: str = None
    serial_number: str = None
    region: str = None
    city: str = None
    address: str = None
    install_date: str = None
    warranty_expiry: str = None
    option_expiry: str = None
    usage_years: int = None
    device_count: int = None
    option_info: str = None

# 검색 결과 최대 개수 제한
MAX_RESULTS = 50

@app.post("/search")
def search(query: Query):
    df = data.copy()
    try:
        # 조건 필터링
        for field, col in field_map.items():
            value = getattr(query, field)
            if value is not None:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df = df[df[col] == value]
                else:
                    df = df[df[col].astype(str).str.contains(str(value), case=False, na=False)]

        # 최대 50건만 반환
        return df.head(MAX_RESULTS).to_dict(orient="records")

    except Exception as e:
        # 에러 발생 시 메시지 반환
        return {"error": str(e)}

# 선택적으로 루트 경로에 메시지 추가
@app.get("/")
def root():
    return {"message": "장비 검색 API가 실행 중입니다."}
