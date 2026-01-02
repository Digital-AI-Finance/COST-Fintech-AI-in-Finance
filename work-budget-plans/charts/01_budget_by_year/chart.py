"""Budget by Grant Period - Bar Chart"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams.update({
    'font.size': 14, 'axes.labelsize': 14, 'axes.titlesize': 16,
    'xtick.labelsize': 13, 'ytick.labelsize': 13, 'legend.fontsize': 13,
    'figure.figsize': (10, 6), 'figure.dpi': 150
})

COST_PURPLE = '#5B2D8A'
COST_BLUE = '#2B5F9E'
COST_TEAL = '#00A0B0'
COST_ORANGE = '#E87722'
COST_GREEN = '#7AB800'

# Data
grant_periods = ['GP1\n(Nov 2020-\nOct 2021)', 'GP2\n(Nov 2021-\nMay 2022)', 'GP3\n(Jun 2022-\nOct 2022)',
                 'GP4\n(Nov 2022-\nOct 2023)', 'GP5\n(Nov 2023-\nSep 2024)']
budgets = [62985.50, 202607.00, 169820.50, 257925.91, 270315.26]

x = np.arange(len(grant_periods))
width = 0.6

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(x, [b/1000 for b in budgets], width, color=[COST_PURPLE, COST_BLUE, COST_TEAL, COST_ORANGE, COST_GREEN])

ax.set_xlabel('Grant Period')
ax.set_ylabel('Budget (EUR thousands)')
ax.set_title('COST Action CA19130 - Budget by Grant Period')
ax.set_xticks(x)
ax.set_xticklabels(grant_periods)
ax.set_ylim(0, 320)

# Add value labels on bars
for bar, budget in zip(bars, budgets):
    height = bar.get_height()
    ax.annotate(f'{budget/1000:.1f}K',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontsize=11, fontweight='bold')

# Add total
total = sum(budgets)
ax.text(0.98, 0.95, f'Total: {total/1000:.1f}K EUR', transform=ax.transAxes,
        fontsize=12, verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(Path(__file__).parent / 'chart.pdf', dpi=300, bbox_inches='tight')
plt.savefig(Path(__file__).parent / 'chart.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: 01_budget_by_year")
