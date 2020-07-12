import cv2
import numpy as np
import math
    
WINDOW_NAME='A-Star Algorithm Test'
C_START = (0,0,200) # RED
C_PATH = (200,0,0) # BLUE
C_END = (0,200,0) # GREEN
C_WALL = (0,0,0) # BLACK
C_ALIVE = (192,192,192) # WHITE
C_DEAD = (64,64,64) # GRAY


class Node(object):
    __slots__ = 'neighbours', 'location', 'isActive', 'isWall', 'parent', 'localGoal', 'globalGoal'

    def __init__(self,location=None, 
            isActive=False, 
            isWall=False, 
            parent=None, 
            localGoal=math.inf, 
            globalGoal=math.inf):

        self.neighbours = list()
        self.isActive = isActive
        self.localGoal = localGoal
        self.globalGoal = globalGoal
        self.parent = parent
        self.location = location
        self.isWall = isWall

    def __str__(self):
        return f"GRID LOCATION : {self.location}, NEIGHBOURS : {len(self.neighbours)}, COLOR : {self.color}"

    def reset(self):
        self.isActive=False
        self.parent=None 
        self.localGoal=math.inf 
        self.globalGoal=math.inf

    @staticmethod
    def dist(n1, n2):
        x1,y1 = n1.location
        x2,y2 = n2.location
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)

class Nodes:
    __slots__ = 'nodeGrid','startNode', 'endNode', 'size', 'w','b'
    def __init__(self, gridsize=20, nodesize=25):
        self.nodeGrid = [[Node() for i in range(gridsize)] for j in range(gridsize)]
        for x in range(gridsize):
            for y in range(gridsize):
                element = self.nodeGrid[x][y]
                neighbourList = element.neighbours

                # NSEW connections
                if y>0:
                    neighbourList.append(self.nodeGrid[x][y-1])
                if y<gridsize-1:
                    neighbourList.append(self.nodeGrid[x][y+1])
                if x>0:
                    neighbourList.append(self.nodeGrid[x-1][y])
                if x<gridsize-1:
                    neighbourList.append(self.nodeGrid[x+1][y])

                element.location = [x,y]
        
        self.startNode = self.nodeGrid[(gridsize-1)//2][1]
        self.endNode = self.nodeGrid[(gridsize-1)//2][gridsize-2]
        self.w = gridsize
        self.b = nodesize

        # Disable QT overlay for right click
        cv2.namedWindow(WINDOW_NAME,cv2.WINDOW_AUTOSIZE|cv2.WINDOW_GUI_NORMAL) 
        cv2.setMouseCallback(WINDOW_NAME, self.click)

    def click(self, event, x, y, flags, param):
        element = self.nodeGrid[x//self.b][y//self.b]
        if event == cv2.EVENT_LBUTTONDBLCLK and element is not self.endNode:
            self.startNode = element
            element.isWall = False
        elif event == cv2.EVENT_RBUTTONDBLCLK and element is not self.startNode:
            self.endNode = element
            element.isWall = False
        elif event in (cv2.EVENT_LBUTTONDOWN,cv2.EVENT_RBUTTONDOWN) and element not in (self.startNode, self.endNode):
            element.isWall = not element.isWall
        self.solve()

    def solve(self):
        for row in self.nodeGrid:
            for element in row:
                element.reset()

        currentNode = self.startNode
        currentNode.localGoal = 0
        currentNode.globalGoal = Node.dist(self.startNode,self.endNode)
        nodesToTest = list()
        nodesToTest.append(currentNode)
        while nodesToTest and currentNode is not self.endNode:
            nodesToTest.sort(key=lambda x:x.globalGoal)
            while nodesToTest and nodesToTest[0].isActive:
                nodesToTest.pop(0)
            if not nodesToTest:
                break

            currentNode = nodesToTest[0]
            currentNode.isActive = True
            for neighbour in currentNode.neighbours:
                if not neighbour.isActive and not neighbour.isWall:
                    nodesToTest.append(neighbour)

                newGoal = currentNode.localGoal + Node.dist(currentNode,neighbour)
                if newGoal < neighbour.localGoal:
                    neighbour.parent = currentNode
                    neighbour.localGoal = newGoal
                    neighbour.globalGoal = newGoal + Node.dist(neighbour,self.endNode)



    def update(self):
        while cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) >= 1:
            img = np.zeros((self.w*self.b,self.w*self.b,3),np.uint8)
            for x in range(self.w):
                for y in range(self.w):
                    start_point = tuple([self.b*_ for _ in (x,y)])
                    end_point = tuple([sum(_) for _ in zip(start_point,(self.b,self.b))])
                    element = self.nodeGrid[x][y]
                    color = C_START if self.startNode == element else C_END if self.endNode == element else C_WALL if element.isWall else C_ALIVE if element.isActive else C_DEAD
                    cv2.rectangle(img, start_point, end_point, color, thickness=-1)
                    cv2.rectangle(img, start_point, end_point, C_WALL, thickness=1)

            trace = self.endNode
            while(trace.parent):
                x,y = trace.location
                start_point = tuple([self.b*_ for _ in (x,y)])
                end_point = tuple([sum(_) for _ in zip(start_point,(self.b,self.b))])
                cv2.rectangle(img,start_point,end_point, C_END if trace is self.endNode else C_PATH, -1)
                trace = trace.parent

            cv2.imshow(WINDOW_NAME,img)
            key = cv2.waitKey(20) & 0xFF
            if key in (27, ord('q')):
                break

        cv2.destroyAllWindows()


if __name__== "__main__": 
    a_star = Nodes(15,25)
    a_star.solve()
    a_star.update()