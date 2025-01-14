from stlib3.scene import MainHeader, ContactHeader
from stlib3.physics.rigid import Floor


def createScene(rootNode):
    # A default gravity force is implemented on Sofa. Here we reset it, choosing millimeters as the length unit for the scene.
    MainHeader(rootNode, gravity=[0.0, -981.0, 0.0])
    rootNode.VisualStyle.displayFlags = 'showCollisionModels'

    # Collision built-in function (already used in Step 1)
    ContactHeader(rootNode, alarmDistance=10, contactDistance=5)

    cube = rootNode.addChild("Cube")

    # Mechanical model

    totalMass = 1.0
    volume = 1.0
    inertiaMatrix = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]

    cube.addObject('MechanicalObject', name="DOF", template="Rigid3", translation=[0.0, 0.0, 0.0],
                   rotation=[0.0, 0.0, 0.0])
    cube.addObject('UniformMass', name="vertexMass", vertexMass=[totalMass, volume, inertiaMatrix[:]])

    # Material behaviour when submitted to constraints
    cube.addObject('UncoupledConstraintCorrection')

    # Time integration and solver

    cube.addObject('EulerImplicitSolver', name='odesolver')
    cube.addObject('CGLinearSolver', name='Solver')

    # Visual Object of the Cube

    visual = cube.addChild("CubeVisual")
    # Graphic model based on a mesh
    visual.addObject('MeshObjLoader', name="loader", filename="mesh/smCube27.obj", triangulate=True)
    visual.addObject('OglModel', name="Visual", src="@loader", color=[0.1, 0.0, 1.0], scale=20.0)
    # Building a correspondence between the mechanical and the graphical representation
    visual.addObject('RigidMapping')

    # Collision Object for the Cube

    collision = cube.addChild("CubeCollisionModel")
    collision.addObject('MeshObjLoader', name="loader", filename="mesh/smCube27.obj", triangulate=True, scale=20.0)

    collision.addObject('MeshTopology', src="@loader")
    collision.addObject('MechanicalObject')

    collision.addObject('TriangleCollisionModel')
    collision.addObject('LineCollisionModel')
    collision.addObject('PointCollisionModel')

    collision.addObject('RigidMapping')

    # Adding the Floor for more fun ;)
    floor = Floor(rootNode,
                  name="Floor",
                  translation=[0.0, -300.0, 0.0],
                  uniformScale=5.0,
                  isAStaticObject=True)

    return rootNode
