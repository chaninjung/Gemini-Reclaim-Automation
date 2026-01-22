#!/bin/bash

# Cal.com 설정 스크립트
# config/.env 파일을 대화형으로 생성합니다

set -e

echo "=========================================="
echo "  Cal.com Automation 설정 스크립트"
echo "=========================================="
echo ""

CONFIG_DIR="config"
ENV_FILE="$CONFIG_DIR/.env"

# config 디렉토리 확인
if [ ! -d "$CONFIG_DIR" ]; then
    echo "❌ config 디렉토리를 찾을 수 없습니다."
    exit 1
fi

# 기존 .env 파일 백업
if [ -f "$ENV_FILE" ]; then
    BACKUP_FILE="$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "📦 기존 .env 파일을 백업합니다: $BACKUP_FILE"
    cp "$ENV_FILE" "$BACKUP_FILE"
    echo ""
fi

echo "📝 API 키를 입력해주세요:"
echo ""

# Gemini API Key 입력
echo "1️⃣  Google Gemini API Key"
echo "   발급: https://aistudio.google.com/app/apikey"
read -p "   입력: " GEMINI_KEY

if [ -z "$GEMINI_KEY" ]; then
    echo "❌ Gemini API Key는 필수입니다."
    exit 1
fi

echo ""

# Cal.com API Key 입력
echo "2️⃣  Cal.com API Key"
echo "   발급: http://localhost:3000 → Settings → Developer → API Keys"
read -p "   입력: " CALCOM_KEY

if [ -z "$CALCOM_KEY" ]; then
    echo "❌ Cal.com API Key는 필수입니다."
    exit 1
fi

echo ""

# Cal.com Base URL 입력
echo "3️⃣  Cal.com Base URL"
read -p "   입력 (기본값: http://localhost:3000): " CALCOM_URL
CALCOM_URL=${CALCOM_URL:-http://localhost:3000}

echo ""

# Cal.com User ID 입력 (선택사항)
echo "4️⃣  Cal.com User ID (선택사항)"
echo "   확인: Cal.com → Settings → Profile"
read -p "   입력 (Enter로 건너뛰기): " CALCOM_USER_ID

echo ""

# Timezone 입력
echo "5️⃣  Timezone"
read -p "   입력 (기본값: Asia/Seoul): " TIMEZONE
TIMEZONE=${TIMEZONE:-Asia/Seoul}

echo ""
echo "=========================================="
echo "  설정 파일 생성 중..."
echo "=========================================="

# .env 파일 생성
cat > "$ENV_FILE" << EOF
# Google Gemini API Key
# Get it from: https://aistudio.google.com/app/apikey
# Free tier: 15 requests/min, 1,500 requests/day
GEMINI_API_KEY=$GEMINI_KEY

# Cal.com Configuration
# Self-hosted Cal.com instance
# See docs/CALCOM_SETUP.md for setup instructions
CALCOM_API_KEY=$CALCOM_KEY
CALCOM_BASE_URL=$CALCOM_URL
EOF

# User ID가 있으면 추가
if [ -n "$CALCOM_USER_ID" ]; then
    echo "CALCOM_USER_ID=$CALCOM_USER_ID" >> "$ENV_FILE"
fi

# Timezone 추가
cat >> "$ENV_FILE" << EOF

# Optional: Set timezone for scheduling (default: Asia/Seoul)
TIMEZONE=$TIMEZONE
EOF

echo ""
echo "✅ 설정 파일이 생성되었습니다: $ENV_FILE"
echo ""
echo "📋 설정 내용:"
echo "   - Gemini API Key: ${GEMINI_KEY:0:20}..."
echo "   - Cal.com API Key: ${CALCOM_KEY:0:20}..."
echo "   - Cal.com URL: $CALCOM_URL"
if [ -n "$CALCOM_USER_ID" ]; then
    echo "   - Cal.com User ID: $CALCOM_USER_ID"
fi
echo "   - Timezone: $TIMEZONE"
echo ""
echo "🚀 이제 다음 명령어로 실행할 수 있습니다:"
echo "   source venv/bin/activate"
echo "   python3 src/main.py"
echo ""
