"""
Cal.com API 클라이언트 모듈
분석된 회의록 정보를 Cal.com에 이벤트와 북킹으로 등록합니다.
"""

import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pytz


class CalcomClient:
    """Cal.com API를 사용하는 클라이언트 클래스"""

    def __init__(self, api_key: str, base_url: str = "http://localhost:3000", user_id: Optional[str] = None, timezone: str = "Asia/Seoul"):
        """
        Cal.com Client 초기화

        Args:
            api_key: Cal.com API 키
            base_url: Cal.com 인스턴스 URL (기본값: http://localhost:3000)
            user_id: Cal.com 사용자 ID (선택사항)
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

    def get_user_info(self) -> Dict[str, Any]:
        """
        현재 사용자 정보 조회

        Returns:
            사용자 정보
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v2/me",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return {
                "success": True,
                "user": response.json(),
                "message": "사용자 정보 조회 성공"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": "사용자 정보 조회 실패"
            }

    def get_event_types(self) -> Dict[str, Any]:
        """
        이벤트 타입 목록 조회

        Returns:
            이벤트 타입 목록
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v2/event-types",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return {
                "success": True,
                "event_types": response.json(),
                "message": "이벤트 타입 조회 성공"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": "이벤트 타입 조회 실패"
            }

    def create_event_type(
        self,
        title: str,
        slug: str,
        length: int = 60,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        이벤트 타입 생성 (템플릿)

        Args:
            title: 이벤트 타입 제목
            slug: URL slug (예: "meeting", "review")
            length: 기본 길이 (분)
            description: 설명

        Returns:
            생성된 이벤트 타입 정보
        """
        event_type_data = {
            "title": title,
            "slug": slug,
            "length": length,
            "description": description,
            "hidden": False
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v2/event-types",
                headers=self.headers,
                json=event_type_data,
                timeout=10
            )
            response.raise_for_status()
            return {
                "success": True,
                "event_type": response.json(),
                "message": f"이벤트 타입 생성 완료: {title}"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"이벤트 타입 생성 실패: {title}"
            }

    def create_booking(
        self,
        event_type_id: int,
        start: str,
        attendee_name: str,
        attendee_email: str,
        attendee_timezone: str = "Asia/Seoul",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        북킹(예약) 생성

        Args:
            event_type_id: 이벤트 타입 ID
            start: 시작 시간 (ISO 8601 형식)
            attendee_name: 참석자 이름
            attendee_email: 참석자 이메일
            attendee_timezone: 참석자 타임존
            metadata: 추가 메타데이터

        Returns:
            생성된 북킹 정보
        """
        booking_data = {
            "eventTypeId": event_type_id,
            "start": start,
            "responses": {
                "name": attendee_name,
                "email": attendee_email,
                "location": {"value": "inPerson", "optionValue": ""}
            },
            "timeZone": attendee_timezone,
            "language": "ko",
            "metadata": metadata or {}
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v2/bookings",
                headers=self.headers,
                json=booking_data,
                timeout=10
            )
            response.raise_for_status()
            return {
                "success": True,
                "booking": response.json(),
                "message": f"북킹 생성 완료: {attendee_name}"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"북킹 생성 실패: {attendee_name}"
            }

    def create_simple_event(
        self,
        title: str,
        description: str = "",
        start_time: Optional[str] = None,
        duration_minutes: int = 60,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        간단한 이벤트 생성 (이벤트 타입 자동 생성 후 북킹)

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

            # 이벤트 타입 생성 (slug는 타임스탬프 기반으로 유니크하게)
            slug = f"auto-{int(datetime.now().timestamp())}"
            event_type_result = self.create_event_type(
                title=title,
                slug=slug,
                length=duration_minutes,
                description=description
            )

            if not event_type_result["success"]:
                return event_type_result

            event_type_id = event_type_result["event_type"]["data"]["id"]

            # 북킹 생성
            booking_result = self.create_booking(
                event_type_id=event_type_id,
                start=start_datetime.isoformat(),
                attendee_name="System",
                attendee_email="system@example.com",
                metadata={"description": description, "auto_created": True}
            )

            if booking_result["success"]:
                return {
                    "success": True,
                    "event": booking_result["booking"],
                    "message": f"이벤트 생성 완료: {title} ({date} {start_time})"
                }
            else:
                return booking_result

        except ValueError as e:
            return {
                "success": False,
                "error": f"날짜/시간 형식 오류: {str(e)}",
                "message": f"이벤트 생성 실패: {title}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"이벤트 생성 실패: {title}"
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
        태스크를 이벤트로 생성
        (Cal.com은 태스크 개념이 없으므로 이벤트로 변환)

        Args:
            title: 태스크 제목
            description: 태스크 설명
            due_date: 마감일 (YYYY-MM-DD 형식)
            priority: 우선순위 (high/medium/low)
            duration_minutes: 예상 소요 시간 (분)

        Returns:
            생성된 이벤트 정보
        """
        # 우선순위를 제목에 표시
        priority_emoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        emoji = priority_emoji.get(priority, "🟡")
        full_title = f"{emoji} [TODO] {title}"

        # 설명에 우선순위 정보 추가
        full_description = f"우선순위: {priority.upper()}\n\n{description}"

        # 마감일이 있으면 해당 날짜에 이벤트 생성, 없으면 내일
        if due_date:
            date = due_date
        else:
            date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        # 오후 2시를 기본 시간으로 설정 (작업 시간)
        return self.create_simple_event(
            title=full_title,
            description=full_description,
            start_time="14:00",
            duration_minutes=duration_minutes,
            date=date
        )

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
                results["errors"].append(result["message"])

        # 스케줄 아이템을 이벤트로 생성
        for item in analysis_result.get("schedule_items", []):
            result = self.create_simple_event(
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

    def get_bookings(self) -> List[Dict[str, Any]]:
        """
        현재 북킹 목록 조회

        Returns:
            북킹 목록
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v2/bookings",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"북킹 조회 실패: {e}")
            return []

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
    base_url = os.getenv('CALCOM_BASE_URL', 'http://localhost:3000')

    if not api_key:
        print("CALCOM_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("docs/CALCOM_SETUP.md를 참고하여 Cal.com을 설정하세요.")
        return

    client = CalcomClient(api_key, base_url)

    # 테스트: 사용자 정보 조회
    print("테스트: 사용자 정보 조회")
    result = client.get_user_info()
    print(result)

    if result["success"]:
        print(f"\n사용자: {result['user'].get('name', 'Unknown')}")
        print(f"이메일: {result['user'].get('email', 'Unknown')}")

    # 테스트: 간단한 이벤트 생성
    print("\n테스트: 이벤트 생성")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    result = client.create_simple_event(
        title="테스트 미팅",
        description="자동화 시스템 테스트용 미팅입니다.",
        start_time="14:00",
        duration_minutes=60,
        date=tomorrow
    )
    print(result)


if __name__ == "__main__":
    test_client()
