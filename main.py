from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np

app = FastAPI()

# CSV 로드
data = pd.read_csv("data.csv", encoding="utf-8-sig")

# 사용자 요청 필드 정의 → CSV 열 이름 매핑
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

# 검색 쿼리 모델 정의
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

MAX_RESULTS = 8000  # 최대 반환 행 수

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
                        df = df[np.abs(df[col] - numeric_value) < 0.01]
                    except:
                        continue
                else:
                    df[col] = (
                        df[col]
                        .fillna("")
                        .astype(str)
                        .str.replace(r"\s+", " ", regex=True)
                        .str.strip()
                        .str.lower()
                    )
                    value_str = str(value).strip().lower()
                    df = df[df[col].str.contains(value_str, na=False, regex=False)]

        # NaN, inf 처리 → JSON 직렬화 오류 방지
        df.replace([np.inf, -np.inf], None, inplace=True)
        df.fillna("", inplace=True)

        return df.head(MAX_RESULTS).to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return {"message": "장비 검색 API 정상 작동 중"}
