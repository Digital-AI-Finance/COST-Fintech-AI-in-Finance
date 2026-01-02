"""Actual vs Budget Comparison - Grouped Bar Chart"""
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
COST_ORANGE = '#E87722'

# Data
gps = ['GP1', 'GP2', 'GP3', 'GP4', 'GP5']
budget = [62.99, 202.61, 169.82, 257.93, 270.32]
actual = [47.46, 33.77, 166.26, 256.85, 270.32]

x = np.arange(len(gps))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))

bars1 = ax.bar(x - width/2, budget, width, label='Budget', color=COST_PURPLE, alpha=0.8)
bars2 = ax.bar(x + width/2, actual, width, label='Actual', color=COST_BLUE, alpha=0.8)

ax.set_xlabel('Grant Period')
ax.set_ylabel('Amount (EUR thousands)')
ax.set_title('COST Action CA19130 - Budget vs Actual Expenditure')
ax.set_xticks(x)
ax.set_xticklabels(gps)
ax.legend(loc='upper left', framealpha=0.9)

# Add variance line
variance = [(a - b) for a, b in zip(actual, budget)]
ax2 = ax.twinx()
ax2.plot(x, variance, 'o-', color=COST_ORANGE, linewidth=2, markersize=8, label='Variance')
ax2.set_ylabel('Variance (EUR thousands)', color=COST_ORANGE)
ax2.tick_params(axis='y', labelcolor=COST_ORANGE)
ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax2.set_ylim(-180, 50)

ax.spines['top'].set_visible(False)
ax.grid(axis='y', alpha=0.3)

# Add total annotation
total_budget = sum(budget)
total_actual = sum(actual)
ax.text(0.98, 0.95, f'Total Budget: {total_budget:.1f}K\nTotal Actual: {total_actual:.1f}K',
        transform=ax.transAxes, fontsize=11, verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig(Path(__file__).parent / 'chart.pdf', dpi=300, bbox_inches='tight')
plt.savefig(Path(__file__).parent / 'chart.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: 01_actual_vs_budget")
