# -*- coding: utf-8 -*-
"""
Step 8: Here we are showing how to setup the inverse control
"""
import Sofa
from tutorial import *
from tripod import Tripod
from tripodcontroller import SerialPortController, SerialPortBridgeGeneric, InverseController, DirectController
from maze import Maze
from mazecontroller import MazeController


def EffectorGoal(node, position):
    goal = node.addChild('Goal')
    goal.addObject('EulerImplicitSolver', firstOrder=True)
    goal.addObject('CGLinearSolver', iterations=100, threshold=1e-5, tolerance=1e-5)
    goal.addObject('MechanicalObject', name='goalMO', template='Rigid3', position=position+[0., 0., 0., 1.], showObject=True, showObjectScale=10)
    goal.addObject('RestShapeSpringsForceField', points=0, angularStiffness=1e5, stiffness=1e5)

    spheres = goal.addChild('Spheres')
    spheres.addObject('MechanicalObject', name='mo', position=[[0, 0, 0],  [10, 0, 0],   [0, 10, 0],   [0, 0, 10]])
    spheres.addObject('RigidMapping')

    goal.addObject('UncoupledConstraintCorrection')
    return goal


class GoalController(Sofa.Core.Controller):
    """This controller moves the goal position when the inverse control is activated
    """

    def __init__(self, *args, **kwargs):
        Sofa.Core.Controller.__init__(self, *args, **kwargs)
        self.name = "GoalController"
        self.activated = False
        self.time = 0
        self.dy = 0.1
        goalNode = args[1]
        self.mo = goalNode.goalMO
        self.dt = goalNode.getRoot().dt.value

    def onKeyPressed(self, key):
        if key == Key.I:
            self.activated = True

    def onAnimateBeginEvent(self, e):

        if self.activated:
            self.time = self.time+self.dt

        if self.time >= 1:
            self.time = 0;
            self.dy = -self.dy

        pos = [self.mo.position[0][0], self.mo.position[0][1], self.mo.position[0][2]]
        pos[1] += self.dy
        self.mo.position = [[pos[0], pos[1], pos[2], 0, 0, 0, 1]]


def addInverseComponents(arms, freecenter, goalNode, use_orientation):
    actuators=[]
    for arm in arms:
        actuator = arm.ServoMotor.Articulation.addChild('actuator')
        actuators.append(actuator)
        actuator.activated = False
        actuator.addObject('JointActuator', name='JointActuator', template='Vec1',
                                                index=0, applyForce=True,
                                                minAngle=-1.5, maxAngle=1.5, maxAngleVariation=0.1)

    effector = freecenter.addChild("Effector")
    effector.activated = False
    actuators.append(effector)
    if goalNode is None:
        effector.addObject('PositionEffector', name='effector', template='Rigid3',
                               useDirections=[1, 1, 1, 0, 0, 0],
                               indices=0, effectorGoal=[10, 40, 0], limitShiftToTarget=True,
                               maxShiftToTarget=5)
    elif use_orientation:
        effector.addObject('PositionEffector', name='effector', template='Rigid3',
                               useDirections=[0, 1, 0, 1, 0, 1],
                               indices=0, effectorGoal=goalNode.goalMO.getLinkPath() + '.position',
                               limitShiftToTarget=True, maxShiftToTarget=5)
    else:
        effector.addObject('PositionEffector', name='effector', template='Rigid3',
                               useDirections=[1, 1, 1, 0, 0, 0],
                               indices=0, effectorGoal=goalNode.goalMO.getLinkPath() + '.position',
                               limitShiftToTarget=True, maxShiftToTarget=5)
    return actuators


def createScene(rootNode):
    from stlib3.scene import Scene
    scene = Scene(rootNode, gravity=[0., -9810., 0.], dt=0.01, iterative=False, plugins=["SofaSparseSolver", "SofaOpenglVisual", "SofaSimpleFem", "SoftRobots","SoftRobots.Inverse", 'SofaBoundaryCondition', 'SofaDeformable', 'SofaEngine', 'SofaGeneralRigid', 'SofaMiscMapping', 'SofaRigid', 'SofaGraphComponent', 'SofaGeneralAnimationLoop', 'SofaGeneralEngine'])
    scene.addObject('AttachBodyButtonSetting', stiffness=10)  # Set mouse spring stiffness

    # Choose here to control position or orientation of end-effector
    orientation = True

    if orientation:
        # inverse in orientation
        goalNode = EffectorGoal(rootNode, [0, 30, 50])
    else:
        # inverse in position
        goalNode = EffectorGoal(rootNode, [0, 40, 0])

    goalNode.addObject(MazeController(goalNode,False))

    # Adding contact handling
    scene.addMainHeader()
    scene.addObject('DefaultVisualManagerLoop')

    # Inverse Solver
    scene.addObject('FreeMotionAnimationLoop')
    scene.addObject('QPInverseProblemSolver', name='QP', printLog=False)
    scene.Simulation.addObject('GenericConstraintCorrection')

    scene.VisualStyle.displayFlags = "showBehavior showCollisionModels"

    tripod = scene.Modelling.addChild(Tripod())
    actuators = addInverseComponents(tripod.actuatedarms, tripod.RigidifiedStructure.FreeCenter, goalNode, orientation)
    maze = tripod.RigidifiedStructure.FreeCenter.addChild(Maze())
    maze.addObject("RigidMapping", index=0)

    # Serial port bridge
    serial = SerialPortBridgeGeneric(rootNode)

    # The real robot receives data from the 3 actuators
    # serialportctrl = scene.addObject(SerialPortController(scene, inputs=tripod.actuatedarms, serialport=serial))

    scene.Simulation.addChild(tripod.RigidifiedStructure)
    invCtr = scene.addObject(InverseController(scene, goalNode, actuators, tripod.ActuatedArm0.ServoMotor.Articulation.ServoWheel.RigidParts,
                                                tripod, serial,
                                                [tripod.ActuatedArm0, tripod.ActuatedArm1, tripod.ActuatedArm2]))

    # The regular controller that is being used for the last 2 steps but with small additions
    scene.addObject(DirectController(scene, tripod.actuatedarms, invCtr))

    motors = scene.Simulation.addChild("Motors")
    for i in range(3):
        motors.addChild(tripod.getChild('ActuatedArm'+str(i)))

    # Temporary additions to have the system correctly built in SOFA
    # Will no longer be required in SOFA v22.06
    scene.Simulation.addObject('MechanicalMatrixMapper',
                                 name="mmmFreeCenter",
                                 template='Vec3,Rigid3',
                                 object1="@RigidifiedStructure/DeformableParts/dofs",
                                 object2="@RigidifiedStructure/FreeCenter/dofs",
                                 nodeToParse="@RigidifiedStructure/DeformableParts/ElasticMaterialObject")

    for i in range(3):
        scene.Simulation.addObject('MechanicalMatrixMapper',
                                   name="mmmDeformableAndArm" + str(i),
                                   template='Vec1,Vec3',
                                   object1="@Modelling/Tripod/ActuatedArm" + str(i) + "/ServoMotor/Articulation/dofs",
                                   object2="@Simulation/RigidifiedStructure/DeformableParts/dofs",
                                   skipJ2tKJ2=True,
                                   nodeToParse="@Simulation/RigidifiedStructure/DeformableParts/ElasticMaterialObject")

