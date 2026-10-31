# -*- coding: utf-8 -*-
"""커머스 인사이트 Vol.137 인포그래픽.

좌: 무신사를 두고 거론되는 기업가치 범위. 기관 간 구주거래 평가액(4.2조)부터
    시장에서 거론되는 상단(10조)까지 다섯 개 숫자를 한 줄에 세워 간격을 보여준다.
우: 같은 다섯 숫자를 2025년 연결 매출(1조4,679억원)로 나눈 배수.
    매출 대비 몇 배를 인정받느냐의 차이라는 본문 서술을 눈으로 확인하게 한다.
한 장(좌우 2패널)으로 합쳐 CLAUDE.md 규칙 17의 개수 제한을 지킨다.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', '..', 'assets', 'brand'))

from chart_style import (COLORS, new_branded_figure, panel_header, add_badge,
                         add_footer, style_axes, save_chart)

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# chart_style.py는 윈도우 기준으로 'Malgun Gothic'을 지정한다.
# 이 환경(리눅스)에는 없어서 koreanize-matplotlib이 들고 있는 나눔고딕을 등록해 쓴다.
# 색상과 레이아웃은 chart_style.py 그대로 유지한다.
try:
    import koreanize_matplotlib  # noqa: F401
    _font_dir = os.path.join(os.path.dirname(koreanize_matplotlib.__file__), 'fonts')
    for _f in ('NanumGothic.ttf', 'NanumGothicBold.ttf'):
        _p = os.path.join(_font_dir, _f)
        if os.path.exists(_p):
            fm.fontManager.addfont(_p)
    plt.rcParams['font.family'] = 'NanumGothic'
except ImportError:
    pass
plt.rcParams['axes.unicode_minus'] = False

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'musinsa-ipo-밸류에이션.png')

# 2025년 연결 매출 (억원) - 무신사 뉴스룸 2026.03.31
REVENUE_2025 = 14679

LABELS = ['구주거래\n평가액', '장외 추정\n시가총액', '투자사 동의\n최소선', '공모 목표\n거론 수준', '시장 거론\n상단']
VALUES_JO = [4.2, 5.5, 7.0, 8.0, 10.0]          # 단위: 조원
MULTIPLES = [round(v * 10000 / REVENUE_2025, 1) for v in VALUES_JO]


def draw_left(ax):
    """거론되는 기업가치 범위 (가로 막대)."""
    y = list(range(len(LABELS)))[::-1]
    bars = ax.barh(y, VALUES_JO, height=0.55, color=COLORS['accent'], zorder=3)
    # 목표 구간(8조)만 색을 살짝 달리해 본문 서술과 맞춘다
    bars[3].set_color('#1B4FBF')

    for yi, v in zip(y, VALUES_JO):
        ax.text(v + 0.18, yi, f'{v:g}조원', va='center', ha='left',
                fontsize=12.5, fontweight='bold', color=COLORS['text'])

    ax.set_yticks(y)
    ax.set_yticklabels(LABELS, fontsize=11.5, color=COLORS['text'])
    ax.set_xlim(0, 12.2)
    ax.set_xticks([0, 2, 4, 6, 8, 10, 12])
    style_axes(ax)
    ax.grid(axis='y', visible=False)
    ax.grid(axis='x', color=COLORS['grid'], linewidth=1, zorder=0)

    add_badge(ax, 10.1, y[0] - 0.62, '구주거래 대비 공모 목표 약 1.9배',
              kind='neutral', fontsize=11.5)


def draw_right(ax):
    """2025년 연결 매출 대비 환산 배수 (가로 막대)."""
    y = list(range(len(LABELS)))[::-1]
    bars = ax.barh(y, MULTIPLES, height=0.55, color='#9CC0FF', zorder=3)
    bars[3].set_color(COLORS['accent'])

    for yi, m in zip(y, MULTIPLES):
        ax.text(m + 0.12, yi, f'{m}배', va='center', ha='left',
                fontsize=12.5, fontweight='bold', color=COLORS['text'])

    ax.set_yticks(y)
    ax.set_yticklabels([])
    ax.set_xlim(0, 8.3)
    ax.set_xticks([0, 2, 4, 6, 8])
    style_axes(ax)
    ax.grid(axis='y', visible=False)
    ax.grid(axis='x', color=COLORS['grid'], linewidth=1, zorder=0)

    add_badge(ax, 6.3, y[0] - 0.62, '2026년 상반기 매출 환산 기준이면 8조원은 4.9배',
              kind='neutral', fontsize=11.5)


def main():
    fig = new_branded_figure(
        'MUSINSA IPO VALUATION',
        '무신사 몸값, 4조원대부터 10조원까지',
        '상장예비심사 결과를 앞두고 거론되는 기업가치와 2025년 연결 매출 대비 환산 배수. '
        '기업가치와 시가총액은 부채를 넣는 기준이 달라 대략의 눈금으로 본 값',
    )

    panel_header(fig, 0.045, 0.47, 0.76, '거론되는 기업가치 범위', '단위: 조원')
    panel_header(fig, 0.53, 0.955, 0.76, '2025년 연결 매출 대비 배수', '단위: 배')

    ax_left = fig.add_axes([0.105, 0.17, 0.355, 0.56])
    ax_right = fig.add_axes([0.545, 0.17, 0.40, 0.56])

    draw_left(ax_left)
    draw_right(ax_right)

    add_footer(fig, '머니투데이 · 한국경제 · 무신사 뉴스룸 (2026)')
    save_chart(fig, OUT)


if __name__ == '__main__':
    main()
