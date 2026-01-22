"""
Reclaim.ai API 클라이언트 모듈
분석된 회의록 정보를 Reclaim.ai에 태스크와 이벤트로 등록합니다.
"""

import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pytz


class ReclaimClient:
    """Reclaim.ai API를 사용하는 클라이언트 클래스"""

    def __init__(self, api_token: str, timezone: str = "Asia/Seoul"):
        """
        Reclaim Client 초기화

        Args:
            api_token: Reclaim.ai API 토큰
            timezone: 타임존 (기본값: Asia/Seoul)
        """
        self.api_token = api_token
        self.base_url = "https://api.app.reclaim.ai"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.timezone = pytz.timezone(timezone)

    def create_task(
        self,
        title: str,
        description: str = "",
        due_date: Optional[str] = None,
        priority: str = "medium",
        duration_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Reclaim.ai에 태스크 생성

        Args:
            title: 태스크 제목
            description: 태스크 설명
            due_date: 마감일 (YYYY-MM-DD 형식)
            priority: 우선순위 (high/medium/low)
            duration_minutes: 예상 소요 시간 (분)

        Returns:
            생성된 태스크 정보
        """
        # 우선순위 매핑 (Reclaim.ai는 P1-P4 사용)
        priority_map = {
            "high": "P1",
            "medium": "P2",
            "low": "P3"
        }

        task_data = {
            "title": title,
            "notes": description,
            "eventCategory": "WORK",
            "timeSchemeId": "default",
            "snoozeUntil": None,
            "due": None,
            "minChunkSize": min(30, duration_minutes),
            "maxChunkSize": duration_minutes,
            "alwaysPrivate": False,
            "priority": priority_map.get(priority, "P2")
        }

        # 마감일 설정
        if due_date:
            try:
                # YYYY-MM-DD 형식을 ISO 8601 형식으로 변환
                due_datetime = datetime.strptime(due_date, "%Y-%m-%d")
                # 타임존 적용
                due_datetime = self.timezone.localize(due_datetime.replace(hour=23, minute=59))
                task_data["due"] = due_datetime.isoformat()
            except ValueError:
                print(f"잘못된 날짜 형식: {due_date}")

        try:
            response = requests.post(
                f"{self.base_url}/api/tasks",
                headers=self.headers,
                json=task_data,
                timeout=10
            )
            response.raise_for_status()
            return {
                "success": True,
                "task": response.json(),
                "message": f"태스크 생성 완료: {title}"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"태스크 생성 실패: {title}"
            }

    def create_event(
        self,
        title: str,
        description: str = "",
        start_time: Optional[str] = None,
        duration_minutes: int = 60,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reclaim.ai에 이벤트 생성

        Args:
            title: 이벤트 제목
            description: 이벤트 설명
            start_time: 시작 시간 (HH:MM 형식)
            duration_minutes: 소요 시간 (분)
            date: 날짜 (YYYY-MM-DD 형식)

        Returns:
            생성된 이벤트 정보
        """
        if not date:
            # 날짜가 없으면 다음 주로 설정
            date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        if not start_time:
            # 시간이 없으면 오전 10시로 설정
            start_time = "10:00"

        try:
            # 시작 시간 파싱
            date_time_str = f"{date} {start_time}"
            start_datetime = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
            start_datetime = self.timezone.localize(start_datetime)

            # 종료 시간 계산
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)

            event_data = {
                "title": title,
                "eventCategory": "WORK",
                "start": start_datetime.isoformat(),
                "end": end_datetime.isoformat(),
                "notes": description,
                "allDay": False
            }

            response = requests.post(
                f"{self.base_url}/api/events",
                headers=self.headers,
                json=event_data,
                timeout=10
            )
            response.raise_for_status()
            return {
                "success": True,
                "event": response.json(),
                "message": f"이벤트 생성 완료: {title} ({date} {start_time})"
            }
        except ValueError as e:
            return {
                "success": False,
                "error": f"날짜/시간 형식 오류: {str(e)}",
                "message": f"이벤트 생성 실패: {title}"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"이벤트 생성 실패: {title}"
            }

    def sync_meeting_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        회의록 분석 결과를 Reclaim.ai에 동기화

        Args:
            analysis_result: GeminiAnalyzer.analyze_meeting_notes()의 결과

        Returns:
            동기화 결과 요약
        """
        results = {
            "tasks_created": [],
            "events_created": [],
            "errors": []
        }

        # TODO 태스크 생성
        for task in analysis_result.get("todo_tasks", []):
            result = self.create_task(
                title=task.get("title", "제목 없음"),
                description=task.get("description", ""),
                due_date=task.get("deadline"),
                priority=task.get("priority", "medium"),
                duration_minutes=60  # 기본 1시간
            )

            if result["success"]:
                results["tasks_created"].append(result["message"])
            else:
                results["errors"].append(result["message"])

        # 스케줄 아이템을 이벤트로 생성
        for item in analysis_result.get("schedule_items", []):
            result = self.create_event(
                title=item.get("title", "제목 없음"),
                description=item.get("description", ""),
                start_time=item.get("time"),
                duration_minutes=item.get("duration_minutes", 60),
                date=item.get("date")
            )

            if result["success"]:
                results["events_created"].append(result["message"])
            else:
                results["errors"].append(result["message"])

        return results

    def get_tasks(self) -> List[Dict[str, Any]]:
        """
        현재 태스크 목록 조회

        Returns:
            태스크 목록
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tasks",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"태스크 조회 실패: {e}")
            return []

    def print_sync_results(self, results: Dict[str, Any]):
        """
        동기화 결과를 보기 좋게 출력

        Args:
            results: sync_meeting_analysis()의 결과
        """
        print("\n" + "=" * 60)
        print("📤 Reclaim.ai 동기화 결과")
        print("=" * 60)

        if results["tasks_created"]:
            print(f"\n✅ 생성된 태스크 ({len(results['tasks_created'])}개):")
            for msg in results["tasks_created"]:
                print(f"  - {msg}")

        if results["events_created"]:
            print(f"\n📅 생성된 이벤트 ({len(results['events_created'])}개):")
            for msg in results["events_created"]:
                print(f"  - {msg}")

        if results["errors"]:
            print(f"\n❌ 오류 ({len(results['errors'])}개):")
            for msg in results["errors"]:
                print(f"  - {msg}")

        total_created = len(results["tasks_created"]) + len(results["events_created"])
        print(f"\n총 {total_created}개 항목이 Reclaim.ai에 추가되었습니다.")
        print("=" * 60 + "\n")


def test_client():
    """테스트 함수"""
    import os

    api_token = os.getenv('RECLAIM_API_TOKEN')
    if not api_token:
        print("RECLAIM_API_TOKEN 환경 변수가 설정되지 않았습니다.")
        return

    client = ReclaimClient(api_token)

    # 테스트: 태스크 생성
    print("테스트: 태스크 생성")
    result = client.create_task(
        title="테스트 태스크",
        description="자동화 시스템 테스트용 태스크입니다.",
        priority="high",
        duration_minutes=30
    )
    print(result)

    # 테스트: 이벤트 생성
    print("\n테스트: 이벤트 생성")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    result = client.create_event(
        title="테스트 미팅",
        description="자동화 시스템 테스트용 미팅입니다.",
        start_time="14:00",
        duration_minutes=60,
        date=tomorrow
    )
    print(result)


if __name__ == "__main__":
    test_client()
