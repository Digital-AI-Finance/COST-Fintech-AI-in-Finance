"""Country Participation - Horizontal Bar Chart"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams.update({
    'font.size': 12, 'axes.labelsize': 12, 'axes.titlesize': 14,
    'xtick.labelsize': 11, 'ytick.labelsize': 10, 'legend.fontsize': 11,
    'figure.figsize': (10, 8), 'figure.dpi': 150
})

COST_PURPLE = '#5B2D8A'
COST_ORANGE = '#E87722'

# Country data with participant counts (from extracted data)
data = [
    ('Romania', 18, True), ('Albania', 15, True), ('Turkey', 12, True),
    ('Germany', 11, False), ('Italy', 10, False), ('Switzerland', 10, False),
    ('Czech Republic', 7, True), ('Netherlands', 7, False), ('North Macedonia', 6, True),
    ('Ireland', 6, False), ('United Kingdom', 5, False), ('France', 4, False),
    ('Poland', 4, True), ('Greece', 4, True), ('Latvia', 3, True),
    ('Croatia', 3, True), ('Slovakia', 3, True), ('Cyprus', 3, True),
    ('Portugal', 3, True), ('Spain', 3, False), ('Lithuania', 3, True),
    ('Hungary', 3, True), ('Finland', 2, False), ('Ukraine', 2, True),
    ('Belgium', 2, False), ('Norway', 2, False), ('Estonia', 1, True),
    ('Israel', 1, False), ('Iceland', 1, False), ('Austria', 1, False),
    ('Bulgaria', 1, True), ('Serbia', 1, True), ('United States', 1, False)
]

# Sort by count
data.sort(key=lambda x: x[1], reverse=True)

# Take top 20 for visibility
data = data[:20]

countries = [d[0] for d in data]
counts = [d[1] for d in data]
itc_flags = [d[2] for d in data]
colors = [COST_ORANGE if itc else COST_PURPLE for itc in itc_flags]

fig, ax = plt.subplots(figsize=(10, 8))

y = np.arange(len(countries))
bars = ax.barh(y, counts, color=colors, height=0.7)

ax.set_yticks(y)
ax.set_yticklabels(countries)
ax.set_xlabel('Number of Participants')
ax.set_title('COST Action CA19130 - Top 20 Countries by Participation')
ax.invert_yaxis()

# Add value labels
for bar, count in zip(bars, counts):
    width = bar.get_width()
    ax.annotate(str(count),
                xy=(width, bar.get_y() + bar.get_height() / 2),
                xytext=(3, 0), textcoords="offset points",
                ha='left', va='center', fontsize=10)

# Custom legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=COST_ORANGE, label='ITC Countries'),
                   Patch(facecolor=COST_PURPLE, label='Non-ITC Countries')]
ax.legend(handles=legend_elements, loc='lower right', framealpha=0.9)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(Path(__file__).parent / 'chart.pdf', dpi=300, bbox_inches='tight')
plt.savefig(Path(__file__).parent / 'chart.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: 04_country_participation")
