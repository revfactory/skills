# 흑백 A4 인쇄물 디자인 가이드라인

> 이 가이드라인은 흑백 프린터로 출력해도 가독성이 좋은 A4 문서를 만들기 위한 지침입니다.

---

## 1. 페이지 설정

### 크기 및 여백
- **페이지 크기**: 210mm x 297mm (A4)
- **여백**: 10~15mm (상하좌우 동일)
- **배율 100% 인쇄** 기준으로 설계

### CSS 기본 설정
```css
.page {
    width: 210mm;
    height: 297mm;
    padding: 10mm 12mm;  /* 또는 12mm 15mm */
    margin: 0 auto;
    overflow: hidden;
    position: relative;
}

@media print {
    @page {
        size: A4;
        margin: 0;
    }
    body {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .page {
        page-break-after: always;
        page-break-inside: avoid;
    }
    .page:last-child {
        page-break-after: auto;
    }
}
```

---

## 2. 컬러 팔레트

**3가지 톤만 사용**: 블랙 / 화이트 / 그레이

```css
:root {
    --main-color: #000000;      /* 메인 컬러 (제목, 강조, 아이콘) */
    --bg-light: #F5F5F5;        /* 강조 박스 배경 (1개만 사용) */
    --text-dark: #000000;       /* 본문 텍스트 */
    --text-gray: #666666;       /* 부가 설명, 힌트 */
    --border-color: #999999;    /* 테두리, 구분선 */
}
```

### 컬러 사용 원칙
| 요소 | 컬러 |
|------|------|
| 제목, 강조 텍스트 | `#000000` |
| 본문 텍스트 | `#000000` |
| 부가 설명, 힌트 | `#666666` |
| 박스 배경 (기본) | `#FFFFFF` |
| 박스 배경 (강조) | `#F5F5F5` - **1종류만** |
| 테두리 | `#999999` |
| 섹션 번호 배경 | `#000000` (흰 글씨) |

---

## 3. 타이포그래피

### 폰트
- **권장 폰트**: Noto Sans KR, Pretendard, 본고딕
- **line-height**: 1.4~1.6

### 크기 가이드
| 용도 | 크기 | 굵기 |
|------|------|------|
| 문서 제목 | 18~22pt | 700 |
| 섹션 제목 | 12~14pt | 700 |
| 카드/박스 제목 | 10~11pt | 600~700 |
| 본문 | 10~11pt | 400 |
| 힌트/부가설명 | 8~9pt | 400 |
| 최소 크기 | **8pt 이상** | - |

```css
body {
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #000000;
}
```

---

## 4. 박스 스타일

### 기본 박스 (흰색 배경)
대부분의 박스에 사용합니다.

```css
.card {
    background: #ffffff;
    border: 1px solid #999999;
    border-radius: 5px;
    padding: 8px 10px;
}
```

### 강조 박스 (회색 배경)
**문서당 1종류만 사용**을 권장합니다. 너무 많으면 산만해집니다.

```css
.highlight-box {
    background: #F5F5F5;
    border: 1px solid #999999;
    border-radius: 8px;
    padding: 12px 15px;
}
```

### 왼쪽 강조선 박스
팁, 인용, 중요 안내에 사용합니다.

```css
.tip-box {
    background: #ffffff;
    border: 1px solid #999999;
    border-left: 3px solid #000000;
    border-radius: 0 5px 5px 0;
    padding: 6px 10px;
}
```

---

## 5. 섹션 번호

검정 원 안에 흰색 숫자로 표시합니다.

```css
.section-number {
    width: 20~24px;
    height: 20~24px;
    background: #000000;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 10~12px;
}
```

---

## 6. 구분선

### 섹션 구분 (굵은 선)
```css
border-bottom: 2px solid #000000;
/* 또는 */
border-bottom: 3px solid #000000;
```

### 글쓰기 라인 (점선)
핸드아웃에서 참가자가 글을 쓸 공간에 사용합니다.

```css
.write-line {
    border-bottom: 1px dashed #999999;
    height: 18~24px;
}
```

### 카드 제목 밑줄
```css
.card-title {
    padding-bottom: 4px;
    border-bottom: 2px solid #000000;
}
```

---

## 7. 레이아웃 패턴

### 2열 그리드
```css
.two-column {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8~10px;
}
```

### 전체 너비 항목
```css
.full-width {
    grid-column: 1 / -1;
}
```

---

## 8. 헤더 & 푸터

### 문서 헤더
```css
.header {
    text-align: center;
    margin-bottom: 10~15px;
    padding-bottom: 8~12px;
    border-bottom: 3px solid #000000;
}
```

### 페이지 번호
```css
.page-number {
    position: absolute;
    bottom: 6~8mm;
    right: 12~15mm;
    font-size: 8~9pt;
    color: #000000;
}
```

---

## 9. 체크리스트

```css
.checklist li {
    padding-left: 14px;
    position: relative;
}

.checklist li::before {
    content: "☐";
    position: absolute;
    left: 0;
    color: #000000;
}
```

---

## 10. 디자인 원칙 요약

1. **회색 배경은 1종류만** - 강조 효과를 위해 아껴서 사용
2. **나머지는 흰색 + 테두리** - 깔끔하고 잉크 절약
3. **텍스트는 검정 위주** - `#666666`은 힌트에만
4. **최소 8pt 이상** - 인쇄 시 가독성 확보 (본문 10pt 권장)
5. **여백 충분히** - 답답하지 않게
6. **배율 100%** 기준으로 테스트

---

## 11. 화면 미리보기 스타일

개발 중 확인을 위한 스타일입니다.

```css
@media screen {
    body {
        background: #888;
        padding: 20px 0;
    }
    .page {
        background: white;
        box-shadow: 0 0 15px rgba(0,0,0,0.3);
        margin: 20px auto;
    }
}
```

---

## 크레딧

이 문서는 **CC-BY-NC 라이선스**(저작자표시-비영리)로 배포됩니다.

**Branding × Tech = SOMILAND**

**민다솜** — Creative Director

📧 ysmlgyee@gmail.com
🌐 mindasom.com
