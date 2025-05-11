# app/main.py: FastAPI 서버 진입점 및 라우터 설정 모듈
#
# 이 파일은 FastAPI 애플리케이션을 초기화하고,
# 데이터베이스 테이블을 생성(Base.metadata.create_all)하며,
# URL 단축 기능을 제공하는 라우터를 등록합니다.

from fastapi import FastAPI
from app.auth.api.user import router as user_router
from app.shortener.api import v1 as shortener_api
from app.analytics.api import v1 as analytics_api

from app.db.database import Base, engine

# OpenAPI 스펙에 추가할 보안 스킴 정의
openapi_security_scheme = {
    "Bearer": { # 스킴 이름 (Swagger UI에 표시될 이름)
        "type": "http",      # HTTP 보안 스킴 타입
        "scheme": "bearer",  # 스킴 이름 (여기서는 'bearer')
        "bearerFormat": "JWT" # Bearer 토큰 형식 (선택 사항이지만 명시하면 좋음)
    }
    # 만약 x-api-key도 나중에 추가한다면 여기에 추가
    # "ApiKeyAuth": { # 스킴 이름
    #     "type": "apiKey",
    #     "in": "header",
    #     "name": "x-api-key"
    # }
}

# 보호된 API에 적용될 보안 요구사항 (이 스킴이 적용된 엔드포인트는 이 보안 방식을 따라야 함)
# 여기서는 모든 보호된 API에 대해 "Bearer" 스킴을 요구합니다.
openapi_security_requirements = [
    {"Bearer": []} # "Bearer" 스킴을 사용하며, 추가적인 scope는 없습니다.
    # 만약 API Key도 필수로 요구한다면:
    # {"ApiKeyAuth": []}
    # 만약 둘 중 하나만 요구한다면 (더 복잡한 설정 필요, Depends 조합 함수 사용이 더 간편)
]

app = FastAPI(title="URL Shortener with Auth")

app.include_router(user_router)
app.include_router(shortener_api.router)
app.include_router(analytics_api.router)

# 자동 테이블 생성 (개발용)
Base.metadata.create_all(bind=engine)