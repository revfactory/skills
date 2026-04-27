# Claude Code Skills

Robin이 만들어 사용하는 Claude Code Skill 모음입니다.

## Skills 목록

| 스킬 | 설명 | 트리거 예시 |
|------|------|------------|
| [spring-boot-init](#spring-boot-init) | Spring Boot 프로젝트 초기 생성 | `스프링 부트 프로젝트 만들어줘` |
| [a4-print-design](#a4-print-design) | 흑백 A4 인쇄물 디자인 | `워크샵 핸드아웃 만들어줘` |
| [hwp](#hwp) | HWP/HWPX 파일 읽기·쓰기·변환 | `이 hwp 파일 마크다운으로 변환해줘` |
| [gemini-3-pro-imagegen](#gemini-3-pro-imagegen) | Google Gemini 이미지 생성/편집 | `AI 이미지 생성해줘` |
| [gpt-image2](#gpt-image2) | OpenAI GPT Image 2 이미지 생성/편집 | `gpt-image-2로 로고 만들어줘` |
| [agent-research](#agent-research) | 에이전트 팀 기반 종합 리서치 | `~에 대해 조사해줘` |
| [agent-1on1](#agent-1on1) | 에이전트 1:1 대화로 개선 | `에이전트랑 1on1 하고 싶어` |
| [manpower](#manpower) | AI 프롬프팅 스킬 레벨 측정 | `/manpower` |
| [paper-trending](#paper-trending) | HuggingFace 트렌딩 논문 요약 | `트렌딩 논문 보여줘` |
| [worklog](#worklog) | Claude Code 세션 기반 워크로그 | `/worklog` |

---

### spring-boot-init

Spring Boot 프로젝트를 빠르게 생성하는 스킬입니다.

- start.spring.io API를 활용하여 프로젝트 생성
- 다양한 프리셋 지원: REST API, 웹 애플리케이션, AI 애플리케이션, 배치 처리, 마이크로서비스
- Spring AI (OpenAI, Claude, Ollama 등) 통합 지원
- Java/Kotlin 선택 가능

**사용 예시:**
```
/spring-boot-init 스킬을 이용해서 @API_SPEC.md 문서를 토대로 api 서버 개발해줘
```

---

### a4-print-design

흑백 프린터로 출력해도 가독성이 좋은 A4 문서를 전문적인 디자인 가이드라인에 따라 생성합니다.

- 블랙/화이트/그레이만 사용하는 인쇄 최적화 디자인
- 2열 그리드, 섹션 번호, 체크리스트 등 다양한 레이아웃 패턴
- HTML artifact 기본 출력 (브라우저에서 Ctrl+P로 인쇄)
- 요청 시 docx, PDF 변환 지원

**적합한 용도:** 워크샵 핸드아웃, 교육 자료, 워크시트, 체크리스트, 회의 문서

---

### hwp

한글(HWP/HWPX) 파일을 처리하는 스킬입니다.

- HWP 바이너리(OLE2/CFB) 및 HWPX(ZIP/XML) 포맷 지원
- 텍스트, 테이블, 이미지 추출
- 마크다운 등 다른 포맷으로 변환
- HWPX 파일 생성 (마크다운/텍스트 → HWPX)
- Node.js/TypeScript 및 Python 코드 레시피 제공

---

### gemini-3-pro-imagegen

Google Gemini 모델을 사용한 고품질 이미지 생성 및 편집 스킬입니다.

- **Nano Banana Pro** (`gemini-3-pro-image-preview`): 고품질, 4K, 텍스트 렌더링
- **Nano Banana 2** (`gemini-3.1-flash-image-preview`): Flash 속도 + Pro 품질
- 텍스트→이미지 생성, 기존 이미지 편집, 멀티턴 편집
- Google 검색 그라운딩으로 실시간 정보 기반 이미지 생성
- 다양한 비율(1:1, 16:9, 9:16 등) 및 해상도(1K~4K) 지원

---

### gpt-image2

OpenAI `gpt-image-2` 모델을 사용한 고품질 이미지 생성 및 편집 스킬입니다.

- 모델은 `gpt-image-2` 로 고정 (최대 3840px 한 변, 2K/4K 자산 생성 가능)
- Image API 기반 텍스트→이미지, 단일/마스킹 편집, 멀티 레퍼런스 합성
- Responses API 멀티턴 편집 (`previous_response_id` 로 이어서 수정)
- 부분 이미지 스트리밍(`partial_images`) 지원
- 사실적 사진·텍스트 렌더링·인물·로고 보존력 강화 (`background="transparent"` 미지원)
- CLI 헬퍼 `scripts/generate_image.py` 제공

---

### agent-research

에이전트 팀을 구성하여 종합 리서치 보고서를 작성하는 스킬입니다.

- 조사 대상을 분석하여 11개 전문가 풀에서 최적의 에이전트를 동적으로 선택·구성
- 3단계 조사 깊이: quick(2~3명) / standard(3~4명) / deep(4~6명)
- 에이전트 간 교차 공유 프로토콜로 정보 품질 향상
- 교차 검증, 갭 분석, 보충 조사를 거쳐 분석적 종합 보고서 산출
- 정보 신뢰도 등급(확인됨/보도됨/미확인/상충) 표시

**전문가 풀:** 공식 정보, 미디어, 커뮤니티, 학술, 재무, 산업·경쟁, 평판, 경력·배경, 업적·저작, 기술 심층, 규제·정책

---

### agent-1on1

하네스 에이전트와 1:1 대화를 통해 에이전트 정의를 점검하고 개선하는 스킬입니다.

- Claude가 선택한 에이전트로 1인칭 몰입(roleplay)하여 대화
- 역할 명확성, 실패 복기, 엣지 케이스 발굴, 협업 개선 등을 점검
- 대화에서 도출된 개선점을 에이전트 정의 파일(`.claude/agents/*.md`)에 직접 반영
- 기존 내용 보존 원칙 — 추가·정제·강화 우선, 삭제는 명시적 요청 시에만

---

### manpower

Claude Code 세션 로그에서 사용자의 AI 프롬프팅 스킬 레벨을 측정합니다.

- 8개 역량 축 분석: 명확성, 구체성, 컨텍스트 제공, 작업 분해, 도구 활용, 반복 개선, 창의적 활용, 효율성
- 방사형 그래프로 역량 시각화
- 주간 성장 추이 추적

---

### paper-trending

HuggingFace Daily Papers에서 트렌딩 논문을 수집하여 한줄 요약 리포트를 생성합니다.

- 특정 날짜, 주차, 월 단위로 논문 조회
- 한국어 한줄 요약 테이블 출력
- 선택적으로 논문 PDF 다운로드 (상위 N개 또는 전체)
- arxiv HTML 버전을 읽어 상세 분석 가능

---

### worklog

오늘 진행한 모든 Claude Code 세션을 분석하여 주간 워크로그로 정리합니다.

- `~/.claude/projects/` 하위의 JSONL 세션 로그를 자동 수집
- 오늘(00시~현재) 진행한 전체 세션 분석
- 주간 워크로그 마크다운 파일(`YYYY-WXX.md`) 생성

---

## 설치 방법

1. 이 repository를 clone합니다:
```bash
git clone https://github.com/revfactory/skills.git
```

2. 원하는 skill 폴더를 `~/.claude/skills/` 디렉토리에 복사하거나 심볼릭 링크를 생성합니다:
```bash
ln -s /path/to/skills/spring-boot-init ~/.claude/skills/spring-boot-init
```

## 라이선스

MIT License
