#!/usr/bin/env python3
"""
ManPower Score Calculator — 정량 지표 기반 자동 채점
JSONL 세션 데이터에서 정량 지표를 추출하고, 공식 기반으로 점수를 산출한다.

Usage:
    python3 score_calculator.py [--days 28] [--output /path/to/output.json]

출력: JSON (각 축의 점수 + 산출 근거)
"""

import json, os, glob, re, sys, argparse
from datetime import datetime, timezone, timedelta
from collections import defaultdict

KST = timezone(timedelta(hours=9))

# === 정량 채점 공식 ===
# 각 공식은 투명하고 재현 가능하다. LLM 판단 없음.

def score_tool_usage(unique_commands, total_invocations, has_harness, has_agent_team, has_custom_skill, has_plugin):
    """도구 활용 점수 (완전 자동)
    - unique_commands: 고유 슬래시 커맨드 종류 수 (/exit, /clear 제외)
    - total_invocations: 총 호출 횟수 (/exit, /clear 제외)
    - has_harness: /harness 또는 /harness:harness 사용 여부
    - has_agent_team: 에이전트 팀 관련 커맨드 사용 여부
    - has_custom_skill: 커스텀 스킬 생성/사용 여부
    - has_plugin: /plugin, /reload-plugins 사용 여부
    """
    base = min(unique_commands * 8, 40)  # 최대 40점 (5종이면 40)
    frequency = min(total_invocations * 0.5, 20)  # 최대 20점
    advanced = 0
    if has_harness: advanced += 15
    if has_agent_team: advanced += 10
    if has_custom_skill: advanced += 10
    if has_plugin: advanced += 5
    return min(round(base + frequency + advanced), 100)

def score_context(claude_dir_ratio, file_path_rate, screenshot_count, url_count, error_paste_rate):
    """컨텍스트 제공 점수 (완전 자동)
    - claude_dir_ratio: .claude/ 디렉토리 보유 세션 비율 (0~1)
    - file_path_rate: 세션당 파일 경로 명시 비율
    - screenshot_count: 스크린샷/이미지 첨부 횟수
    - url_count: URL 참조 횟수
    - error_paste_rate: 에러 메시지 붙여넣기 비율
    """
    # .claude/ = 환경 사전 구성 — 가장 중요한 컨텍스트 전략
    # 50% 이상이면 체계적 사용자. 비선형 스케일 적용.
    if claude_dir_ratio >= 0.7: env_setup = 55
    elif claude_dir_ratio >= 0.5: env_setup = 45
    elif claude_dir_ratio >= 0.3: env_setup = 35
    elif claude_dir_ratio >= 0.1: env_setup = 20
    else: env_setup = 0

    inline = 0
    # 파일 경로 — 세션 당 비율이 아닌, 사용 여부 + 빈도 기반
    inline += min(file_path_rate * 100, 15)  # 파일 경로. 최대 15점
    inline += min(screenshot_count, 10)  # 스크린샷. 최대 10점
    inline += min(url_count, 10)  # URL. 최대 10점
    inline += min(error_paste_rate * 100, 10)  # 에러 붙여넣기. 최대 10점
    return min(round(env_setup + inline), 100)

def score_creativity(unique_domains, unique_projects, has_meta_usage):
    """창의성 점수 (완전 자동)
    - unique_domains: 활용 도메인 종류 수 (8개 카테고리 기준)
    - unique_projects: 고유 프로젝트 수
    - has_meta_usage: AI로 AI 환경을 만드는 메타적 활용 여부 (하네스 설계 등)
    """
    domain_score = min(unique_domains * 10, 60)  # 최대 60점 (6종이면 60)
    project_diversity = min(unique_projects * 1.5, 25)  # 최대 25점
    meta_bonus = 15 if has_meta_usage else 0  # 메타적 활용 보너스
    return min(round(domain_score + project_diversity + meta_bonus), 100)

def score_efficiency(median_turns, correction_rate, interrupt_rate):
    """효율성 점수 (완전 자동)
    - median_turns: 세션당 턴 수 중앙값
    - correction_rate: 수정/교정 비율 (0~1)
    - interrupt_rate: 중단 비율 (0~1)
    """
    # 턴 수: 낮을수록 좋음 (단, 1~3턴은 너무 짧은 세션이므로 중립)
    if median_turns <= 5: turn_score = 40
    elif median_turns <= 10: turn_score = 38
    elif median_turns <= 20: turn_score = 35
    elif median_turns <= 30: turn_score = 30
    elif median_turns <= 50: turn_score = 25
    elif median_turns <= 80: turn_score = 20
    else: turn_score = 15

    # 수정 비율: 낮을수록 좋음
    if correction_rate <= 0.01: correction_score = 30
    elif correction_rate <= 0.03: correction_score = 25
    elif correction_rate <= 0.05: correction_score = 20
    elif correction_rate <= 0.10: correction_score = 15
    else: correction_score = 10

    # 중단 비율: 낮을수록 좋음
    if interrupt_rate <= 0.02: interrupt_score = 30
    elif interrupt_rate <= 0.05: interrupt_score = 25
    elif interrupt_rate <= 0.10: interrupt_score = 20
    else: interrupt_score = 15

    return min(turn_score + correction_score + interrupt_score, 100)

def classify_prompt_role(clean_text, prev_assistant_text="", has_command=False):
    """프롬프트의 대화 역할을 분류한다.

    대화 흐름에서 각 프롬프트가 수행하는 역할을 파악하여,
    역할에 맞지 않는 채점 기준이 적용되는 것을 방지한다.

    Returns:
        str: 'instruction' | 'confirmation' | 'refinement' | 'feedback' |
             'operational' | 'command' | 'noise'
    """
    t = clean_text.strip()
    t_lower = t.lower()

    # 1. command — 슬래시 커맨드가 포함된 턴
    if has_command:
        return "command"

    # 2. noise — 시스템 출력, 인터럽트, 무의미 텍스트
    noise_patterns = [
        r"^Full transcript available",
        r"^Read the output file",
        r"^\[Request interrupted",
        r"^Tool loaded",
        r"^Unknown skill:",
        r"^<bash-input>",
        r"^This session is being continued",
    ]
    for pat in noise_patterns:
        if re.match(pat, t):
            return "noise"

    # 3. confirmation — 이전 AI 응답에 대한 확인/동의
    confirmation_patterns = [
        r"^(네|예|ㅇㅇ|ㅇㅋ|ok|okay|yes|sure|맞아|맞습니다|동일합니다|동일|좋아|좋습니다|좋아요|괜찮아|그래|그렇게|진행|시작합니다|시작|고|ㄱ|ㄱㄱ|go)[\s.!]*$",
        r"^(알겠습니다|확인|understood|agreed|동의)[\s.!]*$",
    ]
    if len(t) < 30:
        for pat in confirmation_patterns:
            if re.match(pat, t, re.IGNORECASE):
                return "confirmation"

    # 4. operational — 서버/빌드/커밋 등 운영 명령
    operational_patterns = [
        r"^\d{4}\s*포트",          # "3001 포트로 실행해"
        r"\d{4}\s*번?\s*포트",     # "3000번 포트로 서버 재시작"
        r"포트로\s*(실행|올려|시작|재시작|내려)",
        r"^(커밋|commit|push|푸시|커밋\s*푸시)",
        r"^서버\s*(재시작|시작|중지|올려|내려)",
        r"^(swift run|npm run|yarn |pip |python3?\s)",
        r"^(cd |ls |mkdir |rm )",
        r"포트\s*(내려|올려|열어|닫아)",
        r"^nextjs\s*(모든\s*)?서버\s*(중지|시작)",
    ]
    for pat in operational_patterns:
        if re.search(pat, t, re.IGNORECASE):
            return "operational"

    # 5. feedback — 이전 결과에 대한 피드백 (개선 방향 포함)
    #    "이상해" 같은 짧은 증상 보고도 feedback에 해당
    feedback_patterns = [
        r"(이상하[게다]|이상합니다|이상해|이상함)",
        r"(안\s*됨|안됨|안\s*돼|안돼|안\s*나옴|안\s*뜸|안\s*보임)",
        r"(로딩이|깨짐|깨져|넘침|넘쳐|잘림|잘려|없어$|없음$|없습니다$)",
        r"(에러|오류|버그|실패|failed|error)",
        r"^.{0,10}(없어|없음|빠졌|누락|missing)",
    ]
    # feedback은 이전 assistant 턴이 있을 때만 (첫 턴이 아닌 경우)
    if prev_assistant_text:
        for pat in feedback_patterns:
            if re.search(pat, t, re.IGNORECASE):
                return "feedback"

    # 6. refinement — 이전 결과를 기반으로 세부 조정
    #    "좀 더", "거기에", "추가로" 등의 증분 요청
    refinement_patterns = [
        r"(좀\s*더|조금\s*더|더\s*크게|더\s*작게|더\s*넓게|더\s*좁게)",
        r"(거기에|추가로|추가해|그리고|또|다시\s*그려|다시\s*만들)",
        r"(수정해|변경해|바꿔|고쳐|빼줘|넣어줘|제거|삭제해줘)",
        r"^(여백|폰트|색|크기|비율|간격|사이즈|높이|너비|위치)",
    ]
    if prev_assistant_text:
        for pat in refinement_patterns:
            if re.search(pat, t, re.IGNORECASE):
                return "refinement"

    # 7. instruction — 새로운 작업 지시 (기본값)
    return "instruction"


def score_decomposition(plan_implement_count, harness_setup_ratio, avg_prompt_length,
                        agent_count=0, skill_count=0):
    """작업 분해 점수 (반자동 — 패턴 기반 + 환경 스캔)
    - plan_implement_count: Plan→Implement 패턴 사용 횟수
    - harness_setup_ratio: 하네스로 사전 설계한 세션 비율
    - avg_prompt_length: 프롬프트 중앙값 길이
    - agent_count: 프로젝트에 정의된 에이전트 파일 총 수 (환경 스캔)
    - skill_count: 프로젝트에 정의된 스킬 파일 총 수 (환경 스캔)
    """
    plan_score = min(plan_implement_count * 10, 15)  # 최대 15점
    harness_score = min(harness_setup_ratio * 50, 30)  # 최대 30점

    # 에이전트/스킬 사전 정의 = 고급 작업 분해 (환경 레벨)
    # 에이전트를 미리 정의하고 스킬을 구성하는 것 자체가 시스템적 분해
    if agent_count >= 50: agent_score = 25
    elif agent_count >= 20: agent_score = 20
    elif agent_count >= 5: agent_score = 15
    elif agent_count >= 1: agent_score = 10
    else: agent_score = 0

    if skill_count >= 30: skill_score = 15
    elif skill_count >= 10: skill_score = 12
    elif skill_count >= 3: skill_score = 8
    elif skill_count >= 1: skill_score = 5
    else: skill_score = 0

    # 프롬프트 길이 (보조 지표)
    if 50 <= avg_prompt_length <= 300: length_score = 15
    elif 30 <= avg_prompt_length <= 500: length_score = 12
    elif avg_prompt_length < 30: length_score = 10
    else: length_score = 8

    return min(plan_score + harness_score + agent_score + skill_score + length_score, 100)


def scan_project_environments(session_cwds):
    """프로젝트 디렉토리에서 .claude/ 환경 구성을 스캔.
    세션의 cwd 목록에서 중복 제거 후 각 프로젝트를 검사한다.

    Returns:
        dict: 환경 구성 통계
    """
    unique_cwds = set(cwd for cwd in session_cwds if cwd and os.path.exists(cwd))

    env = {
        "total_projects": len(unique_cwds),
        "has_claude_dir": 0,
        "has_claude_md": 0,
        "has_settings_json": 0,
        "agent_count": 0,
        "skill_count": 0,
        "has_commands": 0,
        "external_tools": set(),
        "projects_with_agents": 0,
        "projects_with_skills": 0,
    }

    for cwd in unique_cwds:
        claude_dir = os.path.join(cwd, ".claude")
        if not os.path.exists(claude_dir):
            continue

        env["has_claude_dir"] += 1

        # CLAUDE.md
        for md_path in [os.path.join(cwd, "CLAUDE.md"), os.path.join(claude_dir, "CLAUDE.md")]:
            if os.path.exists(md_path):
                env["has_claude_md"] += 1
                try:
                    with open(md_path, errors='replace') as f:
                        content = f.read()[:5000].lower()
                        for tool in ["riper", "superpower", "ohmyclaudecode", "ohmyclaudcode",
                                     "ultrathink", "sparc", "boomerang", "cursor-rules",
                                     "aider", "maestro"]:
                            if tool in content:
                                env["external_tools"].add(tool)
                except: pass
                break

        # settings.json (hooks, permissions 등)
        settings_path = os.path.join(claude_dir, "settings.json")
        if os.path.exists(settings_path):
            env["has_settings_json"] += 1

        # agents/
        agents_dir = os.path.join(claude_dir, "agents")
        if os.path.exists(agents_dir):
            count = len(glob.glob(os.path.join(agents_dir, "*.md")))
            if count > 0:
                env["projects_with_agents"] += 1
                env["agent_count"] += count

        # skills/
        skills_dir = os.path.join(claude_dir, "skills")
        if os.path.exists(skills_dir):
            count = len(glob.glob(os.path.join(skills_dir, "*/skill.md")))
            if count > 0:
                env["projects_with_skills"] += 1
                env["skill_count"] += count

        # commands/
        commands_dir = os.path.join(claude_dir, "commands")
        if os.path.exists(commands_dir):
            if len(os.listdir(commands_dir)) > 0:
                env["has_commands"] += 1

    # 글로벌 스킬도 카운트
    global_skills = os.path.expanduser("~/.claude/skills/")
    if os.path.exists(global_skills):
        for sd in os.listdir(global_skills):
            if os.path.isdir(os.path.join(global_skills, sd)):
                env["skill_count"] += 1

    # 글로벌 플러그인
    global_plugins = os.path.expanduser("~/.claude/plugins/")
    if os.path.exists(global_plugins):
        for pd in os.listdir(global_plugins):
            if os.path.isdir(os.path.join(global_plugins, pd)):
                env["external_tools"].add(f"plugin:{pd}")

    # 글로벌 CLAUDE.md
    global_md = os.path.expanduser("~/.claude/CLAUDE.md")
    if os.path.exists(global_md):
        try:
            with open(global_md, errors='replace') as f:
                content = f.read()[:3000].lower()
                for tool in ["riper", "superpower", "ohmyclaudecode", "ultrathink", "sparc"]:
                    if tool in content:
                        env["external_tools"].add(tool)
        except: pass

    env["external_tools"] = list(env["external_tools"])
    return env


# === 데이터 수집 ===

def collect_sessions(days=28):
    """최근 N일간의 세션 수집."""
    now_kst = datetime.now(KST)
    start_date = (now_kst - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
    start_utc_iso = start_date.astimezone(timezone.utc).isoformat()
    start_unix = start_date.timestamp()

    projects_dir = os.path.expanduser("~/.claude/projects/")
    sessions = []

    for proj_dir in os.listdir(projects_dir):
        dpath = os.path.join(projects_dir, proj_dir)
        if not os.path.isdir(dpath): continue
        for jf in glob.glob(os.path.join(dpath, "*.jsonl")):
            if os.path.getmtime(jf) < start_unix: continue
            first_ts = None; cwd = None
            with open(jf) as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("type") in ("user", "system"):
                            first_ts = entry.get("timestamp")
                            cwd = entry.get("cwd")
                            break
                    except: pass
            if first_ts and first_ts >= start_utc_iso:
                sessions.append({"path": jf, "first_ts": first_ts, "cwd": cwd})

    sessions.sort(key=lambda x: x["first_ts"])
    return sessions, start_date, now_kst


def extract_metrics(sessions, max_sample=50):
    """세션에서 정량 지표를 추출."""
    import random
    sample = random.sample(sessions, min(max_sample, len(sessions))) if len(sessions) > max_sample else sessions

    domain_patterns = {
        "coding": r"(function|class |import |def |const |var |let |error|bug|fix|debug|build|deploy|port |npm|pip)",
        "writing": r"(소설|글|작성|챕터|에필로그|서문|문체|집필|원고|스토리)",
        "image": r"(이미지|삽화|그려|표지|cover|image|사진|스크린샷|일러스트)",
        "analysis": r"(분석|평가|조사|리서치|정책|과제|사업|인력|통계)",
        "design": r"(설계|아키텍처|하네스|에이전트|스킬|플러그인|harness|architect)",
        "document": r"(문서|번역|translate|마크다운|markdown|pdf|docx|pptx|hwp)",
        "management": r"(일정|캘린더|스케줄|회의|미팅|git|커밋|push|merge|PR)",
        "education": r"(멘토링|강의|워크샵|교육|학습|실습|튜토리얼)",
    }

    utility_commands = {'/exit', '/clear', '/compact', '/login', '/init', '/voice'}

    m = {
        "total_sessions": len(sessions),
        "sampled_sessions": len(sample),
        "slash_commands": defaultdict(int),
        "unique_projects": set(),
        "total_user_turns": 0,
        "total_corrections": 0,
        "total_interrupts": 0,
        "prompt_lengths": [],
        "turns_per_session": [],
        "claude_dir_count": 0,
        "screenshot_count": 0,
        "url_count": 0,
        "error_paste_count": 0,
        "file_path_count": 0,
        "plan_implement_count": 0,
        "domain_sessions": defaultdict(int),
        "harness_sessions": 0,
        # 대화 역할 분류 통계
        "prompt_roles": defaultdict(int),
        "scorable_turns": 0,  # 채점 대상 프롬프트 수 (instruction + refinement + feedback)
    }

    for s in sample:
        cwd = s.get("cwd", "")
        if cwd:
            m["unique_projects"].add(os.path.basename(cwd))
            if os.path.exists(os.path.join(cwd, ".claude")):
                m["claude_dir_count"] += 1

        user_turns = 0
        session_domains = set()
        has_harness = False
        prev_assistant_text = ""  # 이전 assistant 턴 텍스트 (대화 맥락 추적)

        with open(s["path"], errors='replace') as f:
            for line in f:
                try:
                    entry = json.loads(line)

                    # === assistant 턴 추적 (대화 맥락용) ===
                    if entry.get("type") == "assistant":
                        msg = entry.get("message", {})
                        content = msg.get("content", "") if isinstance(msg, dict) else ""
                        if isinstance(content, str):
                            prev_assistant_text = content[:500]
                        elif isinstance(content, list):
                            for b in content:
                                if isinstance(b, dict) and b.get("type") == "text":
                                    prev_assistant_text = b.get("text", "")[:500]
                                    break
                        continue

                    if entry.get("type") != "user": continue
                    user_turns += 1
                    msg = entry.get("message", {})
                    content = msg.get("content", "") if isinstance(msg, dict) else ""
                    text = ""
                    if isinstance(content, str): text = content
                    elif isinstance(content, list):
                        for b in content:
                            if isinstance(b, dict) and b.get("type") == "text":
                                text = b["text"]; break

                    if not text.strip(): continue

                    # 슬래시 커맨드 (원본 text에서 추출)
                    has_command = False
                    cmd = re.search(r"<command-name>(/[\w:-]+)</command-name>", text)
                    if cmd:
                        c = cmd.group(1)
                        m["slash_commands"][c] += 1
                        if "harness" in c.lower(): has_harness = True
                        has_command = True

                    # === 시스템 태그 전처리 ===
                    # 스킬 본문, 커맨드 메시지, 시스템 알림 등을 제거하여
                    # 순수 사용자 프롬프트만 추출. 이 clean 텍스트를
                    # 이후 모든 지표(도메인, 수정, 컨텍스트 등)에 사용.
                    clean = text
                    # XML 태그 쌍 제거 (스킬 본문, 시스템 알림 등)
                    clean = re.sub(r'<command-message>.*?</command-message>', '', clean, flags=re.DOTALL)
                    clean = re.sub(r'<command-name>.*?</command-name>', '', clean, flags=re.DOTALL)
                    clean = re.sub(r'<command-args>.*?</command-args>', '', clean, flags=re.DOTALL)
                    clean = re.sub(r'<system-reminder>.*?</system-reminder>', '', clean, flags=re.DOTALL)
                    clean = re.sub(r'<local-command-stdout>.*?</local-command-stdout>', '', clean, flags=re.DOTALL)
                    clean = re.sub(r'<local-command-caveat>.*?</local-command-caveat>', '', clean, flags=re.DOTALL)
                    clean = re.sub(r'<task-notification>.*?</task-notification>', '', clean, flags=re.DOTALL)
                    clean = re.sub(r'<teammate-message[^>]*>.*?</teammate-message>', '', clean, flags=re.DOTALL)
                    clean = re.sub(r'<hook-[^>]*>.*?</hook-[^>]*>', '', clean, flags=re.DOTALL)
                    clean = re.sub(r'<user-prompt-submit-hook>.*?</user-prompt-submit-hook>', '', clean, flags=re.DOTALL)
                    clean = re.sub(r'<bash-stdout>.*?</bash-stdout>', '', clean, flags=re.DOTALL)
                    clean = re.sub(r'<bash-stderr>.*?</bash-stderr>', '', clean, flags=re.DOTALL)
                    # "Base directory for this skill:" 이후 스킬 본문 제거
                    clean = re.sub(r'Base directory for this skill:.*', '', clean, flags=re.DOTALL)
                    # "ARGUMENTS:" 이후 부분만 보존 (슬래시 커맨드의 실제 사용자 인자)
                    args_match = re.search(r'ARGUMENTS:\s*(.*)', clean, flags=re.DOTALL)
                    if args_match and len(clean) > 500:
                        # 스킬 본문이 포함된 긴 텍스트에서 ARGUMENTS 부분만 추출
                        clean = args_match.group(1)
                    clean = clean.strip()

                    # === 대화 역할 분류 ===
                    role = classify_prompt_role(clean, prev_assistant_text, has_command)
                    m["prompt_roles"][role] += 1

                    # 채점 대상: instruction, refinement, feedback만
                    is_scorable = role in ("instruction", "refinement", "feedback")
                    if is_scorable:
                        m["scorable_turns"] += 1

                    # 프롬프트 길이 (채점 대상만)
                    if is_scorable and 5 < len(clean) < 5000:
                        m["prompt_lengths"].append(len(clean))

                    # clean이 너무 짧으면 (시스템 메시지만 있었던 경우) 스킵
                    if len(clean) < 3:
                        prev_assistant_text = ""  # reset for next turn
                        continue

                    # 수정/교정 — confirmation/operational은 제외
                    # "다시 해"는 refinement 맥락에서는 교정이 아닌 정상 반복 요청
                    if is_scorable:
                        for pat in [r"아니[요]?\s", r"그게 아니", r"잘못", r"되돌려", r"취소"]:
                            if re.search(pat, clean[:300]):
                                m["total_corrections"] += 1; break

                    # 중단
                    if "[Request interrupted" in text:
                        m["total_interrupts"] += 1

                    # 컨텍스트 지표 (clean 텍스트 기반)
                    if "[Image:" in text or "스크린샷" in clean: m["screenshot_count"] += 1
                    if re.search(r"https?://", clean): m["url_count"] += 1
                    if re.search(r"(Error|error|Exception|Failed|failed|Cannot|cannot)", clean): m["error_paste_count"] += 1
                    if re.search(r"/[A-Za-z][A-Za-z0-9_/.-]+\.\w{1,5}", clean): m["file_path_count"] += 1

                    # 작업 분해
                    if "Implement the following plan" in clean: m["plan_implement_count"] += 1

                    # 도메인 (clean 텍스트 기반 — 스킬 본문 오탐 방지)
                    for domain, pattern in domain_patterns.items():
                        if re.search(pattern, clean, re.IGNORECASE):
                            session_domains.add(domain)

                    # 이전 assistant 텍스트 리셋 (다음 user 턴을 위해)
                    prev_assistant_text = ""

                except: pass

        m["total_user_turns"] += user_turns
        m["turns_per_session"].append(user_turns)
        if has_harness: m["harness_sessions"] += 1
        for d in session_domains:
            m["domain_sessions"][d] += 1

    m["unique_projects"] = list(m["unique_projects"])
    m["slash_commands"] = dict(m["slash_commands"])
    m["domain_sessions"] = dict(m["domain_sessions"])
    m["prompt_roles"] = dict(m["prompt_roles"])
    return m


def calculate_scores(m, env=None):
    """정량 지표에서 점수를 산출.
    Args:
        m: extract_metrics 결과
        env: scan_project_environments 결과 (optional)
    """
    n = m["sampled_sessions"]
    utility_commands = {'/exit', '/clear', '/compact', '/login', '/init', '/voice'}

    # 도구 활용
    functional_cmds = {k: v for k, v in m["slash_commands"].items() if k not in utility_commands}
    unique_cmds = len(functional_cmds)
    total_invocations = sum(functional_cmds.values())
    has_harness = any("harness" in k for k in m["slash_commands"])
    has_plugin = any("plugin" in k or "reload" in k for k in m["slash_commands"])
    has_meta = has_harness

    # 환경 스캔에서 추가 도구 정보 반영
    has_custom_skill = has_harness
    if env:
        has_custom_skill = has_custom_skill or env.get("skill_count", 0) > 0
        has_plugin = has_plugin or len(env.get("external_tools", [])) > 0

    tool_score = score_tool_usage(
        unique_commands=unique_cmds,
        total_invocations=total_invocations,
        has_harness=has_harness,
        has_agent_team=has_harness,
        has_custom_skill=has_custom_skill,
        has_plugin=has_plugin
    )

    # 컨텍스트 — 환경 스캔으로 .claude/ 비율을 더 정확하게 측정
    claude_dir_ratio = m["claude_dir_count"] / max(n, 1)
    if env:
        # 전체 프로젝트 대비 .claude/ 비율 (샘플이 아닌 실제 비율)
        env_ratio = env.get("has_claude_dir", 0) / max(env.get("total_projects", 1), 1)
        claude_dir_ratio = max(claude_dir_ratio, env_ratio)  # 더 높은 쪽 사용

    context_score = score_context(
        claude_dir_ratio=claude_dir_ratio,
        file_path_rate=m["file_path_count"] / max(m["total_user_turns"], 1),
        screenshot_count=m["screenshot_count"],
        url_count=m["url_count"],
        error_paste_rate=m["error_paste_count"] / max(m["total_user_turns"], 1)
    )
    # CLAUDE.md 보너스: 프로젝트에 CLAUDE.md를 작성한 경우 추가 컨텍스트 제공
    if env and env.get("has_claude_md", 0) >= 3:
        context_score = min(context_score + 10, 100)

    # 창의성
    creativity_score = score_creativity(
        unique_domains=len(m["domain_sessions"]),
        unique_projects=len(m["unique_projects"]),
        has_meta_usage=has_meta
    )

    # 효율성 — 수정률은 채점 대상 턴 기준으로 계산
    tps = m["turns_per_session"]
    median_turns = sorted(tps)[len(tps) // 2] if tps else 0
    scorable = max(m.get("scorable_turns", m["total_user_turns"]), 1)
    efficiency_score = score_efficiency(
        median_turns=median_turns,
        correction_rate=m["total_corrections"] / scorable,
        interrupt_rate=m["total_interrupts"] / max(m["total_user_turns"], 1)
    )

    # 작업 분해 — 환경 스캔의 에이전트/스킬 수 반영
    pl = m["prompt_lengths"]
    median_pl = sorted(pl)[len(pl) // 2] if pl else 0
    agent_count = env.get("agent_count", 0) if env else 0
    skill_count = env.get("skill_count", 0) if env else 0
    decomposition_score = score_decomposition(
        plan_implement_count=m["plan_implement_count"],
        harness_setup_ratio=m["harness_sessions"] / max(n, 1),
        avg_prompt_length=median_pl,
        agent_count=agent_count,
        skill_count=skill_count
    )

    # 근거 문자열 생성
    tool_basis = f"기능커맨드 {unique_cmds}종 {total_invocations}회, harness={has_harness}, plugin={has_plugin}"
    context_basis = f".claude/ {claude_dir_ratio*100:.0f}%, 파일경로 {m['file_path_count']}, 스크린샷 {m['screenshot_count']}, URL {m['url_count']}"
    decomp_basis = f"Plan→Impl {m['plan_implement_count']}회, 하네스 {m['harness_sessions']}/{n} ({m['harness_sessions']/max(n,1)*100:.0f}%), 에이전트 {agent_count}개, 스킬 {skill_count}개"

    if env:
        ext_tools = env.get("external_tools", [])
        if ext_tools:
            tool_basis += f", 외부도구 {len(ext_tools)}종"
        if env.get("has_claude_md", 0) > 0:
            context_basis += f", CLAUDE.md {env['has_claude_md']}개"

    return {
        "tool_usage": {"score": tool_score, "basis": tool_basis},
        "context": {"score": context_score, "basis": context_basis},
        "creativity": {"score": creativity_score, "basis": f"도메인 {len(m['domain_sessions'])}종, 프로젝트 {len(m['unique_projects'])}개, 메타활용={has_meta}"},
        "efficiency": {"score": efficiency_score, "basis": f"중앙값 {median_turns}턴, 수정률 {m['total_corrections']/max(m['total_user_turns'],1)*100:.1f}%, 중단률 {m['total_interrupts']/max(m['total_user_turns'],1)*100:.1f}%"},
        "decomposition": {"score": decomposition_score, "basis": decomp_basis},
    }


def grade(score):
    if score >= 90: return 'S'
    if score >= 80: return 'A'
    if score >= 70: return 'B'
    if score >= 60: return 'C'
    if score >= 50: return 'D'
    return 'F'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=28)
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    sessions, start, end = collect_sessions(args.days)
    print(f"기간: {start.strftime('%Y-%m-%d')} ~ {end.strftime('%Y-%m-%d')}")
    print(f"세션: {len(sessions)}개")

    if not sessions:
        print("분석할 세션이 없습니다.")
        sys.exit(0)

    metrics = extract_metrics(sessions)

    # 프로젝트 환경 스캔 (에이전트/스킬/CLAUDE.md/외부 도구)
    session_cwds = [s.get("cwd") for s in sessions]
    env = scan_project_environments(session_cwds)
    print(f"환경: {env['has_claude_dir']}/{env['total_projects']}개 프로젝트에 .claude/, "
          f"에이전트 {env['agent_count']}개, 스킬 {env['skill_count']}개, "
          f"CLAUDE.md {env['has_claude_md']}개, 외부도구 {len(env['external_tools'])}종")

    # 대화 역할 분류 통계 출력
    roles = metrics.get("prompt_roles", {})
    scorable = metrics.get("scorable_turns", 0)
    total = metrics.get("total_user_turns", 0)
    print(f"\n대화 역할 분류: 총 {total}턴 → 채점 대상 {scorable}턴 ({scorable/max(total,1)*100:.0f}%)")
    for role in ["instruction", "refinement", "feedback", "confirmation", "operational", "command", "noise"]:
        cnt = roles.get(role, 0)
        tag = " ← 채점" if role in ("instruction", "refinement", "feedback") else " ← 제외"
        print(f"  {role:15s}: {cnt:4d}개 ({cnt/max(total,1)*100:.1f}%){tag}")
    print()

    scores = calculate_scores(metrics, env=env)

    print("=== 정량 채점 결과 (자동) ===\n")
    print("| 역량 | 점수 | 등급 | 산출 근거 |")
    print("|------|------|------|----------|")
    for dim, data in scores.items():
        print(f"| {dim} | {data['score']} | {grade(data['score'])} | {data['basis']} |")

    auto_scores = [v["score"] for v in scores.values()]
    auto_avg = sum(auto_scores) / len(auto_scores)
    print(f"\n자동 채점 5축 평균: {auto_avg:.1f}")
    print(f"\n※ 명확성(clarity), 구체성(specificity), 반복개선(iteration) 3축은")
    print(f"  프롬프트 텍스트의 질적 분석이 필요하여 LLM 판단으로 채점합니다.")
    print(f"  LLM 판단 축은 채점 근거를 프롬프트 인용과 함께 명시합니다.")

    if args.output:
        result = {
            "period": f"{start.strftime('%Y-%m-%d')} ~ {end.strftime('%Y-%m-%d')}",
            "total_sessions": len(sessions),
            "auto_scores": {k: v["score"] for k, v in scores.items()},
            "auto_basis": {k: v["basis"] for k, v in scores.items()},
            "metrics": {k: v for k, v in metrics.items() if k != "prompt_lengths"},
            "prompt_roles": metrics.get("prompt_roles", {}),
            "scorable_turns": metrics.get("scorable_turns", 0),
            "environment": env,
            "llm_required": ["clarity", "specificity", "iteration"]
        }
        with open(args.output, 'w') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n저장: {args.output}")
