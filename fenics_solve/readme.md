# Fenics 学习笔记
学习采用Fenics求解偏微分方程
```python
import fenics as fe
```

## 泊松方程

控制方程：
$$
-\nabla^2 u = f
$$
```python
u_function_space = fe.FunctionSpace(mesh, "Lagrange", Degree)
```

注意，泊松方程的解可以是一个标量，如果是标量则对应控制方程
$$ u_{j, ii} = f_j \ \ \mathrm{or} \ \ \nabla^{2} u_j = f_j $$
对应求解空间写作：
```python
u_function_space = fe.VectorFunctionSpace(mesh, "Lagrange", Degree)
```
也可以是一个向量.

上述中的`Degree`并不是维度`dim`，而是类似`order`的量，具体是什么我还没有弄清楚。。。

