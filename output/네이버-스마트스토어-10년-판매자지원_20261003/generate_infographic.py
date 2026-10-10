import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'brand'))
from chart_style import COLORS, new_branded_figure, panel_header, add_badge, add_footer, style_axes, save_chart

fig = new_branded_figure(
    eyebrow='D-COMMERCE REPORT 2026',
    title='스마트스토어 판매자, 단계마다 원하는 지원이 달라요',
    subtitle='네이버, 서울대 유병준·연세대 최보름 연구팀 공동 보고서 (2026.09.30)',
)

# 왼쪽: 스마트스토어 주력 운영 이유 (단계별)
ax1 = fig.add_axes([0.06, 0.15, 0.40, 0.58])
panel_header(fig, 0.045, 0.46, 0.765, '스마트스토어를 주력으로 쓰는 이유', '단위: %, 응답 비율')
stages = ['진입기', '성장기', '성숙기']
fin = [50.6, 53.2, 40.0]
biz = [43.2, 39.2, 48.3]
x = [0, 1, 2]
w = 0.36
bars_f = ax1.bar([i - w / 2 for i in x], fin, width=w, color=COLORS['accent'], zorder=3, label='금융적 이유 (수수료·정산)')
bars_b = ax1.bar([i + w / 2 for i in x], biz, width=w, color=COLORS['positive_bar'], zorder=3, label='사업적 이유 (노출·판로·물류)')
ax1.set_xticks(x)
ax1.set_xticklabels(stages)
style_axes(ax1)
ax1.set_ylim(0, 70)
for bar, val in list(zip(bars_f, fin)) + list(zip(bars_b, biz)):
    ax1.annotate(f'{val:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, val),
                 xytext=(0, 6), textcoords='offset points',
                 ha='center', fontsize=12, fontweight='bold', color=COLORS['text'])
ax1.legend(loc='upper left', frameon=False, fontsize=10)
add_badge(ax1, 2, 62, '성숙기에서 순서가 바뀌어요', kind='positive', fontsize=11)

# 오른쪽: 판매자쿠폰 도입 스토어의 매출 효과 (미사용 스토어 대비 배수)
ax2 = fig.add_axes([0.56, 0.15, 0.395, 0.58])
panel_header(fig, 0.54, 0.955, 0.765, '판매자쿠폰 도입 효과 (미사용 스토어 대비)', '단위: 배, 성향점수매칭 분석')
periods = ['도입 첫 달', '1개월 뒤', '3개월 뒤']
mult = [6.1, 3.2, 2.1]
bars2 = ax2.bar(periods, mult, color=COLORS['accent'], width=0.5, zorder=3)
style_axes(ax2)
ax2.set_ylim(0, 7.5)
for bar, val in zip(bars2, mult):
    ax2.annotate(f'{val:g}배', xy=(bar.get_x() + bar.get_width() / 2, val),
                 xytext=(0, 8), textcoords='offset points',
                 ha='center', fontsize=14, fontweight='bold', color=COLORS['text'])
add_badge(ax2, 2, 4.0, '석 달 뒤에도 2배 유지', kind='neutral', fontsize=11)

add_footer(fig, '네이버 D-커머스 리포트 2026 · 뉴스핌 · 아이티데일리 (2026)')

save_chart(fig, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'naver-smartstore-dcommerce-2026.png'))
