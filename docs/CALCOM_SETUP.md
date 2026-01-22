# Cal.com Self-Hosting Setup Guide

이 가이드는 Docker를 사용하여 Cal.com을 로컬에서 셀프호스팅하는 방법을 안내합니다.

## 📋 사전 요구사항

### 1. Docker 설치 확인

```bash
# Docker 버전 확인
docker --version

# Docker Compose 버전 확인
docker compose version
```

Docker가 설치되어 있지 않다면:
- **Ubuntu/Debian**: `sudo apt-get install docker.io docker-compose-plugin`
- **macOS**: [Docker Desktop](https://www.docker.com/products/docker-desktop) 설치
- **Windows**: [Docker Desktop](https://www.docker.com/products/docker-desktop) 설치

### 2. 시스템 요구사항

- **RAM**: 최소 2GB (권장 4GB)
- **디스크 공간**: 최소 10GB
- **포트**: 3000, 5433, 5555가 사용 가능해야 함

## 🚀 Cal.com 배포하기

### 1단계: 보안 키 생성

Cal.com은 두 개의 보안 키가 필요합니다:

```bash
# NEXTAUTH_SECRET 생성
openssl rand -base64 32

# CALENDSO_ENCRYPTION_KEY 생성
openssl rand -base64 24
```

생성된 키를 복사해두세요!

### 2단계: Docker Compose 파일 수정

`docker-compose.calcom.yml` 파일을 열고 다음 값들을 수정하세요:

```yaml
# 1단계에서 생성한 키로 변경
NEXTAUTH_SECRET: <첫번째_생성한_키>
CALENDSO_ENCRYPTION_KEY: <두번째_생성한_키>

# 데이터베이스 비밀번호 변경 (선택사항)
POSTGRES_PASSWORD: <강력한_비밀번호>
DATABASE_URL: postgresql://calcom:<강력한_비밀번호>@calcom-database:5432/calcom
```

### 3단계: Cal.com 시작

```bash
# Docker Compose로 Cal.com 시작
docker compose -f docker-compose.calcom.yml up -d

# 로그 확인 (문제 발생 시)
docker compose -f docker-compose.calcom.yml logs -f calcom
```

첫 실행 시 이미지 다운로드와 데이터베이스 초기화로 인해 3-5분 정도 걸릴 수 있습니다.

### 4단계: Cal.com 접속 및 초기 설정

1. 브라우저에서 http://localhost:3000 접속
2. **Setup Wizard**가 나타나면:
   - 이름 입력
   - 이메일 주소 입력 (로그인 ID로 사용됨)
   - 비밀번호 설정
   - 타임존 확인 (Asia/Seoul)
3. **완료!** 이제 Cal.com 대시보드가 표시됩니다.

## 🔑 API 키 생성

자동화 스크립트에서 Cal.com API를 사용하려면 API 키가 필요합니다:

1. Cal.com에 로그인
2. **Settings** (설정) → **Developer** → **API Keys** 이동
3. **Create New API Key** 클릭
4. 키 이름 입력 (예: "Gemini Automation")
5. **Create** 클릭
6. 생성된 API 키를 **안전한 곳에 복사** (한 번만 표시됨!)

## 📝 환경 변수 설정

`config/.env` 파일에 Cal.com 설정 추가:

```bash
# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Cal.com Configuration
CALCOM_API_KEY=<생성한_API_키>
CALCOM_BASE_URL=http://localhost:3000
CALCOM_USER_ID=<사용자_ID>  # Settings → Profile에서 확인 가능

# Timezone
TIMEZONE=Asia/Seoul
```

### 사용자 ID 찾기

1. Cal.com에서 **Settings** → **Profile** 이동
2. URL을 확인: `http://localhost:3000/settings/my-account/profile`
3. 또는 API로 확인:
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" \
        http://localhost:3000/api/v2/me
   ```

## 🛠️ 유용한 명령어

```bash
# Cal.com 중지
docker compose -f docker-compose.calcom.yml stop

# Cal.com 재시작
docker compose -f docker-compose.calcom.yml restart

# Cal.com 완전 제거 (데이터 포함)
docker compose -f docker-compose.calcom.yml down -v

# 로그 실시간 확인
docker compose -f docker-compose.calcom.yml logs -f

# Prisma Studio 접속 (데이터베이스 관리)
# 브라우저에서 http://localhost:5555 접속
```

## 🔍 문제 해결

### Cal.com이 시작되지 않는 경우

```bash
# 컨테이너 상태 확인
docker compose -f docker-compose.calcom.yml ps

# 로그 확인
docker compose -f docker-compose.calcom.yml logs calcom

# 데이터베이스 연결 확인
docker compose -f docker-compose.calcom.yml logs calcom-database
```

### 포트 충돌 오류

다른 서비스가 포트를 사용 중이라면 `docker-compose.calcom.yml`에서 포트 번호를 변경:

```yaml
ports:
  - "3001:3000"  # 3000 대신 3001 사용
```

### 데이터베이스 초기화 오류

```bash
# 모든 것을 제거하고 다시 시작
docker compose -f docker-compose.calcom.yml down -v
docker compose -f docker-compose.calcom.yml up -d
```

## 📚 추가 리소스

- [Cal.com 공식 문서](https://cal.com/docs)
- [Cal.com API 문서](https://cal.com/docs/api-reference)
- [Cal.com GitHub](https://github.com/calcom/cal.com)

## ⚠️ 라이선스 주의사항

Cal.com은 **AGPLv3** 라이선스를 사용합니다:
- 오픈소스 프로젝트로 자유롭게 사용 가능
- 네트워크를 통해 서비스를 제공하는 경우 소스코드 공개 의무
- 상업적 사용 시 라이선스 제약 없이 사용하려면 [상업 라이선스](https://cal.com/sales) 필요

개인 사용 및 내부 도구로 사용하는 경우 문제없습니다!
