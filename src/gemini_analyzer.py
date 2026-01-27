"""
Google Gemini API를 사용한 회의록 분석 모듈
회의록에서 태스크, 일정, 중요 정보를 추출합니다.
"""

import os
import json
from typing import Dict, List, Any
from datetime import datetime
import google.generativeai as genai
import time


class GeminiAnalyzer:
    """Gemini API를 사용해 회의록을 분석하는 클래스"""

    def __init__(self, api_key: str):
        """
        Gemini Analyzer 초기화

        Args:
            api_key: Google Gemini API 키
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config={"temperature": 0.2}
        )

    def analyze_meeting_notes(self, text: str) -> Dict[str, Any]:
        """
        회의록 텍스트를 분석하여 구조화된 데이터를 반환

        Args:
            text: 분석할 회의록 텍스트

        Returns:
            분석 결과를 담은 딕셔너리
        """

        prompt = f"""
다음은 회의록 텍스트입니다. 이 텍스트를 분석하여 JSON 형식으로 정보를 추출해주세요.

회의록:
\"\"\"
{text}
\"\"\"

**중요한 요구사항 (Language Requirement)**:
- **반드시 회의록 원본과 '동일한 언어'로 결과를 생성하세요.**
- 회의록이 **한국어**라면, 요약, 태스크 제목, 설명 등 모든 텍스트를 **한국어**로 작성하세요.
- 회의록이 **영어(English)**라면, 모든 결과를 **영어**로 작성하세요.
- 회의록이 **일본어**라면, 모든 결과를 **일본어**로 작성하세요.

분석 요구사항:
1.  **요약(summary)**: 사용자가 선호하는 다음 'Notion 스타일' 구조로 작성해주세요. (마크다운 포맷)
    -   **핵심 요약 정리**: 회의의 핵심 주제와 결론을 구조화하여 정리
    -   **주요 프로세스/기준**: (해당하는 경우) 판정 기준, 작업 방식 등
    -   **입력/출력 데이터**: (해당하는 경우) Input 소스, Output 산출물
    -   **회의록 개요**: 일시, 소요시간, 참석자 (AI 개발팀/상대 부서 구분)
    -   **주요 논의 사항**: 안건별 현황, 문제점, 해결 방안 (번호 매겨서 정리)
    -   **기대 효과**: (해당하는 경우)
    -   **액션 아이템**: (체크박스 스타일)

2.  **태스크 추출(todo_tasks)**: 
    -   **정의**: "누군가가 시간을 들여 수행해야 하는 **작업(Action Item)**"입니다.
    -   **구분 기준**: 
        -   단순한 미팅 일정이나 마감일 알림은 태스크가 아닙니다.
        -   "~작성하기", "~개발하기", "~검토하기", "~수정하기" 처럼 **동사형 작업**을 추출하세요.
    -   **필수 조건**: 담당자(Who)나 마감일(When)이 불확실해도, **해야 할 일(What)**이 명확하면 포함하세요.
    -   "논의했다", "공유했다" 같은 단순 사실 나열은 제외합니다.

3.  **일정 추출(schedule_items)**:
    -   **정의**: "특정 시간에 사람들이 모이는 **이벤트(Event/Meeting)**"입니다.
    -   **절대 태스크를 여기에 넣지 마세요**: "보고서 제출 마감"은 태스크의 마감일이지, 일정(미팅)이 아닙니다.
    -   **포함 대상**: 주간 회의, 킥오프 미팅, 시연회, 워크샵, 점심 약속 등 **'장소'와 '시간'이 동반되는 약속**만 추출하세요.

다음 형식의 JSON으로 응답해주세요:
{{
    "meeting_title": "회의 제목을 다음 형식으로 생성: '회의주제/부서명/YY-MM-DD'. 원본 언어에 맞게 생성하세요.",
    "meeting_date": "회의록에서 추출한 실제 회의 날짜 (YYYY-MM-DD 형식). 회의록에 명시된 날짜를 사용하고, 없으면 오늘 날짜를 사용하세요.",
    "department_name": "회의에 참석한 주요 부서명. 회의록에서 추출하세요.",
    "summary": "위 요구사항에 맞춘 마크다운 형식의 상세 요약 텍스트 (원본 언어와 동일하게)",
    "completed_tasks": [
        {{
            "title": "완료된 작업 제목",
            "description": "작업 상세 설명",
            "who": "담당자 (있으면)"
        }}
    ],
    "todo_tasks": [
        {{
            "title": "작업 제목 (예: '법규 검토 보고서 작성')",
            "description": "작업 상세 설명",
            "priority": "high/medium/low",
            "who": "담당자 (있으면)",
            "deadline": "마감일 (YYYY-MM-DD). 없으면 null",
            "context": "원문 문장"
        }}
    ],
    "schedule_items": [
        {{
            "title": "미팅 제목 (예: '2차 주간 회의', '디자인 시연회')",
            "description": "미팅 목적",
            "date": "YYYY-MM-DD",
            "time": "HH:MM",
            "duration_minutes": 60,
            "context": "원문 문장"
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
5. **상대적 날짜 표현을 구체적인 날짜로 변환하세요**:
   - "1월 말까지" → 해당 월의 마지막 날 (예: 2026-01-31)
   - "다음주 중반" → 다음주 수요일 날짜
   - "금요일까지" → 다음 금요일 날짜
   - "~일 후" → 회의 날짜 기준 계산
   - 오늘 날짜는 {datetime.now().strftime('%Y-%m-%d')}입니다. 이를 기준으로 계산하세요.
"""

        max_retries = 3
        retry_delay = 2

        try:
            for attempt in range(max_retries):
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

                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str or "Quota exceeded" in error_str or "ResourceExhausted" in error_str:
                        print(f"Rate limit hit (Attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay}s...")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                            continue
                        else:
                             return {
                                "summary": "분석 실패: API 사용량이 초과되었습니다. 잠시 후 다시 시도해주세요. (Rate Limit Exceeded)",
                                "completed_tasks": [],
                                "todo_tasks": [],
                                "schedule_items": [],
                                "important_dates": [],
                                "participants": [],
                                "key_decisions": [],
                                "error": "Rate Limit Exceeded"
                            }
                    elif isinstance(e, json.JSONDecodeError):
                         print(f"JSON 파싱 에러: {e}")
                         # ... (fall through to normal error handling or return here)
                         return {
                            "summary": "분석 실패: JSON 파싱 오류",
                            "completed_tasks": [],
                            "todo_tasks": [],
                            "schedule_items": [],
                            "important_dates": [],
                            "participants": [],
                            "key_decisions": [],
                            "raw_response": response.text if 'response' in locals() else ""
                        }
                    else:
                        raise e
        
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
