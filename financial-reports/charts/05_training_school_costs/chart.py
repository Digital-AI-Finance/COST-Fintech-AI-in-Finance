"""Training School Costs and Attendance - Horizontal Bar Chart"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams.update({
    'font.size': 12, 'axes.labelsize': 12, 'axes.titlesize': 14,
    'xtick.labelsize': 11, 'ytick.labelsize': 10, 'legend.fontsize': 11,
    'figure.figsize': (10, 7), 'figure.dpi': 150
})

COST_PURPLE = '#5B2D8A'
COST_BLUE = '#2B5F9E'

# Training school data
schools = [
    'Tirana 2023\n(AL - ITC)',
    'Enschede 2023\n(NL)',
    'Berlin 2023\n(DE)',
    'Naples 2023\n(IT)',
    'Cosenza 2024\n(IT)',
    'Enschede 2024\n(NL)',
    'Naples 2024\n(IT)'
]

costs = [7.4, 22.4, 8.7, 10.9, 11.3, 22.9, 25.2]  # in thousands
trainees = [15, 14, 11, 10, 11, 15, 22]

y = np.arange(len(schools))
height = 0.35

fig, ax1 = plt.subplots(figsize=(10, 7))

bars1 = ax1.barh(y - height/2, costs, height, label='Cost (EUR K)', color=COST_PURPLE, alpha=0.8)
ax1.set_yticks(y)
ax1.set_yticklabels(schools)
ax1.set_xlabel('Cost (EUR thousands)', color=COST_PURPLE)
ax1.tick_params(axis='x', labelcolor=COST_PURPLE)
ax1.set_title('Training Schools - Cost and Attendance (7 Schools Total)')

# Secondary axis for trainees
ax2 = ax1.twiny()
bars2 = ax2.barh(y + height/2, trainees, height, label='Trainees', color=COST_BLUE, alpha=0.8)
ax2.set_xlabel('Number of Trainees', color=COST_BLUE)
ax2.tick_params(axis='x', labelcolor=COST_BLUE)

# Add value labels
for bar, val in zip(bars1, costs):
    ax1.annotate(f'{val:.1f}K', xy=(bar.get_width(), bar.get_y() + bar.get_height()/2),
                 xytext=(3, 0), textcoords="offset points", ha='left', va='center', fontsize=9, color=COST_PURPLE)

for bar, val in zip(bars2, trainees):
    ax2.annotate(f'{val}', xy=(bar.get_width(), bar.get_y() + bar.get_height()/2),
                 xytext=(3, 0), textcoords="offset points", ha='left', va='center', fontsize=9, color=COST_BLUE)

ax1.invert_yaxis()
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# Custom legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=COST_PURPLE, alpha=0.8, label='Cost (EUR K)'),
                   Patch(facecolor=COST_BLUE, alpha=0.8, label='Trainees')]
ax1.legend(handles=legend_elements, loc='lower right', framealpha=0.9)

# Add totals
total_cost = sum(costs)
total_trainees = sum(trainees)
ax1.text(0.98, 0.02, f'Total: {total_cost:.1f}K EUR | {total_trainees} trainees',
         transform=ax1.transAxes, fontsize=11, verticalalignment='bottom', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig(Path(__file__).parent / 'chart.pdf', dpi=300, bbox_inches='tight')
plt.savefig(Path(__file__).parent / 'chart.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: 05_training_school_costs")
