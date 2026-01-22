# 🤖 Gemini-Cal.com-Automation

**완전 무료** 회의록 자동 분석 & 스케줄 관리 시스템

웹 인터페이스에서 회의록 텍스트를 입력하면 Gemini AI가 자동으로 분석해서 Cal.com에 태스크와 일정으로 등록해줍니다!

## ✨ 주요 기능

- 🌐 **웹 인터페이스**: 브라우저에서 쉽게 회의록 입력
- 📝 **회의록 자동 분석**: Google Gemini AI로 회의록에서 중요 정보 추출
- 📅 **자동 스케줄링**: 분석 결과를 Cal.com에 자동으로 태스크/이벤트 등록
- 💰 **완전 무료**: Gemini 무료 티어 사용 (일 1,500회 요청)
- 🚀 **간편한 사용**: 텍스트만 입력하면 끝!
- 🐳 **Docker 지원**: Docker Compose로 한 번에 배포

## 🎯 분석 내용

- ✅ 완료된 작업
- 📌 해야 할 작업 (TODO)
- 📆 예정된 일정
- 👥 참석자
- 💡 주요 결정사항
- 📅 중요 날짜

## 🚀 빠른 시작

### 방법 1: 웹 인터페이스 사용 (추천!)

#### 1단계: API 키 발급

**Google Gemini API Key (필수)**
1. https://aistudio.google.com/app/apikey 접속
2. Google 계정으로 로그인
3. "Create API Key" 클릭
4. API 키 복사
5. **무료 한도**: 분당 15회, 하루 1,500회 요청

**Cal.com API Key (필수)**
1. https://app.cal.com 접속 (공식 Cal.com 사용)
2. Settings → Developer → API Keys 이동
3. "Create New API Key" 클릭
4. API 키 복사

> **참고**: Cal.com 셀프호스팅은 복잡하고 에러가 많습니다. **공식 Cal.com 사용을 강력히 권장**합니다!

#### 2단계: 설치 및 설정

```bash
# 저장소 클론
git clone https://github.com/chaninjung/meeting-notes-automation.git
cd meeting-notes-automation

# .env 파일 수정
nano .env
# 또는
vim .env
```

`.env` 파일에서 API 키 입력:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
CALCOM_API_KEY=your_calcom_api_key_here
CALCOM_BASE_URL=https://api.cal.com/v1
TIMEZONE=Asia/Seoul
```

#### 3단계: 실행

**Docker 사용 (추천)**
```bash
# Docker Compose로 실행
docker compose up -d

# 로그 확인
docker compose logs -f
```

**Python 직접 실행**
```bash
# 패키지 설치
pip install -r requirements.txt

# 웹 서버 실행
python app.py
```

#### 4단계: 사용하기

1. 브라우저에서 http://localhost:5000 접속
2. 회의록 텍스트 입력 또는 붙여넣기
3. "📅 Cal.com에 자동으로 등록하기" 체크
4. "🚀 분석 및 등록하기" 버튼 클릭
5. 결과 확인!

---

### 방법 2: 커맨드라인 사용

```bash
# 패키지 설치
pip install -r requirements.txt

# 회의록 txt 파일을 input/ 폴더에 넣기
cp my_meeting_notes.txt input/

# 실행!
python src/main.py
```

## 📖 사용 방법

### 웹 인터페이스 (추천)

1. **서버 실행**
   ```bash
   # Docker 사용
   docker compose up -d

   # 또는 Python 직접 실행
   python app.py
   ```

2. **브라우저 접속**
   - http://localhost:5000

3. **회의록 입력**
   - 텍스트 입력창에 회의록 붙여넣기
   - 또는 직접 입력

4. **분석 및 등록**
   - "📅 Cal.com에 자동으로 등록하기" 체크 (원하는 경우)
   - "🚀 분석 및 등록하기" 버튼 클릭

5. **결과 확인**
   - 분석 결과가 화면에 표시됩니다
   - Cal.com에 자동으로 등록됩니다

### 커맨드라인 인터페이스

#### 기본 사용 (한번 실행)

```bash
python src/main.py
```

`input/` 폴더의 모든 txt 파일을 처리하고, Cal.com에 동기화합니다.

#### 감시 모드 (자동 처리)

```bash
python src/main.py --mode watch
```

`input/` 폴더를 감시하다가 새 txt 파일이 추가되면 자동으로 처리합니다.

#### 분석만 (동기화 안함)

```bash
python src/main.py --no-sync
```

회의록 분석만 수행하고 Cal.com에는 등록하지 않습니다. (테스트용)

#### 특정 파일만 처리

```bash
python src/main.py --file input/meeting_2024.txt
```

## 📁 프로젝트 구조

```
meeting-notes-automation/
├── .env.example              # API 키 설정 예시
├── .env                      # 실제 API 키 (git에 추가 안됨)
├── app.py                    # Flask 웹 애플리케이션
├── Dockerfile                # Docker 이미지 빌드 설정
├── docker-compose.yml        # Docker Compose 설정
├── requirements.txt          # Python 패키지
├── templates/                # 웹 UI 템플릿
│   └── index.html           # 메인 페이지
├── input/                    # 회의록 txt 파일을 넣는 곳 (CLI 모드)
├── processed/                # 처리된 파일과 분석 결과 보관
├── src/
│   ├── gemini_analyzer.py   # Gemini AI 분석 모듈
│   ├── calcom_client.py     # Cal.com API 클라이언트
│   └── main.py              # CLI 자동화 스크립트
└── README.md
```

## 💡 회의록 작성 팁

분석 정확도를 높이려면:

```
회의 제목: 2024년 1월 프로젝트 회의

날짜: 2024-01-22
참석자: 김철수, 박영희, 이민준

완료한 작업:
- 백엔드 API 개발 완료 (김철수)
- UI 디자인 초안 작성 (박영희)

해야 할 일:
- 프론트엔드 개발 시작 (이민준) - 마감: 1월 26일
- API 테스트 및 버그 수정 (김철수) - 높은 우선순위

다음 미팅:
- 날짜: 2024년 1월 29일
- 시간: 오후 2시
- 장소: 회의실 A

주요 결정사항:
- 베타 테스트 2월 5일 시작
```

## 🔧 고급 사용법

### 개별 모듈 테스트

```bash
# Gemini 분석만 테스트
cd src
export GEMINI_API_KEY=your_key
python3 gemini_analyzer.py

# Reclaim 연동만 테스트
export CALCOM_API_KEY=your_key
export CALCOM_BASE_URL=http://localhost:3000
python3 calcom_client.py
```

### 분석 결과 확인

처리된 파일은 `processed/` 폴더에 저장됩니다:
- `*_analysis.json`: 분석 결과 (JSON)
- `*.txt`: 원본 회의록

## 💰 비용

완전 **무료**입니다!

- **Gemini API**: 무료 티어로 하루 1,500회 요청 가능
- **Cal.com**: 무료 플랜 사용 가능 (공식 서비스)
- **서버**: 로컬에서 실행 (서버 비용 없음)

일일 회의록 10개 정도는 무료 한도 내에서 충분히 처리 가능합니다.

## 🛠️ 문제 해결

### API 키 오류
```bash
❌ GEMINI_API_KEY가 설정되지 않았습니다.
```
→ `config/.env` 파일에 API 키가 제대로 입력되었는지 확인

### Python 패키지 오류
```bash
ModuleNotFoundError: No module named 'google.generativeai'
```
→ 가상환경 활성화 및 패키지 재설치:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Cal.com 동기화 오류
- Cal.com이 실행 중인지 확인: `docker compose -f docker-compose.calcom.yml ps`
- API 키가 유효한지 확인
- 인터넷 연결 확인
- `docs/CALCOM_SETUP.md` 문제 해결 섹션 참고

## 📝 라이선스

MIT License - 자유롭게 사용하세요!

## 🤝 기여

버그 리포트, 기능 제안, PR 모두 환영합니다!

## 📧 문의

Issues 탭에서 질문하시면 답변드리겠습니다.

---

**Made with ❤️ by Claude Code**
