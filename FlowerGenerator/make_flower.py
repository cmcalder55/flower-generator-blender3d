
from os import system
import math
from mathutils import Euler
from bpy import data, ops, context
  
def init_collection(name):

    if name not in data.collections:
        col = data.collections.new(name)
        context.scene.collection.children.link(col)
    else:
        col = data.collections[name]

    return col

def generate_stamen(n=10):
    '''Generate stamens from the middle of the flower.'''

    # Create a new collection for stamens if it doesn't exist
    col = init_collection("stamen")

    # generate nurbs curve and bezier circle
    ops.curve.primitive_nurbs_curve_add()
    stamen_curve = context.active_object.data.name
    ops.curve.primitive_bezier_circle_add(radius=0.02)

    # apply circle as cross section for cylinder
    x_section = context.active_object
    curve_data = data.curves[stamen_curve]
    curve_data.bevel_mode = 'OBJECT'
    curve_data.bevel_object = x_section

    # convert curve to mesh
    obj1 = data.objects['NurbsCurve']
    obj1.select_set(True)    
    context.view_layer.objects.active = obj1
    ops.object.convert(target='MESH')

    # generate stamen tip and join with beveled curve
    ops.mesh.primitive_uv_sphere_add(radius=0.05)
    ops.transform.translate(value=(-0.75,0.83,0.0))
    rot_tip = (-23.5, 91, 1.4)
    rot_tip = list(map(lambda x: math.radians(x), rot_tip))
    stamen1 = data.objects['Sphere.001']
    stamen1.rotation_euler = Euler((rot_tip), 'XYZ')
    
    obj1.select_set(True)
    # consider "bridge edge"
    ops.object.join()
    ops.transform.resize(value=(2.0, 2.0, 2.0))
    
    rot = [
        (-59, 186, -2.01),
        (-52.6, 180, 33.3),
        (-59, 186, 54.2),
        (-33.3, 186, 103),
        (-57.7, 178, -84.2),
        (126, 0, 62.6),
        (124, -6, -6.81),
        (-58, 186, -47.7),
        (122, 11.9, -7.91),
        (-59, 186, 89.8)
    ]
    trans = [
        (0.04, -1.94, 1.81),
        (0.9, -1.45, 2.04),
        (1.63, -0.84, 1.81),
        (0.45, 0.52, 2.27),         # center stamen
        (-1.88, 0.06, 1.91),
        (-1.52, 1.08, 1.76),
        (-0.01, 2.02, 1.88),
        (-1.27, -1.41, 1.81),
        (0.94, 1.92, 1.73),
        (2.02, 0.3, 1.81)
    ]

    stamen1.name = 'stamen_1'
    rot_new = list(map(lambda x: math.radians(x), rot[0]))
    stamen1.rotation_euler = Euler((rot_new), 'XYZ')
    stamen1.location.xyz = trans[0]
    ops.object.move_to_collection(collection_index = 3)

    for i in range(1, n):
        # duplicate first petal
        ops.object.duplicate()
        new_stamen = context.active_object
        new_stamen.name = f'stamen_{i + 1}'

        rot_new = list(map(lambda x: math.radians(x), rot[i]))
        new_stamen.rotation_euler = Euler((rot_new), 'XYZ')
        new_stamen.location.xyz = trans[i]

        # col.objects.link(new_stamen)

    add_color()

def add_color():
    '''Generate sepal; leaves on the stem on underside of the petals.'''

    ## PETALS ##
    petal_color = (0.857,0.594,1,1)
    petal_material = "pink"
    
    for i in range(1,5):
        id = f"petal_{i}"
        obj = data.objects[id]
        obj.color = petal_color
        mat = data.materials.new(petal_material)
        mat.use_nodes = True
        mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0,0,1,1)
        obj.data.materials.append(mat)     
    
    ## STAMEN BASE ##
    obj = data.objects['Cone']
    obj.color = (.156,.384,.062,1)
    mat = data.materials.new('green')
    mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0,0,1,1)
    obj.data.materials.append(mat)
    
    obj = data.objects['Sphere']
    obj.color = (0.384,0.011,0.1,1)
    mat = data.materials.new('maroon')
    mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0,0,1,1)
    obj.data.materials.append(mat)
    
    obj = data.objects['basecap']
    obj.color = (0.384,0.011,0.1,1)
    mat = data.materials.new('maroon')
    mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0,0,1,1)
    obj.data.materials.append(mat)

    ## STAMEN ##
    stamen_color = (0.814, 0.396, 0.536, 1)
    stamen_material = "pink-white"

    for i in range(1, 10):
        obj = data.objects[f'stamen_{i}']
        obj.color = stamen_color
        mat = data.materials.new(stamen_material)
        mat.use_nodes = True
        mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0,0,1,1)
        obj.data.materials.append(mat)

def generate_stamen_base():
    '''Generate base to connect stamen to the stem.'''
    ops.object.mode_set(mode='OBJECT')
    # add cone for receptacle
    ops.mesh.primitive_cone_add(rotation=(0,math.pi,0))
    # scale and rotate
    # ops.transform.rotate(value = math.radians(180), orient_axis = 'X')
    cone_scale = 0.629
    base_scale = (cone_scale, cone_scale, cone_scale)
    ops.transform.resize(value=base_scale)
    # translate to align with petals
    cone_trans = (0.02, 0.09, -1.22)
    ops.transform.translate(value=cone_trans) 
    # add torus for top of the stamen base and scale
    ops.mesh.primitive_torus_add(major_radius=0.93,minor_radius=.12)
    # torus_scale = 0.918
    # top_scale = (torus_scale, torus_scale, torus_scale)
    top_scale = base_scale
    ops.transform.resize(value=top_scale)
    torus_trans = (0.02, 0.09, -0.55)
    ops.transform.translate(value=torus_trans)
    context.active_object.name = 'basecap'
    ops.mesh.primitive_uv_sphere_add(location=(0.02,0.09,-1.4))
    # points to keep 
    points = [0, 1, 2]
    keep = []
    ob = points

    for i in range(32):
        if i == 0:
            keep.extend(points)
        else:
            if i == 1:
                extend = 10
            elif i == 22:
                extend = 16
            else: 
                extend = 15
            ob = list(map(lambda x: x+extend, ob))
            keep.extend(ob)
    keep.append(325)

    obj = context.active_object
    ops.object.mode_set(mode='EDIT')
    ops.mesh.select_mode(type='VERT')
    ops.mesh.select_all(action='DESELECT')
    ops.object.mode_set(mode='OBJECT')
    
    for i in range(482):
        if i not in keep:
            obj.data.vertices[i].select = True

    ops.object.mode_set(mode='EDIT')
    ops.mesh.dissolve_verts()
    
    name = 'stamen base'
    col = data.collections.new(name)
    context.scene.collection.children.link(col)
    
    generate_stamen()
    # ops.object.mode_set(mode='EDIT')

def reset_scene():
    ''' Print names of objects and scenes already present in 
    workspace and delete them. '''

    # clear interpreter console
    clear = lambda: system('cls')
    clear() 

    # select all objects currently in the scene and delete
    ops.object.select_all(action='SELECT')
    ops.object.delete(use_global=False)
    print(' Objects deleted.')

    # print list of all scene names
    print(' Scene collection: ',data.scenes.keys(),'\n')

    for col in data.collections:
        print('Collection: ',col.name)
        for o in col.objects:
            print('Object: ',o.name)
    print('')

    # check if petal collection exists, add and link to scene if needed
    name = 'petal'
    col = data.collections.new(name)
    context.scene.collection.children.link(col)

def generate_petals():
    '''Generate five cherry blossom petals.'''

    reset_scene()
    
    rot_init = 25
    rot = 70
    loc_init = (0.0, -2.5, 0.0)

    ## TEMPLATE PETAL ##
    # Create the petal using a bezier circle and enter edit mode
    ops.curve.primitive_bezier_circle_add()
    base_petal = context.active_object
    base_petal.name = "petal_1"
    ops.object.mode_set(mode='EDIT')

    # Randomize the vertices of the bezier circle
    ops.transform.vertex_random(offset=1.0, uniform=0.1, normal=0.0, seed=0)
    # Scale the curve while in edit mode and convert to a mesh
    ops.transform.resize(value=(2.0, 1.5, 2.5))
    ops.object.mode_set(mode='OBJECT')
    ops.object.convert(target='MESH')
    # go to edit mode and create face from mesh vertices
    ops.object.mode_set(mode='EDIT')
    ops.mesh.select_all(action='SELECT')
    ops.mesh.edge_face_add()
    # back to object mode and translate so end of flower will meet the center
    ops.object.mode_set(mode='OBJECT')

    # initial adjustments of first petal
    base_petal.rotation_euler.z -= math.radians(rot_init)
    base_petal.location = loc_init

    # connect vertex pairs to shear sides of petals
    ops.object.mode_set(mode='EDIT')
    ops.mesh.select_all(action='DESELECT')
    
    ops.object.mode_set(mode='OBJECT')
    obj = context.active_object
    for i in range(2,11):
        obj.data.vertices[i].select = True

    # connect vertices and dissolve to shape petal edge
    ops.object.mode_set(mode='EDIT')
    ops.mesh.vert_connect()
    ops.mesh.dissolve_verts()
    
    # repeat for other side
    ops.object.mode_set(mode='OBJECT')
    for i in range(6,14):
        obj.data.vertices[i].select = True
    
    ops.object.mode_set(mode='EDIT')
    ops.mesh.vert_connect()
    ops.mesh.dissolve_verts()

    ops.object.mode_set(mode='OBJECT')

    # Rotations and translations for other four petals 
    trans_petal = [
        (2.55, 1.8, 0.0), 
        (-0.83, 3.18, -0.04),                       # 0.007, 0.025, -0.03
        (-3.25, -0.17, 0.0), 
        (-0.95, -2.95, 0.0) 
        ]

    loc_current = loc_init
    for idx, translation in enumerate(trans_petal):
        # duplicate first petal
        ops.object.duplicate_move()
        new_petal = context.active_object
        new_petal.name = f'petal_{idx + 2}'

        # apply rot and trans
        new_petal.rotation_euler.z += math.radians(rot)
        loc_current = tuple(a + b for a, b in zip(loc_current, translation))
        new_petal.location = loc_current

    # move petals into 'petal' collection and call next part generation
    ops.object.select_all(action = 'SELECT')
    ops.object.move_to_collection(collection_index = 1)

    generate_stamen_base()

if __name__ == '__main__':
    generate_petals()
