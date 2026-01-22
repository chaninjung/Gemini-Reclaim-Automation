# 📖 상세 사용 가이드

## 🎯 이 시스템은 이렇게 작동합니다

1. **회의록 작성**: 클로바노트, Google Docs 등에서 회의 내용을 txt로 저장
2. **파일 업로드**: `input/` 폴더에 txt 파일 넣기
3. **자동 분석**: Google Gemini AI가 회의록을 분석해서:
   - 완료한 작업 찾기
   - 해야 할 작업 (TODO) 추출
   - 스케줄 일정 파악
   - 중요 날짜 인식
   - 참석자 및 결정사항 정리
4. **자동 등록**: Reclaim.ai에 태스크와 일정으로 자동 등록
5. **결과 저장**: `processed/` 폴더에 분석 결과 저장

## 🚀 시작하기

### Step 1: 설치

```bash
# 프로젝트 클론
git clone https://github.com/chaninjung/Gemini-Reclaim-Automation.git
cd Gemini-Reclaim-Automation

# 자동 설정
chmod +x setup.sh
./setup.sh
```

### Step 2: API 키 설정

#### Gemini API 키 발급 (무료)
1. https://aistudio.google.com/app/apikey 접속
2. Google 계정으로 로그인
3. "Create API Key" 버튼 클릭
4. 생성된 API 키 복사

**무료 한도:**
- 분당 15회 요청
- 하루 1,500회 요청
- 개인 사용에 충분한 양!

#### Reclaim.ai API 토큰 발급
1. https://reclaim.ai 접속 및 가입
2. 설정(Settings) → 통합(Integrations) → API 이동
3. "Generate API Token" 클릭
4. 생성된 토큰 복사

#### .env 파일에 키 입력
```bash
# config/.env 파일 열기
nano config/.env
# 또는
code config/.env
# 또는
vim config/.env
```

다음 내용 입력:
```
GEMINI_API_KEY=여기에_Gemini_API_키_붙여넣기
RECLAIM_API_TOKEN=여기에_Reclaim_토큰_붙여넣기
TIMEZONE=Asia/Seoul
```

### Step 3: 실행

```bash
# 가상환경 활성화
source venv/bin/activate

# 회의록 파일 준비 (예시 파일 사용)
# input/example_meeting.txt 파일이 이미 준비되어 있습니다!

# 실행!
python3 src/main.py
```

## 📝 회의록 작성 가이드

### 좋은 회의록 예시

```text
2024년 1월 22일 프로젝트 회의

참석자: 김철수, 박영희, 이민준

완료한 작업:
- API 개발 완료 (김철수)
- 디자인 초안 작성 (박영희)

해야 할 일:
- 프론트엔드 개발 (이민준) - 마감: 2024-01-26
- 테스트 진행 (김철수) - 높은 우선순위

다음 미팅:
- 날짜: 2024-01-29
- 시간: 14:00
- 소요시간: 1시간

주요 결정:
- 베타 테스트 2월 5일 시작
- 주간 회의 매주 월요일 2시
```

### 인식되는 키워드

**완료한 작업:**
- "완료", "완성", "끝냄", "마침"
- "Done", "Completed", "Finished"

**해야 할 일:**
- "해야 할", "할 일", "TODO", "Action Item"
- "예정", "계획"

**날짜 표현:**
- "2024-01-22" (권장)
- "2024년 1월 22일"
- "1월 22일"

**우선순위:**
- "높은 우선순위", "긴급", "중요"
- "보통", "일반"
- "낮은 우선순위"

**시간 표현:**
- "14:00", "오후 2시", "2시"

## 🎨 실행 모드

### 1. 기본 모드 (한번 실행)
```bash
python3 src/main.py
```
- `input/` 폴더의 모든 txt 파일 처리
- 분석 후 Reclaim.ai에 자동 등록
- 처리된 파일은 `processed/`로 이동

### 2. 감시 모드 (자동 처리)
```bash
python3 src/main.py --mode watch
```
- `input/` 폴더를 계속 감시
- 새 txt 파일이 추가되면 자동으로 처리
- 종료: Ctrl+C

**사용 시나리오:**
- 회의가 끝나면 바로 txt 파일을 input/ 폴더에 드래그앤드롭
- 자동으로 분석되고 Reclaim.ai에 등록됨!

### 3. 분석만 모드 (동기화 안함)
```bash
python3 src/main.py --no-sync
```
- 회의록 분석만 수행
- Reclaim.ai에 등록하지 않음
- 테스트용으로 좋음

### 4. 특정 파일만 처리
```bash
python3 src/main.py --file input/meeting_2024.txt
```
- 지정한 파일만 처리

## 📊 결과 확인

### 콘솔 출력
```
============================================================
📋 회의록 분석 결과
============================================================

📝 전체 요약:
  프로젝트 킥오프 회의로 역할 분담 및 일정 확정...

✅ 완료된 작업:
  - 시장 조사 및 경쟁사 분석 완료 (최지은)
  - 기술 스택 검토 및 선정 완료 (이민준)

📌 해야 할 작업:
  🔴 상세 기능 명세서 작성 (김철수) [마감: 2024-01-24]
  🟡 UI/UX 디자인 시안 제작 (박영희) [마감: 2024-01-26]

📅 예정된 일정:
  - 주간 스탠드업 미팅 [2024-01-29 10:00] (30분)

============================================================

📤 Reclaim.ai 동기화 결과
============================================================

✅ 생성된 태스크 (4개):
  - 태스크 생성 완료: 상세 기능 명세서 작성
  - 태스크 생성 완료: UI/UX 디자인 시안 제작
  ...

📅 생성된 이벤트 (1개):
  - 이벤트 생성 완료: 주간 스탠드업 미팅 (2024-01-29 10:00)

총 5개 항목이 Reclaim.ai에 추가되었습니다.
============================================================
```

### 저장된 파일

`processed/` 폴더에 다음 파일들이 저장됩니다:

1. **원본 회의록**: `example_meeting_20240122_153045.txt`
2. **분석 결과 JSON**: `example_meeting_20240122_153045_analysis.json`

JSON 파일 내용:
```json
{
  "summary": "프로젝트 킥오프 회의로...",
  "completed_tasks": [...],
  "todo_tasks": [...],
  "schedule_items": [...],
  "participants": [...],
  "key_decisions": [...]
}
```

## 🔄 일상적인 사용 흐름

### 매일 회의 후
```bash
# 1. 회의록을 txt로 저장 (클로바노트 등에서 다운로드)
# 2. input/ 폴더에 복사

# 3. 감시 모드로 실행 (아침에 한번만)
source venv/bin/activate
python3 src/main.py --mode watch

# 이후로는 파일만 input/에 넣으면 자동 처리!
```

### 주간 정리
```bash
# processed/ 폴더의 JSON 파일들을 확인
# 지난 주에 무엇을 했는지 한눈에 파악!

ls -lt processed/*.json | head -10
```

## ⚙️ 고급 설정

### 타임존 변경
```bash
# config/.env
TIMEZONE=America/New_York  # 뉴욕
TIMEZONE=Europe/London     # 런던
TIMEZONE=Asia/Tokyo        # 도쿄
```

### Python 가상환경 수동 설정
```bash
# 가상환경 생성
python3 -m venv venv

# 활성화 (Linux/Mac)
source venv/bin/activate

# 활성화 (Windows)
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

## 🐛 문제 해결

### "GEMINI_API_KEY가 설정되지 않았습니다"
→ `config/.env` 파일이 제대로 생성되었는지 확인
→ API 키에 공백이나 따옴표가 없는지 확인

### "ModuleNotFoundError"
```bash
# 가상환경 활성화 확인
source venv/bin/activate

# 패키지 재설치
pip install -r requirements.txt
```

### Reclaim.ai 동기화 실패
- API 토큰이 유효한지 확인
- 인터넷 연결 확인
- Reclaim.ai 웹사이트에서 계정 상태 확인

### 분석 결과가 이상함
- 회의록에 명확한 키워드 사용 ("완료", "해야 할 일", "날짜" 등)
- 날짜는 YYYY-MM-DD 형식 권장
- 구조화된 형식으로 작성 (섹션 나누기)

## 💡 팁

1. **회의록 템플릿 만들기**: input/example_meeting.txt를 템플릿으로 사용
2. **정기 회의는 감시 모드**: 매일 아침 감시 모드로 실행해두기
3. **분석 결과 확인**: --no-sync로 먼저 테스트 후 실제 동기화
4. **JSON 파일 보관**: 나중에 검색이나 리포팅에 활용

## 📈 활용 아이디어

### 1. 주간 회의록 자동 정리
```bash
# 매주 월요일 회의 후
cp "Monday_Meeting.txt" input/
python3 src/main.py
# → 자동으로 이번 주 할 일이 Reclaim.ai에 등록!
```

### 2. 1on1 미팅 관리
```bash
# 팀원과의 1on1 후
cp "1on1_김철수.txt" input/
python3 src/main.py
# → 팀원별 액션 아이템이 자동 트래킹됨
```

### 3. 프로젝트 킥오프
```bash
# 킥오프 미팅 후
cp "Project_Kickoff.txt" input/
python3 src/main.py
# → 전체 프로젝트 일정과 태스크가 한번에 등록
```

## 🎓 더 배우기

### 모듈별 테스트

```bash
# Gemini 분석기만 테스트
cd src
export GEMINI_API_KEY=your_key
python3 gemini_analyzer.py

# Reclaim 클라이언트만 테스트
export RECLAIM_API_TOKEN=your_token
python3 reclaim_client.py
```

### 코드 수정

각 모듈은 독립적으로 작동하므로 쉽게 커스터마이징 가능:

- `src/gemini_analyzer.py`: 분석 프롬프트 수정
- `src/reclaim_client.py`: Reclaim.ai 연동 방식 수정
- `src/main.py`: 파일 처리 로직 수정

---

**더 궁금한 점이 있다면 Issues에 남겨주세요!**
