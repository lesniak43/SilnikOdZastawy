from abc import ABCMeta, abstractmethod
import os

class SceneLoader:
    __metaclass__=ABCMeta

    @abstractmethod
    def loadFile(self, file_name):
        pass

    @abstractmethod
    def getFloors(self):
        pass

    @abstractmethod
    def getWalls(self):
        pass

class SceneLoaderException(Exception):
    pass

    

##########################################################################
# Concrete loader of OBJ files                                           #
##########################################################################

class ObjSceneLoader(SceneLoader):
    """Loads the scene from a Wavefront OBJ file"""

    def __init__(self):
        self.in_file = None
        self.floors = []
        self.walls = []
        self.objects = {}
        
    def loadFile(self, fileName):
        if not fileName.lower().endswith(('.obj')):
            raise SceneLoaderException("Wrong file extension")

        self.in_file = open(fileName, "r")

        while self.__getNextObject():
            pass

        print self.objects
        
    def getFloors(self):
        pass

    def getWalls(self):
        pass

    def __getNextObject(self):
        obj_name = ''
        obj_vertices = []
        while True:
            line = self.in_file.readline().rstrip()
            if line == '':
                return False
            data = line.split(' ')
            if data[0] == 'o':
                obj_name = data[1]
            elif data[0] == 'v' and obj_name != '':
                obj_vertices.append([data[i] for i in xrange(1,4)])
            elif obj_name != '' and data[0] != 'v':
                self.objects[obj_name] = obj_vertices
                return True
                
##########################################################################
# Test                                                                   #
##########################################################################

if __name__ == '__main__':

    loader = ObjSceneLoader()
    loader.loadFile("stage1.obj")
    

