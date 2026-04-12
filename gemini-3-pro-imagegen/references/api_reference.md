# Gemini Image API Reference (2026-03)

## 모델 정보

### Nano Banana 2 (최신)
- **모델명**: `gemini-3.1-flash-image-preview`
- **특징**: Flash 속도 + Pro 품질, 이미지 검색 그라운딩, 주제 일관성, 정밀 지시 수행
- **지원 해상도**: 1K, 2K, 4K
- **최대 참조 이미지**: 14개

### Nano Banana Pro
- **모델명**: `gemini-3-pro-image-preview`
- **특징**: 전문 자산 제작용, 고급 추론(Thinking), 최고 품질 출력
- **지원 해상도**: 1K, 2K, 4K
- **최대 참조 이미지**: 14개 (객체 6개 + 인물 5개 + 기타)

### Nano Banana
- **모델명**: `gemini-2.5-flash-image`
- **특징**: 안정판, 속도와 효율성 최적화, 대량 처리에 적합
- **지원 해상도**: 1K, 2K

## API 엔드포인트

```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

## 요청 구조

### Python SDK

```python
from google import genai
from google.genai import types

client = genai.Client()  # GOOGLE_API_KEY 환경변수 사용

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=["프롬프트", image_object],  # 문자열 또는 리스트
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="2K"
        ),
        tools=[{"google_search": {}}]  # 선택사항
    )
)
```

### REST API

```bash
curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [
        {"text": "프롬프트"},
        {"inline_data": {"mime_type": "image/png", "data": "BASE64_DATA"}}
      ]
    }],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"],
      "imageConfig": {
        "aspectRatio": "16:9",
        "imageSize": "2K"
      }
    },
    "tools": [{"google_search": {}}]
  }'
```

## 설정 옵션

### response_modalities
응답에 포함할 콘텐츠 유형:
- `['TEXT', 'IMAGE']`: 텍스트와 이미지 모두 반환 (권장)
- `['IMAGE']`: 이미지만 반환

### image_config

#### aspect_ratio (비율)
| 값 | 설명 | 용도 |
|----|------|------|
| `1:1` | 정사각형 | 프로필, 로고, 썸네일 |
| `2:3` | 세로 2:3 | 세로 포스터 |
| `3:2` | 가로 3:2 | 표준 사진 |
| `3:4` | 세로 3:4 | 세로 인물 사진 |
| `4:3` | 가로 4:3 | 클래식 사진, 문서 |
| `4:5` | 세로 4:5 | 인스타그램 세로 |
| `5:4` | 가로 5:4 | 가로 인물 |
| `9:16` | 세로 9:16 | 모바일, 스토리/릴스 |
| `16:9` | 가로 16:9 | 와이드스크린, 프레젠테이션 |
| `21:9` | 울트라와이드 | 시네마틱 |

#### image_size (해상도)
| 값 | 설명 | 지원 모델 |
|----|------|-----------|
| `1K` | 기본 해상도 | 모두 |
| `2K` | 고해상도 | 모두 |
| `4K` | 최고 해상도 | Pro, Nano Banana 2 |

**주의**: 대문자 'K' 사용 필수 (소문자 'k'는 거부됨)

### tools

#### Google 검색 그라운딩
```python
tools=[{"google_search": {}}]
```
- 실시간 정보 기반 이미지 생성
- 날씨, 뉴스, 스포츠 결과 등에 유용
- 응답에 `groundingMetadata` 포함
- **Nano Banana 2**: 이미지 검색 그라운딩도 지원 (텍스트 + 이미지 검색)

## 응답 구조

### Python SDK
```python
for part in response.parts:
    if part.text:
        print(part.text)  # 텍스트 설명
    elif part.inline_data:
        image = part.as_image()  # PIL Image 객체
        image.save("output.png")
```

### 응답 필드
- `parts`: 응답 파트 목록
  - `text`: 텍스트 내용
  - `inline_data`: 이미지 데이터
    - `mime_type`: MIME 타입 (image/png 등)
    - `data`: Base64 인코딩된 이미지 데이터
  - `thought`: Thinking 모드 플래그 (Pro만)
  - `thought_signature`: Thought signature (멀티턴용)

## 멀티턴 대화

### 채팅 세션 생성
```python
chat = client.chats.create(
    model="gemini-3-pro-image-preview",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        tools=[{"google_search": {}}]
    )
)
```

### 메시지 전송
```python
response = chat.send_message("첫 번째 요청")
response = chat.send_message("수정 요청")  # 이전 컨텍스트 유지
```

### 설정 변경 (턴별)
```python
response = chat.send_message(
    "스페인어로 번역해줘",
    config=types.GenerateContentConfig(
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="2K"
        ),
    )
)
```

## Thinking 모드 (Pro, Nano Banana 2)

Gemini 3 Pro와 Nano Banana 2는 복잡한 프롬프트에 대해 "Thinking" 프로세스를 사용합니다.

### Thinking 파트 확인
```python
for part in response.parts:
    if part.thought:
        # Thinking 과정 (중간 이미지 포함 가능)
        if part.text:
            print(f"[Thinking] {part.text}")
    else:
        # 최종 결과
        if image := part.as_image():
            image.save("final.png")
```

### Thought Signatures
멀티턴 대화에서 Thinking 컨텍스트 유지를 위해 자동으로 처리됨.

## 이미지 입력

### PIL Image
```python
from PIL import Image
image_input = Image.open('photo.jpg')
contents = ["프롬프트", image_input]
```

### Base64 (REST)
```json
{
  "inline_data": {
    "mime_type": "image/jpeg",
    "data": "BASE64_ENCODED_DATA"
  }
}
```

### 지원 형식
- JPEG (`image/jpeg`)
- PNG (`image/png`)
- GIF (`image/gif`)
- WebP (`image/webp`)

## 오류 처리

### 일반적인 오류
| 오류 | 원인 | 해결 |
|------|------|------|
| API key invalid | 잘못된 API 키 | GOOGLE_API_KEY 확인 |
| Rate limit exceeded | 요청 한도 초과 | 잠시 후 재시도 |
| Content blocked | 안전 필터 | 프롬프트 수정 |
| Invalid aspect ratio | 잘못된 비율 | 지원 비율 사용 |

### 예외 처리
```python
try:
    response = client.models.generate_content(...)
except Exception as e:
    print(f"오류: {e}")
```

## 제한사항

- 모든 생성 이미지에 SynthID 워터마크 포함
- 저작권 있는 콘텐츠 생성 제한
- 유해 콘텐츠 생성 차단
- API 사용량에 따른 비용 발생

## 환경 변수

```bash
export GOOGLE_API_KEY="your-api-key"
```

또는 클라이언트 생성 시 직접 지정:
```python
client = genai.Client(api_key="your-api-key")
```
