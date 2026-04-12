---
name: gemini-3-pro-imagegen
description: "Google Gemini 이미지 생성/편집 스킬. Nano Banana 2 (gemini-3.1-flash-image-preview), Nano Banana (gemini-3-pro-image-preview), 텍스트-이미지, 이미지 편집, 멀티턴 편집 수행. 사용 시점: AI 이미지 생성, 이미지 편집/수정, 인포그래픽 생성, 로고/스티커 디자인, 제품 목업, 만화/스토리보드, 고해상도(4K) 이미지 필요시. 나노바나나, Gemini 이미지, Google 검색 기반 이미지 생성에 사용."
---

# Gemini Image Generation

Google Gemini 이미지 생성 모델을 사용한 고품질 이미지 생성 및 편집. (2026-03 기준)

## 설치

```bash
pip install google-genai pillow --break-system-packages
```

## 모델 선택

| 모델 | 모델명 | 특징 |
|------|--------|------|
| **Nano Banana Pro** | `gemini-3-pro-image-preview` | 고품질, 4K, 텍스트 렌더링, Thinking |
| **Nano Banana 2** | `gemini-3.1-flash-image-preview` | 최신, Flash 속도 + Pro 품질, 이미지 검색 그라운딩 |

**기본 추천**: 일반 용도 `gemini-3.1-flash-image-preview`, 최고 품질 `gemini-3-pro-image-preview`

## 기본 사용법

### 텍스트 → 이미지 생성

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="미니멀한 커피숍 로고, 'Morning Brew' 텍스트 포함",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="1:1",
            image_size="2K"
        ),
    )
)

for part in response.parts:
    if part.text:
        print(part.text)
    elif image := part.as_image():
        image.save("output.png")
```

### 이미지 편집

```python
from PIL import Image

image_input = Image.open('input.png')
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=["이 이미지의 배경을 일몰로 바꿔줘", image_input],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
    )
)
```

### 멀티턴 편집 (채팅)

```python
chat = client.chats.create(
    model="gemini-3-pro-image-preview",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
    )
)

response1 = chat.send_message("광합성을 설명하는 인포그래픽 만들어줘")
response2 = chat.send_message("이걸 스페인어로 번역해줘")
```

## 설정 옵션

### 비율 (aspect_ratio)

| 비율 | 용도 |
|------|------|
| `1:1` | 정사각형, 프로필, 로고 |
| `16:9` | 와이드스크린, 프레젠테이션 |
| `9:16` | 모바일, 스토리/릴스 |
| `4:3` | 클래식 사진 |
| `3:4` | 세로 인물 |
| `21:9` | 시네마틱 |

### 해상도 (image_size)

| 값 | 설명 |
|----|------|
| `1K` | 기본값 |
| `2K` | 고해상도 |
| `4K` | 최고 해상도 (Pro, Nano Banana 2 지원) |

## 고급 기능

### Google 검색 그라운딩

실시간 정보 기반 이미지 생성 (모든 모델 지원, Nano Banana 2는 **이미지 검색**도 지원):

```python
response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents="오늘 서울 날씨를 시각화한 인포그래픽",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        tools=[{"google_search": {}}]
    )
)
```

### 다중 참조 이미지 (최대 14장)

```python
from PIL import Image

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        "이 사람들의 단체 사진을 만들어줘",
        Image.open('person1.png'),
        Image.open('person2.png'),
        Image.open('person3.png'),
    ],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="5:4",
            image_size="2K"
        ),
    )
)
```

## 스크립트 사용

이미지 생성 스크립트 실행:

```bash
python scripts/generate_image.py "프롬프트" --ratio 16:9 --size 2K --output output.png
```

옵션:
- `--ratio`: 비율 (기본: 1:1)
- `--size`: 해상도 1K/2K/4K (기본: 1K)
- `--output`: 출력 파일명
- `--search`: Google 검색 그라운딩 활성화
- `--input`: 편집할 입력 이미지

## 프롬프트 작성 팁

1. **장면 묘사**: 키워드 나열 대신 서술형 설명
2. **스타일 명시**: "수채화", "3D 렌더링", "미니멀리즘"
3. **조명/구도**: "골든아워 조명", "45도 각도에서"
4. **텍스트 포함시**: 정확한 문구를 따옴표로 감싸기

## 워크플로우

1. 프롬프트 준비 → 구체적이고 상세한 설명
2. 설정 선택 → 비율/해상도 결정
3. 이미지 생성 → `generate_content` 호출
4. **결과 저장 → 반드시 현재 작업 디렉토리(cwd)에 저장. `/tmp` 사용 금지**
5. 파일 공유 → `present_files` 도구로 전달

### 출력 경로 규칙 (필수)

- `--output` 옵션에는 반드시 **현재 작업 디렉토리 기준 상대경로** 또는 **현재 작업 디렉토리의 절대경로**를 사용할 것
- `/tmp`, `/var/tmp` 등 임시 디렉토리에 저장하지 말 것
- 예시: `--output ./generated_image.png` 또는 `--output cat_infographic.png`

## 참고 자료

- API 상세 정보: `references/api_reference.md` 참조
