"""Budget by Activity Type - Stacked Bar Chart"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams.update({
    'font.size': 14, 'axes.labelsize': 14, 'axes.titlesize': 16,
    'xtick.labelsize': 13, 'ytick.labelsize': 13, 'legend.fontsize': 11,
    'figure.figsize': (10, 6), 'figure.dpi': 150
})

COST_PURPLE = '#5B2D8A'
COST_BLUE = '#2B5F9E'
COST_TEAL = '#00A0B0'
COST_ORANGE = '#E87722'
COST_GREEN = '#7AB800'
COST_GRAY = '#6c757d'

# Data by category for each GP
categories = ['Meetings', 'Training Schools', 'STSM', 'Virtual Mobility', 'Dissemination', 'Other']
colors = [COST_PURPLE, COST_BLUE, COST_TEAL, COST_ORANGE, COST_GREEN, COST_GRAY]

gps = ['GP1', 'GP2', 'GP3', 'GP4', 'GP5']
data = {
    'Meetings': [10.3, 22.1, 111.6, 111.3, 120.8],
    'Training Schools': [0, 0, 0, 49.4, 59.4],
    'STSM': [20.8, 0, 24.1, 10.5, 4.6],
    'Virtual Mobility': [4.0, 6.8, 6.0, 36.0, 42.5],
    'Dissemination': [0.3, 0.5, 0.5, 10.5, 4.3],
    'Other': [12.1, 4.4, 24.0, 39.2, 38.7]
}

x = np.arange(len(gps))
width = 0.6

fig, ax = plt.subplots(figsize=(10, 6))

bottom = np.zeros(len(gps))
for i, (cat, color) in enumerate(zip(categories, colors)):
    values = data[cat]
    ax.bar(x, values, width, label=cat, bottom=bottom, color=color)
    bottom += values

ax.set_xlabel('Grant Period')
ax.set_ylabel('Expenditure (EUR thousands)')
ax.set_title('COST Action CA19130 - Expenditure by Activity Type')
ax.set_xticks(x)
ax.set_xticklabels(gps)
ax.legend(loc='upper left', framealpha=0.9, ncol=2)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(Path(__file__).parent / 'chart.pdf', dpi=300, bbox_inches='tight')
plt.savefig(Path(__file__).parent / 'chart.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: 02_budget_by_activity")
