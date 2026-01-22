"""
Cal.com API 클라이언트 모듈
분석된 회의록 정보를 Cal.com에 이벤트와 예약으로 등록합니다.
"""

import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pytz


class CalcomClient:
    """Cal.com API를 사용하는 클라이언트 클래스"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.cal.com/v1",
        user_id: Optional[str] = None,
        timezone: str = "Asia/Seoul"
    ):
        """
        Cal.com Client 초기화

        Args:
            api_key: Cal.com API 키
            base_url: Cal.com API 베이스 URL (공식: https://api.cal.com/v1, 셀프호스팅: http://localhost:3000/api/v1)
            user_id: Cal.com 사용자 ID (옵션)
            timezone: 타임존 (기본값: Asia/Seoul)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.user_id = user_id
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.timezone = pytz.timezone(timezone)

    def get_event_types(self) -> List[Dict[str, Any]]:
        """
        사용 가능한 이벤트 타입 목록 조회

        Returns:
            이벤트 타입 목록
        """
        try:
            response = requests.get(
                f"{self.base_url}/event-types",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("event_types", [])
        except requests.exceptions.RequestException as e:
            print(f"❌ 이벤트 타입 조회 실패: {e}")
            return []

    def create_event_type(
        self,
        title: str,
        length: int = 60,
        description: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        새 이벤트 타입 생성 (회의 유형)

        Args:
            title: 이벤트 타입 제목
            length: 길이 (분 단위)
            description: 설명

        Returns:
            생성된 이벤트 타입 정보
        """
        try:
            event_type_data = {
                "title": title,
                "slug": title.lower().replace(" ", "-"),
                "length": length,
                "description": description,
            }

            response = requests.post(
                f"{self.base_url}/event-types",
                headers=self.headers,
                json=event_type_data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ 이벤트 타입 생성 실패: {e}")
            return None

    def create_booking(
        self,
        event_type_id: int,
        start: str,
        responses: Dict[str, Any],
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cal.com에 예약(이벤트) 생성

        Args:
            event_type_id: 이벤트 타입 ID
            start: 시작 시간 (ISO 8601 형식)
            responses: 예약 응답 데이터 (name, email 등)
            title: 커스텀 제목 (옵션)
            description: 커스텀 설명 (옵션)

        Returns:
            생성 결과
        """
        booking_data = {
            "eventTypeId": event_type_id,
            "start": start,
            "responses": responses,
            "timeZone": str(self.timezone),
            "language": "ko",
        }

        if title:
            booking_data["metadata"] = {"title": title}
        if description:
            booking_data["metadata"] = booking_data.get("metadata", {})
            booking_data["metadata"]["description"] = description

        try:
            response = requests.post(
                f"{self.base_url}/bookings",
                headers=self.headers,
                json=booking_data,
                timeout=10
            )
            response.raise_for_status()
            return {
                "success": True,
                "booking": response.json(),
                "message": f"예약 생성 완료: {title or 'Untitled'}"
            }
        except requests.exceptions.RequestException as e:
            error_detail = ""
            if hasattr(e.response, 'text'):
                error_detail = e.response.text
            return {
                "success": False,
                "error": str(e),
                "detail": error_detail,
                "message": f"예약 생성 실패: {title or 'Untitled'}"
            }

    def create_task_as_event(
        self,
        title: str,
        description: str = "",
        due_date: Optional[str] = None,
        priority: str = "medium",
        duration_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        태스크를 Cal.com 이벤트로 생성
        (Cal.com은 별도 태스크 API가 없으므로 이벤트로 처리)

        Args:
            title: 태스크 제목
            description: 태스크 설명
            due_date: 마감일 (YYYY-MM-DD 형식)
            priority: 우선순위 (high/medium/low)
            duration_minutes: 예상 소요 시간 (분)

        Returns:
            생성 결과
        """
        # 우선순위를 제목에 포함
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
        full_title = f"{priority_emoji} [태스크] {title}"

        # 마감일이 있으면 그 날짜로, 없으면 내일로 설정
        if due_date:
            try:
                task_date = datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                task_date = datetime.now() + timedelta(days=1)
        else:
            task_date = datetime.now() + timedelta(days=1)

        # 시간은 오전 9시로 기본 설정
        task_datetime = self.timezone.localize(
            task_date.replace(hour=9, minute=0, second=0, microsecond=0)
        )

        # 이벤트 타입 조회 또는 생성
        event_types = self.get_event_types()
        task_event_type = None

        for et in event_types:
            if et.get("title") == "Task" or et.get("slug") == "task":
                task_event_type = et
                break

        if not task_event_type:
            # Task 이벤트 타입이 없으면 생성
            task_event_type = self.create_event_type(
                title="Task",
                length=duration_minutes,
                description="Automated task from meeting notes"
            )

        if not task_event_type:
            return {
                "success": False,
                "error": "Failed to get or create Task event type",
                "message": f"태스크 생성 실패: {title}"
            }

        # 예약 생성
        return self.create_booking(
            event_type_id=task_event_type.get("id"),
            start=task_datetime.isoformat(),
            responses={
                "name": "Automated Task",
                "email": "task@automated.local",
                "notes": description
            },
            title=full_title,
            description=f"{description}\n\n우선순위: {priority}\n마감일: {due_date or 'N/A'}"
        )

    def create_scheduled_event(
        self,
        title: str,
        description: str = "",
        date: Optional[str] = None,
        time: Optional[str] = None,
        duration_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Cal.com에 스케줄된 이벤트 생성

        Args:
            title: 이벤트 제목
            description: 이벤트 설명
            date: 날짜 (YYYY-MM-DD 형식)
            time: 시작 시간 (HH:MM 형식)
            duration_minutes: 소요 시간 (분)

        Returns:
            생성 결과
        """
        if not date:
            # 날짜가 없으면 다음 주로 설정
            date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        if not time:
            # 시간이 없으면 오후 2시로 설정
            time = "14:00"

        try:
            # 시작 시간 파싱
            date_time_str = f"{date} {time}"
            start_datetime = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
            start_datetime = self.timezone.localize(start_datetime)

            # 이벤트 타입 조회 또는 생성
            event_types = self.get_event_types()
            meeting_event_type = None

            for et in event_types:
                if et.get("title") == "Meeting" or et.get("slug") == "meeting":
                    meeting_event_type = et
                    break

            if not meeting_event_type:
                # Meeting 이벤트 타입이 없으면 생성
                meeting_event_type = self.create_event_type(
                    title="Meeting",
                    length=duration_minutes,
                    description="Automated meeting from meeting notes"
                )

            if not meeting_event_type:
                return {
                    "success": False,
                    "error": "Failed to get or create Meeting event type",
                    "message": f"이벤트 생성 실패: {title}"
                }

            # 예약 생성
            return self.create_booking(
                event_type_id=meeting_event_type.get("id"),
                start=start_datetime.isoformat(),
                responses={
                    "name": "Automated Event",
                    "email": "event@automated.local",
                    "notes": description
                },
                title=f"📅 {title}",
                description=description
            )

        except ValueError as e:
            return {
                "success": False,
                "error": f"날짜/시간 형식 오류: {str(e)}",
                "message": f"이벤트 생성 실패: {title}"
            }

    def sync_meeting_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        회의록 분석 결과를 Cal.com에 동기화

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

        # TODO 태스크를 이벤트로 생성
        for task in analysis_result.get("todo_tasks", []):
            result = self.create_task_as_event(
                title=task.get("title", "제목 없음"),
                description=task.get("description", ""),
                due_date=task.get("deadline"),
                priority=task.get("priority", "medium"),
                duration_minutes=60  # 기본 1시간
            )

            if result["success"]:
                results["tasks_created"].append(result["message"])
            else:
                results["errors"].append(f"{result['message']}: {result.get('error', 'Unknown error')}")

        # 스케줄 아이템을 이벤트로 생성
        for item in analysis_result.get("schedule_items", []):
            result = self.create_scheduled_event(
                title=item.get("title", "제목 없음"),
                description=item.get("description", ""),
                date=item.get("date"),
                time=item.get("time"),
                duration_minutes=item.get("duration_minutes", 60)
            )

            if result["success"]:
                results["events_created"].append(result["message"])
            else:
                results["errors"].append(f"{result['message']}: {result.get('error', 'Unknown error')}")

        return results

    def print_sync_results(self, results: Dict[str, Any]):
        """
        동기화 결과를 보기 좋게 출력

        Args:
            results: sync_meeting_analysis()의 결과
        """
        print("\n" + "=" * 60)
        print("📤 Cal.com 동기화 결과")
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
        print(f"\n총 {total_created}개 항목이 Cal.com에 추가되었습니다.")
        print("=" * 60 + "\n")


def test_client():
    """테스트 함수"""
    import os

    api_key = os.getenv('CALCOM_API_KEY')
    base_url = os.getenv('CALCOM_BASE_URL', 'https://api.cal.com/v1')

    if not api_key:
        print("CALCOM_API_KEY 환경 변수가 설정되지 않았습니다.")
        return

    client = CalcomClient(api_key, base_url)

    # 이벤트 타입 조회
    print("=== 이벤트 타입 조회 ===")
    event_types = client.get_event_types()
    for et in event_types:
        print(f"  - {et.get('title')} (ID: {et.get('id')}, {et.get('length')}분)")

    # 테스트: 태스크 생성
    print("\n=== 테스트: 태스크 생성 ===")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    result = client.create_task_as_event(
        title="테스트 태스크",
        description="자동화 시스템 테스트용 태스크입니다.",
        due_date=tomorrow,
        priority="high",
        duration_minutes=30
    )
    print(result)

    # 테스트: 이벤트 생성
    print("\n=== 테스트: 이벤트 생성 ===")
    next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    result = client.create_scheduled_event(
        title="테스트 미팅",
        description="자동화 시스템 테스트용 미팅입니다.",
        date=next_week,
        time="14:00",
        duration_minutes=60
    )
    print(result)


if __name__ == "__main__":
    test_client()
