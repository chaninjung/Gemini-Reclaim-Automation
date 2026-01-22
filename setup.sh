#!/bin/bash
# 회의록 자동화 시스템 설정 스크립트

set -e

echo "======================================"
echo "회의록 자동화 시스템 설정 시작"
echo "======================================"
echo ""

# Python 버전 확인
echo "1️⃣  Python 버전 확인..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3가 설치되어 있지 않습니다."
    echo "   Python 3.8 이상을 설치해주세요."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "   ✅ Python $PYTHON_VERSION 설치됨"
echo ""

# 가상환경 생성
echo "2️⃣  Python 가상환경 생성..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✅ 가상환경 생성 완료"
else
    echo "   ℹ️  가상환경이 이미 존재합니다"
fi
echo ""

# 가상환경 활성화
echo "3️⃣  가상환경 활성화..."
source venv/bin/activate
echo "   ✅ 가상환경 활성화됨"
echo ""

# 패키지 설치
echo "4️⃣  필요한 패키지 설치 중..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "   ✅ 패키지 설치 완료"
echo ""

# .env 파일 설정
echo "5️⃣  환경 변수 파일 설정..."
if [ ! -f "config/.env" ]; then
    cp config/.env.example config/.env
    echo "   ✅ config/.env 파일 생성됨"
    echo ""
    echo "⚠️  중요: config/.env 파일을 열고 API 키를 설정해주세요!"
    echo ""
    echo "   필요한 API 키:"
    echo "   1. GEMINI_API_KEY - https://aistudio.google.com/app/apikey"
    echo "   2. RECLAIM_API_TOKEN - https://reclaim.ai (Settings → Integrations → API)"
    echo ""
else
    echo "   ℹ️  config/.env 파일이 이미 존재합니다"
fi
echo ""

# 실행 권한 설정
echo "6️⃣  실행 권한 설정..."
chmod +x src/main.py
echo "   ✅ 실행 권한 설정 완료"
echo ""

echo "======================================"
echo "✨ 설정 완료!"
echo "======================================"
echo ""
echo "다음 단계:"
echo "1. config/.env 파일을 열고 API 키를 설정하세요"
echo "2. 가상환경 활성화: source venv/bin/activate"
echo "3. 테스트 실행: python3 src/main.py"
echo ""
echo "사용법:"
echo "  - 한번 실행: python3 src/main.py"
echo "  - 감시 모드: python3 src/main.py --mode watch"
echo "  - 분석만: python3 src/main.py --no-sync"
echo ""
