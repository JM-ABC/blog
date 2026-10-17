# -*- coding: utf-8 -*-
"""커머스 인사이트 Vol.135 인포그래픽.

좌: 개인정보 유출 사건에 걸린 금액 (쿠팡 자체 보상안 / 개인정보위 과징금)
우: 공정위 조사 거부에 매길 수 있는 과태료 상한 (이번 건 / 반복 위반)
두 패널의 단위는 같은 억원이지만 자릿수가 크게 달라서 축을 나눠 그린다.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', '..', 'assets', 'brand'))

from chart_style import (COLORS, new_branded_figure, panel_header, add_badge,
                         add_footer, style_axes, save_chart)

import matplotlib.pyplot as plt

# chart_style.py는 윈도우 기준으로 'Malgun Gothic'을 지정한다.
# 이 환경(리눅스)에는 없어서 설치된 나눔고딕으로 바꿔준다. 색상과 레이아웃은 그대로 쓴다.
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '쿠팡-규제금액-비교.png')


def draw_panel(ax, rows, xmax, xticks, xticklabels):
    """rows: [(라벨, 상태설명, 값, 색, 값표기)] 를 가로 막대로 그린다.

    y축 눈금 대신 막대 위에 라벨을 얹어서 좌우 여백에 글자가 잘리지 않게 한다."""
    style_axes(ax)
    ax.grid(axis='y', visible=False)
    ax.grid(axis='x', color=COLORS['grid'], linewidth=1, zorder=0)
    ax.set_xlim(0, xmax)
    ax.set_ylim(len(rows), 0)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_yticks([])

    for i, (label, status, value, color, value_text) in enumerate(rows):
        y = i + 0.5
        ax.text(0, y - 0.30, label, fontsize=14, fontweight='bold',
                color=COLORS['text'], ha='left', va='bottom')
        ax.text(0, y - 0.30, '   ' + status, fontsize=11.5,
                color=COLORS['sub'], ha='left', va='top',
                transform=ax.transData)
        ax.barh(y + 0.08, value, color=color, height=0.30, zorder=3)
        ax.text(value + xmax * 0.015, y + 0.08, value_text,
                va='center', ha='left', fontsize=14, fontweight='bold',
                color=COLORS['text'])


fig = new_branded_figure(
    eyebrow='REGULATORY ACTION SCALE',
    title='쿠팡을 둘러싼 두 사건, 걸려 있는 금액',
    subtitle='개인정보 유출 사건의 과징금·보상 규모와, 공정위 조사 거부에 매길 수 있는 과태료 상한',
)

# ── 왼쪽 패널: 개인정보 유출 사건 ──────────────────────────────
panel_header(fig, 0.045, 0.47, 0.73, '개인정보 유출 사건', '단위: 억원')
ax1 = fig.add_axes([0.045, 0.21, 0.425, 0.48])
draw_panel(
    ax1,
    rows=[
        ('쿠팡 자체 보상안', '2025년 12월 발표, 이행', 16850, COLORS['accent'],
         '1조 6,850억원'),
        ('개인정보위 과징금', '2026년 6월 의결, 쿠팡이 불복해 소송 중', 6246.81,
         COLORS['negative_bar'], '6,246억 8,100만원'),
    ],
    xmax=24000,
    xticks=[0, 5000, 10000, 15000, 20000],
    xticklabels=['0', '5,000', '10,000', '15,000', '20,000'],
)

# ── 오른쪽 패널: 조사 거부 과태료 상한 ─────────────────────────
panel_header(fig, 0.545, 0.955, 0.73, '공정위 조사 거부 과태료 상한', '단위: 억원')
ax2 = fig.add_axes([0.545, 0.21, 0.41, 0.48])
draw_panel(
    ax2,
    rows=[
        ('이번 건', '첫 조사 거부라 적용되는 상한', 1, COLORS['negative_bar'], '1억원'),
        ('반복 위반 사업자', '대규모유통업법상 최대', 2, COLORS['sub'], '2억원'),
    ],
    xmax=2.9,
    xticks=[0, 1, 2],
    xticklabels=['0', '1', '2'],
)

add_badge(ax2, 1.45, 1.95, '왼쪽 패널과 자릿수가 다릅니다', kind='neutral', fontsize=12)

add_footer(fig, '뉴시스 · 경향신문 · 뉴스핌 · 헤럴드경제 (2025~2026)')
save_chart(fig, OUT)
