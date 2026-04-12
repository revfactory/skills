#!/usr/bin/env python3
"""
ManPower Radar Chart Generator
사용자의 AI 스킬 레벨을 방사형 그래프로 시각화한다.

Usage:
    python3 radar_chart.py <output_path> <json_data_path>

json_data_path의 JSON 구조:
{
  "overall": {
    "labels": ["명확성", "구체성", ...],
    "scores": [85, 72, ...],
    "max_score": 100
  },
  "weekly": [
    {
      "week": "W12",
      "scores": [80, 70, ...],
      "total": 75.0
    },
    ...
  ]
}
"""

import sys
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

# 한글 폰트 설정
def setup_korean_font():
    """macOS에서 한글 폰트를 찾아 설정한다."""
    korean_fonts = [
        '/System/Library/Fonts/Supplemental/AppleGothic.ttf',
        '/System/Library/Fonts/AppleSDGothicNeo.ttc',
        '/Library/Fonts/NanumGothic.ttf',
        '/Library/Fonts/NanumBarunGothic.ttf',
    ]
    for fp in korean_fonts:
        if Path(fp).exists():
            fm.fontManager.addfont(fp)
            prop = fm.FontProperties(fname=fp)
            plt.rcParams['font.family'] = prop.get_name()
            plt.rcParams['axes.unicode_minus'] = False
            return prop
    # 폴백
    plt.rcParams['font.family'] = 'sans-serif'
    return None

def grade_label(score):
    """점수를 등급 라벨로 변환."""
    if score >= 90: return 'S'
    if score >= 80: return 'A'
    if score >= 70: return 'B'
    if score >= 60: return 'C'
    if score >= 50: return 'D'
    return 'F'

def create_radar_chart(data, output_path):
    font_prop = setup_korean_font()

    overall = data['overall']
    weekly = data.get('weekly', [])
    labels = overall['labels']
    scores = overall['scores']
    max_score = overall.get('max_score', 100)
    N = len(labels)

    # 각도 계산
    angles = [n / float(N) * 2 * math.pi for n in range(N)]
    angles += angles[:1]
    scores_closed = scores + scores[:1]

    # 전체 평균
    avg_score = sum(scores) / len(scores)
    grade = grade_label(avg_score)

    # 색상 팔레트
    BG_COLOR = '#0d1117'
    GRID_COLOR = '#1e2937'
    TEXT_COLOR = '#c9d1d9'
    ACCENT_COLOR = '#58a6ff'
    FILL_COLOR = '#58a6ff'
    HIGHLIGHT_COLOR = '#f0883e'
    TREND_UP = '#3fb950'
    TREND_DOWN = '#f85149'
    TREND_FLAT = '#8b949e'

    # 주간 트렌드가 있으면 2열, 없으면 1열
    has_weekly = len(weekly) >= 2
    if has_weekly:
        fig = plt.figure(figsize=(16, 9), facecolor=BG_COLOR)
        gs = fig.add_gridspec(1, 2, width_ratios=[1.1, 0.9], wspace=0.05)
        ax_radar = fig.add_subplot(gs[0, 0], polar=True)
        ax_trend = fig.add_subplot(gs[0, 1])
    else:
        fig = plt.figure(figsize=(10, 9), facecolor=BG_COLOR)
        ax_radar = fig.add_subplot(111, polar=True)
        ax_trend = None

    # === 레이더 차트 ===
    ax_radar.set_facecolor(BG_COLOR)

    # 그리드 원 (20, 40, 60, 80, 100)
    grid_levels = [20, 40, 60, 80, 100]
    for level in grid_levels:
        grid_angles = np.linspace(0, 2 * np.pi, 100)
        ax_radar.plot(grid_angles, [level] * 100, color=GRID_COLOR, linewidth=0.5, linestyle='-')
        # 레벨 라벨
        ax_radar.text(math.pi / N * 0.3, level + 2, str(level),
                     color='#484f58', fontsize=7, ha='center')

    # 축 라인
    for angle in angles[:-1]:
        ax_radar.plot([angle, angle], [0, max_score], color=GRID_COLOR, linewidth=0.5)

    # 데이터 플롯
    ax_radar.plot(angles, scores_closed, color=ACCENT_COLOR, linewidth=2.5, linestyle='-')
    ax_radar.fill(angles, scores_closed, color=FILL_COLOR, alpha=0.15)

    # 데이터 포인트 + 점수 라벨
    for i, (angle, score) in enumerate(zip(angles[:-1], scores)):
        # 포인트
        ax_radar.scatter(angle, score, color=ACCENT_COLOR, s=60, zorder=5, edgecolors='white', linewidths=0.5)
        # 점수 텍스트
        offset = 12
        ax_radar.text(angle, score + offset, str(score),
                     color=TEXT_COLOR, fontsize=11, fontweight='bold',
                     ha='center', va='center')

    # 축 라벨
    ax_radar.set_xticks(angles[:-1])
    ax_radar.set_xticklabels(labels, color=TEXT_COLOR, fontsize=11,
                              fontproperties=font_prop)

    # 축 스타일
    ax_radar.set_ylim(0, max_score + 15)
    ax_radar.set_yticks([])
    ax_radar.spines['polar'].set_visible(False)
    ax_radar.grid(False)

    # 중앙 등급 표시
    ax_radar.text(0, 0, grade, fontsize=42, fontweight='bold',
                 color=ACCENT_COLOR, ha='center', va='center', zorder=10)
    ax_radar.text(0, -18, f'{avg_score:.1f}점', fontsize=12,
                 color=TEXT_COLOR, ha='center', va='center', zorder=10,
                 fontproperties=font_prop)

    # === 주간 트렌드 차트 ===
    if has_weekly and ax_trend is not None:
        ax_trend.set_facecolor(BG_COLOR)

        weeks = [w['week'] for w in weekly]
        totals = [w['total'] for w in weekly]

        # 트렌드 방향
        if len(totals) >= 2:
            diff = totals[-1] - totals[0]
            if diff > 3:
                trend_color = TREND_UP
                trend_arrow = '+'
            elif diff < -3:
                trend_color = TREND_DOWN
                trend_arrow = ''
            else:
                trend_color = TREND_FLAT
                trend_arrow = ''
        else:
            trend_color = TREND_FLAT
            trend_arrow = ''

        # 라인 + 포인트
        ax_trend.plot(weeks, totals, color=trend_color, linewidth=2.5, marker='o',
                     markersize=8, markerfacecolor=trend_color, markeredgecolor='white',
                     markeredgewidth=1.5, zorder=5)

        # 영역 채우기
        ax_trend.fill_between(weeks, totals, alpha=0.1, color=trend_color)

        # 각 포인트에 점수 표시
        for i, (week, total) in enumerate(zip(weeks, totals)):
            ax_trend.annotate(f'{total:.0f}',
                            (week, total),
                            textcoords="offset points",
                            xytext=(0, 14),
                            ha='center',
                            color=TEXT_COLOR,
                            fontsize=10,
                            fontweight='bold')

        # 각 축별 미니 트렌드 (배경에 연하게)
        if len(weekly) >= 2 and len(weekly[0].get('scores', [])) == N:
            for dim_idx in range(N):
                dim_scores = [w['scores'][dim_idx] for w in weekly]
                ax_trend.plot(weeks, dim_scores, color='#30363d', linewidth=0.8,
                             linestyle='--', alpha=0.5)

        # 스타일
        ax_trend.set_xlim(-0.5, len(weeks) - 0.5)
        y_min = max(0, min(totals) - 15)
        y_max = min(100, max(totals) + 15)
        ax_trend.set_ylim(y_min, y_max)

        ax_trend.set_title('주간 성장 추이', color=TEXT_COLOR, fontsize=14,
                          fontweight='bold', pad=15, fontproperties=font_prop)

        # 변화량 표시
        if len(totals) >= 2:
            diff = totals[-1] - totals[0]
            sign = '+' if diff > 0 else ''
            ax_trend.text(0.98, 0.95, f'{sign}{diff:.1f}점',
                         transform=ax_trend.transAxes,
                         color=trend_color, fontsize=18, fontweight='bold',
                         ha='right', va='top',
                         fontproperties=font_prop)

        ax_trend.tick_params(colors=TEXT_COLOR, labelsize=9)
        ax_trend.set_xlabel('')
        ax_trend.set_ylabel('')

        for spine in ax_trend.spines.values():
            spine.set_color(GRID_COLOR)

        ax_trend.yaxis.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.5)
        ax_trend.xaxis.grid(False)

    # 전체 타이틀
    fig.suptitle('ManPower — AI Skill Assessment',
                color=TEXT_COLOR, fontsize=18, fontweight='bold', y=0.97)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor=BG_COLOR, edgecolor='none')
    plt.close()
    print(f"Chart saved: {output_path}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 radar_chart.py <output_path> <json_data_path>")
        sys.exit(1)

    output_path = sys.argv[1]
    json_path = sys.argv[2]

    with open(json_path) as f:
        data = json.load(f)

    create_radar_chart(data, output_path)
