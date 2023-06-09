import taichi as ti
import taichi.math as tm
import Util
import matplotlib.image as mpimg

ti.init(arch=ti.gpu)

eulerSimParam = {
    'use_image': False,
    'load_image':'../img/test2.jpg',
    'shape': [512, 512],
    'dt': 1 / 60.,
    'iteration_step': 20,
    'mouse_radius':0.01,# [0.0,1.0] float
    'mouse_speed': 125.,
    'mouse_respondDistance':0.5, # for every frame, only half the trace of the mouse will influence water
    'curl_param':15,
    'GUI_type':'GUI' #fill 'GUI' or 'CGUI'
}

velocityField = ti.Vector.field(2, float, shape=(eulerSimParam['shape']))
_new_velocityField = ti.Vector.field(2, float, shape=(eulerSimParam['shape']))
colorField = ti.Vector.field(3, float, shape=(eulerSimParam['shape']))
_new_colorField = ti.Vector.field(3, float, shape=(eulerSimParam['shape']))

curlField = ti.field(float, shape=(eulerSimParam['shape']))

divField = ti.field(float, shape=(eulerSimParam['shape']))
pressField = ti.field(float, shape=(eulerSimParam['shape']))
_new_pressField = ti.field(float, shape=(eulerSimParam['shape']))

velocities_pair = Util.TexPair(velocityField, _new_velocityField)
pressure_pair = Util.TexPair(pressField, _new_pressField)
color_pair = Util.TexPair(colorField, _new_colorField)

# @ti.kernel
def init_field():
    # init pressure and velocity fieldfield
    pressField.fill(0)
    velocityField.fill(0)
    if eulerSimParam['use_image']:
        I = mpimg.imread(eulerSimParam['load_image'])
        init_field_withpic(I,colorField)
    else:
        Util.paint(eulerSimParam['shape'][0],eulerSimParam['shape'][1], colorField)

@ti.kernel
def init_field_withpic(scr: ti.types.ndarray(),field:ti.template()):
    # init color field
    for i, j in ti.ndrange(eulerSimParam['shape'][0], eulerSimParam['shape'][1]):
        field[i, j] = (
            scr[eulerSimParam['shape'][1] - j - 1, i, 0] / 255., scr[eulerSimParam['shape'][1] - j - 1, i, 1] / 255.,
            scr[eulerSimParam['shape'][1] - j - 1, i, 2] / 255.)
@ti.kernel
def advection(vf: ti.template(), qf: ti.template(), new_qf: ti.template()):
    for i, j in vf:
        coord_cur = ti.Vector([i, j]) + ti.Vector([0.5, 0.5])
        vel_cur = vf[i, j]
        coord_prev = coord_cur - vel_cur * eulerSimParam['dt']
        q_prev = Util.bilerp(qf, coord_prev[0], coord_prev[1], (eulerSimParam['shape']))
        new_qf[i, j] = q_prev

@ti.kernel
def curl(vf: ti.template(), cf: ti.template()):
    for i,j in vf:
        cf[i,j] = 0.5 * ((vf[i+1,j][1] - vf[i-1,j][1]) - (vf[i,j+1][0] - vf[i,j-1][0]))

@ti.kernel
def vorticity_projection(cf: ti.template(), vf: ti.template(), vf_new: ti.template()):
    for i, j in cf:
        gradcurl = ti.Vector([0.5 * (cf[i + 1, j] - cf[i - 1, j]),
                              0.5 * (cf[i, j + 1] - cf[i, j - 1]), 0])
        GradCurlLength = tm.length(gradcurl)
        if (GradCurlLength > 1e-5):
            force = eulerSimParam['curl_param'] * tm.cross(gradcurl / GradCurlLength, ti.Vector([0, 0, 1]))
            vf_new[i, j] = vf[i, j] + eulerSimParam['dt'] * force[:2]

@ti.kernel
def divergence(vf: ti.template(), divf: ti.template()):
    for i, j in vf:
        divf[i, j] = 0.5 * (vf[i + 1, j][0] - vf[i - 1, j][0] + vf[i, j + 1][1] - vf[i, j - 1][1])

@ti.kernel
def pressure_iteration(divf: ti.template(), pf: ti.template(), new_pf: ti.template()):
    for i, j in pf:
        new_pf[i, j] = (pf[i + 1, j] + pf[i - 1, j] + pf[i, j - 1] + pf[i, j + 1] - divf[i, j]) / 4

def pressure_solve(presspair: Util.TexPair, divf: ti.template()):
    for i in range(eulerSimParam['iteration_step']):
        pressure_iteration(divf, presspair.cur, presspair.nxt)
        presspair.swap()
        apply_p_bc(presspair.cur)

@ti.kernel
def pressure_projection(pf: ti.template(), vf: ti.template(), vf_new: ti.template()):
    for i, j in vf:
        vf_new[i, j] = vf[i, j] - ti.Vector([(p_with_boundary(pf, i + 1, j,eulerSimParam['shape']) - p_with_boundary(pf, i - 1, j, eulerSimParam['shape'])) / 2.0,
                                             (p_with_boundary(pf, i, j + 1,eulerSimParam['shape']) - p_with_boundary(pf, i, j - 1, eulerSimParam['shape'])) / 2.0])

# Boundry Condition
@ti.func
def vel_with_boundary(vf: ti.template(), i: int, j: int, shape) -> ti.f32:
    if (i <= 0) or (i >= shape[0] - 1) or (j >= shape[1] - 1) or ( j <= 0):
        vf[i, j] = ti.Vector([0.0, 0.0])
    return vf[i, j]

@ti.func
def p_with_boundary(pf: ti.template(), i: int, j: int, shape) -> ti.f32:
    if (i == j == 0) or (i == shape[0] - 1 and j == shape[1] - 1) or (i == 0 and j == shape[1] - 1) or (
            i == shape[0] - 1 and j == 0):
        pf[i, j] = 0.0
    elif i == 0:
        pf[0, j] = pf[1, j]
    elif j == 0:
        pf[i, 0] = pf[i, 1]
    elif i == shape[0] - 1:
        pf[shape[0] - 1, j] = pf[shape[0] - 2, j]
    elif j == shape[1] - 1:
        pf[i, shape[1] - 1] = pf[i, shape[1] - 2]
    return pf[i, j]

@ti.func
def c_with_boundary(cf: ti.template(), i: int, j: int, shape) -> ti.f32:
    if (i <= 0) or (i >= shape[0] - 1) or (j >= shape[1] - 1) or (j <= 0):
        cf[i, j] = 0.0
    return cf[i, j]

@ti.kernel
def apply_vel_bc(vf: ti.template()):
    for i, j in vf:
        vel_with_boundary(vf, i, j, eulerSimParam['shape'])

@ti.kernel
def apply_p_bc(pf: ti.template()):
    for i, j in pf:
        p_with_boundary(pf, i, j, eulerSimParam['shape'])

@ti.kernel
def apply_c_bc(cf: ti.template()):
    for i, j in cf:
        c_with_boundary(cf, i, j, eulerSimParam['shape'])

def mouse_interaction(prev_posx:int,prev_posy:int):
    mouse_x, mouse_y = window.get_cursor_pos()
    mousePos_x = int(mouse_x*eulerSimParam['shape'][0])
    mousePos_y = int(mouse_y*eulerSimParam['shape'][1])
    if prev_posx == 0 and prev_posy == 0:
        prev_posx = mousePos_x
        prev_posy = mousePos_y
    mouseRadius = eulerSimParam['mouse_radius'] * min(eulerSimParam['shape'][0],eulerSimParam['shape'][1])

    mouse_addspeed(mousePos_x,mousePos_y,prev_posx,prev_posy,mouseRadius,velocities_pair.cur,velocities_pair.nxt)
    velocities_pair.swap()
    prev_posx = mousePos_x
    prev_posy = mousePos_y
    return prev_posx,prev_posy

@ti.kernel
def mouse_addspeed(cur_posx:int,cur_posy:int,prev_posx:int,prev_posy:int,mouseRadius:float,vf:ti.template(),new_vf:ti.template()):
    for i,j in vf:
        vec1 = ti.Vector([cur_posx-prev_posx,cur_posy-prev_posy])
        vec2 = ti.Vector([i-prev_posx,j-prev_posy])
        dotans = tm.dot(vec1,vec2)
        distance = abs(tm.cross(vec1,vec2)) / (tm.length(vec1)+0.001)
        if dotans >= 0 and dotans <= eulerSimParam['mouse_respondDistance'] * tm.length(vec1) and distance <= mouseRadius:
            new_vf[i,j] = vf[i,j] + vec1 * eulerSimParam['mouse_speed']
        else:
            new_vf[i,j] = vf[i,j]

def advaction_step():
    advection(velocities_pair.cur, color_pair.cur, color_pair.nxt)
    advection(velocities_pair.cur, velocities_pair.cur, velocities_pair.nxt)
    color_pair.swap()
    velocities_pair.swap()
    apply_vel_bc(velocities_pair.cur)

def voricity_step():
    curl(velocities_pair.cur,curlField)
    apply_c_bc(curlField)
    vorticity_projection(curlField,velocities_pair.cur,velocities_pair.nxt)
    velocities_pair.swap()
    apply_vel_bc(velocities_pair.cur)

def pressure_step():
    divergence(velocities_pair.cur, divField)
    pressure_solve(pressure_pair, divField)
    pressure_projection(pressure_pair.cur, velocities_pair.cur, velocities_pair.nxt)
    velocities_pair.swap()
    apply_vel_bc(velocities_pair.cur)

# The Euler Solver starts!
init_field()
apply_vel_bc(velocities_pair.cur)

if eulerSimParam['GUI_type']=='GUI':
    window = ti.GUI("Euler 2D Simulation", res=(eulerSimParam['shape'][0], eulerSimParam['shape'][1]))
elif eulerSimParam['GUI_type']=='CGUI':
    window = ti.ui.Window("Euler 2D Simulation", res = (eulerSimParam['shape'][0], eulerSimParam['shape'][1]))
    canvas = window.get_canvas()

mouse_prevposx, mouse_prevposy = 0, 0
while window.running:
    # advection
    advaction_step()
    # curl
    voricity_step()
    # mouse interact with water
    mouse_prevposx, mouse_prevposy = mouse_interaction(mouse_prevposx, mouse_prevposy)
    # pressure iteration and projection
    pressure_step()

    if eulerSimParam['GUI_type'] == 'GUI':
        window.set_image(colorField)
    elif eulerSimParam['GUI_type'] == 'CGUI':
        canvas.set_image(colorField)
    window.show()
