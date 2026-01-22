# 🤖 Gemini-Reclaim-Automation

**완전 무료** 회의록 자동 분석 & 스케줄 관리 시스템

클로바노트 등에서 다운받은 회의록 텍스트를 AI가 자동으로 분석해서 Reclaim.ai에 태스크와 일정으로 등록해줍니다!

## ✨ 주요 기능

- 📝 **회의록 자동 분석**: Google Gemini AI로 회의록에서 중요 정보 추출
- 📅 **자동 스케줄링**: 분석 결과를 Reclaim.ai에 자동으로 태스크/이벤트 등록
- 💰 **완전 무료**: Gemini 무료 티어 사용 (일 1,500회 요청)
- 🚀 **간편한 사용**: txt 파일만 넣으면 끝!

## 🎯 분석 내용

- ✅ 완료된 작업
- 📌 해야 할 작업 (TODO)
- 📆 예정된 일정
- 👥 참석자
- 💡 주요 결정사항
- 📅 중요 날짜

## 🚀 빠른 시작

### 1단계: API 키 발급 (무료!)

#### Google Gemini API Key
1. https://aistudio.google.com/app/apikey 접속
2. Google 계정으로 로그인
3. "Create API Key" 클릭
4. API 키 복사
5. **무료 한도**: 분당 15회, 하루 1,500회 요청

#### Reclaim.ai API Token
1. https://reclaim.ai 가입
2. Settings → Integrations → API 이동
3. API 토큰 생성 및 복사

### 2단계: 설치

```bash
# 저장소 클론
git clone https://github.com/chaninjung/Gemini-Reclaim-Automation.git
cd Gemini-Reclaim-Automation

# 자동 설정 스크립트 실행
chmod +x setup.sh
./setup.sh
```

### 3단계: API 키 설정

`config/.env` 파일을 열고 API 키 입력:

```bash
# config/.env
GEMINI_API_KEY=your_gemini_api_key_here
RECLAIM_API_TOKEN=your_reclaim_api_token_here
TIMEZONE=Asia/Seoul
```

### 4단계: 사용하기

```bash
# 가상환경 활성화
source venv/bin/activate

# 회의록 txt 파일을 input/ 폴더에 넣기
cp my_meeting_notes.txt input/

# 실행!
python3 src/main.py
```

## 📖 사용 방법

### 기본 사용 (한번 실행)

```bash
python3 src/main.py
```

`input/` 폴더의 모든 txt 파일을 처리하고, Reclaim.ai에 동기화합니다.

### 감시 모드 (자동 처리)

```bash
python3 src/main.py --mode watch
```

`input/` 폴더를 감시하다가 새 txt 파일이 추가되면 자동으로 처리합니다.

### 분석만 (동기화 안함)

```bash
python3 src/main.py --no-sync
```

회의록 분석만 수행하고 Reclaim.ai에는 등록하지 않습니다. (테스트용)

### 특정 파일만 처리

```bash
python3 src/main.py --file input/meeting_2024.txt
```

## 📁 프로젝트 구조

```
Gemini-Reclaim-Automation/
├── config/
│   ├── .env.example          # API 키 설정 예시
│   └── .env                  # 실제 API 키 (git에 추가 안됨)
├── input/                    # 회의록 txt 파일을 넣는 곳
├── processed/                # 처리된 파일과 분석 결과 보관
├── src/
│   ├── gemini_analyzer.py   # Gemini AI 분석 모듈
│   ├── reclaim_client.py    # Reclaim.ai API 클라이언트
│   └── main.py              # 메인 자동화 스크립트
├── requirements.txt         # Python 패키지
├── setup.sh                 # 자동 설정 스크립트
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
export RECLAIM_API_TOKEN=your_token
python3 reclaim_client.py
```

### 분석 결과 확인

처리된 파일은 `processed/` 폴더에 저장됩니다:
- `*_analysis.json`: 분석 결과 (JSON)
- `*.txt`: 원본 회의록

## 💰 비용

완전 **무료**입니다!

- **Gemini API**: 무료 티어로 하루 1,500회 요청 가능
- **Reclaim.ai**: 무료 플랜 사용 가능
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

### Reclaim.ai 동기화 오류
- API 토큰이 유효한지 확인
- 인터넷 연결 확인
- Reclaim.ai 계정이 활성화되어 있는지 확인

## 📝 라이선스

MIT License - 자유롭게 사용하세요!

## 🤝 기여

버그 리포트, 기능 제안, PR 모두 환영합니다!

## 📧 문의

Issues 탭에서 질문하시면 답변드리겠습니다.

---

**Made with ❤️ by Claude Code**
