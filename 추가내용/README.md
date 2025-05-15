# Todo API 과제

FastAPI, SQLAlchemy, SQLite를 사용한 사용자 인증 기반의 Todo 관리 RESTful API입니다.

## 설치 및 실행 방법

1. **저장소 클론**:
   ```bash
   git clone <repository-url>
   cd todo_api_assignment
   ```

2. **가상 환경 설정**:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   ```

3. **종속성 설치**:
   ```bash
   pip install -r requirements.txt
   ```

4. **데이터베이스 초기화**:
   ```bash
   sqlite3 todo.db < init_db.sql
   ```

5. **애플리케이션 실행**:
   ```bash
   uvicorn main:app --reload
   ```
   - 에서 접근 가능.

6. **테스트 실행**:
   ```bash
   pytest --cov=. --cov-report=term-missing
   ```

## API 엔드포인트

| 메서드 | 엔드포인트            | 설명                            | 인증 필요 |
|--------|----------------------|---------------------------------|:---------:|
| POST   |       | 새 사용자 등록                  |    X      |
| POST   |        | 로그인 및 JWT 토큰 발급         |    X      |
| GET    |           | 현재 사용자 정보 조회           |    O      |
| PUT    |           | 현재 사용자 정보 수정           |    O      |
| DELETE |           | 현재 사용자 삭제                |    O      |
| POST   |              | 새 Todo 생성                    |    O      |
| GET    |              | 사용자 Todo 목록 조회           |    O      |
| GET    |       | 제목으로 Todo 검색              |    O      |
| GET    |         | 특정 Todo 조회                  |    O      |
| PUT    |         | 특정 Todo 수정                  |    O      |
| DELETE |         | 특정 Todo 삭제                  |    O      |

### 요청 예시

- **사용자 등록**:
  ```bash
  curl -X POST http://127.0.0.1:8000/users/signup -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"password123"}'
  ```

- **로그인**:
  ```bash
  curl -X POST http://127.0.0.1:8000/users/login -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"password123"}'
  ```

- **Todo 생성**:
  ```bash
  curl -X POST http://127.0.0.1:8000/todos -H "Content-Type: application/json" -H "Authorization: Bearer <token>" -d '{"title":"Test Todo","description":"Test","completed":false}'
  ```

## 종속성

자세한 목록은 를 참조하세요. 주요 라이브러리:
- FastAPI: API 프레임워크
- SQLAlchemy: SQLite ORM
- python-jose: JWT 처리
- passlib: 비밀번호 해싱
- pytest: 테스트 프레임워크
