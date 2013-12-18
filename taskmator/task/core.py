import abc
import json

'''
abstract class for all Task
'''
class Task:
    __metaclass__ = abc.ABCMeta

    modelUri = None
    aliases = None
    namespaces = None
    description = None
    params = None
    haltOnError = False

    _parent = None
    _children = []

    def __init__(self, name):
        self.name = name

    def setParent(self, parent):
        self._parent = parent

    def getParent(self):
        return self._parent

    def getRootParent(self):
        node = self
        while node._parent is not None:
            node = node._parent
        return node

    def addChild(self, child):
        self._children.append(child)

    def getChildren(self):
        self._children

    def getChildAt(self, idx):
        self._children[idx]

    def validateParam(self):
        return True

    @abc.abstractmethod
    def execute(self):
        '''Concrete classes muse implement this method'''
        return

class CompositeTask(Task):

    def __init__(self, name):
        super(CompositeTask, self).__init__(name)

    def validateParam(self):
        if (not 'tasks' in self.params):
            # check if ther eis no tasks either
            return False
        return True

    def execute(self):
        print (self.params['command'])
        return 0

'''
Task that runs a Shell Command line
The param must contain "command"
The command are OS specific.
'''
class CommandLineTask(Task):

    def validateParam(self):
        if ( not 'command' in self.params):
            return False
        return True

    def execute(self):
        print (self.params['command'])
        return 0



'''
Task that runs a Shell Command line
The param must contain "command"
The command are OS specific.
'''
class CronTask(Task):

    def validateParam(self):
        if ( not 'command' in self.params):
            return False
        return True

    def execute(self):
        print (self.params['command'])
        return 0


