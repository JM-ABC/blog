# -*- coding: utf-8 -*-
"""커머스 인사이트 Vol.136 인포그래픽.

좌: 번개장터 연간 매출과 영업손익 (2024 -> 2025). 매출은 늘었지만 영업손실은 줄지 않았다.
우: 결제수수료로 번 돈과 결제를 처리하며 낸 지급수수료 (2024 -> 2025).
    2024년에는 받은 수수료가 나간 수수료보다 적었고, 2025년에 그 관계가 뒤집혔다.
한 장(좌우 2패널)으로 합쳐 CLAUDE.md 규칙 17의 개수 제한을 지킨다.
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
                   '번개장터-실적추이.png')

YEARS = ['2024년', '2025년']


def draw_left(ax):
    """매출(파랑)과 영업손익(빨강) 그룹 막대."""
    revenue = [449, 581]
    op_loss = [-196, -199]
    x = [0, 1]
    w = 0.3

    ax.bar([i - w / 2 for i in x], revenue, width=w,
           color=COLORS['accent'], zorder=3, label='매출')
    ax.bar([i + w / 2 for i in x], op_loss, width=w,
           color=COLORS['negative_bar'], zorder=3, label='영업손익')

    for i, v in zip(x, revenue):
        ax.text(i - w / 2, v + 18, f'{v:,}억원', ha='center', va='bottom',
                fontsize=13, fontweight='bold', color=COLORS['text'], zorder=4)
    for i, v in zip(x, op_loss):
        ax.text(i + w / 2, v - 18, f'{v:,}억원', ha='center', va='top',
                fontsize=13, fontweight='bold', color=COLORS['negative'], zorder=4)

    ax.axhline(0, color=COLORS['sub'], linewidth=1, zorder=4)
    ax.set_xticks(x)
    ax.set_xticklabels(YEARS, fontsize=13, fontweight='bold',
                       color=COLORS['text'])
    ax.set_ylim(-320, 760)
    ax.set_yticks([])
    style_axes(ax)
    ax.grid(False)

    add_badge(ax, 0.5, 690, '매출은 늘고 영업손실은 그대로',
              kind='negative', fontsize=12.5)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.17), ncol=2,
              frameon=False, fontsize=12, labelcolor=COLORS['sub'])


def draw_right(ax):
    """결제수수료 매출과 지급수수료 그룹 막대."""
    earned = [226, 370]
    paid = [228, 280]
    x = [0, 1]
    w = 0.3

    ax.bar([i - w / 2 for i in x], earned, width=w,
           color=COLORS['accent'], zorder=3, label='결제수수료 매출')
    ax.bar([i + w / 2 for i in x], paid, width=w,
           color=COLORS['sub'], zorder=3, label='지급수수료')

    for i, v in zip(x, earned):
        ax.text(i - w / 2, v + 9, f'{v:,}억원', ha='center', va='bottom',
                fontsize=13, fontweight='bold', color=COLORS['text'], zorder=4)
    for i, v in zip(x, paid):
        ax.text(i + w / 2, v + 9, f'{v:,}억원', ha='center', va='bottom',
                fontsize=13, fontweight='bold', color=COLORS['sub'], zorder=4)

    ax.set_xticks(x)
    ax.set_xticklabels(YEARS, fontsize=13, fontweight='bold',
                       color=COLORS['text'])
    ax.set_ylim(0, 540)
    ax.set_yticks([])
    style_axes(ax)
    ax.grid(False)

    add_badge(ax, 0, 470, '받은 수수료 < 나간 수수료',
              kind='negative', fontsize=12)
    add_badge(ax, 1, 470, '받은 수수료 > 나간 수수료',
              kind='positive', fontsize=12)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.17), ncol=2,
              frameon=False, fontsize=12, labelcolor=COLORS['sub'])


def main():
    fig = new_branded_figure(
        'BUNJANG ANNUAL PERFORMANCE REVIEW',
        '매출은 늘었는데 영업손실은 줄지 않은 번개장터',
        '안전결제 의무화 이후 수수료로 번 돈이 늘었지만, 결제를 처리하며 나간 수수료도 함께 늘었어요',
    )

    ax_left = fig.add_axes([0.045, 0.19, 0.40, 0.54])
    ax_right = fig.add_axes([0.555, 0.19, 0.40, 0.54])

    panel_header(fig, 0.045, 0.445, 0.76, '연간 매출과 영업손익', '단위: 억원')
    panel_header(fig, 0.555, 0.955, 0.76, '결제수수료 매출과 지급수수료', '단위: 억원')

    draw_left(ax_left)
    draw_right(ax_right)

    add_footer(fig, '전자신문 · 유니콘팩토리 (2025~2026)')
    save_chart(fig, OUT)


if __name__ == '__main__':
    main()
