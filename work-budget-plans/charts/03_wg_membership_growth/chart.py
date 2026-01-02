"""Working Group Membership Growth - Line Chart"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams.update({
    'font.size': 14, 'axes.labelsize': 14, 'axes.titlesize': 16,
    'xtick.labelsize': 13, 'ytick.labelsize': 13, 'legend.fontsize': 12,
    'figure.figsize': (10, 6), 'figure.dpi': 150
})

COST_PURPLE = '#5B2D8A'
COST_BLUE = '#2B5F9E'
COST_GREEN = '#7AB800'

# Data: WG membership over grant periods
periods = ['GP1\n(2020-21)', 'GP2-3\n(2022)', 'GP4\n(2023)', 'GP5\n(2024)']
wg1 = [30, 50, 169, 277]
wg2 = [30, 57, 179, 248]
wg3 = [30, 41, 130, 218]

x = np.arange(len(periods))

fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(x, wg1, 'o-', linewidth=2.5, markersize=10, color=COST_PURPLE, label='WG1: Transparency in FinTech')
ax.plot(x, wg2, 's-', linewidth=2.5, markersize=10, color=COST_BLUE, label='WG2: Black Box Models')
ax.plot(x, wg3, '^-', linewidth=2.5, markersize=10, color=COST_GREEN, label='WG3: Investment Performance')

# Add value labels
for i, (y1, y2, y3) in enumerate(zip(wg1, wg2, wg3)):
    ax.annotate(str(y1), (i, y1), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=10, color=COST_PURPLE)
    ax.annotate(str(y2), (i, y2), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=10, color=COST_BLUE)
    ax.annotate(str(y3), (i, y3), textcoords="offset points", xytext=(0, -15), ha='center', fontsize=10, color=COST_GREEN)

ax.set_xlabel('Grant Period')
ax.set_ylabel('Number of Members')
ax.set_title('Working Group Membership Growth (2020-2024)')
ax.set_xticks(x)
ax.set_xticklabels(periods)
ax.set_ylim(0, 320)
ax.legend(loc='upper left', framealpha=0.9)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3)

# Add total annotation
total = wg1[-1] + wg2[-1] + wg3[-1]
ax.text(0.98, 0.3, f'Total WG Members (GP5): {total}', transform=ax.transAxes,
        fontsize=11, verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig(Path(__file__).parent / 'chart.pdf', dpi=300, bbox_inches='tight')
plt.savefig(Path(__file__).parent / 'chart.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: 03_wg_membership_growth")
