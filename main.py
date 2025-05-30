from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

# CSV 로딩
data = pd.read_csv("data.csv", encoding="utf-8-sig")

# 영문 → 한글 열 이름 매핑
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

# 요청 바디 모델 정의
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

# 검색 API
@app.post("/search")
def search(query: Query):
    df = data.copy()
    
    for field, col in field_map.items():
        value = getattr(query, field)
        if value is not None:
            if df[col].dtype == "int64":
                # 정수형 필드 (사용년, 총장비수 등)
                df = df[df[col] == value]
            else:
                # 문자열 필드 - 부분 일치 검색
                df = df[df[col].astype(str).str.contains(str(value), case=False, na=False)]
    
    return df.to_dict(orient="records")


MAX_RESULTS = 50  # 예: 50건까지만 반환

@app.post("/search")
def search(query: Query):
    df = data.copy()
    for field, col in field_map.items():
        value = getattr(query, field)
        if value is not None:
            if pd.api.types.is_numeric_dtype(df[col]):
                df = df[df[col] == value]
            else:
                df = df[df[col].astype(str).str.contains(str(value), case=False, na=False)]
    return df.head(MAX_RESULTS).to_dict(orient="records")  # ✅ 개수 제한
