#!/usr/bin/env python3
"""
Gemini 3 Pro 이미지 생성 스크립트

사용법:
    python generate_image.py "프롬프트" [옵션]

예시:
    python generate_image.py "귀여운 고양이가 책을 읽는 모습"
    python generate_image.py "로고 디자인" --ratio 1:1 --size 2K --output logo.png
    python generate_image.py "날씨 인포그래픽" --search --ratio 16:9
    python generate_image.py "배경을 바꿔줘" --input photo.jpg --output edited.png
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path


def generate_image(
    prompt: str,
    aspect_ratio: str = "1:1",
    image_size: str = "1K",
    output_path: str = None,
    use_search: bool = False,
    input_image: str = None,
    model: str = "gemini-3.1-flash-image-preview"
) -> list[str]:
    """
    Gemini API를 사용하여 이미지 생성
    
    Args:
        prompt: 이미지 생성 프롬프트
        aspect_ratio: 비율 (1:1, 16:9, 9:16, 4:3, 3:4, 21:9 등)
        image_size: 해상도 (1K, 2K, 4K)
        output_path: 출력 파일 경로
        use_search: Google 검색 그라운딩 사용 여부
        input_image: 편집할 입력 이미지 경로
        model: 사용할 모델명
    
    Returns:
        생성된 이미지 파일 경로 목록
    """
    from google import genai
    from google.genai import types
    from PIL import Image
    
    client = genai.Client()
    
    # 설정 구성
    config_params = {
        "response_modalities": ['TEXT', 'IMAGE'],
        "image_config": types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=image_size
        ),
    }
    
    # Google 검색 그라운딩 추가
    if use_search:
        config_params["tools"] = [{"google_search": {}}]
    
    config = types.GenerateContentConfig(**config_params)
    
    # 컨텐츠 구성
    if input_image and os.path.exists(input_image):
        image_input = Image.open(input_image)
        contents = [prompt, image_input]
    else:
        contents = prompt
    
    # 이미지 생성
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config
    )
    
    # 결과 처리
    saved_files = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, part in enumerate(response.parts):
        if part.text:
            print(f"[설명] {part.text}")
        elif image := part.as_image():
            if output_path and i == 0:
                filepath = output_path
            else:
                filename = f"gemini_image_{timestamp}_{i}.png"
                filepath = os.path.join(
                    os.path.dirname(output_path) if output_path else ".",
                    filename
                )
            
            image.save(filepath)
            saved_files.append(filepath)
            print(f"[저장됨] {filepath}")
    
    return saved_files


def main():
    parser = argparse.ArgumentParser(
        description="Gemini 3 Pro 이미지 생성 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  %(prog)s "귀여운 고양이"
  %(prog)s "로고 디자인" --ratio 1:1 --size 2K
  %(prog)s "날씨 차트" --search --ratio 16:9
  %(prog)s "배경 변경" --input photo.jpg
        """
    )
    
    parser.add_argument("prompt", help="이미지 생성 프롬프트")
    parser.add_argument("--ratio", default="1:1",
                        choices=["1:1", "2:3", "3:2", "3:4", "4:3", 
                                "4:5", "5:4", "9:16", "16:9", "21:9"],
                        help="이미지 비율 (기본: 1:1)")
    parser.add_argument("--size", default="1K",
                        choices=["1K", "2K", "4K"],
                        help="이미지 해상도 (기본: 1K)")
    parser.add_argument("--output", "-o", help="출력 파일 경로")
    parser.add_argument("--search", action="store_true",
                        help="Google 검색 그라운딩 활성화")
    parser.add_argument("--input", "-i", help="편집할 입력 이미지 경로")
    parser.add_argument("--model", default="gemini-3.1-flash-image-preview",
                        help="사용할 모델 (기본: gemini-3.1-flash-image-preview)")
    
    args = parser.parse_args()
    
    # 출력 경로 기본값 설정
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"gemini_image_{timestamp}.png"
    
    try:
        saved_files = generate_image(
            prompt=args.prompt,
            aspect_ratio=args.ratio,
            image_size=args.size,
            output_path=args.output,
            use_search=args.search,
            input_image=args.input,
            model=args.model
        )
        
        if saved_files:
            print(f"\n✅ {len(saved_files)}개 이미지 생성 완료")
            for f in saved_files:
                print(f"   - {f}")
        else:
            print("\n⚠️ 이미지가 생성되지 않았습니다")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
