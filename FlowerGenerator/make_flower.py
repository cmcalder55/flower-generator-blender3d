import sys, random, math
from os import system
from mathutils import Euler, Vector
from bpy import data, ops, context
import bmesh
import numpy as np

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
    obj = data.objects['base_cone']
    obj.color = (.156,.384,.062,1)
    mat = data.materials.new('green')
    mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0,0,1,1)
    obj.data.materials.append(mat)
    
    obj = data.objects['base_ring']
    obj.color = (0.384,0.011,0.1,1)
    mat = data.materials.new('maroon')
    mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0,0,1,1)
    obj.data.materials.append(mat)
    
    obj = data.objects['base_cap']
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

def create_lens_shape():
    # Ensure we are in Object Mode and deselect all objects
    ops.object.mode_set(mode='OBJECT')
    ops.object.select_all(action='DESELECT')
    
    # Add a UV Sphere
    ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
    sphere = context.object
    sphere.name = 'base_cap'
    
    # Switch to Edit Mode
    ops.object.mode_set(mode='EDIT')
    # Get the bmesh representation
    bm = bmesh.from_edit_mesh(sphere.data)
    
    # Define the plane for bisecting (cutting through the z-axis)
    plane_co = (0, 0, 0.7)  # Plane point (origin)
    plane_no = (0, 0, -1)  # Plane normal (z-axis)
    
    # Bisect the sphere, cutting it into two halves
    bmesh.ops.bisect_plane(bm, geom=bm.faces[:] + bm.edges[:] + bm.verts[:], 
                           plane_co=plane_co, plane_no=plane_no, clear_outer=True)
    
    # Update the mesh with the bisection
    bmesh.update_edit_mesh(sphere.data)
    
    # Switch back to Object Mode
    ops.object.mode_set(mode='OBJECT')
    
    # (Optional) Add a Subdivision Surface modifier to smooth the lens
    sphere.modifiers.new(name='Subsurf', type='SUBSURF')
    sphere.modifiers['Subsurf'].levels = 2  # Adjust this for smoother appearance
    
    # Apply the modifier (optional, depending on whether you want to keep the modifier adjustable)
    ops.object.modifier_apply(modifier='Subsurf')
    ops.transform.resize(value=(0.85, 0.85, 1.0))
    ops.transform.translate(value=(0, 0, -0.7)) 

def generate_torus_points(num_points=10):
    """
    Generate points on the surface of a torus in a normal distribution.

    Parameters:
    - R: Major radius of the torus.
    - r: Minor radius of the torus.
    - num_points: Number of points to generate.

    Returns:
    - A list of (x, y, z) tuples representing points on the torus.
    """
    r = 1.2  # Major radius
    R = 0.7  # Minor radius
    # Mean values for theta and phi
    mean_theta = np.pi
    mean_phi = np.pi

    # Standard deviation (spread or “width”) of the distribution.
    # Adjust these values to change the distribution characteristics.
    std_theta = np.pi
    std_phi = np.pi

    z_base = 0.9 # Base Z level for variation
    z_variation = 0.25  # Allowable variation from the base Z level
    
    # Generate theta and phi values from a normal distribution
    theta = np.random.normal(mean_theta, std_theta, num_points)
    phi = np.random.normal(mean_phi, std_phi, num_points)

    # Ensure theta and phi are within the valid range [0, 2pi]
    theta = np.mod(theta, 2 * np.pi)
    phi = np.mod(phi, 2 * np.pi)

    # Calculate the x, y, and z coordinates
    x = (R + r * np.cos(theta)) * np.cos(phi) + 0.6
    y = (R + r * np.cos(theta)) * np.sin(phi) + 1
    z = [z_base + np.random.uniform(-z_variation, z_variation) for _ in range(num_points)]  # Random Z level
    
    print(z)
    # Return the points as a list of tuples
    return list(zip(x, y, z))

def generate_stamen(n=10):
    '''Generate stamens from the middle of the flower.'''

    # Create a new collection for stamens if it doesn't exist
    col = init_collection("stamen")
    names = [f"stamen_{idx + 1}" for idx in range(n)]

    rot = [
        (-90, 135, 70),
        (-90, 135, 70),
        (-90, 135, 75),
        (-90, 135, 75),
        (-90, 135, 60),
        (-90, 135, 60),
        (-90, 135, 150),
        (-90, 135, 150),
        (-90, 135, -30),
        (-90, 135, -30),
    ]
    rot = [(math.radians(x), math.radians(y), math.radians(z)) for x, y, z in rot]
    
    trans = generate_torus_points()
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

    col = init_collection("stamen base")

    ops.object.mode_set(mode='OBJECT')
    # add cone for receptacle
    ops.mesh.primitive_cone_add(rotation=(0,math.pi,0))
    cone = context.active_object
    cone.location = (0,0,-0.7)
    cone.name = "base_cone"

    # scale
    cone_scale = 0.629
    base_scale = (cone_scale, cone_scale, cone_scale)
    ops.transform.resize(value=base_scale)

    # add torus for top of the stamen base and scale
    ops.mesh.primitive_torus_add(major_radius=0.93,minor_radius=.12)
    torus = context.active_object
    torus.location = (0,0,0)
    ops.transform.resize(value=base_scale)
    torus.name = 'base_ring'

    create_lens_shape()    
    
    link_to_col(col, ["base_cap", "base_ring", "base_cone"])
    generate_stamen()

def generate_petals(n=5):
    '''Generate five cherry blossom petals.'''

    # reset the scene and init the collection
    reset_scene()
    col = init_collection("petal")
    names = [f"petal_{idx + 1}" for idx in range(n)]

    # rotations
    rot = [
        (0, 5, -20),
        (0, 5, 50),
        (0, 5, 270),
        (0, 5, 195),
        (0, 5, 125)
    ]
    rot = [(math.radians(x), math.radians(y), math.radians(z)) for x, y, z in rot]
    # translations
    trans = [
        (0.2, -2.9, 0.6),
        (2.8, -0.8, 0.6),
        (-2.6, -1.0, 0.6),    
        (-1.8, 2.3, 0.6),
        (1.6, 2.5, 0.6)
        ]

    # Create the initial petal using a bezier circle
    ops.curve.primitive_bezier_circle_add()

    for idx, translation in enumerate(trans):
        
        name = names[idx]
        if idx != 0:
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
        petal.rotation_euler = Euler(rot[idx], "XYZ")
        petal.location = translation

    # link to collection / unlink from scene
    link_to_col(col, names)

    # generate base collection
    generate_stamen_base()



if __name__ == '__main__':
    generate_petals()