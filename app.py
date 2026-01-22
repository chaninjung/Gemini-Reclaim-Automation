#!/usr/bin/env python3
"""
회의록 자동화 웹 애플리케이션
텍스트 입력 → Gemini 분석 → Cal.com 자동 등록
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from dotenv import load_dotenv

# 프로젝트 루트 설정
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# 환경 변수 로드
env_path = PROJECT_ROOT / "config" / ".env"
if not env_path.exists():
    env_path = PROJECT_ROOT / ".env"

load_dotenv(env_path)

from gemini_analyzer import GeminiAnalyzer
from calcom_client import CalcomClient

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# API 클라이언트 초기화
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
CALCOM_API_KEY = os.getenv('CALCOM_API_KEY')
CALCOM_BASE_URL = os.getenv('CALCOM_BASE_URL', 'https://api.cal.com/v1')
CALCOM_USER_ID = os.getenv('CALCOM_USER_ID')
TIMEZONE = os.getenv('TIMEZONE', 'Asia/Seoul')

if not GEMINI_API_KEY:
    print("⚠️  GEMINI_API_KEY가 설정되지 않았습니다.")
    print("   .env 파일을 확인해주세요.")

if not CALCOM_API_KEY:
    print("⚠️  CALCOM_API_KEY가 설정되지 않았습니다.")
    print("   Cal.com에서 API 키를 발급받아 .env 파일에 설정해주세요.")


@app.route('/')
def index():
    """메인 페이지 - 텍스트 입력 폼"""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """회의록 분석 및 Cal.com 동기화"""

    # API 키 확인
    if not GEMINI_API_KEY:
        return jsonify({
            'success': False,
            'error': 'GEMINI_API_KEY가 설정되지 않았습니다.'
        }), 500

    # 텍스트 입력 받기
    meeting_notes = request.form.get('meeting_notes', '').strip()
    auto_sync = request.form.get('auto_sync', 'true') == 'true'

    if not meeting_notes:
        return jsonify({
            'success': False,
            'error': '회의록 내용을 입력해주세요.'
        }), 400

    try:
        # Gemini로 분석
        analyzer = GeminiAnalyzer(GEMINI_API_KEY)
        analysis_result = analyzer.analyze_meeting_notes(meeting_notes)

        # Cal.com 동기화
        sync_results = None
        if auto_sync and CALCOM_API_KEY:
            calcom = CalcomClient(CALCOM_API_KEY, CALCOM_BASE_URL, CALCOM_USER_ID, TIMEZONE)
            sync_results = calcom.sync_meeting_analysis(analysis_result)

        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'sync_results': sync_results,
            'auto_sync_enabled': auto_sync and bool(CALCOM_API_KEY)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health')
def health():
    """헬스체크 엔드포인트"""
    status = {
        'status': 'ok',
        'gemini_configured': bool(GEMINI_API_KEY),
        'calcom_configured': bool(CALCOM_API_KEY),
    }
    return jsonify(status)


@app.route('/api/test-gemini', methods=['POST'])
def test_gemini():
    """Gemini API 테스트"""
    if not GEMINI_API_KEY:
        return jsonify({
            'success': False,
            'error': 'GEMINI_API_KEY가 설정되지 않았습니다.'
        }), 500

    try:
        analyzer = GeminiAnalyzer(GEMINI_API_KEY)
        test_text = "회의: 내일 오후 2시 프로젝트 미팅"
        result = analyzer.analyze_meeting_notes(test_text)

        return jsonify({
            'success': True,
            'message': 'Gemini API 연결 성공!',
            'test_result': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/test-calcom', methods=['POST'])
def test_calcom():
    """Cal.com API 테스트"""
    if not CALCOM_API_KEY:
        return jsonify({
            'success': False,
            'error': 'CALCOM_API_KEY가 설정되지 않았습니다.'
        }), 500

    try:
        calcom = CalcomClient(CALCOM_API_KEY, CALCOM_BASE_URL, CALCOM_USER_ID, TIMEZONE)
        event_types = calcom.get_event_types()

        return jsonify({
            'success': True,
            'message': 'Cal.com API 연결 성공!',
            'event_types': event_types
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # 개발 서버 실행
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print("\n" + "=" * 60)
    print("🚀 회의록 자동화 웹 서버 시작")
    print("=" * 60)
    print(f"📍 URL: http://localhost:{port}")
    print(f"🔑 Gemini API: {'✅ 설정됨' if GEMINI_API_KEY else '❌ 미설정'}")
    print(f"📅 Cal.com API: {'✅ 설정됨' if CALCOM_API_KEY else '❌ 미설정'}")
    print("=" * 60 + "\n")

    app.run(host='0.0.0.0', port=port, debug=debug)
