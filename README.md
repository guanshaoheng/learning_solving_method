# learning_solving_method
在这里我们使用了Galerkin方法和FDM方法求解了方程，并且对比了方程的求解结果。

中文解说参考 [Here](https://zhuanlan.zhihu.com/p/622256859)


# Deep Ritz方法

## 求解颗粒系统 Particle systems
当前难以解决的问题：
- 无法模拟系统在牛顿第二定律控制下的运动过程；
- 尚未论证该结果为系统最优结果，目前尚处于近似真实结果的阶段，或者说只能从现象上说明模拟的真实性，而未能从理论上证明结果的有效性；
- 如何处理摩擦耗散、粘性问题？


### 密集堆积系统
- 对于密集堆积的颗粒系统我们能够看到，优化过程能够得到最终的稳定平衡状态，但是其运动过程没有**牛顿第二定律**的控制，也忽略了**颗粒间的摩擦耗散**作用。

| ![space-1.jpg](deepRitz_particle/img/dense/step_0.png) | ![space-1.jpg](deepRitz_particle/img/dense/step_1000.png) |
|:--:| :--:| 
| **Initial state** |**Optimized 1000 steps**|
| ![space-1.jpg](deepRitz_particle/img/dense/step_2000.png) | ![space-1.jpg](deepRitz_particle/img/dense/step_3000.png) |
| **Optimized 2000 steps** |**Optimized 3000 steps**|


### 稳定的最终状态
- 然后我们采用倒三角的初始堆积，模拟过程如图所示：

| ![space-1.jpg](./deepRitz_particle/img/stable/step_0.png) | ![space-1.jpg](./deepRitz_particle/img/stable/step_1000.png) |
|:--:| :--:| 
| **Initial state** |**Optimized 1000 steps**|
| ![space-1.jpg](./deepRitz_particle/img/stable/step_2000.png) | ![space-1.jpg](./deepRitz_particle/img/stable/step_3000.png) |
| **Optimized 2000 steps** |**Optimized 3000 steps**|
| ![space-1.jpg](./deepRitz_particle/img/stable/step_4000.png) | ![space-1.jpg](./deepRitz_particle/img/stable/step_5000.png) |
| **Optimized 4000 steps** |**final state (stable)**|

### 不稳定的最终状态
- 然后，采用倒三角的初始堆积，而且并未将颗粒错开，模拟过程如图所示：

| ![space-1.jpg](./deepRitz_particle/img/unstable/step_0.png) | ![space-1.jpg](./deepRitz_particle/img/unstable/step_1000.png) |
|:--:| :--:| 
| **Initial state** |**Optimized 1000 steps**|
| ![space-1.jpg](./deepRitz_particle/img/unstable/step_2000.png) | ![space-1.jpg](./deepRitz_particle/img/unstable/step_3000.png) |
| **Optimized 2000 steps** |**Optimized 3000 steps**|
| ![space-1.jpg](./deepRitz_particle/img/unstable/step_4000.png) | ![space-1.jpg](./deepRitz_particle/img/unstable/step_5000.png) |
| **Optimized 4000 steps** |**final state (unstable)**|

- 上述不同结果源于不同初始堆积，在第一种堆积中我们得到了优化后的稳定结果最终整体势能为2.2e5，而后者我们得到的整体势能为5.4e5，远高于前者。
并且由于高层堆积导致底部
接触力较大，因此，非稳定堆积的接触势能也要大于前者（5e3>3.4e2）
- 在日常生活中，经验告诉我们，对于足够光滑、无粘性的圆球体系，只有非常非常小的几率出现图中的不稳定结果。但是在数值模拟中，这种结果确确实实出现了。
或者换一种说法，优化算法陷入了**局部最优**，而且这种局部最优相当容易发生。

### 引入微小不稳定因素的初始状态求解
本例中，小球的半径为0.1，我们在最下方的红色小球处添加一个**水平向右的0.001**的微小扰动，计算结果如下所示：

| ![space-1.jpg](./deepRitz_particle/img/disturbed_bottom/step_0.png) | ![space-1.jpg](./deepRitz_particle/img/disturbed_bottom/step_1000.png) |
|:--:| :--:| 
| **Initial state** |**Optimized 1000 steps**|
| ![space-1.jpg](./deepRitz_particle/img/disturbed_bottom/step_2000.png) | ![space-1.jpg](./deepRitz_particle/img/disturbed_bottom/step_3000.png) |
| **Optimized 2000 steps** |**Optimized 3000 steps**|
| ![space-1.jpg](./deepRitz_particle/img/disturbed_bottom/step_4000.png) | ![space-1.jpg](./deepRitz_particle/img/disturbed_bottom/step_5000.png) |
| **Optimized 4000 steps** |**final state (unstable)**|

然后，在第一列最上方的小球处，我们添加一个水平向左的0.001的微小扰动，计算结果如下所示：
| ![space-1.jpg](./deepRitz_particle/img/disturbed_top/step_0.png) | ![space-1.jpg](./deepRitz_particle/img/disturbed_top/step_1000.png) |
|:--:| :--:| 
| **Initial state** |**Optimized 1000 steps**|
| ![space-1.jpg](./deepRitz_particle/img/disturbed_top/step_2000.png) | ![space-1.jpg](./deepRitz_particle/img/disturbed_top/step_3000.png) |
| **Optimized 2000 steps** |**Optimized 3000 steps**|
| ![space-1.jpg](./deepRitz_particle/img/disturbed_top/step_4000.png) | ![space-1.jpg](./deepRitz_particle/img/disturbed_top/step_5000.png) |
| **Optimized 4000 steps** |**final state (unstable)**|

- 由此可见，只要添加非常微小的扰动，Adam优化算法就能够根据整体的能量优化到最终平衡的位置；
- 实际上，在非晶态的颗粒体系中，一般都采用不规则堆积，不会**由于规则堆积而导致陷入局部最优**。

### 具有不同级配颗粒材料的自由落体到平衡状态求解
然后我们研究了具有不通颗粒大小的颗粒集合体在该模拟方法下的加载结果：

| ![space-1.jpg](./deepRitz_particle/img/dense_PSD/step_0.png) | ![space-1.jpg](./deepRitz_particle/img/dense_PSD/step_1000.png) |
|:--:| :--:| 
| **Initial state** |**Optimized 1000 steps**|
| ![space-1.jpg](./deepRitz_particle/img/dense_PSD/step_2000.png) | ![space-1.jpg](./deepRitz_particle/img/dense_PSD/step_3000.png) |
| **Optimized 2000 steps** |**Optimized 3000 steps**|
| ![space-1.jpg](./deepRitz_particle/img/dense_PSD/step_4000.png) | ![space-1.jpg](./deepRitz_particle/img/dense_PSD/step_5000.png) |
| **Optimized 4000 steps** |**final state (unstable)**|

### 颗粒材料伺服固结模拟
此后我们尝试计算颗粒材料在自由落地运动中对边界的压力，计算结果如下

| ![space-1.jpg](./deepRitz_particle/img/dense_PSD_servo/history.png) | ![space-1.jpg](./deepRitz_particle/img/dense_PSD_servo/force.png) |
|:--:| :--:| 
| **Initial state** |**Optimized 1000 steps**|
| ![space-1.jpg](./deepRitz_particle/img/dense_PSD_servo/step_1000.png) | ![space-1.jpg](./deepRitz_particle/img/dense_PSD_servo/step_10000.png) |
| **Optimized 2000 steps** |**Optimized 3000 steps**|

在该计算中我们统计了具有不平衡力的颗粒，统计所有具有不平衡力的颗粒，分别累加其在X和Y方向的力，因此得到其作用在边界上的力。

### 颗粒材料简单剪切模拟
pending...

# Fenics solver tutorial 
在这里学习Fenics的求解偏微分方程
## 泊松方程

$ \nabla^{2} u = f \ \ $
所以

