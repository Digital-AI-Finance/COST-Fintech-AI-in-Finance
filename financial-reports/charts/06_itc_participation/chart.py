"""ITC Participation Over Time - Pie and Line Chart"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams.update({
    'font.size': 14, 'axes.labelsize': 14, 'axes.titlesize': 16,
    'xtick.labelsize': 13, 'ytick.labelsize': 13, 'legend.fontsize': 12,
    'figure.figsize': (12, 5), 'figure.dpi': 150
})

COST_PURPLE = '#5B2D8A'
COST_ORANGE = '#E87722'
COST_TEAL = '#00A0B0'

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Left: Pie chart - overall ITC participation
itc_count = 87
non_itc_count = 66
total = itc_count + non_itc_count

colors = [COST_ORANGE, COST_PURPLE]
wedges, texts, autotexts = ax1.pie([itc_count, non_itc_count],
                                    labels=['ITC Countries', 'Non-ITC Countries'],
                                    autopct='%1.1f%%', colors=colors,
                                    wedgeprops=dict(edgecolor='white', linewidth=2),
                                    textprops={'fontsize': 12})
for autotext in autotexts:
    autotext.set_fontweight('bold')
    autotext.set_color('white')

ax1.set_title('ITC vs Non-ITC Participation\n(153 Participants)', fontsize=14)

# Right: Line chart - ITC % over grant periods
gps = ['GP1', 'GP2-3', 'GP4', 'GP5']
itc_pct = [54.5, 57.1, 58, 59]
mc_itc_pct = [54.5, 57.1, 58, 59]
wg_itc_pct = [50, 55, 58, 59]

x = np.arange(len(gps))

ax2.plot(x, itc_pct, 'o-', linewidth=2.5, markersize=10, color=COST_ORANGE, label='Overall ITC %')
ax2.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='Target (50%)')

# Add value labels
for i, pct in enumerate(itc_pct):
    ax2.annotate(f'{pct}%', (i, pct), textcoords="offset points", xytext=(0, 10),
                 ha='center', fontsize=11, fontweight='bold', color=COST_ORANGE)

ax2.set_xlabel('Grant Period')
ax2.set_ylabel('ITC Participation (%)')
ax2.set_title('ITC Participation Growth Over Time', fontsize=14)
ax2.set_xticks(x)
ax2.set_xticklabels(gps)
ax2.set_ylim(40, 70)
ax2.legend(loc='lower right', framealpha=0.9)

ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.grid(axis='y', alpha=0.3)

# Add target achieved annotation
ax2.text(0.02, 0.95, 'Target: 50% ITC\nAchieved: 59%', transform=ax2.transAxes,
        fontsize=10, verticalalignment='top', horizontalalignment='left',
        bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))

plt.tight_layout()
plt.savefig(Path(__file__).parent / 'chart.pdf', dpi=300, bbox_inches='tight')
plt.savefig(Path(__file__).parent / 'chart.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: 06_itc_participation")
