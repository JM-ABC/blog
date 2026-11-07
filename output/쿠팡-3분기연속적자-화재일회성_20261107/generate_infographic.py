# -*- coding: utf-8 -*-
"""커머스 인사이트 Vol.138 인포그래픽
좌: 분기별 영업손익과 그 안의 일회성 비용 / 우: 3분기 부문별 조정 EBITDA 전년 대비
환율 기준이 분기마다 달라 수치 혼용을 막기 위해 두 패널 모두 달러(백만달러) 기준으로 그린다.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', '..', 'assets', 'brand'))
from chart_style import (COLORS, new_branded_figure, panel_header, add_badge,
                         add_footer, style_axes, save_chart)

# 공통 스타일 모듈은 Malgun Gothic(윈도우 폰트)을 지정하므로, 리눅스에서는
# 설치된 한글 폰트로만 교체한다. 색상·배지·헤더·푸터 스타일은 그대로 쓴다.
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

for _cand in ('/usr/share/fonts/truetype/korean/Korean.ttf',):
    if os.path.exists(_cand):
        fm.fontManager.addfont(_cand)
        plt.rcParams['font.family'] = fm.FontProperties(fname=_cand).get_name()
        break
plt.rcParams['axes.unicode_minus'] = False

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'coupang-3q-영업손익-조정EBITDA.png')

fig = new_branded_figure(
    eyebrow='QUARTERLY PERFORMANCE REVIEW',
    title='쿠팡 3분기 영업손실 4억5,000만달러, 화재를 빼도 2억200만달러',
    subtitle='분기마다 적용 환율이 달라 원화 환산 대신 달러 기준으로 정리했어요 (2026년 3분기 기준)',
)

# ---------------------------------------------------------------- 좌측 패널
panel_header(fig, 0.045, 0.47, 0.775, '분기별 영업손익과 일회성 비용', '단위: 백만달러')
ax1 = fig.add_axes([0.045, 0.165, 0.425, 0.575])
style_axes(ax1)

labels = ['2025년\n3분기', '2026년\n1분기', '2026년\n2분기', '2026년\n3분기']
totals = [162, -242, -556, -450]
# 각 분기 손실 가운데 회사가 일회성으로 설명한 금액 (없으면 0)
oneoff = [0, 0, -410, -248]
oneoff_name = ['', '', '과징금\n410', '화재\n248']

xs = range(len(labels))
for x, total in zip(xs, totals):
    color = COLORS['positive_bar'] if total > 0 else COLORS['negative_bar']
    ax1.bar(x, total, width=0.52, color=color, zorder=3)

# 일회성 부분은 같은 막대 안에 진한 색으로 덧그려 구분한다
for x, one in zip(xs, oneoff):
    if one:
        ax1.bar(x, one, width=0.52, color=COLORS['negative'], zorder=4)

for x, total in zip(xs, totals):
    va = 'bottom' if total > 0 else 'top'
    off = 22 if total > 0 else -22
    ax1.text(x, total + off, f'{total:+,}'.replace('+', '+'), ha='center', va=va,
             fontsize=14, fontweight='bold',
             color=COLORS['positive'] if total > 0 else COLORS['negative'], zorder=5)

for x, one, name in zip(xs, oneoff, oneoff_name):
    if one:
        ax1.text(x, one / 2, name, ha='center', va='center', fontsize=10,
                 fontweight='bold', color='#FFFFFF', zorder=6)

ax1.axhline(0, color=COLORS['text'], linewidth=1.1, zorder=5)
ax1.set_xticks(list(xs))
ax1.set_xticklabels(labels, fontsize=11.5)
ax1.set_ylim(-700, 330)
ax1.set_yticks([-600, -400, -200, 0, 200])
ax1.set_yticklabels(['-600', '-400', '-200', '0', '200'])
add_badge(ax1, 1.5, 250, '3개 분기 연속 영업손실', kind='negative', fontsize=12)
ax1.text(-0.45, -690, '진한 색은 회사가 일회성으로 설명한 비용이에요',
         ha='left', va='bottom', fontsize=10, color=COLORS['sub'])

# ---------------------------------------------------------------- 우측 패널
panel_header(fig, 0.53, 0.955, 0.775, '3분기 부문별 조정 EBITDA', '단위: 백만달러')
ax2 = fig.add_axes([0.53, 0.165, 0.425, 0.575])
style_axes(ax2)

seg = ['프로덕트 커머스', '디벨로핑 오퍼링', '연결 전체']
prev = [705, -292, 413]
curr = [385, -269, 116]

import numpy as np
idx = np.arange(len(seg))
w = 0.33
ax2.bar(idx - w / 2, prev, width=w, color='#C7D7F7', zorder=3, label='2025년 3분기')
ax2.bar(idx + w / 2, curr, width=w, color=COLORS['accent'], zorder=3, label='2026년 3분기')

for i, (p, c) in enumerate(zip(prev, curr)):
    for xpos, val in ((i - w / 2, p), (i + w / 2, c)):
        va = 'bottom' if val > 0 else 'top'
        off = 20 if val > 0 else -20
        ax2.text(xpos, val + off, f'{val:,}', ha='center', va=va, fontsize=12.5,
                 fontweight='bold', color=COLORS['text'], zorder=5)

ax2.axhline(0, color=COLORS['text'], linewidth=1.1, zorder=5)
ax2.set_xticks(idx)
ax2.set_xticklabels(seg, fontsize=11.5)
ax2.set_ylim(-480, 860)
ax2.set_yticks([-400, -200, 0, 200, 400, 600, 800])
add_badge(ax2, 0, 790, '45% 감소', kind='negative', fontsize=12)
ax2.legend(loc='upper right', frameon=False, fontsize=11.5,
           labelcolor=COLORS['sub'])
ax2.text(-0.45, -470, '조정 EBITDA는 감가상각과 주식보상 등을 빼기 전 이익 지표예요',
         ha='left', va='bottom', fontsize=10, color=COLORS['sub'])

add_footer(fig, '쿠팡Inc 2026년 3분기 실적 발표 · 뉴스1 · 바이라인네트워크 (2026)')
save_chart(fig, OUT)
