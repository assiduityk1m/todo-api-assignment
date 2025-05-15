# JWT 발급 및 검증 흐름

## 1. JWT 발급 (POST /users/login)
- 클라이언트: 이메일/비밀번호 전송
- 서버: 
  - DB에서 사용자 조회
  - 비밀번호 검증 (passlib.bcrypt)
  - JWT 생성 (python-jose, HS256)
  - {access_token, token_type: "bearer"} 반환

## 2. JWT 검증 (보호된 엔드포인트, 예: GET /todos)
- 클라이언트: Authorization: Bearer <token> 헤더 전송
- 서버:
  - OAuth2PasswordBearer로 토큰 추출
  - JWT 디코딩 (python-jose, HS256)
  - 이메일 추출 및 DB 사용자 조회
  - 사용자 반환 또는 401 에러

## 3. OAuth2 흐름
- OAuth2 Password Flow:
  - 클라이언트가 /users/login에 POST 요청
  - 서버가 토큰 발급
  - 클라이언트가 토큰으로 보호된 리소스 접근
