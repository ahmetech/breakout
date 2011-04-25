from os.path import join

class Describer(object):
    def __repr__(self):
        currentClassName = self.__class__.__name__
        outString = "\n\n<instance of '%s' class>"%currentClassName
        attributeNameList = self.__dict__.keys()
        attributeNameList.sort()
        for attributeName in attributeNameList:
            outString += "\n\t<attr name='%s' value='%s' />"%(attributeName,self.__dict__[attributeName])
        outString += "\n</instance>\n\n"
        return outString

class ResourceManager(object):
    def __init__(self, root_path):
        self.root_path = root_path
    def getImagePath(self, imageFilename):
        return join(self.root_path, "images", imageFilename)
    def getGameLevelPath(self, pathFilename):
        return join(self.root_path, "levels", pathFilename)
    def getSoundPath(self, soundFilename):
        return join(self.root_path, "sounds", soundFilename)
    def getFont(self, fontName):
        return join(self.root_path, "fonts", fontName)

rm = ResourceManager(join("game", "resources"))


