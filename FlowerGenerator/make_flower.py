import sys, random, math
from os import system
from mathutils import Euler, Vector
from bpy import data, ops, context

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

def init_collection(name):

    if name not in data.collections:
        col = data.collections.new(name)
        context.scene.collection.children.link(col)
    else:
        col = data.collections[name]

    return col

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

def link_to_col(col, names):
    for name in names:
        obj = data.objects[name]
        # link obj to collection
        col.objects.link(obj)
        # unlink from scene to prevent duplicating if re-run
        if name in context.scene.collection.objects:
            context.scene.collection.objects.unlink(obj)

def create_stamen_curve():

    # Create a new NURBS curve data block
    nurbs_data = data.curves.new("NurbsCurve", type='CURVE')
    nurbs_data.dimensions = '3D'

    # Add a new NURBS curve
    nurbs_curve = nurbs_data.splines.new(type='NURBS')
    
    # Add points to the curve. Each point is a list of (x, y, z, w) where w is the weight.
    coords = [
        (-1.5, 0.0, 0.0, 1.0),
        (-1.0, 1.0, 0.0, 1.0),
        (1.0, 1.0, 0.0, 1.0),
        (1.5, 0.0, 0.0, 1.0),
    ]
    # For example, adding a simple curve with two points:
    points = nurbs_curve.points
    points.add(len(coords))  # Adding one point so we have two points (one is added by default)
    
    # Set the coordinates and weights of the points
    for i, coord in enumerate(coords):
        points[i].co = coord
    
    # Enable the endpoints to create a smoother curve
    nurbs_curve.use_endpoint_u = True
    nurbs_curve.use_endpoint_v = True

    # Create an object that will use the curve data
    curve_obj = data.objects.new("NurbsCurve", nurbs_data)
    context.collection.objects.link(curve_obj)    

    # Create a Bezier circle to be used as a bevel object
    bezier_data = data.curves.new(name="BezierCircle", type='CURVE')
    bezier_data.dimensions = '2D'
    bezier_circle = bezier_data.splines.new(type='BEZIER')
    bezier_circle.bezier_points.add(3)  # Adding points for a total of 4

    # Setup bezier points to form a circle
    r = 0.02  # Radius
    circle_coords = [(r, 0, 0), (0, r, 0), (-r, 0, 0), (0, -r, 0)]
    handles = [
        (r / 2, r / 2), 
        (-r / 2, r / 2), 
        (-r / 2, -r / 2), 
        (r / 2, -r / 2)]
    for i, bp in enumerate(bezier_circle.bezier_points):
        bp.co = Vector((circle_coords[i][0], circle_coords[i][1], 0))
        bp.handle_right_type = bp.handle_left_type = 'AUTO'
        # Optionally adjust handles for more accurate circle approximation
        bp.handle_left = bp.co + Vector((handles[i][0], handles[i][1], 0))
        bp.handle_right = bp.co - Vector((handles[i][0], handles[i][1], 0))
    
    bezier_obj = data.objects.new("BezierCircle", bezier_data)
    context.collection.objects.link(bezier_obj)

    # Set the Bezier circle as the bevel object for the curve
    nurbs_data.bevel_mode = "OBJECT"
    nurbs_data.bevel_object = bezier_obj
    nurbs_data.use_fill_caps = True
    
    # Convert the curve to mesh using ops
    context.view_layer.objects.active = curve_obj
    ops.object.select_all(action='DESELECT')
    curve_obj.select_set(True)
    ops.object.convert(target='MESH')

    sphere = create_stamen_tip()
    curve_obj.select_set(True)
    sphere.select_set(True)
    context.view_layer.objects.active = curve_obj

    ops.object.join()

    data.objects.remove(bezier_obj)

    # Return the created NURBS curve object
    return context.active_object

def create_stamen_tip():

    scale = 2.0

    ops.mesh.primitive_uv_sphere_add(
        radius=0.05, location=(-1.5, 0.0, 0.0)
        )
    sphere = context.active_object
    rot = (math.radians(-23.5), math.radians(89), math.radians(1.4))
    sphere.rotation_euler = Euler((rot), 'XYZ')
    ops.transform.resize(value=(scale, scale, scale))

    sphere.select_set(True)

    return sphere

def generate_stamen_like_points(num_points=10):
    """
    Generate a set of points with a distribution similar to a stamen arrangement.

    Parameters:
    - num_points: The number of points to generate.

    Returns:
    A list of tuples, each representing the (x, y, z) coordinates of a point.
    """
    points = []
    center = (0.0, 0.0)  # Approximated center from the example
    z_base = 0.5 # Base Z level for variation
    z_variation = 0.3  # Allowable variation from the base Z level

    for i in range(num_points):
        distance = random.uniform(0.5, 1.5)        
        if i > 5:
            distance = distance*-1
        #     distance = random.uniform(0, 0.5)
        # else:

        angle = 2 * math.pi * random.random()  # Random angle
        # distance = random.uniform(-1.5, 1.5)  # Random distance from the center, adjust as needed
        x = center[0] + distance * math.cos(angle)
        y = center[1] + distance * math.sin(angle)
        z = z_base + random.uniform(-z_variation, z_variation)  # Random Z level

        points.append((x, y, z))  # Round for simplicity

    return points

def generate_stamen(n=10):
    '''Generate stamens from the middle of the flower.'''

    # Create a new collection for stamens if it doesn't exist
    col = init_collection("stamen")
    names = [f"stamen_{idx + 1}" for idx in range(n)]

    rot = [
        (-90, 135, -30),
        (-90, 135, -30),
        (-90, 135, 0),
        (-90, 135, 0),
        (-90, 135, 30),
        (90, 45, 60),
        (90, 45, 60),
        (90, 45, -60),
        (90, 45, -60),
        (90, 45, 30),
    ]
    rot = [(math.radians(x), math.radians(y), math.radians(z)) for x, y, z in rot]
    
    trans = generate_stamen_like_points()
    print(trans)


    stamen_curve = create_stamen_curve()

    for i in range(n):
        if i == 0:
            stamen = stamen_curve
        else:
            stamen = stamen_curve.copy()
            stamen.data = stamen_curve.data.copy()

        stamen.name = f"stamen_{i + 1}"        

        stamen_curve.rotation_euler = Euler(rot[i], "XYZ")
        stamen_curve.location.xyz = trans[i]

    link_to_col(col, names)

    add_color()

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

def generate_petals(n=5):
    '''Generate five cherry blossom petals.'''

    # reset the scene and init the collection
    reset_scene()
    col = init_collection("petal")
    names = [f"petal_{idx + 1}" for idx in range(n)]

    # rotations
    rots = [-25, 70]
    # translations
    trans = [
        (0.0, -2.5, 0.0),
        (2.55, 1.8, 0.0), 
        (-0.83, 3.18, -0.04),     
        (-3.25, -0.17, 0.0), 
        (-0.95, -2.95, 0.0) 
        ]
    loc = (0.0, 0.0, 0.0)

    # Create the initial petal using a bezier circle
    ops.curve.primitive_bezier_circle_add()

    for idx, translation in enumerate(trans):
        
        name = names[idx]
        rot = rots[0]
        if idx != 0:
            rot = rots[1]
            ops.object.duplicate_move()

        petal = context.active_object

        ## TEMPLATE PETAL ##
        if idx == 0:
            # EDIT MODE
            ops.object.mode_set(mode='EDIT')
            # Randomize the vertices of the bezier circle
            ops.transform.vertex_random(offset=1.0, uniform=0.1, normal=0.0, seed=0)
            # Scale the curve
            ops.transform.resize(value=(2.0, 1.5, 2.5))

            # OBJECT MODE
            ops.object.mode_set(mode='OBJECT')
            # convert to mesh
            ops.object.convert(target='MESH')

            # EDIT MODE
            ops.object.mode_set(mode='EDIT')
            # create face from mesh vertices            
            ops.mesh.select_all(action='SELECT')
            ops.mesh.edge_face_add()
            ops.mesh.select_all(action='DESELECT')

            for petal_edge in [range(2,11), range(6,14)]:
                # OBJECT MODE
                ops.object.mode_set(mode='OBJECT')
                # select vertices
                obj = context.active_object
                for i in petal_edge:
                    obj.data.vertices[i].select = True

                # EDIT MODE
                ops.object.mode_set(mode='EDIT')
                # connect vertices and dissolve to shape petal edge            
                ops.mesh.vert_connect()
                ops.mesh.dissolve_verts()

            # OBJECT MODE
            ops.object.mode_set(mode='OBJECT')

        petal.name = name
        # apply rot and trans
        petal.rotation_euler.z += math.radians(rot)
        loc = tuple(a + b for a, b in zip(loc, translation))
        petal.location = loc

    # link to collection / unlink from scene
    link_to_col(col, names)

    # generate base collection
    generate_stamen_base()



if __name__ == '__main__':
    generate_petals()
