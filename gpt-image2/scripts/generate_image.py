#!/usr/bin/env python3
"""OpenAI GPT Image 2 이미지 생성·편집 CLI.

이 스크립트는 모델을 ``gpt-image-2`` 로 고정한다.

사용 예시.
    # 텍스트 → 이미지
    python generate_image.py "귀여운 고양이가 책을 읽는 모습"

    # 크기·품질 지정
    python generate_image.py "로고 디자인" --size 1024x1024 --quality high --output logo.png

    # 편집 (단일 이미지, 프롬프트만)
    python generate_image.py "배경을 바다로 바꿔줘" --input photo.png --output edited.png

    # 마스킹 편집 (투명 영역만 재생성)
    python generate_image.py "빈 공간에 소파" --input room.png --mask mask.png

    # 멀티 레퍼런스 합성
    python generate_image.py "선물 바구니" --input lotion.png soap.png candle.png

    # 여러 장 한번에
    python generate_image.py "미니멀 아이콘 세트" --n 4

    # 스트리밍 (중간 이미지도 저장)
    python generate_image.py "흐르는 강" --stream --partial 2
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
from datetime import datetime
from pathlib import Path


MODEL = "gpt-image-2"  # 이 스킬은 gpt-image-2로 고정


def _save_b64(b64: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(b64))


def _resolve_output_paths(output: str | None, n: int, ext: str) -> list[Path]:
    if output:
        base = Path(output)
        if n == 1:
            return [base]
        stem, suffix = base.stem, base.suffix or f".{ext}"
        return [base.with_name(f"{stem}_{i+1}{suffix}") for i in range(n)]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if n == 1:
        return [Path(f"gpt_image_{ts}.{ext}")]
    return [Path(f"gpt_image_{ts}_{i+1}.{ext}") for i in range(n)]


def generate(
    prompt: str,
    size: str = "auto",
    quality: str = "auto",
    n: int = 1,
    output_format: str = "png",
    output_compression: int | None = None,
    moderation: str | None = None,
    output: str | None = None,
) -> list[Path]:
    """텍스트 → 이미지 생성."""
    from openai import OpenAI

    client = OpenAI()

    kwargs = {
        "model": MODEL,
        "prompt": prompt,
        "n": n,
        "size": size,
        "quality": quality,
        "output_format": output_format,
    }
    if output_compression is not None and output_format in {"jpeg", "webp"}:
        kwargs["output_compression"] = output_compression
    if moderation:
        kwargs["moderation"] = moderation

    result = client.images.generate(**kwargs)

    paths = _resolve_output_paths(output, n, output_format)
    for i, data in enumerate(result.data):
        _save_b64(data.b64_json, paths[i])
    return paths


def edit(
    prompt: str,
    images: list[str],
    mask: str | None = None,
    size: str = "auto",
    quality: str = "auto",
    n: int = 1,
    output_format: str = "png",
    output: str | None = None,
) -> list[Path]:
    """이미지 편집 (단일/멀티 레퍼런스, 선택적 마스크)."""
    from openai import OpenAI

    client = OpenAI()

    opened = [open(p, "rb") for p in images]
    mask_fh = open(mask, "rb") if mask else None
    try:
        image_arg = opened[0] if len(opened) == 1 else opened
        kwargs = {
            "model": MODEL,
            "image": image_arg,
            "prompt": prompt,
            "n": n,
            "size": size,
            "quality": quality,
        }
        if mask_fh:
            kwargs["mask"] = mask_fh
        result = client.images.edit(**kwargs)
    finally:
        for fh in opened:
            fh.close()
        if mask_fh:
            mask_fh.close()

    paths = _resolve_output_paths(output, n, output_format)
    for i, data in enumerate(result.data):
        _save_b64(data.b64_json, paths[i])
    return paths


def stream_generate(
    prompt: str,
    size: str = "auto",
    quality: str = "auto",
    partial_images: int = 2,
    output: str | None = None,
) -> list[Path]:
    """스트리밍으로 중간·최종 이미지 저장."""
    from openai import OpenAI

    client = OpenAI()

    stream = client.images.generate(
        model=MODEL,
        prompt=prompt,
        size=size,
        quality=quality,
        stream=True,
        partial_images=partial_images,
    )

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_base = Path(output) if output else Path(f"gpt_image_{ts}.png")
    saved: list[Path] = []
    for event in stream:
        etype = getattr(event, "type", "")
        if etype == "image_generation.partial_image":
            idx = getattr(event, "partial_image_index", len(saved))
            p = out_base.with_name(
                f"{out_base.stem}_partial{idx}{out_base.suffix or '.png'}"
            )
            _save_b64(event.b64_json, p)
            saved.append(p)
            print(f"  partial {idx} → {p}", file=sys.stderr)
        elif etype in {"image_generation.completed", "image_generation.final_image"}:
            p = out_base if out_base.suffix else out_base.with_suffix(".png")
            _save_b64(event.b64_json, p)
            saved.append(p)
    return saved


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"OpenAI GPT Image CLI (model fixed to {MODEL})",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("prompt", help="이미지 생성·편집 프롬프트")
    parser.add_argument("--size", default="auto",
                        help='크기 예: 1024x1024, 1536x1024, 1024x1536, auto')
    parser.add_argument("--quality", default="auto",
                        choices=["low", "medium", "high", "auto"])
    parser.add_argument("--n", type=int, default=1, help="생성 장수")
    parser.add_argument("--output", "-o", help="출력 파일 경로")
    parser.add_argument("--format", dest="output_format", default="png",
                        choices=["png", "jpeg", "webp"])
    parser.add_argument("--compression", type=int, default=None,
                        help="jpeg/webp 압축 0-100")
    parser.add_argument("--moderation", choices=["auto", "low"])
    parser.add_argument("--input", "-i", nargs="+",
                        help="편집할 입력 이미지(여러 개 가능)")
    parser.add_argument("--mask", help="마스크 PNG (투명 영역만 재생성)")
    parser.add_argument("--stream", action="store_true",
                        help="스트리밍 모드 (중간 이미지 저장)")
    parser.add_argument("--partial", type=int, default=2,
                        help="스트리밍 시 중간 이미지 개수 (0-3)")

    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print("[!] OPENAI_API_KEY 환경변수가 없습니다.", file=sys.stderr)
        return 2

    try:
        if args.stream:
            if args.input:
                print("[!] --stream은 생성 전용입니다. --input과 함께 쓸 수 없습니다.",
                      file=sys.stderr)
                return 2
            paths = stream_generate(
                args.prompt,
                size=args.size,
                quality=args.quality,
                partial_images=args.partial,
                output=args.output,
            )
        elif args.input:
            paths = edit(
                args.prompt,
                images=args.input,
                mask=args.mask,
                size=args.size,
                quality=args.quality,
                n=args.n,
                output_format=args.output_format,
                output=args.output,
            )
        else:
            paths = generate(
                args.prompt,
                size=args.size,
                quality=args.quality,
                n=args.n,
                output_format=args.output_format,
                output_compression=args.compression,
                moderation=args.moderation,
                output=args.output,
            )
    except ImportError:
        print("[!] openai 패키지가 필요합니다. `pip install openai pillow`",
              file=sys.stderr)
        return 2
    except Exception as e:
        print(f"[!] 실패: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    for p in paths:
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
