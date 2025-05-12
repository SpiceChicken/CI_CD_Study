# app/user/api/v1.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # OAuth2Form을 위한 임포트
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List

# 절대 경로로 app.user 패키지에서 직접 가져오기
from app.auth.schemas.user import *
from app.auth.crud.user    import *
from app.auth.crud.token   import *
from app.auth.models.user  import *
from app.auth.schemas import Token, RefreshTokenRequest
from app.db.database import get_db
from app import security

# 비밀번호 재설정 토큰 생성에 필요
import secrets

# JWT 토큰 만료 시간 설정 (utils/password.py에서 가져와 사용)
ACCESS_TOKEN_EXPIRE_MINUTES = security.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = security.REFRESH_TOKEN_EXPIRE_DAYS

router = APIRouter(
    prefix="/user/v1", # API 경로 접두사 설정
    tags=["user"], # 문서화에 사용될 태그
)

# 회원가입 엔드포인트
@router.post("/register/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    새로운 사용자를 등록합니다.
    """
    # 1. 이메일 중복 확인
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 2. 사용자 생성 (비밀번호 해싱은 CRUD 함수 내에서 수행)
    return create_user(db=db, user_in=user)

# 로그인 엔드포인트 (Swagger UI 전용)
@router.post("/login/oauth2", response_model=Token)
def login_for_access_token_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Swagger UI 전용 로그인 엔드포인트 (OAuth2PasswordBearer 호환)
    """
    user = get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = security.create_access_token(data={"sub": user.email})
    refresh_token = security.create_refresh_token(data={"sub": user.email})
    create_token(db, token=refresh_token, token_type='refresh', user_id=user.id, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

# 로그인 엔드포인트 (액세스 토큰 발급)
# 요청 본문을 JSON으로 받고, schemas.UserLogin 스키마를 사용합니다.
@router.post("/login/", response_model=Token)
def login_for_access_token(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    이메일과 비밀번호(JSON 본문)로 로그인하여 JWT 액세스 토큰을 발급받습니다.
    """
    # 1. 사용자 조회 (입력받은 이메일 사용)
    user = get_user_by_email(db, email=user_login.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            # "WWW-Authenticate": "Bearer" 헤더는 OAuth2PasswordBearer와 함께 사용되므로,
            # 여기서는 필수는 아니지만 인증 실패 응답에 포함될 수 있습니다.
            # headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. 비밀번호 검증 (utils 모듈의 verify_password 함수 사용)
    if not security.verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            # headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 계정 활성 상태 확인
    if not user.is_active:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, # 또는 401 UNAUTHORIZED
            detail="Inactive user",
        )

    # 4. JWT 액세스 토큰 생성 (utils 모듈의 create_access_token 함수 사용)
    access_token = security.create_access_token(data={"sub": user.email})
    refresh_token = security.create_refresh_token(data={"sub": user.email})
    create_token(db, token=refresh_token, token_type='refresh', user_id=user.id, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


# 토큰 리프레시 엔드포인트 (리프레시 토큰 -> 새 액세스 토큰 발급)
# /auth/refresh/ 대신 /user/v1/refresh/ 으로 경로 변경
@router.post("/refresh/", response_model=Token)
def refresh_access_token(token_request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    리프레시 토큰을 사용하여 새 액세스 토큰을 발급받습니다.
    요청 본문에 refresh_token 필드를 포함해야 합니다.
    """
    # 1. 리프레시 토큰 검증 및 조회
    # crud.py에 get_token_by_value 함수가 구현되어 있어야 합니다.
    db_token = get_token_by_value(db, token=token_request.refresh_token, token_type='refresh')

    # 토큰 존재 및 만료 시간 확인
    if not db_token or db_token.expires_at < datetime.utcnow():
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. 토큰에 연결된 사용자 조회
    # crud.py에 get_user_by_id 함수가 구현되어 있어야 합니다.
    user = get_user_by_id(db, user_id=db_token.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user associated with token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 사용된 리프레시 토큰 무효화 (삭제)
    # crud.py에 delete_token 함수가 구현되어 있어야 합니다.
    delete_token(db, db_token)

    # 4. 새 액세스 토큰 및 리프레시 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = security.create_access_token(data={"sub": user.email})

    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_DAYS)
    new_refresh_token_value = security.create_refresh_token(data={"sub": user.email})
    create_token(db, token=new_refresh_token_value, token_type='refresh', user_id=user.id, expires_delta=refresh_token_expires)

    # 5. 새 토큰 정보 반환
    return {"access_token": new_access_token, "token_type": "bearer", "refresh_token": new_refresh_token_value}


# # 프로필 조회 엔드포인트 (인증 필요)
# # /users/me/ 대신 /user/v1/me/ 으로 경로 변경
# @router.get("/me/", response_model=schemas.UserResponse)
# def read_users_me(current_user: models.User = Depends(password.get_current_user)):
#     """
#     현재 로그인된 사용자의 프로필 정보를 조회합니다.
#     """
#     # Depends(utils.get_current_user) 덕분에
#     # 이곳에 도달했다는 것은 유효한 토큰을 가진 사용자로 인증되었다는 의미입니다.
#     # current_user 객체는 utils.get_current_user 함수가 데이터베이스에서 조회한 User 모델 객체입니다.
#     return current_user

# # 프로필 수정 엔드포인트 (인증 필요)
# # /users/me/ 대신 /user/v1/me/ 으로 경로 변경
# @router.patch("/me/", response_model=schemas.UserResponse)
# def update_users_me(user_update: schemas.UserUpdate, db: Session = Depends(get_db),
#                     current_user: models.User = Depends(password.get_current_user)):
#     """
#     현재 로그인된 사용자의 프로필 정보를 수정합니다.
#     """
#     # schemas.UserUpdate 스키마에 수정 가능한 필드를 정의하고
#     # crud.update_user 함수에서 해당 필드를 업데이트하는 로직을 구현해야 합니다.
#     updated_user = crud.update_user(db=db, db_user=current_user, user_update=user_update)
#     return updated_user

# 비밀번호 재설정 요청 엔드포인트 (이메일 발송 - 이메일 발송 기능은 별도 구현 필요)
# /auth/password-reset-request/ 대신 /user/v1/password-reset-request/ 으로 경로 변경
@router.post("/password-reset-request/", response_model=Message)
def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    비밀번호 재설정 링크/코드를 포함한 이메일 발송을 요청합니다.
    실제 이메일 발송 로직은 포함되어 있지 않으며, 토큰 생성까지만 구현합니다.
    """
    user = get_user_by_email(db, email=request.email)

    # 보안 상, 사용자가 존재하든 안 하든 동일한 응답을 반환하는 것이 좋습니다.
    if user and user.is_active:
        # 1. 비밀번호 재설정 토큰 생성 및 저장
        reset_token_value = secrets.token_urlsafe(32) # 안전한 토큰 생성

        # 기존 비밀번호 재설정 토큰이 있다면 무효화 (선택 사항, 보안 강화)
        # db.query(models.Token).filter(models.Token.user_id == user.id, models.Token.token_type == 'reset').delete()
        # db.commit()

        reset_token_expires = timedelta(hours=1) # 재설정 토큰 유효 시간 (예: 1시간)
        # crud.py에 create_token 함수가 구현되어 있어야 합니다.
        create_token(db, token=reset_token_value, token_type='reset', user_id=user.id, expires_delta=reset_token_expires)

        # 2. (실제) 사용자 이메일로 재설정 링크 또는 토큰 발송
        # 이 부분은 SMTP 서버 설정 및 이메일 라이브러리 사용이 필요합니다.
        print(f"비밀번호 재설정 토큰: {reset_token_value} (실제 환경에서는 이메일로 발송됩니다)")
        # send_email(user.email, "비밀번호 재설정", f"토큰: {reset_token_value}")


    # 사용자 존재 여부와 상관없이 성공 응답 반환 (이메일 주소 유출 방지)
    return {"message": "Password reset instructions sent to your email (if the user exists)."}

# 비밀번호 재설정 완료 엔드포인트
# /auth/password-reset/ 대신 /user/v1/password-reset/ 으로 경로 변경
@router.post("/password-reset/", response_model=Message)
def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    """
    제공된 토큰과 새 비밀번호로 비밀번호를 재설정합니다.
    """
    # 1. 재설정 토큰 검증 및 조회 (유효한 토큰인지, 만료되지 않았는지)
    # crud.py에 get_valid_password_reset_token 함수가 구현되어 있어야 합니다.
    db_token = get_valid_password_reset_token(db, token=reset_data.token)

    if not db_token:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, # 또는 401 Unauthorized
            detail="Invalid or expired password reset token",
        )

    # 2. 토큰에 연결된 사용자 조회
    # crud.py에 get_user_by_id 함수가 구현되어 있어야 합니다.
    user = get_user_by_id(db, user_id=db_token.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, # 또는 401 Unauthorized
            detail="Invalid user associated with token",
        )

    # 3. 비밀번호 업데이트
    # utils/password.py에 get_password_hash 함수가 구현되어 있어야 합니다.
    hashed_new_password = security.get_password_hash(reset_data.new_password)
    user.hashed_password = hashed_new_password # 사용자 모델 직접 업데이트
    # 또는 crud 함수 사용: crud.update_user_password(db, user=user, hashed_password=hashed_new_password)
    db.commit()
    db.refresh(user)

    # 4. 사용된 비밀번호 재설정 토큰 삭제 (매우 중요)
    # crud.py에 delete_token 함수가 구현되어 있어야 합니다.
    delete_token(db, db_token)

    return {"message": "Password has been reset successfully."}

# 파워 유저용 비밀번호 초기화 엔드포인트 (파워 유저 인증 필요)
# PATCH 메서드는 부분 업데이트에 적합하며, 리소스(사용자)의 비밀번호를 업데이트하는 의미를 가집니다.
@router.patch("/reset-password-by-poweruser/", response_model=Message) # POST도 가능하지만 PATCH가 더 의미 명확
def reset_user_password_by_poweruser(
    reset_data: PasswordResetByPowerUserRequest, # 요청 본문: 대상 유저 이메일과 새 비밀번호
    db: Session = Depends(get_db), # 데이터베이스 세션
    current_power_user: User = Depends(security.get_current_active_superuser) # <-- 파워 유저 인증 및 권한 확인
):
    """
    파워 유저가 다른 사용자의 비밀번호를 초기화(변경)합니다.

    요청 본문에는 'target_user_email' 필드를 포함해야 합니다.
    이 엔드포인트는 유효한 Access Token (Bearer 타입)으로 인증된 파워 유저만 호출할 수 있습니다.
    """
    # Depends(utils.get_current_power_user) 덕분에 이 함수에 도달했다는 것은
    # 현재 사용자가 유효한 토큰을 가지고 있고, is_superuser=True 인 상태임을 의미합니다.

    # 1. 초기화할 대상 사용자를 이메일로 조회합니다.
    # crud.py에 get_user_by_email 함수가 구현되어 있는지 확인해주세요.
    target_user = get_user_by_email(db, email=reset_data.target_user_email)

    # 2. 대상 사용자가 존재하지 않으면 오류 응답
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found"
        )

    # 3. 초기화할 '기본 비밀번호' 값을 안전하게 해싱합니다.
    # utils/password.py에 get_password_hash 함수가 올바르게 구현되어 있는지 확인해주세요.
    hashed_new_password = security.get_password_hash("password")

    # 4. 대상 사용자의 비밀번호 해시를 새로 생성한 해시로 업데이트합니다.
    target_user.hashed_password = hashed_new_password

    # 5. 데이터베이스에 변경 사항을 커밋하고 대상 객체를 갱신합니다.
    db.commit()
    db.refresh(target_user)

    # 6. 비밀번호 초기화 성공 메시지를 반환합니다.
    # 어떤 사용자의 비밀번호가 초기화되었는지 메시지에 포함할 수 있습니다.
    return {"message": f"Password for user {target_user.email} has been reset."}