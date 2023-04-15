import numpy as np
import matplotlib.pyplot as plt

nx = 200  #x方向网格节点数量
dx = 2/(nx-1)  #空间网格步长，x方向总长度2
dt = 0.005  # 时间步长
nt = int(1.0/dt) # 时间步数
c = 1 #常数

# 指定初始条件
u = np.ones(nx)
u[int(0.5/dx):int(1/dx + 1)] = 2 #这一行实际上是制造了一个方波
# 下面将初始条件画出来
fig = plt.figure()
x_axis = np.linspace(0,2,nx)
plt.ylim(-0.5, 2.5)
plt.plot(x_axis,u, 'r',lw=3, label = 'init')

# 计算25个时间步后的波形
un = np.ones(nx)
for n in range(nt):
   un = u.copy() #后面的计算会改变u，所以将u拷贝一份
   for i in range(1, nx):
       u[i] = un[i] - c * dt / dx * (un[i] - un[i-1])
   plt.cla()
   plt.plot(x_axis, u, lw=3)
   plt.pause(0.001)

plt.plot(np.linspace(0, 2, nx), u , 'b',lw =3,label= 'current')
plt.legend()
plt.show()