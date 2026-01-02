"""Expenditure Breakdown - Donut Chart"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams.update({
    'font.size': 14, 'axes.labelsize': 14, 'axes.titlesize': 16,
    'xtick.labelsize': 13, 'ytick.labelsize': 13, 'legend.fontsize': 12,
    'figure.figsize': (10, 8), 'figure.dpi': 150
})

COST_PURPLE = '#5B2D8A'
COST_BLUE = '#2B5F9E'
COST_TEAL = '#00A0B0'
COST_ORANGE = '#E87722'
COST_GREEN = '#7AB800'
COST_GRAY = '#6c757d'

# Total expenditure by category across all GPs
categories = ['Meetings', 'Training Schools', 'STSMs', 'Virtual Mobility', 'ITC Grants', 'FSAC', 'Dissemination']
values = [376.1, 108.8, 60.1, 95.3, 9.2, 100.6, 16.1]
colors = [COST_PURPLE, COST_BLUE, COST_TEAL, COST_ORANGE, COST_GREEN, COST_GRAY, '#c4c4c4']

fig, ax = plt.subplots(figsize=(10, 8))

# Create donut
wedges, texts, autotexts = ax.pie(values, labels=categories, autopct='%1.1f%%',
                                   colors=colors, pctdistance=0.75,
                                   wedgeprops=dict(width=0.5, edgecolor='white'),
                                   textprops={'fontsize': 11})

# Make percentage text white on dark segments
for i, autotext in enumerate(autotexts):
    if values[i] > 50:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

# Center text
total = sum(values)
ax.text(0, 0, f'Total\n{total:.1f}K EUR', ha='center', va='center', fontsize=16, fontweight='bold')

ax.set_title('COST Action CA19130 - Total Expenditure by Category (2020-2024)', fontsize=14, pad=20)

plt.tight_layout()
plt.savefig(Path(__file__).parent / 'chart.pdf', dpi=300, bbox_inches='tight')
plt.savefig(Path(__file__).parent / 'chart.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: 02_expenditure_breakdown")
