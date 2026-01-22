"""
Google Gemini API를 사용한 회의록 분석 모듈
회의록에서 태스크, 일정, 중요 정보를 추출합니다.
"""

import os
import json
from typing import Dict, List, Any
import google.generativeai as genai


class GeminiAnalyzer:
    """Gemini API를 사용해 회의록을 분석하는 클래스"""

    def __init__(self, api_key: str):
        """
        Gemini Analyzer 초기화

        Args:
            api_key: Google Gemini API 키
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def analyze_meeting_notes(self, text: str) -> Dict[str, Any]:
        """
        회의록 텍스트를 분석하여 구조화된 데이터를 반환

        Args:
            text: 분석할 회의록 텍스트

        Returns:
            분석 결과를 담은 딕셔너리:
            - summary: 회의 요약
            - completed_tasks: 완료된 작업 리스트
            - todo_tasks: 해야 할 작업 리스트
            - schedule_items: 스케줄링 필요한 항목 리스트
            - important_dates: 중요 날짜/시간 리스트
        """

        prompt = f"""
다음은 회의록 텍스트입니다. 이 텍스트를 분석하여 JSON 형식으로 정보를 추출해주세요.

회의록:
\"\"\"
{text}
\"\"\"

다음 형식의 JSON으로 응답해주세요:
{{
    "summary": "회의 전체 요약 (2-3문장)",
    "completed_tasks": [
        {{
            "title": "완료된 작업 제목",
            "description": "작업 상세 설명",
            "who": "담당자 (있으면)"
        }}
    ],
    "todo_tasks": [
        {{
            "title": "해야 할 작업 제목",
            "description": "작업 상세 설명",
            "priority": "high/medium/low",
            "who": "담당자 (있으면)",
            "deadline": "마감일 (있으면, YYYY-MM-DD 형식)"
        }}
    ],
    "schedule_items": [
        {{
            "title": "일정 제목",
            "description": "일정 설명",
            "date": "날짜 (있으면, YYYY-MM-DD 형식)",
            "time": "시간 (있으면, HH:MM 형식)",
            "duration_minutes": 예상 소요 시간 (숫자, 분 단위)
        }}
    ],
    "important_dates": [
        {{
            "date": "YYYY-MM-DD",
            "description": "날짜의 중요성"
        }}
    ],
    "participants": ["참석자1", "참석자2"],
    "key_decisions": ["결정사항1", "결정사항2"]
}}

주의사항:
1. 정확한 JSON 형식으로만 응답해주세요 (다른 텍스트 없이)
2. 정보가 없으면 빈 배열 []을 반환하세요
3. 날짜 형식은 반드시 YYYY-MM-DD를 따르세요
4. 시간 형식은 24시간 형식 HH:MM을 사용하세요
"""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # JSON 코드 블록 제거 (```json ... ``` 형태)
            if result_text.startswith('```'):
                lines = result_text.split('\n')
                result_text = '\n'.join(lines[1:-1])

            # JSON 파싱
            result = json.loads(result_text)

            return result

        except json.JSONDecodeError as e:
            print(f"JSON 파싱 에러: {e}")
            print(f"원본 응답: {response.text}")
            # 기본 구조 반환
            return {
                "summary": "분석 실패: JSON 파싱 오류",
                "completed_tasks": [],
                "todo_tasks": [],
                "schedule_items": [],
                "important_dates": [],
                "participants": [],
                "key_decisions": [],
                "raw_response": response.text
            }
        except Exception as e:
            print(f"분석 중 에러 발생: {e}")
            return {
                "summary": f"분석 실패: {str(e)}",
                "completed_tasks": [],
                "todo_tasks": [],
                "schedule_items": [],
                "important_dates": [],
                "participants": [],
                "key_decisions": [],
                "error": str(e)
            }

    def create_smart_summary(self, analysis_result: Dict[str, Any]) -> str:
        """
        분석 결과를 사람이 읽기 쉬운 형식으로 정리

        Args:
            analysis_result: analyze_meeting_notes()의 반환값

        Returns:
            읽기 쉬운 요약 텍스트
        """
        summary_parts = []

        summary_parts.append("=" * 60)
        summary_parts.append("📋 회의록 분석 결과")
        summary_parts.append("=" * 60)
        summary_parts.append("")

        # 요약
        summary_parts.append("📝 전체 요약:")
        summary_parts.append(f"  {analysis_result.get('summary', '요약 없음')}")
        summary_parts.append("")

        # 참석자
        if analysis_result.get('participants'):
            summary_parts.append("👥 참석자:")
            for participant in analysis_result['participants']:
                summary_parts.append(f"  - {participant}")
            summary_parts.append("")

        # 주요 결정사항
        if analysis_result.get('key_decisions'):
            summary_parts.append("✅ 주요 결정사항:")
            for decision in analysis_result['key_decisions']:
                summary_parts.append(f"  - {decision}")
            summary_parts.append("")

        # 완료된 작업
        if analysis_result.get('completed_tasks'):
            summary_parts.append("✔️ 완료된 작업:")
            for task in analysis_result['completed_tasks']:
                who = f" ({task['who']})" if task.get('who') else ""
                summary_parts.append(f"  - {task['title']}{who}")
                if task.get('description'):
                    summary_parts.append(f"    → {task['description']}")
            summary_parts.append("")

        # 해야 할 작업
        if analysis_result.get('todo_tasks'):
            summary_parts.append("📌 해야 할 작업:")
            for task in analysis_result['todo_tasks']:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                    task.get('priority', 'medium'), "⚪"
                )
                who = f" ({task['who']})" if task.get('who') else ""
                deadline = f" [마감: {task['deadline']}]" if task.get('deadline') else ""
                summary_parts.append(
                    f"  {priority_emoji} {task['title']}{who}{deadline}"
                )
                if task.get('description'):
                    summary_parts.append(f"    → {task['description']}")
            summary_parts.append("")

        # 일정
        if analysis_result.get('schedule_items'):
            summary_parts.append("📅 예정된 일정:")
            for item in analysis_result['schedule_items']:
                date_time = ""
                if item.get('date'):
                    date_time = f" [{item['date']}"
                    if item.get('time'):
                        date_time += f" {item['time']}"
                    date_time += "]"
                duration = f" ({item['duration_minutes']}분)" if item.get('duration_minutes') else ""
                summary_parts.append(f"  - {item['title']}{date_time}{duration}")
                if item.get('description'):
                    summary_parts.append(f"    → {item['description']}")
            summary_parts.append("")

        # 중요 날짜
        if analysis_result.get('important_dates'):
            summary_parts.append("📆 중요 날짜:")
            for date_info in analysis_result['important_dates']:
                summary_parts.append(
                    f"  - {date_info['date']}: {date_info['description']}"
                )
            summary_parts.append("")

        summary_parts.append("=" * 60)

        return "\n".join(summary_parts)


def test_analyzer():
    """테스트 함수"""
    # 환경 변수에서 API 키 로드
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        return

    # 테스트 회의록
    test_notes = """
2024년 1월 22일 프로젝트 회의

참석자: 김철수, 박영희, 이민준

주요 논의사항:
1. 지난 주 완료한 작업
   - 백엔드 API 개발 완료 (김철수)
   - UI 디자인 초안 작성 완료 (박영희)

2. 이번 주 할 일
   - 프론트엔드 개발 시작 (이민준) - 마감: 1월 26일
   - API 테스트 및 버그 수정 (김철수) - 높은 우선순위
   - 디자인 피드백 반영 (박영희)

3. 다음 미팅
   - 날짜: 2024년 1월 29일 오후 2시
   - 장소: 회의실 A
   - 예상 시간: 1시간

결정사항:
- 베타 테스트는 2월 5일부터 시작
- 주간 회의는 매주 월요일 오후 2시로 고정
"""

    analyzer = GeminiAnalyzer(api_key)
    result = analyzer.analyze_meeting_notes(test_notes)

    print(analyzer.create_smart_summary(result))
    print("\n원본 JSON 결과:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_analyzer()
