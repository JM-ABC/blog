"""
커머스 인사이트 인포그래픽 공통 스타일 모듈.

output/<post>/generate_infographic.py 에서 다음과 같이 불러와 쓴다.

    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'brand'))
    from chart_style import COLORS, new_branded_figure, add_footer, add_badge, save_chart
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

BRAND_NAME = '커머스의 모든 것'
BRAND_HANDLE = 'brunch @aboutcommerce'

COLORS = {
    'bg': '#FFFFFF',
    'text': '#111111',
    'sub': '#6B7280',
    'eyebrow': '#2F6FED',
    'accent': '#2F6FED',
    'line_fill': '#E8F0FE',
    'grid': '#ECECEC',
    'divider': '#E5E7EB',
    'positive': '#16A34A',
    'negative': '#DC2626',
    'negative_bar': '#F2757D',
    'positive_bar': '#16A34A',
    'badge_neg_bg': '#FDE7E9',
    'badge_neg_text': '#DC2626',
    'badge_pos_bg': '#E5F6EA',
    'badge_pos_text': '#16A34A',
    'badge_neutral_bg': '#EFF3FF',
    'badge_neutral_text': '#2F6FED',
}


def new_branded_figure(eyebrow, title, subtitle, figsize=(18, 9.6)):
    """헤더(eyebrow/제목/부제목 + 브랜드명)가 찍힌 빈 캔버스를 만든다.
    차트 축은 이 함수가 반환한 fig 위에 fig.add_axes(...)로 직접 배치할 것.
    좌우 여백은 x=0.045 ~ x=0.955 를 기준으로 맞춘다."""
    fig = plt.figure(figsize=figsize, facecolor=COLORS['bg'])

    fig.text(0.045, 0.955, eyebrow, fontsize=13, fontweight='bold',
              color=COLORS['eyebrow'], ha='left', va='top')
    fig.text(0.045, 0.905, title, fontsize=30, fontweight='bold',
              color=COLORS['text'], ha='left', va='top')
    fig.text(0.045, 0.848, subtitle, fontsize=13.5,
              color=COLORS['sub'], ha='left', va='top')

    fig.text(0.955, 0.955, BRAND_NAME, fontsize=12, fontweight='bold',
              color=COLORS['text'], ha='right', va='top')
    fig.text(0.955, 0.925, BRAND_HANDLE, fontsize=10.5,
              color=COLORS['sub'], ha='right', va='top')

    return fig


def panel_header(fig, x0, x1, y, title, unit_label):
    """차트 패널 하나의 소제목(좌측)과 단위 표기(우측)를 그린다."""
    fig.text(x0, y, title, fontsize=16, fontweight='bold',
              color=COLORS['text'], ha='left', va='bottom')
    fig.text(x1, y, unit_label, fontsize=11,
              color=COLORS['sub'], ha='right', va='bottom')


_BADGE_KEY = {'negative': 'neg', 'positive': 'pos', 'neutral': 'neutral'}


def add_badge(ax, x, y, text, kind='negative', fontsize=12, transform=None):
    """알약 모양 배지. kind: 'negative' | 'positive' | 'neutral'"""
    key = _BADGE_KEY[kind]
    bg = COLORS[f'badge_{key}_bg']
    fg = COLORS[f'badge_{key}_text']
    ax.annotate(text, xy=(x, y), xycoords=transform or ax.transData,
                ha='center', va='center', fontsize=fontsize, fontweight='bold',
                color=fg,
                bbox=dict(boxstyle='round,pad=0.5', facecolor=bg, edgecolor='none'))


def add_footer(fig, source_text):
    """하단 구분선 + 출처(좌) + 그래픽 크레딧(우)."""
    line = plt.Line2D([0.045, 0.955], [0.065, 0.065],
                       color=COLORS['divider'], linewidth=1,
                       transform=fig.transFigure)
    fig.add_artist(line)
    fig.text(0.045, 0.045, f'출처: {source_text}', fontsize=10.5,
              color=COLORS['sub'], ha='left', va='center')
    fig.text(0.955, 0.045, f'그래픽: {BRAND_NAME}', fontsize=10.5,
              color=COLORS['sub'], ha='right', va='center')


def style_axes(ax):
    """공통 축 스타일: 테두리 제거, 옅은 가로 그리드만."""
    ax.set_facecolor(COLORS['bg'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.grid(axis='y', color=COLORS['grid'], linewidth=1, zorder=0)
    ax.tick_params(colors=COLORS['sub'], labelsize=11)


def save_chart(fig, path):
    fig.savefig(path, dpi=150, facecolor=COLORS['bg'])
    plt.close(fig)
    print('[완료] 인포그래픽 저장: ' + path)
