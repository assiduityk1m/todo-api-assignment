
아래는 이 과제를 처음부터 완성하기 위해 설계한 단일 프롬프트입니다. 
실제 개발은 반복적 디버깅으로 진행되었지만, 이 프롬프트는 모든 요구사항을 한 번에 충족하도록 구성했습니다.

## 요청 개요
Python 3.12와 FastAPI, SQLAlchemy 2.0, SQLite를 사용해 사용자 인증 기반의 Todo 관리 RESTful API를 개발해 주세요.
 과제는 다음 요구사항을 충족해야 하며, 모든 설명과 문서는 한글로 작성해 주세요. 
 최종 결과물은 테스트 커버리지 80% 이상을 보장하고, 제출 항목(소스코드, SQLite 초기화 코드, JWT 흐름 다이어그램, README, 테스트 코드, 프롬프트 정리)을 포함해야 합니다. 저의 헬스케어 IT 시스템 경험(4년, C# 기반 HIS 시스템)을 참고해 안정적인 DB 처리와 체계적인 문서화를 강조해 주세요.

## 요구사항
1. **기능**:
   - **사용자 관리**:
     - 회원가입(`/users/signup`): 이메일, 비밀번호로 사용자 등록.
     - 로그인(`/users/login`): JWT 토큰 발급.
     - 사용자 조회/수정/삭제(`/users/me`): 현재 사용자 정보 관리.
   - **Todo 관리**:
     - Todo 생성(`/todos`): 제목, 설명, 완료 여부.
     - Todo 목록 조회(`/todos`): 현재 사용자의 Todo 목록.
     - Todo 검색(`/todos/search?q=`): 제목 기반 검색.
     - Todo 조회/수정/삭제(`/todos/{id}`): 특정 Todo 관리.
   - 인증: JWT(OAuth2 Password Flow)로 보호된 엔드포인트.

2. **기술 스택**:
   - Python 3.12, FastAPI, SQLAlchemy 2.0, SQLite.
   - JWT: python-jose (HS256 알고리즘).
   - 비밀번호 해싱: passlib (bcrypt).
   - 테스트: pytest, pytest-cov, httpx.
   - SQLite 로컬 DB 사용, 외부 서비스 금지.

3. **테스트**:
   - 통합 테스트로 CRUD, 인증, 검색 기능 검증.
   - 커버리지 80% 이상.
   - 테스트 파일: `tests/test_todos.py`, `tests/test_users.py`.

4. **제출 항목**:
   - **소스코드**: `main.py`, `auth.py`, `database.py`, `models.py`, `schemas.py`.
   - **SQLite 초기화**: `init_db.sql` (users, todos 테이블).
   - **JWT 흐름 다이어그램**: `jwt_flow.md` (JWT 발급/검증, OAuth2 흐름).
   - **README**: `README_ko.md` (한글, 실행 방법, API 명세).
   - **테스트 코드**: `tests/` 디렉토리.
   - **프롬프트 정리**: `prompts/used_prompts_ko.md` (이 프롬프트 포함).
   - **종속성**: `requirements.txt`.

## 디버깅 과정
## 1. 초기 설정 및 데이터베이스 초기화
- **프롬프트**:  
  "pytest 실행 시 `sqlalchemy.exc.OperationalError: no such table: users` 에러가 발생했습니다. 다음은 pytest 출력입니다: [pytest 출력]. `database.py`, `test_todos.py`, `test_users.py`를 확인하고, SQLite 데이터베이스(`todo.db`, `test.db`)가 제대로 초기화되도록 수정된 코드를 제공해주세요. 특히, 테스트 환경에서 DB 초기화가 안정적으로 이루어져야 합니다."
- **Grok 응답**:  
  - `database.py`에서 `init_db()` 함수가 `todo.db`와 `test.db`를 명시적으로 초기화하도록 수정 제안.
  - 테스트 픽스처에 `init_db()` 호출을 추가하고, `TEST_DATABASE_URL`을 사용해 테스트 DB를 별도로 관리하도록 권장.
  - `test_todos.py`, `test_users.py`에 `setup_database` 픽스처를 추가하여 각 테스트 전에 DB를 초기화하도록 제안.
- **결과**:  
  - 테이블 생성 문제가 해결되어 모든 테스트가 DB 관련 에러 없이 실행됨.
  - `init_db.sql`의 테이블 정의(`users`, `todos`)가 올바르게 적용됨을 확인.

## 2. 테스트 실패 디버깅
### 2.1. `test_signup_and_login` - 400 Bad Request
- **프롬프트**:  
  "`test_signup_and_login` 테스트가 400 에러로 실패했습니다: [pytest 출력]. 에러 메시지는 'Email already registered'입니다. `test_users.py`와 `database.py`를 확인하고, 테스트 간 DB 상태가 중복되지 않도록 초기화하는 방법을 제안해주세요. 테스트 픽스처를 활용한 해결책이 이상적입니다."
- **Grok 응답**:  
  - `test_users.py`와 `test_todos.py`의 `setup_database` 픽스처에 `text("DELETE FROM users")`와 `text("DELETE FROM todos")`를 추가하여 각 테스트 시작 전 테이블을 비우도록 수정.
  - SQLAlchemy의 `text()`를 사용해 SQL 문자열을 실행 가능하도록 조정.
  - `engine.connect()`를 사용한 트랜잭션 커밋 로직 추가.
- **결과**:  
  - 중복 이메일 문제가 해결되어 `test_signup_and_login`이 200 OK로 통과.
  - 모든 테스트가 독립적으로 실행되며, DB 상태가 일관되게 유지됨.

### 2.2. `test_search_todos` - 422 Unprocessable Entity
- **프롬프트**:  
  "`test_search_todos` 테스트가 422 에러로 실패했습니다: [pytest 출력]. 에러 메시지는 `Input should be a valid integer, unable to parse string as an integer, input: 'search'`입니다. `/todos/search` 엔드포인트가 `/todos/{id}`로 잘못 라우팅되는 것 같아요. 다음은 `main.py`와 `test_todos.py`입니다. 라우팅 문제를 분석하고 수정된 코드를 제공해주세요."
- **Grok 응답**:  
  - `main.py`에서 `/todos/{id}` 엔드포인트가 `/todos/search`보다 먼저 정의되어 FastAPI의 경로 매칭 순서로 인해 `search`가 `id`로 잘못 해석됨을 파악.
  - `/todos/search`를 `/todos/{id}`보다 위로 재배치하여 라우팅 우선순위를 조정.
  - `q: Optional[str] = Query(None, min_length=1)`를 추가해 쿼리 파라미터 검증 강화.
- **결과**:  
  - 라우팅 문제가 해결되어 `/todos/search?q=Test` 요청이 200 OK로 처리됨.
  - `test_search_todos`가 예상대로 1개의 Todo를 반환하며 통과.

### 2.3. SQLAlchemy 실행 에러
- **프롬프트**:  
  "pytest에서 `sqlalchemy.exc.ObjectNotExecutableError: Not an executable object: 'DELETE FROM todos'` 에러가 발생했습니다: [pytest 출력]. `test_todos.py`와 `test_users.py`의 DB 초기화 로직을 확인하고, SQLAlchemy 2.0에서 올바르게 SQL 쿼리를 실행하도록 수정해주세요."
- **Grok 응답**:  
  - `conn.execute("DELETE FROM ...")`를 `conn.execute(text("DELETE FROM ..."))`로 변경하여 SQLAlchemy 2.0의 `text()` API 사용.
  - `from sqlalchemy import text` 임포트 추가.
- **결과**:  
  - DB 초기화 로직이 정상 작동하여 모든 테스트가 실행 가능해짐.
  - 커버리지가 49%에서 91%로 상승.

## 3. 제출 준비 및 요구사항 검증
- **프롬프트**:  
  "과제 제출 요구사항은 다음과 같습니다: [소스코드, SQLite 초기화 코드, JWT 흐름 다이어그램, README.md, 테스트 코드, 프롬프트 정리]. 현재 pytest 결과는 7개 테스트 통과, 커버리지 93%입니다. 누락된 항목이 있는지 확인하고, `README.md`, `jwt_flow.md`, `used_prompts.md`를 작성해 제출을 완료할 수 있도록 도와주세요. 또한, 프롬프트는 한글로 번역해달라."
- **Grok 응답**:  
  - `README.md`에 실행 방법(venv 설정, DB 초기화, uvicorn 실행)과 API 명세(엔드포인트 표, 예제 요청) 포함.
  - `jwt_flow.md`에 JWT 발급/검증 흐름과 OAuth2 Password Flow 설명.
  - `used_prompts_ko.md`에 주요 프롬프트와 결과를 한글로 정리.
  - 모든 파일이 요구사항 충족 확인, 테스트 결과 저장(`test_results.txt`).
- **결과**:  
  - 모든 제출 파일 준비 완료.
  - ZIP 파일 생성 명령 제공, 불필요 파일(`venv/`, `*.db`) 제외 확인.

## 4. 최종 검증 및 커버리지 개선
- **프롬프트**:  
  "pytest 결과는 7개 테스트 통과, 커버리지 93%입니다. `main.py`의 21-25, 37-39줄이 미커버 상태입니다. 커버리지를 95% 이상으로 높일 수 있는 추가 테스트를 제안해주세요. 또한, 제출 전 최종 점검 항목을 알려주세요."
- **Grok 응답**:  
  - `test_todos.py`에 `test_invalid_token` 추가하여 `get_current_user`의 예외 처리(401 에러) 테스트.
  - 제출 전 점검: 소스코드, `init_db.sql`, `requirements.txt`, 테스트 결과, 다이어그램, 프롬프트 파일 포함 여부 확인.
  - ZIP 생성 시 `venv/`, `__pycache__/`, `*.db` 제외 명령 제공.
- **결과**:  
  - 커버리지 93%에서 95%로 개선 가능성 확인.
  - 제출 준비 완료, 마감 내 업로드 가능.

