---
name: gpt-image2
description: "OpenAI GPT Image 2 이미지 생성/편집 스킬. 모델은 gpt-image-2로 고정. 텍스트→이미지, 이미지 편집(마스킹), 멀티 이미지 합성, Responses API 멀티턴 편집, 스트리밍 부분 이미지를 수행. 사용 시점: OpenAI/ChatGPT 이미지 생성, AI 이미지 생성(특히 텍스트 렌더링 품질이 중요하거나 2K 이상 해상도·사실적 사진·인포그래픽·로고·제품 목업·마스킹 편집·멀티 레퍼런스 합성이 필요할 때), GPT Image, DALL-E 후속 모델, ChatGPT Images 2.0 언급 시. Gemini·Nano Banana 요청은 gemini-3-pro-imagegen 스킬이 담당."
---

# OpenAI GPT Image 2

OpenAI `gpt-image-2` 모델로 고품질 이미지 생성·편집을 수행하는 스킬. (2026-04 기준)

이 스킬은 **모델을 `gpt-image-2` 로 고정**한다. 다른 OpenAI 이미지 모델(구세대 `gpt-image-1` 계열, mini 변형 등)은 이 스킬의 범위가 아니다. 비용·속도 최적화를 위해 다른 모델을 쓰고 싶다면 직접 API를 호출한다.

## 설치

```bash
pip install openai pillow --break-system-packages
```

API 키는 환경변수로 설정한다.

```bash
export OPENAI_API_KEY="sk-..."
```

모델을 처음 사용할 때는 OpenAI 개발자 콘솔에서 **Organization Verification**이 필요할 수 있다.

## 모델 특성 (gpt-image-2)

- 최대 3840px (한 변) 고해상도. 2K/4K 자산 생성 가능
- 자동 고충실도 편집 (`input_fidelity` auto-high). 얼굴·로고·텍스트 보존력이 이전 세대보다 크게 향상
- 사실적 사진·텍스트 렌더링 강점. 복잡한 타이포는 여전히 재시도 필요
- `background="transparent"` **미지원** (이 기능이 필수라면 Gemini 계열 등 다른 도구 고려)

## 두 가지 접근 방식

OpenAI는 이미지 생성을 두 가지 API로 제공한다. 상황에 맞게 고른다.

1. **Image API** (`/v1/images/generations`, `/v1/images/edits`). 단일 요청으로 이미지를 생성·편집. 파라미터 제어가 명시적이다. 대부분의 경우 이쪽을 쓴다.
2. **Responses API** (`/v1/responses` + `image_generation` tool). 대화형 멀티턴 편집. `previous_response_id`로 이어서 수정 가능. 모델 추론을 곁들인 반복 루프에 적합.

## 기본 사용법 (Image API)

### 텍스트 → 이미지

```python
from openai import OpenAI
import base64

client = OpenAI()

result = client.images.generate(
    model="gpt-image-2",
    prompt="미니멀한 커피숍 로고, 상단에 'Morning Brew' 텍스트",
    size="1024x1024",
    quality="high",
)

b64 = result.data[0].b64_json
with open("output.png", "wb") as f:
    f.write(base64.b64decode(b64))
```

응답은 항상 base64(`b64_json`)이다. URL 반환은 더 이상 지원되지 않으므로 파일로 저장한다.

### 이미지 편집 (단일 이미지, 프롬프트만)

```python
result = client.images.edit(
    model="gpt-image-2",
    image=open("photo.png", "rb"),
    prompt="배경을 일몰 하늘로 바꿔줘. 인물은 그대로 유지.",
    size="1536x1024",
)
```

### 마스킹 편집 (특정 영역만 수정)

마스크 PNG에서 **투명(알파 0) 영역이 재생성될 부분**이다. 불투명(알파 255)은 원본 유지.

```python
result = client.images.edit(
    model="gpt-image-2",
    image=open("room.png", "rb"),
    mask=open("mask.png", "rb"),
    prompt="빈 공간에 빨간 소파를 놓아줘",
)
```

마스크를 PIL로 만드는 법. L 모드(그레이스케일) 마스크를 알파 채널로 변환.

```python
from PIL import Image
from io import BytesIO

mask = Image.open("mask_gray.png").convert("L")
rgba = mask.convert("RGBA")
rgba.putalpha(mask)
buf = BytesIO()
rgba.save(buf, format="PNG")
with open("mask.png", "wb") as f:
    f.write(buf.getvalue())
```

### 멀티 이미지 합성 (여러 레퍼런스로 새 장면 생성)

```python
result = client.images.edit(
    model="gpt-image-2",
    image=[
        open("lotion.png", "rb"),
        open("soap.png", "rb"),
        open("candle.png", "rb"),
    ],
    prompt="이 제품들이 담긴 우아한 선물 바구니, 흰 배경, 스튜디오 조명",
    size="1024x1024",
)
```

## 번들 헬퍼 스크립트

반복 작업용 CLI를 `scripts/generate_image.py`로 제공한다. 프롬프트만 전달하면 바로 이미지가 저장된다.

```bash
# 텍스트 → 이미지
python scripts/generate_image.py "귀여운 고양이가 책을 읽는 모습"

# 크기·품질 지정
python scripts/generate_image.py "로고 디자인" --size 1024x1024 --quality high --output logo.png

# 편집 (단일 이미지)
python scripts/generate_image.py "배경을 바다로 바꿔줘" --input photo.png --output edited.png

# 마스킹 편집
python scripts/generate_image.py "빈 공간에 소파" --input room.png --mask mask.png

# 멀티 레퍼런스 합성
python scripts/generate_image.py "선물 바구니" --input lotion.png soap.png candle.png

# 여러 장 한번에
python scripts/generate_image.py "미니멀 아이콘 세트" --n 4
```

스크립트는 자동으로 타임스탬프 파일명(`gpt_image_YYYYMMDD_HHMMSS.png`)으로 저장하며 `--output` 지정 시 덮어쓴다.

## 주요 파라미터 요약

| 파라미터 | 값 | 메모 |
|----------|------|------|
| `size` | `"1024x1024"`, `"1024x1536"`, `"1536x1024"`, `"auto"` 등 | gpt-image-2는 최대 3840px 한 변, 16의 배수, 종횡비 3:1 이내 |
| `quality` | `"low"` / `"medium"` / `"high"` / `"auto"` | 토큰 비용이 크게 달라짐 |
| `n` | 정수 (기본 1) | 한번에 생성할 장수 |
| `output_format` | `"png"` (기본) / `"jpeg"` / `"webp"` | png만 무손실 |
| `output_compression` | 0~100 | jpeg/webp 전용 |
| `background` | `"opaque"` (실질 고정) | gpt-image-2는 `"transparent"` 미지원 |
| `moderation` | `"auto"` (기본) / `"low"` | 정책 검증 강도 |
| `stream`, `partial_images` | bool, 0~3 | 중간 이미지 스트리밍 (아래 참고) |

정확한 조합·제약은 `references/api_reference.md` 참고.

## Responses API (멀티턴 편집)

대화형으로 한 이미지를 계속 수정해 나갈 때 사용한다. 추론 모델이 이미지 생성을 툴처럼 호출한다.

```python
from openai import OpenAI
import base64

client = OpenAI()

# 1턴. 초안
resp1 = client.responses.create(
    model="gpt-5.4",
    input="회색 태비 고양이와 수달이 포옹하는 따뜻한 일러스트",
    tools=[{"type": "image_generation"}],
)

# 2턴. 1턴 결과를 이어받아 수정
resp2 = client.responses.create(
    model="gpt-5.4",
    previous_response_id=resp1.id,
    input="사실적인 사진 스타일로 바꿔줘",
    tools=[{"type": "image_generation"}],
)

image_data = [o.result for o in resp2.output if o.type == "image_generation_call"]
with open("final.png", "wb") as f:
    f.write(base64.b64decode(image_data[0]))
```

`image_generation_call` 출력의 `revised_prompt` 필드에 모델이 실제로 사용한 정제된 프롬프트가 담긴다. 디버깅·재현에 유용.

## 스트리밍 (부분 이미지)

긴 생성 중에 중간 이미지를 받아 UX를 개선.

```python
stream = client.images.generate(
    model="gpt-image-2",
    prompt="올빼미 깃털로 흐르는 강",
    stream=True,
    partial_images=2,  # 최대 3
)

import base64
for event in stream:
    if event.type == "image_generation.partial_image":
        with open(f"partial_{event.partial_image_index}.png", "wb") as f:
            f.write(base64.b64decode(event.b64_json))
    elif event.type == "image_generation.completed":
        with open("final.png", "wb") as f:
            f.write(base64.b64decode(event.b64_json))
```

`partial_images`는 장당 +100 토큰의 추가 비용이 든다.

## 품질 높이는 프롬프트 팁

GPT Image 2는 DALL·E보다 훨씬 "문장을 그대로 반영"한다. 그림의 **구성·피사체·스타일·조명·렌즈·분위기**를 구체적으로 적는다.

- **나쁜 예**. "예쁜 커피숍 로고"
- **좋은 예**. "미니멀한 원형 커피숍 로고, 중앙에 라떼아트 하트, 하단에 산세리프 굵은 글자로 'Morning Brew', 따뜻한 브라운-크림 팔레트, 단색 배경, 벡터 스타일"

텍스트 렌더링이 필요하면 **따옴표로 정확한 문구를 감싼다**. gpt-image-2는 길고 단순한 문구의 철자 정확도가 크게 개선됐지만, 복잡한 레이아웃·손글씨는 여전히 흔들릴 수 있어 필요 시 1~2회 재시도한다.

편집 시에는 "무엇을 유지할지"를 명시한다. 예. "인물의 얼굴과 포즈는 그대로 두고 배경만 교체".

## 한계·주의

- 복잡한 프롬프트는 최대 2분까지 지연될 수 있다.
- 텍스트 렌더링은 개선됐으나 완벽하지 않다. 중요한 문구는 후처리(이미지에 합성)를 병행한다.
- 정확한 요소 배치·반복 생성 일관성은 여전히 제한적이다. 레퍼런스 이미지를 활용하거나 Responses API의 멀티턴으로 보완한다.
- 콘텐츠 정책 위반 시 생성이 거부된다. 실재 인물, 저작권 있는 캐릭터·로고는 대체 표현으로 우회한다.

## 비용 감각 (gpt-image-2, 이미지당 대략)

| Quality | 1024×1024 | 1024×1536 | 1536×1024 |
|---------|-----------|-----------|-----------|
| low     | ~$0.006   | ~$0.005   | ~$0.005   |
| medium  | ~$0.053   | ~$0.041   | ~$0.041   |
| high    | ~$0.211   | ~$0.165   | ~$0.165   |

반복 탐색은 `quality=low`로 구도를 잡고 최종 렌더만 `quality=high`로 뽑는 2단계 워크플로우가 비용 효율적.

## 확장 레퍼런스

- `references/api_reference.md`. 전체 파라미터, 응답 스키마, 오류 코드, 모델별 차이표.
- `scripts/generate_image.py`. CLI 헬퍼 (Image API 기반 생성·편집·마스킹·멀티 레퍼런스).
