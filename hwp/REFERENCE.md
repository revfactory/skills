# HWP/HWPX Advanced Reference

## MDView Project Implementation

This reference covers the advanced HWP processing patterns used in the MDView project.

### File Locations

| File | Role |
|------|------|
| `src/types/hwp.ts` | Type definitions for worker messages |
| `src/lib/hwp-converter.ts` | Main API (4 exported functions) |
| `src/hooks/use-hwp.ts` | React hooks: `useHwpImport()`, `useHwpExport()` |
| `src/workers/hwp-parser.worker.ts` | Parser worker (1,387 lines) — HWP binary & HWPX |
| `src/workers/hwp-generator.worker.ts` | Generator worker (852 lines) — Markdown → HWPX |
| `src/components/features/import-export/hwp-import.tsx` | Import UI with drag-and-drop |
| `src/components/features/import-export/hwp-export.tsx` | Export UI with paper/font options |

### Data Flow

**Import:**
```
File (HWP/HWPX)
  → hwp-parser.worker.ts (format detection → record/XML parsing → tree → markdown)
  → hwp-converter.ts (worker lifecycle)
  → use-hwp.ts hook (progress state management)
  → hwp-import.tsx (UI with preview)
  → Editor (markdown content)
```

**Export:**
```
Markdown text
  → hwp-generator.worker.ts (marked → HTML → paragraph structures → HWPX XML → ZIP)
  → hwp-converter.ts (worker lifecycle)
  → use-hwp.ts hook (progress & download via file-saver)
  → hwp-export.tsx (configuration UI)
  → .hwpx file download
```

### Worker Message Protocol

```typescript
// Import messages
interface HwpParserMessage {
  type: 'parse';
  data: ArrayBuffer;
  fileName: string;
  options?: HwpImportOptions;
}

interface HwpParserResponse {
  type: 'progress' | 'complete' | 'error';
  progress?: number;          // 0-100
  message?: string;           // Progress description
  markdown?: string;          // Final result
  metadata?: HwpDocumentMetadata;
  warnings?: string[];        // Non-fatal issues
  error?: string;
}

// Export messages
interface HwpGenerateMessage {
  type: 'generate';
  markdown: string;
  options?: HwpExportOptions;
}

interface HwpGenerateResponse {
  type: 'progress' | 'complete' | 'error';
  progress?: number;
  message?: string;
  data?: ArrayBuffer;         // HWPX blob
  error?: string;
}
```

### Import Options

```typescript
interface HwpImportOptions {
  preserveStyles?: boolean;    // Attempt to keep formatting
  convertTables?: boolean;     // Convert tables to markdown/HTML
  extractImages?: boolean;     // Extract embedded images
  imageFormat?: 'base64' | 'blob';  // Image output format
}
```

### Export Options & Defaults

```typescript
interface HwpExportOptions {
  paperSize?: 'A4' | 'Letter' | 'B5';    // default: 'A4'
  orientation?: 'portrait' | 'landscape';  // default: 'portrait'
  margins?: {                              // default: 20mm all sides
    top: number; bottom: number;
    left: number; right: number;
  };
  fontSize?: number;                       // default: 10 (pt)
  fontFamily?: string;                     // default: '맑은 고딕'
  lineHeight?: number;                     // default: 1.6
}
```

### Progress Milestones

**Parser:**
- 10% — File loaded, format detected
- 20% — Container opened (CFB/ZIP)
- 25% — Compression handled
- 30% — Records/XML parsed
- 50% — Images extracted
- 60% — Document tree built
- 80% — Markdown generated
- 90% — Post-processing
- 100% — Complete

**Generator:**
- 10% — Markdown received
- 30% — HTML conversion done
- 50% — HWPX XML generated
- 80% — ZIP packaging
- 100% — Complete

### Document Tree Structure

The parser builds an intermediate tree before markdown conversion:

```typescript
type DocNodeType = 'paragraph' | 'table' | 'cell' | 'textbox' | 'image';

interface DocNode {
  type: DocNodeType;
  text?: string;
  children?: DocNode[];
  // Table-specific
  rows?: number;
  cols?: number;
  colspan?: number;
  rowspan?: number;
  // Image-specific
  imageData?: string;  // data:mime;base64,...
}
```

### HWPX Paper Sizes (1/100mm)

| Size | Width | Height |
|------|-------|--------|
| A4 | 21000 | 29700 |
| Letter | 21590 | 27940 |
| B5 | 17600 | 25000 |

### HWPX Heading Font Sizes (1/100pt)

| Level | Size |
|-------|------|
| h1 | 2400 |
| h2 | 2000 |
| h3 | 1600 |
| h4 | 1400 |
| h5 | 1200 |
| h6 | 1000 |
| body | 1000 |

### Content Size Guard

If text content exceeds 2MB, strip all base64 image data to prevent editor/DOM overload:

```typescript
if (markdown.length > 2 * 1024 * 1024) {
  markdown = markdown.replace(/!\[([^\]]*)\]\(data:[^)]+\)/g, '![$1](image-removed)');
  warnings.push('Content too large, images removed');
}
```

### Chunked Base64 Encoding

To avoid stack overflow with `btoa()` on large binary data:

```typescript
function chunkedBase64(data: Uint8Array): string {
  const CHUNK = 8192;
  let result = '';
  for (let i = 0; i < data.length; i += CHUNK) {
    const chunk = data.slice(i, i + CHUNK);
    result += String.fromCharCode(...chunk);
  }
  return btoa(result);
}
```
