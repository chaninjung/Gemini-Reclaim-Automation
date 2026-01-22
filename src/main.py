#!/usr/bin/env python3
"""
회의록 자동화 메인 스크립트

input/ 폴더의 txt 파일을 자동으로 분석하여 Reclaim.ai에 동기화합니다.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# 현재 스크립트의 디렉토리 기준으로 프로젝트 루트 찾기
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# 환경 변수 로드
env_path = PROJECT_ROOT / "config" / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # .env 파일이 없으면 .env.example을 복사하도록 안내
    print("⚠️  config/.env 파일이 없습니다.")
    print("   config/.env.example을 config/.env로 복사하고 API 키를 설정해주세요.")
    sys.exit(1)

from gemini_analyzer import GeminiAnalyzer
from calcom_client import CalcomClient


class MeetingAutomation:
    """회의록 자동화 클래스"""

    def __init__(self):
        """자동화 시스템 초기화"""
        self.input_dir = PROJECT_ROOT / "input"
        self.processed_dir = PROJECT_ROOT / "processed"
        self.output_dir = PROJECT_ROOT / "processed"

        # 디렉토리 생성
        self.input_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)

        # API 클라이언트 초기화
        gemini_key = os.getenv('GEMINI_API_KEY')
        calcom_api_key = os.getenv('CALCOM_API_KEY')
        calcom_base_url = os.getenv('CALCOM_BASE_URL', 'http://localhost:3000')
        calcom_user_id = os.getenv('CALCOM_USER_ID')
        timezone = os.getenv('TIMEZONE', 'Asia/Seoul')

        if not gemini_key:
            print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
            sys.exit(1)

        if not calcom_api_key:
            print("❌ CALCOM_API_KEY가 설정되지 않았습니다.")
            print("   docs/CALCOM_SETUP.md를 참고하여 Cal.com을 설정하세요.")
            sys.exit(1)

        self.analyzer = GeminiAnalyzer(gemini_key)
        self.calcom = CalcomClient(calcom_api_key, calcom_base_url, calcom_user_id, timezone)

    def get_pending_files(self):
        """처리되지 않은 txt 파일 목록 반환"""
        txt_files = list(self.input_dir.glob("*.txt"))
        # .gitkeep 파일 제외
        txt_files = [f for f in txt_files if f.name != ".gitkeep"]
        return sorted(txt_files, key=lambda x: x.stat().st_mtime)

    def process_file(self, file_path: Path, auto_sync: bool = True) -> Optional[dict]:
        """
        회의록 파일 처리

        Args:
            file_path: 처리할 파일 경로
            auto_sync: Reclaim.ai에 자동 동기화 여부

        Returns:
            처리 결과 딕셔너리
        """
        print(f"\n{'='*60}")
        print(f"📄 파일 처리 중: {file_path.name}")
        print(f"{'='*60}\n")

        try:
            # 파일 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                print("⚠️  파일이 비어있습니다.")
                return None

            # Gemini로 분석
            print("🤖 Gemini AI로 회의록 분석 중...")
            analysis_result = self.analyzer.analyze_meeting_notes(content)

            # 분석 결과 출력
            summary = self.analyzer.create_smart_summary(analysis_result)
            print(summary)

            # JSON 파일로 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"{file_path.stem}_{timestamp}_analysis.json"
            json_path = self.processed_dir / json_filename

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, indent=2, ensure_ascii=False)

            print(f"\n💾 분석 결과 저장: {json_filename}")

            # Cal.com에 동기화
            sync_results = None
            if auto_sync:
                print("\n📤 Cal.com에 동기화 중...")
                sync_results = self.calcom.sync_meeting_analysis(analysis_result)
                self.calcom.print_sync_results(sync_results)

            # 처리된 파일 이동
            processed_filename = f"{file_path.stem}_{timestamp}.txt"
            processed_path = self.processed_dir / processed_filename
            shutil.move(str(file_path), str(processed_path))
            print(f"✅ 원본 파일 이동: {processed_filename}")

            return {
                "file": file_path.name,
                "analysis": analysis_result,
                "sync_results": sync_results,
                "json_saved": str(json_path),
                "original_moved": str(processed_path)
            }

        except Exception as e:
            print(f"\n❌ 처리 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return None

    def run_once(self, auto_sync: bool = True):
        """
        한 번 실행 - 대기 중인 모든 파일 처리

        Args:
            auto_sync: Reclaim.ai에 자동 동기화 여부
        """
        print("\n" + "="*60)
        print("🚀 회의록 자동화 시스템 시작")
        print("="*60)

        pending_files = self.get_pending_files()

        if not pending_files:
            print("\n📭 처리할 파일이 없습니다.")
            print(f"   input/ 폴더에 회의록 txt 파일을 추가해주세요.")
            return

        print(f"\n📋 처리할 파일: {len(pending_files)}개")
        for f in pending_files:
            print(f"  - {f.name}")

        results = []
        for file_path in pending_files:
            result = self.process_file(file_path, auto_sync=auto_sync)
            if result:
                results.append(result)

        print(f"\n{'='*60}")
        print(f"✨ 완료: {len(results)}개 파일 처리됨")
        print(f"{'='*60}\n")

    def watch_mode(self):
        """
        감시 모드 - 새 파일이 추가되면 자동으로 처리
        (간단한 구현, 실제로는 watchdog 라이브러리 사용 권장)
        """
        import time

        print("\n" + "="*60)
        print("👀 감시 모드 시작")
        print("   input/ 폴더에 txt 파일을 추가하면 자동으로 처리됩니다.")
        print("   종료하려면 Ctrl+C를 누르세요.")
        print("="*60)

        processed_files = set()

        try:
            while True:
                pending_files = self.get_pending_files()
                new_files = [f for f in pending_files if f not in processed_files]

                if new_files:
                    for file_path in new_files:
                        self.process_file(file_path, auto_sync=True)
                        processed_files.add(file_path)

                time.sleep(2)  # 2초마다 체크

        except KeyboardInterrupt:
            print("\n\n감시 모드 종료")


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(
        description="회의록 자동 분석 및 Cal.com 동기화 시스템"
    )
    parser.add_argument(
        '--mode',
        choices=['once', 'watch'],
        default='once',
        help='실행 모드: once (한번 실행) 또는 watch (감시 모드)'
    )
    parser.add_argument(
        '--no-sync',
        action='store_true',
        help='Cal.com 동기화 비활성화 (분석만 수행)'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='특정 파일만 처리 (파일 이름 또는 경로)'
    )

    args = parser.parse_args()

    automation = MeetingAutomation()

    # 특정 파일 처리
    if args.file:
        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = automation.input_dir / file_path

        if not file_path.exists():
            print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
            sys.exit(1)

        automation.process_file(file_path, auto_sync=not args.no_sync)
        return

    # 모드에 따라 실행
    if args.mode == 'once':
        automation.run_once(auto_sync=not args.no_sync)
    elif args.mode == 'watch':
        automation.watch_mode()


if __name__ == "__main__":
    main()
