from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

# CSV 로딩 (Excel 호환 인코딩)
data = pd.read_csv("data.csv", encoding="utf-8-sig")

# GPT 키 ↔ 실제 CSV 열 매핑
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

# 검색 요청 모델 정의
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
    usage_years: float = None
    device_count: float = None
    option_info: str = None

MAX_RESULTS = 50

@app.post("/search")
def search(query: Query):
    df = data.copy()
    try:
        for field, col in field_map.items():
            value = getattr(query, field)
            if value is not None:
                if pd.api.types.is_numeric_dtype(df[col]):
                    try:
                        numeric_value = float(value)
                        df = df[abs(df[col] - numeric_value) < 0.01]
                    except:
                        continue
                else:
                    # 문자열 정리: 공백 제거, 소문자 변환, 다중 공백 통일
                    df[col] = df[col].astype(str).str.replace(r"\s+", " ", regex=True).str.strip().str.lower()
                    value_str = str(value).strip().lower()
                    df = df[df[col].str.contains(value_str, na=False, regex=False)]

        return df.head(MAX_RESULTS).to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return {"message": "장비 검색 API가 실행 중입니다."}
