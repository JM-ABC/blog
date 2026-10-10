# -*- coding: utf-8 -*-
"""커머스 인사이트 Vol.134 인포그래픽
좌: 올리브영 국내 점포 수 분기별 추이 / 우: 오프라인 매출 중 외국인 비중
공통 스타일은 assets/brand/chart_style.py 를 그대로 사용한다.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'brand'))
from chart_style import (COLORS, new_branded_figure, panel_header, add_badge,
                         add_footer, style_axes, save_chart)

import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

# 리눅스 환경에는 Malgun Gothic이 없어 한글 폰트만 대체한다 (색상·레이아웃은 공통 스타일 그대로)
for _p in ('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',):
    if os.path.exists(_p):
        fm.fontManager.addfont(_p)
        plt.rcParams['font.family'] = 'WenQuanYi Zen Hei'
        break
plt.rcParams['axes.unicode_minus'] = False

fig = new_branded_figure(
    'BEAUTY OFFLINE LANDSCAPE',
    '올리브영 국내 점포 수와 외국인 매출 비중',
    '점포 수는 2025년 3분기부터 세 분기 연속 줄었고, 오프라인 매출에서 외국인이 차지하는 비중은 올랐어요',
)

# ───────── 좌측 패널: 분기별 점포 수 ─────────
q_labels = ['2025\n3분기', '2025\n4분기', '2026\n1분기', '2026\n2분기']
q_values = [1394, 1381, 1369, 1367]

panel_header(fig, 0.045, 0.475, 0.74, '국내 점포 수 분기별 추이', '단위: 개 (세로축 일부 구간)')
ax1 = fig.add_axes([0.045, 0.16, 0.43, 0.54])
bars = ax1.bar(q_labels, q_values, color=COLORS['accent'], width=0.52, zorder=3)
ax1.set_ylim(1340, 1410)
style_axes(ax1)
for b, v in zip(bars, q_values):
    ax1.text(b.get_x() + b.get_width() / 2, v + 2.5, f'{v:,}',
             ha='center', va='bottom', fontsize=14, fontweight='bold',
             color=COLORS['text'], zorder=4)
add_badge(ax1, 2.5, 1399, '세 분기 연속 감소', kind='negative', fontsize=12)

# ───────── 우측 패널: 외국인 매출 비중 ─────────
f_labels = ['2022년', '2026년\n8월 기준']
f_values = [2, 33]

panel_header(fig, 0.525, 0.955, 0.74, '오프라인 매출 중 외국인 비중', '단위: %')
ax2 = fig.add_axes([0.525, 0.16, 0.43, 0.54])
bars2 = ax2.bar(f_labels, f_values, color=[COLORS['grid'], COLORS['positive_bar']],
                width=0.42, zorder=3)
ax2.set_ylim(0, 42)
style_axes(ax2)
for b, v in zip(bars2, f_values):
    ax2.text(b.get_x() + b.get_width() / 2, v + 1.2, f'{v}%',
             ha='center', va='bottom', fontsize=14, fontweight='bold',
             color=COLORS['text'], zorder=4)
add_badge(ax2, 1, 38, '4년 새 31%p 상승', kind='positive', fontsize=12)

add_footer(fig, '뉴스핌 · 헤럴드경제 · 데일리팜 (2026)')
save_chart(fig, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'beauty-offline-landscape.png'))
