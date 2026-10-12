# Claude Code Skills

Robin이 만들어 사용하는 Claude Code Skill 모음입니다.   
잘 활용해주세요!

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
| [agent-stat](#agent-stat) | 트레잇 벡터 기반 에이전트 설계·생성 | `리뷰어 에이전트 만들어줘` |
| [manpower](#manpower) | AI 프롬프팅 스킬 레벨 측정 | `/manpower` |
| [paper-trending](#paper-trending) | HuggingFace 트렌딩 논문 요약 | `트렌딩 논문 보여줘` |
| [worklog](#worklog) | Claude Code 세션 기반 워크로그 | `/worklog` |
| [project-spec-writer](#project-spec-writer) | XML 기반 프로젝트·기능 스펙(PRD)·빌드 플랜 작성 | `프로젝트 스펙 써줘` |
| [codex-cli](#codex-cli) | OpenAI Codex CLI(`codex exec`) 호출·두 번째 의견·코드 리뷰 | `codex 로 한 번 더 봐줘` |
| [codex-image](#codex-image) | Codex CLI 내장 `image_generation` 툴로 N장 병렬 이미지 생성 | `codex 로 이미지 5장 동시에` |
| [power-crawl](#power-crawl) | Playwright MCP 기반 고속 웹 데이터 수집·크롤링 | `이 사이트 전체 페이지 돌면서 긁어와` |
| [photoreal](#photoreal) | AI 티 안 나는 실사 인물 사진 프롬프트 설계 | `AI 티 안 나게 실사 사진 만들어줘` |

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

### agent-stat

에이전트를 막연한 산문 프롬프트 대신 **스탯을 찍듯이** 3계층 구조(Role · Trait Vector · Policy)로 설계·생성하는 스킬입니다.

- **3계층 모델**: Role(무엇을) → Trait Vector(어떤 방식으로) → Policy(실제 행동)로 위에서 아래로 유도
- **8축 트레잇 벡터**(각 1~5): 주도성·근거성·계획성·사회성·협력성·위험성향·도구성향·반성성
- 각 축의 값을 구체적 행동 정책으로 번역하고, 정책 줄마다 출처 트레잇 태그(예: `(근거성5)`)로 추적성 부여
- 아키타입 프리셋(리뷰어·리서처·빌더·코치·조율자·분석가 등)에서 출발해 미세조정
- 정합성 점검(양극 충돌·상승 조합·올-5 경고)과 정책 충돌 해소(안전 > 정확성 > 주도성) 내장
- 결과물은 `.claude/agents/{name}.md` 정의 파일(스탯 시트 표 포함)
- `references/trait-policy-map.md`(축별 정책 사전), `references/archetypes.md`(프리셋), `assets/agent-template.md` 포함

**다른 스킬과의 경계:** 에이전트 1명을 의도적으로 설계·생성하면 이 스킬, 팀 전체 아키텍처+오케스트레이터까지 구성하면 `/harness:harness`, 이미 있는 에이전트를 대화로 점검·개선하면 [`agent-1on1`](#agent-1on1).

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

### project-spec-writer

소프트웨어 프로젝트의 빌드 플랜·기술 스펙(PRD)을 XML 구조의 마크다운 문서로 작성하는 스킬입니다.

- **3가지 모드** — 신규 프로젝트 스펙 / 기존 코드베이스 기능 스펙 / 기존 스펙 정제
- `<project_specification>` 루트 태그 기반 27개 섹션 표준화 (overview, assumptions, technology_stack, core_data_entities, route_definitions, pages_and_interfaces, deployment_and_operations 등)
- 프로젝트 유형별 섹션 교체 — 백엔드는 `api_endpoints`, CLI 는 `commands_and_flags`, 라이브러리는 `public_api`
- 색상은 hex(`#1B4332`), 치수는 px, 라이브러리는 버전까지 — 모호함 없는 구체적 사양 강제
- 스펙 본문은 한국어 기본, XML 태그·필드명·경로·명령어는 영문 유지
- 추측은 `<assumptions>`, 사용자 결정이 필요한 사항은 `<open_questions>` 로 분리해 명시
- 라이브러리 버전은 실제 확인 후 기재 — 미검증 마이너 버전 기입 금지
- `scripts/validate_spec.py` 로 구조·일관성 기계 검증 후 납품

**참조 문서:** `references/xml-schema.md`(스키마), `references/example-spec.md`(웹앱 예시), `references/example-api-spec.md`(백엔드 API 예시), `references/feature-spec-mode.md`(기능 스펙 모드)

**적합한 용도:** 신규 앱 빌드 플랜, 기존 서비스 기능 스펙, 기존 스펙 정제·확장, AI 에이전트에게 위임할 개발 명세 작성

---

### codex-cli

OpenAI Codex CLI(`codex`)를 Claude Code 세션 안에서 비대화형으로 호출하기 위한 스킬입니다.

- `codex exec` 중심 — TUI 회피, 모든 호출에 `--sandbox`(기본 `read-only`) 명시
- 두 번째 의견(second opinion) 패턴: Claude 결론 + 원본 컨텍스트를 같이 넘겨 OpenAI 모델로 독립 판단
- `codex review` 로 브랜치/커밋/언커밋 비대화형 코드 리뷰
- `--json` 이벤트 스트림 + `--output-last-message` 분리, `--output-schema` 로 구조화 출력 강제
- 모델·프로파일 선택(`-m`, `-p`, `--oss`), MCP 서버 등록(`codex mcp`), 세션 재개(`codex resume`)
- 샌드박스 가이드와 안티패턴(예: `codex exec` 에 `--ask-for-approval` 부착 금지)까지 망라

**OpenAI 공식 [`codex-plugin-cc`](https://github.com/openai/codex-plugin-cc) 와의 차이.** `codex-plugin-cc` 는 Claude Code 플러그인으로, `/codex:review` · `/codex:adversarial-review` · `/codex:rescue` · `/codex:status` 같은 **고수준 슬래시 명령**을 제공합니다(코드 리뷰·태스크 위임 중심, 백그라운드 잡 관리 포함). 반면 이 `codex-cli` 스킬은 Claude 가 `codex` 바이너리를 **직접 호출**할 때 필요한 플래그·샌드박스·출력 캡처·MCP·프로파일까지 **저수준 사용법 전반**을 가르치는 가이드입니다. 즉, 정형화된 리뷰·위임 워크플로가 필요하면 공식 플러그인이 빠르고, JSON 자동화·출력 스키마·임의 프롬프트·세션 재개·로컬 OSS 모델 같은 자유도가 필요하면 이 스킬이 적합합니다. 둘은 충돌하지 않으며 함께 써도 됩니다.

---

### codex-image

Codex CLI 의 내장 `image_generation` 툴로 이미지를 생성하는 스킬입니다. 핵심은 **최대 5장 동시 병렬 생성**.

- ChatGPT OAuth 인증만으로 동작 — 별도 `OPENAI_API_KEY` · Python SDK · curl 불필요
- `codex exec` 를 `run_in_background: true` 로 N개 띄워 진정한 병렬 (실측: 5장 동시 = 직렬 대비 약 2.85배)
- 5개씩 묶어 순차 실행하는 배치 헬퍼 `scripts/codex_imagegen_batch.sh` 제공
- 작업 폴더에 PNG 자동 저장, 결과 검증 패턴 포함

---

### power-crawl

Playwright MCP 를 e2e 테스트 도구가 아니라 **고속 데이터 수집 엔진**으로 쓰는 크롤링 스킬입니다.

- **수집 사다리**(L0 내부 JSON API → L1 임베디드 JSON → L2 DOM 추출 → L3 실제 렌더)를 위에서부터 시도해 가장 빠른 경로를 선택
- `browser_network_requests` 로 페이지 뒤에 숨은 JSON API 를 발굴 — 찾으면 수천 건도 호출 몇 번에 종료
- 페이지네이션·무한스크롤을 **단일 도구 호출 안에서 루프**로 처리, 상세 팬아웃은 워커 풀로 동시성 8~16
- 수집 데이터를 모델 컨텍스트에 통과시키지 않고 `filename` 으로 **곧바로 파일 저장**(JSONL/CSV)
- `scripts/finalize.py` 로 중복 제거 + **필드별 채움률** 산출 → 조용한 셀렉터 실패 탐지
- 재현 가능한 `crawl-report.md`(수집 경로·스키마·누락·제약) 산출
- 로그인은 사용자 본인이 수행, 2FA·캡차·봇 차단 우회는 하지 않음
- `references/recipes.md`(상황별 코드 레시피), `references/mechanics.md`(도구 실측 동작), `references/troubleshooting.md` 포함

**적합한 용도:** 상품·가격 수집, 채용공고·리뷰 모니터링, 경쟁사 데이터 수집, 로그인 후 내 데이터 백업

**범위 밖:** 단일 페이지 1회 조회·요약(WebFetch 로 충분), e2e 테스트·QA 자동화

---

### photoreal

이미지 모델이 사람을 그릴 때 기본으로 끌리는 광고·화보식 완벽함을 상쇄해, 폰으로 찍은 스냅처럼 보이는 프롬프트를 만드는 스킬입니다.

- 실사감은 디테일을 더해서 얻는 것이 아니라 모델의 기본 끌림을 깎아서 얻는다는 전제로 설계
- **다섯 개 층**: L1 출처(누가 왜 찍었나) → L2 빛·화질 → L3 구도·순간 → L4 해부학(얼굴·피부·손·머리카락) → L5 미의 상한선
- 모델이 흘리기 쉬운 부정문(`매끄럽게 하지 마`)을 남길 것을 지목하는 긍정문(`모공과 잔털이 보이는 피부`)으로 바꿔 쓰는 대응표
- L5 미의 상한선은 강도 세 단계(약·중·없음)로 조절 — 빼면 초라해지고 세게 쓰면 배우 얼굴로 되돌아간다
- 손의 해부학과 동작 논리를 따로 지시 — 손가락 개수가 맞아도 칼날 앞에 손을 쫙 편 자세가 나온다
- 나이 지정 컷과 여러 명 나오는 컷은 별도 처리 — 피부 질감 지시가 나이를 위로 미는 문제, 시선을 사람 수만큼 나누는 규칙
- 손·눈동자 하이라이트·글자·나이·피부 균질도 등 열한 가지 생성 후 점검 항목. 걸린 항목만 긍정문으로 보강해 재생성
- 같은 프롬프트도 장마다 편차가 크므로 3~5장 병렬 생성을 기본 운용으로 잡음. 변형은 상황 → 촬영 위치 → 거리 → 조명 순으로 크게 갈리므로 조명만 돌리지 않음
- `scripts/build_prompt.py` 로 장면·상세도·셀카 여부·인원수(`--group`)·미의 강도(`--charm`)·나이 고정·언어를 지정해 변형 N개 프롬프트를 한 번에 뽑음
- `references/directives.md`(원본 지시문 20개와 영문 대응), `references/scenes.md`(한국·일본·미국 디테일, 상황 프리셋) 포함

**다른 스킬과의 경계:** 이 스킬은 프롬프트만 만듭니다. 실제 이미지 생성은 [`codex-image`](#codex-image)(병렬 N장), [`gpt-image2`](#gpt-image2), [`gemini-3-pro-imagegen`](#gemini-3-pro-imagegen)이 맡습니다.

**범위 밖:** 일러스트·애니풍·3D 렌더·로고처럼 사진이 아닌 그림체, 실존 인물의 얼굴 재현

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
