# -*- coding: utf-8 -*-
"""
Step 4:
4-1 Adding the ActuatedArm prefab.
    This prefab is defining the servomotor, the servo-arm and the constraint that attaches the end of the arm to the deformable object.
4-2 Rigidify extremity of deformable part to be able to fix it to the actuated arms
4-3 Fix arms to deformable part
"""
from tutorial import *
# Let's define a Tripod prefab in tripod.py, that we can later call in the createScene function
from tripod import Tripod


def createScene(rootNode):
    from stlib3.scene import Scene

    scene = Scene(rootNode, gravity=[0.0, -9810, 0.0], iterative=False, plugins=['SofaSparseSolver', 'SofaGeneralAnimationLoop', 'SofaOpenglVisual', 'SofaSimpleFem', 'SofaDeformable', 'SofaGeneralRigid', 'SofaMiscMapping', 'SofaRigid', 'SofaGraphComponent', 'SofaBoundaryCondition', 'SofaGeneralEngine'])
    scene.addMainHeader()
    scene.addObject('AttachBodyButtonSetting', stiffness=10)  # Set mouse spring stiffness
    scene.addObject('DefaultVisualManagerLoop')
    scene.addObject('FreeMotionAnimationLoop')
    scene.addObject('GenericConstraintSolver', maxIterations=50, tolerance=1e-5)
    scene.Simulation.addObject('GenericConstraintCorrection')
    rootNode.dt = 0.01

    scene.VisualStyle.displayFlags = "showBehavior"

    tripod = Tripod(scene.Modelling)
    tripod.BoxROI0.drawBoxes = True
    tripod.BoxROI1.drawBoxes = True
    tripod.BoxROI2.drawBoxes = True

    scene.Simulation.addChild(tripod.RigidifiedStructure)
    scene.Simulation.addObject('MechanicalMatrixMapper',
                                 name="mmmFreeCenter",
                                 template='Vec3,Rigid3',
                                 object1="@RigidifiedStructure/DeformableParts/dofs",
                                 object2="@RigidifiedStructure/FreeCenter/dofs",
                                 nodeToParse="@RigidifiedStructure/DeformableParts/ElasticMaterialObject")

    motors = scene.Simulation.addChild("Motors")
    for i in range(3):
        motors.addChild(tripod.getChild('ActuatedArm'+str(i)))
        scene.Simulation.addObject('MechanicalMatrixMapper',
                                     name="mmm"+str(i),
                                     template='Vec1,Vec3',
                                     object1="@Simulation/Motors/ActuatedArm"+str(i)+"/ServoMotor/Articulation/dofs",
                                     object2="@Simulation/RigidifiedStructure/DeformableParts/dofs",
                                     skipJ2tKJ2=True,
                                     nodeToParse="@Simulation/RigidifiedStructure/DeformableParts/ElasticMaterialObject")
