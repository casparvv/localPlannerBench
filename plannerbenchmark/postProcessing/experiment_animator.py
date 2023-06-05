import matplotlib.animation as animation
from matplotlib.patches import Circle
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re

sns.set_style('darkgrid')
sns.set_palette('muted')
sns.set_context("talk")

# Select the experiment, type of planners and the date of an experiment
experiment = '../../experiments/b2_regular_vs_sensor_moving/results/'
fabric = 'fabric_0_'
dsi_fabric = 'sensorfabric_64_'
date = '20230426_121826' #date = '20230426_122217' #date = '20230426_122638'
data_fabric = np.loadtxt(f'{experiment}{fabric}{date}/res.csv', delimiter=',', skiprows=1)
data_dsi_fabric = np.loadtxt(f'{experiment}{dsi_fabric}{date}/res.csv', delimiter=',', skiprows=1)

# Find column numbers of robot configuration and obstacles in res.csv
q_pattern = re.compile(r'\bq[01]\b')
obst_pattern = re.compile(r'obst_\d_[^2]_\d')
header = np.genfromtxt(f'{experiment}{fabric}{date}/res.csv', delimiter=',', dtype='str', max_rows=1)
obst_cols = [i for i, col in enumerate(header) if obst_pattern.match(col)]
q_cols = [i for i, col in enumerate(header) if q_pattern.match(col)]

# Select the relevant data for plotting
goal = [0.0, 14.0]
q_fabric = data_fabric[:, [q_cols[0], q_cols[1]]]
q_dsi_fabric = data_dsi_fabric[:, [q_cols[0], q_cols[1]]]
obstacles = {}
for n in range(0, len(obst_cols), 2):
    obstacles[f'o{(int(n/2 + 1))}'] = data_fabric[:, [obst_cols[n], obst_cols[n + 1]]]

# Update function for matplotlib animation of robot(s)/obstacle(s) movements
fig, ax = plt.subplots()
fig.tight_layout()
def update(frame):
    ax.clear()
    plt.axis('square')
    plt.xlim(-8, 8)
    plt.ylim(-1, 15)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(f'Step {frame}')

    # Add goal and obstacle(s)
    goal = Circle((0, 14), radius=0.25, facecolor='green')
    ax.add_artist(goal)
    for obs, pos in obstacles.items():
        obs = Circle((pos[frame, :]), radius=0.5, facecolor='red')
        ax.add_artist(obs)

    # Add robots
    robot_fabric = Circle((q_fabric[frame, :]), radius=0.2, color='blue')
    ax.add_artist(robot_fabric)
    robot_dsi_fabric = Circle((q_dsi_fabric[frame, :]), radius=0.2, color='purple')
    ax.add_artist(robot_dsi_fabric)

    # Add labels as circles
    l1 = Line2D([], [], color="white", marker='o', markersize=12, markerfacecolor="green")
    l2 = Line2D([], [], color="white", marker='o', markersize=12, markerfacecolor="red")
    l3 = Line2D([], [], color="white", marker='o', markersize=12, markerfacecolor="blue")
    l4 = Line2D([], [], color="white", marker='o', markersize=12, markerfacecolor="purple")
    ax.legend((l1, l2, l3, l4), ('Goal', 'Obstacles', 'Fabric', 'DSI Fabric'), numpoints=1, loc=1, prop={'size': 22})


class Toggle:
    def __init__(self) -> None:
        self.paused = False
    def toggler(self):
        self.paused = not self.paused
toggle = Toggle()

# Plot the movements, use save = 1 to store a gif
plot = 1
save = 0
if save == True:
    anim = animation.FuncAnimation(fig, update, frames=len(q_fabric), interval=10, blit=False)
    writergif = animation.PillowWriter(fps=50)
    anim.save(f'{experiment}{date}.gif', writer=writergif)
    #writervid = animation.FFMpegWriter(fps=50)
    #anim.save('anim.mp4', writer=writervid)
    plt.close()
elif plot == True:
    anim = animation.FuncAnimation(fig, update, frames=len(q_fabric), interval=1, blit=False)
    def pause_animation(event):
        if toggle.paused:
            anim.resume()
            toggle.toggler()
        else:
            anim.pause()
            toggle.toggler()
    fig.canvas.mpl_connect('button_press_event', pause_animation)
    plt.show()

