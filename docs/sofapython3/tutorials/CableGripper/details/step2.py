# -*- coding: utf-8 -*-
from stlib3.physics.deformable import ElasticMaterialObject


def Finger(parentNode=None, Name="Finger",
           rotation=[0.0, 0.0, 0.0],
           translation=[0.0, 0.0, 0.0],
           fixingBox=[0.0, 0.0, 0.0], pullPointLocation=[0.0, 0.0, 0.0]):
    finger = parentNode.addChild("Finger")
    mobject = ElasticMaterialObject(finger, volumeMeshFileName="data/mesh/finger.vtk")
    finger.addChild(mobject)

    return None


def createScene(rootNode):
    # -*- coding: utf-8 -*-
    from stlib3.scene import MainHeader
    m = MainHeader(rootNode, plugins=["SoftRobots"])
    rootNode.VisualStyle.displayFlags = "showBehavior showCollisionModels"

    m.getObject("VisualStyle").displayFlags = 'showForceFields showBehaviorModels showInteractionForceFields'

    Finger(rootNode)

    return rootNode
