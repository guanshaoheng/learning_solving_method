import matplotlib.pyplot as plt
plt.figure(figsize=[5, 5])
ax = plt.axes([0.1, 0.1, 0.8, 0.8], xlim=(0, 1), ylim=(0, 1))
points_whole_ax = 5 * 0.8 * 72    # 1 point = dpi / 72 pixels
radius = 0.1
points_radius = 2 * radius / 1.0 * points_whole_ax
ax.scatter(0.5, 0.5, s=points_radius**2, color='r')
plt.grid()
plt.show()