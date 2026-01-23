#!/usr/bin/env python3
"""
회의록 자동화 웹 애플리케이션
텍스트 입력 → Gemini 분석 → Cal.com 자동 등록
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import json
import threading
import shutil
import time
from datetime import datetime
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

# 데이터 저장 경로 설정
DATA_DIR = PROJECT_ROOT / "data"
DB_FILE = DATA_DIR / "db.json"
BACKUP_DIR = DATA_DIR / "backups"

# 초기 데이터 파일 생성
if not DATA_DIR.exists():
    DATA_DIR.mkdir(exist_ok=True)

if not BACKUP_DIR.exists():
    BACKUP_DIR.mkdir(exist_ok=True)


if not DB_FILE.exists():
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump({"meeting_notes": "", "events": []}, f, ensure_ascii=False, indent=2)

# 파일 쓰기 락 (동시성 제어)
db_lock = threading.Lock()

def load_db():
    try:
        with db_lock:
            if not DB_FILE.exists():
                return {"meeting_notes": "", "events": []}
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading DB: {e}")
        return {"meeting_notes": "", "events": []}

def save_db(data):
    try:
        with db_lock:
            # 1. 백업 로직 수행 (10분 간격)
            if DB_FILE.exists():
                should_backup = False
                
                # 가장 최근 백업 파일 확인
                backups = sorted(list(BACKUP_DIR.glob('db_backup_*.json')))
                
                if not backups:
                    should_backup = True
                else:
                    last_backup = backups[-1]
                    # 파일명에서 시간 추출 (db_backup_YYYYMMDD_HHMMSS.json)
                    try:
                        # 파일 수정 시간으로 비교 (더 간단함)
                        last_mtime = last_backup.stat().st_mtime
                        current_time = time.time()
                        
                        # 10분 = 600초
                        if current_time - last_mtime > 600:
                            should_backup = True
                    except Exception:
                        should_backup = True  # 에러나면 안전하게 백업
                
                if should_backup:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = BACKUP_DIR / f"db_backup_{timestamp}.json"
                    shutil.copy2(DB_FILE, backup_path)
                    print(f"Backup created: {backup_path}")

            # 2. 데이터 저장
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving DB: {e}")
        return False

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


@app.route('/sync', methods=['POST'])
def sync_calcom():
    """분석 결과를 Cal.com에 동기화 (수동)"""
    
    # API 키 확인
    if not CALCOM_API_KEY:
        return jsonify({
            'success': False,
            'error': 'CALCOM_API_KEY가 설정되지 않았습니다.'
        }), 500

    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': '데이터가 없습니다.'
            }), 400
            
        calcom = CalcomClient(CALCOM_API_KEY, CALCOM_BASE_URL, CALCOM_USER_ID, TIMEZONE)
        
        # 캘린더 이벤트 직접 동기화 (프론트엔드에서 확정된 일정)
        if 'calendar_events' in data:
            sync_results = calcom.sync_calendar_events(data['calendar_events'])
        # 기존 분석 결과 동기화 (하위 호환성)
        elif 'analysis_result' in data:
            sync_results = calcom.sync_meeting_analysis(data['analysis_result'])
        else:
            return jsonify({
                'success': False,
                'error': '동기화할 데이터가 없습니다 (calendar_events 또는 analysis_result 필요).'
            }), 400
        
        return jsonify({
            'success': True,
            'sync_results': sync_results
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

@app.route('/api/db', methods=['GET', 'POST'])
def handle_db():
    """데이터 조회 및 저장 (Persistent Storage)"""
    if request.method == 'GET':
        data = load_db()
        return jsonify({
            'success': True,
            'data': data
        })
    
    elif request.method == 'POST':
        try:
            new_data = request.json
            if not new_data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            # 기존 데이터 로드하여 병합 (필요한 경우) 또는 전체 덮어쓰기
            # 여기서는 클라이언트가 전체 상태를 관리한다고 가정하고 덮어쓰기/병합을 수행
            # 하지만 안전을 위해 클라이언트에서 보낸 키만 업데이트하는 방식으로 구현 가능
            
            current_data = load_db()
            
            if 'meeting_notes' in new_data:
                current_data['meeting_notes'] = new_data['meeting_notes']
            
            if 'events' in new_data:
                current_data['events'] = new_data['events']
                
            save_db(current_data)
            
            return jsonify({
                'success': True,
                'message': 'Data saved successfully'
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
