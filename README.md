# Smart Scheduler v2

AI 기반 회의록 자동 분석 및 일정 관리 시스템

[English](./README.en.md)

## 개요

Smart Scheduler v2는 Google Gemini AI를 활용하여 회의록을 자동으로 분석하고, 추출된 정보를 통합 캘린더에 등록하는 웹 기반 일정 관리 시스템입니다. 회의록에서 태스크, 일정, 핵심 정보를 자동으로 추출하여 효율적인 업무 관리를 지원합니다.

## 주요 기능

### AI 기반 자동 분석
- Google Gemini 2.5 Flash 모델을 활용한 회의록 분석
- 회의 요약, 태스크, 일정, 참석자, 결정사항 자동 추출
- 상대적 날짜 표현 자동 변환 ("1월 말까지" → `2026-01-31`)
- 부서명 자동 인식 및 태스크/일정 제목에 자동 추가

### 통합 캘린더 관리
- FullCalendar 기반 직관적인 일정 관리 인터페이스
- Summary, Tasks, Meetings 통합 관리
- 이벤트 타입별 색상 구분 (Summary: 파란색, Task: 노란색, Meeting: 초록색)
- 드래그 앤 드롭으로 일정 조정

### Context 링크 시스템
- 태스크 및 일정과 원본 회의록 자동 연결
- 이벤트 클릭 시 관련 회의록 즉시 확인
- 수동 Context 링크 설정 기능

### 고급 편집 기능
- Toast UI Editor 기반 Markdown 편집
- 전체화면 에디터 모드 지원
- 실시간 미리보기

### 데이터 관리
- JSON 기반 로컬 데이터베이스
- 자동 백업 생성 (타임스탬프 포함)
- 이벤트 CRUD 작업 지원

## 시스템 요구사항

- Python 3.8 이상
- Docker 및 Docker Compose (선택사항)
- Google Gemini API 키
- 최신 웹 브라우저 (Chrome, Firefox, Safari, Edge)

## 설치 및 실행

### 1. 저장소 클론

```bash
git clone https://github.com/chaninjung/meeting-notes-automation.git
cd meeting-notes-automation
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 입력합니다:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

**Gemini API 키 발급 방법:**
1. https://aistudio.google.com/app/apikey 접속
2. Google 계정으로 로그인
3. "Create API Key" 클릭
4. 생성된 API 키 복사

### 3. 실행 방법

#### Docker 사용 (권장)

```bash
docker compose up -d
```

#### Python 직접 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python app.py
```

### 4. 접속

웹 브라우저에서 http://localhost:5000 접속

## 사용 방법

### 회의록 분석

1. **회의록 입력**: 좌측 패널의 "Meeting Notes" 영역에 회의록 텍스트 입력
2. **분석 실행**: "Analyze Notes" 버튼 클릭
3. **결과 확인**: Staging Area에서 분석 결과 확인 및 수정
4. **캘린더 등록**: "Add to Calendar" 버튼 클릭하여 이벤트 등록

### Staging Area 활용

분석 결과는 다음 세 가지 카테고리로 구분됩니다:

- **Meeting Summary**: 회의 요약 (제목, 날짜, 내용 수정 가능)
- **Tasks**: 해야 할 작업 (제목, 날짜, 시간, 우선순위 조정)
- **Meetings**: 예정된 일정 (제목, 날짜, 시간 설정)

각 항목은 체크박스로 선택/해제하여 캘린더 등록 여부를 결정할 수 있습니다.

### 이벤트 관리

- **조회**: 캘린더에서 이벤트 클릭
- **수정**: 이벤트 상세 모달에서 "Edit Event" 클릭
- **삭제**: 편집 모달에서 "Delete Event" 클릭
- **Context 연결**: 편집 모달의 "Linked Context" 드롭다운에서 관련 회의록 선택

## 회의록 작성 가이드

분석 정확도를 높이기 위한 권장 형식:

```markdown
# 회의록 - [부서명]

**일시:** YYYY년 MM월 DD일
**시간:** HH:MM - HH:MM
**참석자:** [참석자 목록]

## 논의 사항

1. **[주제 1]**
   - 세부 내용
   - 마감일: [날짜]
   - 담당자: [이름]

2. **[주제 2]**
   - 세부 내용

## 결정 사항

- [결정 내용 1]
- [결정 내용 2]

## 다음 일정

- 날짜: [날짜]
- 시간: [시간]
```

## API 문서

### POST /analyze

회의록 텍스트를 분석합니다.

**Request Body:**
```json
{
  "text": "회의록 내용..."
}
```

**Response:**
```json
{
  "meeting_title": "회의주제/부서명/YY-MM-DD",
  "meeting_date": "YYYY-MM-DD",
  "department_name": "부서명",
  "summary": "마크다운 형식 요약",
  "todo_tasks": [...],
  "schedule_items": [...]
}
```

### GET /events

저장된 모든 이벤트를 조회합니다.

### POST /events

새 이벤트를 생성합니다.

### PUT /events/<id>

특정 이벤트를 수정합니다.

### DELETE /events/<id>

특정 이벤트를 삭제합니다.

## 프로젝트 구조

```
meeting-notes-automation/
├── .env                    # 환경 변수
├── app.py                  # Flask 백엔드 서버
├── docker-compose.yml      # Docker Compose 설정
├── requirements.txt        # Python 의존성
├── data/
│   ├── db.json            # 이벤트 데이터베이스
│   └── backups/           # 자동 백업
├── src/
│   └── gemini_analyzer.py # Gemini AI 분석 모듈
└── templates/
    └── index.html         # 프론트엔드 UI
```

## 기술 스택

### Backend
- Python 3.8+
- Flask 3.0.0
- Google Generative AI (Gemini 2.5 Flash)

### Frontend
- HTML5, CSS3, JavaScript (ES6+)
- Tailwind CSS 3.x
- FullCalendar 6.1.10
- Toast UI Editor
- Marked.js (Markdown 파싱)

## 비용 정보

본 시스템은 무료로 사용 가능합니다:

- **Gemini API**: 무료 티어 (일 1,500회 요청)
- **서버**: 로컬 실행 (별도 서버 비용 없음)

일반적인 사용 환경에서 일일 10~20개의 회의록 분석이 무료 한도 내에서 가능합니다.

## 문제 해결

### API 키 오류

```
Error: GEMINI_API_KEY가 설정되지 않았습니다.
```

**해결 방법**: `.env` 파일에 올바른 API 키가 입력되었는지 확인

### 의존성 오류

```
ModuleNotFoundError: No module named 'google.generativeai'
```

**해결 방법**:
```bash
pip install -r requirements.txt
```

### 포트 충돌

```
Error: Address already in use
```

**해결 방법**:
```bash
PORT=8080 python app.py
```

## 라이선스

MIT License

Copyright (c) 2026

본 소프트웨어는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](./LICENSE) 파일을 참조하십시오.

## 기여

버그 리포트 및 기능 제안은 [Issues](https://github.com/chaninjung/meeting-notes-automation/issues)를 통해 제출해 주시기 바랍니다.

Pull Request는 언제나 환영합니다.

## 문의

프로젝트 관련 문의사항은 Issues 탭을 이용해 주시기 바랍니다.

## 개발자

**nini** - Initial work and development

---

**Powered by Google Gemini AI**
