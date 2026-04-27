# OpenAI GPT Image API 레퍼런스

2026-04 기준. SKILL.md에서 깊은 설명이 필요할 때 참조한다.

## 목차

1. [모델 특성 (gpt-image-2)](#모델-특성-gpt-image-2)
2. [엔드포인트](#엔드포인트)
3. [Image API 파라미터](#image-api-파라미터)
4. [Responses API 이미지 생성](#responses-api-이미지-생성)
5. [응답 스키마](#응답-스키마)
6. [스트리밍 이벤트](#스트리밍-이벤트)
7. [마스크 제작 가이드](#마스크-제작-가이드)
8. [Node.js 예시](#nodejs-예시)
9. [cURL 예시](#curl-예시)
10. [오류 처리](#오류-처리)
11. [프롬프트 패턴](#프롬프트-패턴)
12. [비용 표](#비용-표)

## 모델 특성 (gpt-image-2)

이 스킬은 모델을 `gpt-image-2`로 고정한다. 구세대 `gpt-image-1` 계열·mini 변형 등 다른 OpenAI 이미지 모델은 범위 외다.

- **해상도**. 한 변 최대 3840px (2K·4K 자산 생성 가능)
- **편집 충실도**. `input_fidelity` 기본값이 자동 고충실도. 얼굴·로고·텍스트 보존력 우수
- **텍스트 렌더링**. DALL·E 계열보다 크게 개선, 다만 복잡한 타이포는 재시도 필요
- **사진 리얼리즘**. "Not a screenshot" 수준의 사실감
- **제약**. `background="transparent"` 미지원 (실질 `"opaque"` 고정)

## 엔드포인트

### Image API

| 엔드포인트 | 메서드 | 용도 |
|------------|--------|------|
| `/v1/images/generations` | POST | 텍스트 → 이미지 |
| `/v1/images/edits` | POST | 이미지 편집 (인페인팅·멀티 레퍼런스) |

`/v1/images/variations`는 DALL·E 전용. gpt-image 계열은 지원하지 않는다. 변형이 필요하면 edits에 같은 이미지를 넣고 프롬프트로 지시한다.

### Responses API

`/v1/responses` 엔드포인트에 `tools: [{"type": "image_generation"}]`를 넘기면 추론 모델 (예. `gpt-5.4`)이 필요에 따라 이미지 생성 툴을 호출한다. 멀티턴에 최적.

## Image API 파라미터

### 공통

| 이름 | 타입 | 기본 | 설명 |
|------|------|------|------|
| `model` | string | - | 이 스킬은 `"gpt-image-2"` 로 고정 |
| `prompt` | string | - | 이미지 묘사 (영어·한국어 모두 동작) |
| `n` | int | 1 | 한 요청당 이미지 수 |
| `size` | string | `"auto"` | 해상도. 아래 표 참고 |
| `quality` | string | `"auto"` | `"low" / "medium" / "high" / "auto"` |
| `output_format` | string | `"png"` | `"png" / "jpeg" / "webp"` |
| `output_compression` | int | - | 0-100, jpeg·webp만 |
| `background` | string | `"opaque"` | gpt-image-2는 `"transparent"` 미지원이므로 실질 고정 |
| `moderation` | string | `"auto"` | `"auto" / "low"`. low는 느슨한 검증 |
| `user` | string | - | 최종 사용자 식별자 (악용 탐지용) |

**size 제약 (gpt-image-2)**.
- 한 변 64-3840px
- 16의 배수
- 종횡비 3:1 이내 (즉 긴 변:짧은 변 ≤ 3)
- 자주 쓰는 프리셋. `1024x1024`, `1536x1024`, `1024x1536`, `2048x2048`, `2560x1440`, `1440x2560`
- `"auto"` 지정 시 프롬프트에 맞춰 적절한 크기 선택

### 편집 전용

| 이름 | 타입 | 설명 |
|------|------|------|
| `image` | file / file[] | 편집 대상. 배열이면 멀티 레퍼런스 합성 |
| `mask` | file | 알파 채널 PNG. 알파 0인 영역이 재생성 |
| `input_fidelity` | string | `"auto" / "high"`. 기본은 auto. 얼굴·로고 보존 시 `"high"` |

편집 시 참조 이미지는 최대 10장, 각 20MB 이하. PNG/JPEG/WebP 허용.

### 스트리밍 전용

| 이름 | 타입 | 설명 |
|------|------|------|
| `stream` | bool | true면 SSE 이벤트 스트림 |
| `partial_images` | int | 0-3. 중간 이미지 개수 (각 +100 토큰) |

## Responses API 이미지 생성

```python
resp = client.responses.create(
    model="gpt-5.4",
    input="고양이와 수달의 따뜻한 일러스트",
    tools=[{
        "type": "image_generation",
        "model": "gpt-image-2",       # 선택
        "quality": "high",             # 선택
        "size": "1024x1024",           # 선택
        "action": "auto",              # auto/generate/edit
    }],
)
```

출력 파싱.

```python
for item in resp.output:
    if item.type == "image_generation_call":
        b64 = item.result               # base64 PNG
        revised = item.revised_prompt   # 모델이 사용한 실제 프롬프트
```

**멀티턴 체이닝**. `previous_response_id`에 직전 `resp.id`를 전달하면 이전 이미지와 컨텍스트를 그대로 이어받아 수정한다.

## 응답 스키마

### Image API

```json
{
  "created": 1714100000,
  "data": [
    {
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAA...",
      "revised_prompt": "A minimalist coffee shop logo...",
      "background": "opaque",
      "output_format": "png",
      "size": "1024x1024",
      "quality": "high"
    }
  ],
  "usage": {
    "input_tokens": 42,
    "output_tokens": 4160,
    "input_tokens_details": {"text_tokens": 42, "image_tokens": 0},
    "total_tokens": 4202
  }
}
```

`revised_prompt`는 gpt-image-2가 내부적으로 재작성한 최종 프롬프트. 재현성·디버깅에 유용.

### Responses API `image_generation_call`

```json
{
  "type": "image_generation_call",
  "id": "igc_...",
  "status": "completed",
  "result": "iVBORw0KGgo...",
  "revised_prompt": "..."
}
```

## 스트리밍 이벤트

SSE로 오는 이벤트 타입.

- `image_generation.in_progress` — 생성 시작
- `image_generation.partial_image` — 중간 이미지. `partial_image_index`, `b64_json` 포함
- `image_generation.completed` (또는 `image_generation.final_image`) — 최종 이미지
- `image_generation.failed` — 오류. `error` 필드 확인

## 마스크 제작 가이드

**규칙**. PNG + 알파 채널. 알파 0 = 재생성할 구멍. 알파 255 = 원본 유지.

### PIL로 마스크 만들기

```python
from PIL import Image, ImageDraw

# 원본과 같은 크기의 투명 레이어
orig = Image.open("room.png")
mask = Image.new("RGBA", orig.size, (0, 0, 0, 255))

# 편집할 영역을 알파 0으로 (여기선 사각형)
draw = ImageDraw.Draw(mask)
draw.rectangle([100, 200, 500, 600], fill=(0, 0, 0, 0))

mask.save("mask.png")
```

### 그레이스케일을 알파로 변환

포토샵 등에서 흑백 마스크만 만들었다면 알파 채널로 변환해야 한다.

```python
from PIL import Image

gray = Image.open("mask_gray.png").convert("L")
rgba = Image.new("RGBA", gray.size, (0, 0, 0, 255))
# 어두운 영역을 투명하게 (반전이 필요하면 ImageOps.invert)
rgba.putalpha(gray)
rgba.save("mask.png")
```

**주의**. 마스크는 원본 이미지와 **정확히 같은 해상도**여야 한다.

## Node.js 예시

```javascript
import OpenAI from "openai";
import fs from "fs";

const client = new OpenAI();

// 생성
const gen = await client.images.generate({
  model: "gpt-image-2",
  prompt: "미니멀 로고, 'Morning Brew'",
  size: "1024x1024",
  quality: "high",
});
fs.writeFileSync("logo.png", Buffer.from(gen.data[0].b64_json, "base64"));

// 편집 (멀티 레퍼런스)
const edit = await client.images.edit({
  model: "gpt-image-2",
  image: [fs.createReadStream("a.png"), fs.createReadStream("b.png")],
  prompt: "두 제품을 한 바구니에",
});
fs.writeFileSync("basket.png", Buffer.from(edit.data[0].b64_json, "base64"));
```

## cURL 예시

```bash
# 생성
curl -sS https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "산뜻한 아침 풍경",
    "size": "1536x1024",
    "quality": "high"
  }' \
  | jq -r '.data[0].b64_json' | base64 -d > morning.png

# 편집 (멀티파트)
curl -sS https://api.openai.com/v1/images/edits \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F model="gpt-image-2" \
  -F image="@photo.png" \
  -F mask="@mask.png" \
  -F prompt="빈 공간에 소파" \
  | jq -r '.data[0].b64_json' | base64 -d > edited.png
```

## 오류 처리

| HTTP | 사유 | 대응 |
|------|------|------|
| 400 | 파라미터 오류 (크기, 비율, 파일 형식) | size/비율/mime 검증 |
| 401 | API 키 오류 | `OPENAI_API_KEY` 확인 |
| 403 | 조직 미검증 | 개발자 콘솔에서 Organization Verification |
| 429 | 레이트리밋 | 지수 백오프 재시도 (max 5) |
| 400 `content_policy_violation` | 정책 위반 | 프롬프트 완화·대체 표현 |
| 500/503 | 서버 일시 오류 | 짧은 딜레이 후 재시도 |

예시.

```python
from openai import BadRequestError, RateLimitError
import time

for attempt in range(5):
    try:
        result = client.images.generate(model="gpt-image-2", prompt=p)
        break
    except RateLimitError:
        time.sleep(2 ** attempt)
    except BadRequestError as e:
        if "content_policy_violation" in str(e):
            raise ValueError("프롬프트를 완화하세요") from e
        raise
```

## 프롬프트 패턴

### 사진 스타일

```
35mm film photo, a warm-lit bakery interior at dawn, shallow depth of field,
natural light spilling through large windows, pastries on wooden counter,
cozy nostalgic mood, Kodak Portra 400 color palette.
```

### 인포그래픽·다이어그램

```
Clean flat-style infographic explaining photosynthesis with 3 labeled stages.
Use soft pastel palette (mint green, cream, muted orange). Sans-serif bold
headings "Light", "Water", "CO₂". White background. Vector illustration style.
```

### 로고

```
Minimalist circular logo for a coffee brand "Morning Brew". Abstract latte-art
heart in the center, sans-serif bold wordmark below. Monochrome warm brown on
cream background, flat vector, no gradients.
```

### 제품 목업

```
Photorealistic product mockup of a matte white ceramic mug on a walnut table.
Soft window light from the left, minimal shadow, marketing catalog style,
centered composition, 3:2 ratio, background subtly blurred.
```

### 스토리보드 컷

```
Anime storyboard panel: a young girl runs across a rain-soaked street at night,
neon signs reflecting in puddles, low angle, dynamic motion lines, cinematic
rim lighting, Makoto-Shinkai-inspired atmosphere.
```

## 비용 표

**gpt-image-2** (이미지당 대략, 2026-04 기준).

| Quality | 1024×1024 | 1024×1536 | 1536×1024 | 2048×2048 |
|---------|-----------|-----------|-----------|-----------|
| low     | $0.006    | $0.005    | $0.005    | $0.012    |
| medium  | $0.053    | $0.041    | $0.041    | $0.095    |
| high    | $0.211    | $0.165    | $0.165    | $0.380    |

- 편집(`/images/edits`)은 입력 이미지 토큰이 추가된다.
- `partial_images` 각 +100 토큰.
- `input_fidelity=high`는 입력 이미지 토큰을 약 2배로 쓴다.
**반복 루프 팁**. 같은 `gpt-image-2` 안에서 `quality=low`로 20~30회 돌려 구도·프롬프트를 확정한 뒤, 최종 렌더만 `quality=high`로 뽑는 2단계 워크플로우가 가장 비용 효율적이다.

## 보안·정책 주의

- 실존 인물 사진·얼굴 편집은 동의 없이는 피한다. 유명인 초상은 정책 위반 가능.
- 저작권 있는 캐릭터·브랜드 로고는 거부되거나 변형된다. 레퍼런스 스타일로 대체.
- 의료 진단, 실존 사건 오도, 선거 관련 조작 이미지는 명시적으로 금지.
- `user` 파라미터에 엔드유저 ID 해시를 넣으면 악용 대응 협조·할당량 관리에 유리.
