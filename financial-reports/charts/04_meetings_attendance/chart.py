"""Meetings Attendance by Type - Box/Violin Plot"""
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
COST_TEAL = '#00A0B0'
COST_ORANGE = '#E87722'

# Meeting attendance data by type
mc_attendance = [69, 69, 119, 119, 115, 69, 316, 312, 73]
wg_attendance = [137, 254, 317, 612, 317, 280, 15]
workshop_attendance = [238, 225, 317, 316, 613, 290, 570, 540, 288, 305, 12, 318, 31, 38, 19, 30, 39, 20, 35, 20]
conference_attendance = [197, 198, 315, 313, 590]

data = [mc_attendance, wg_attendance, workshop_attendance, conference_attendance]
labels = ['MC Meetings\n(9)', 'WG Meetings\n(7)', 'Workshops\n(20)', 'Conferences\n(5)']
colors = [COST_PURPLE, COST_BLUE, COST_TEAL, COST_ORANGE]

fig, ax = plt.subplots(figsize=(10, 6))

bp = ax.boxplot(data, labels=labels, patch_artist=True,
                medianprops=dict(color='white', linewidth=2))

for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax.set_ylabel('Number of Participants')
ax.set_title('Meeting Attendance Distribution by Type (40 Meetings Total)')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3)

# Add summary stats
stats_text = f'Mean Attendance:\nMC: {np.mean(mc_attendance):.0f}\nWG: {np.mean(wg_attendance):.0f}\nWorkshop: {np.mean(workshop_attendance):.0f}\nConference: {np.mean(conference_attendance):.0f}'
ax.text(0.98, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig(Path(__file__).parent / 'chart.pdf', dpi=300, bbox_inches='tight')
plt.savefig(Path(__file__).parent / 'chart.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: 04_meetings_attendance")
