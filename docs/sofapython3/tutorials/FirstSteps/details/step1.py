import SofaRuntime
from stlib3.scene import MainHeader, ContactHeader
from stlib3.physics.rigid import Floor, Cube


def createScene(rootNode):
    """This is my first scene"""
    SofaRuntime.importPlugin('SofaRigid')
    SofaRuntime.importPlugin('SofaConstraint')

    rootNode.addObject("OglGrid", nbSubdiv=10, size=1000)

    MainHeader(rootNode, gravity=[0.0,-981.0,0.0])
    ContactHeader(rootNode, alarmDistance=15, contactDistance=10)
    rootNode.VisualStyle.displayFlags = "showCollisionModels"

    Floor(rootNode, translation=[0.0,-160.0,0.0],
          isAStaticObject=True)

    cube = Cube(rootNode, translation=[0.0,0.0,0.0],
                    uniformScale=20.0)

    cube.addObject('UncoupledConstraintCorrection')

    return rootNode
