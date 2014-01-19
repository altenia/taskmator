import logging
import taskmator.task.core
import json
import collections

class TaskFactory:
    """
    Factory class that creates tasks from JSON
    """
    ROOT_NS = "taskmator.task"

    ATTR_PREFIX = u'@'
    TASK_SUFFIX = "Task"
    
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.directory = collections.OrderedDict()

    def registerTaskDef(self, taskName, taskRef):
        self.directory[taskName] = taskRef

    def lookupTaskDef(self, taskName):
        if (taskName in self.directory):
            return self.directory[taskName]
        else:
            return None

    def createTask(self, parent, type, name):
        """
        Dynamically creates a specifc task object and returns that object.
        Returns None it the type does not match to any existing class 
        """
        TaskClass = self._getClass(type)
        if (not TaskClass):
            raise Exception('Task  ' + type + " not found")

        task = TaskClass(name, parent)

        self.registerTaskDef(task.getFqn(), task)

        return task

    def _handleAttribute(self, task, propKey, propVal):
        """
        Handles attributes (field keys that starts with @)
        """
        self.logger.debug ("Handling attribute ("+ propKey + ", " + str(propVal) + ")")
        # all property that starts with '@' is task attribute
        # except for @tasks which is array of tasks, and @task which is a copy of another task 

        if  (propKey == u'tasks'):
            self._handleTaskDefArr(task, propVal)
        else:
            task.setAttribute(propKey, propVal)

    def _handleTaskDefArr(self, task, propVal):
        """
        @param propVal array of task definition
        """
        #print(">> _handTaskDefArr")
        for taskDef in propVal:
            if (u'@decl' not in taskDef):
                raise AttributeError("Attribute @task not found")

            self._handleTaskDef(task, taskDef[u'@decl'], taskDef)

    def _handleTaskDef(self, task, propKey, propVal):
        """ 
        task is the current task in context, which becomes the parent task
        propKey is of format <type> <task name>
        propVal is json parsed task definition part
        """
        # @todo - move task duplication to runtime (instead of load time)
        if (propKey[0] == u'#'):
            refAndTaskname = propKey[1:].split(" ")
            refAndTaskname[0]
            taskname = refAndTaskname[1] if len(refAndTaskname) > 1 else refAndTaskname[0].replace('.', '-')
            # Copy from another task
            origTask = self.lookupTaskDef(refAndTaskname[0])
            #print ("****>>" + str(origTask))
            newTask = origTask.copy(taskname, task)
            return newTask

        #print ("~~Handling taskDef ("+ propKey + ", "+str(propVal)+")")
        self.logger.debug ("Handling taskDef ("+ propKey + ", {propVal})")
        typeAndTaskname = propKey.split(" ")
        if (len(typeAndTaskname) != 2):
            raise Exception('Invalid task declaration ' + propKey)

        # lookup alias
        fqnType = self._getFqTypename(task, typeAndTaskname[0])
        if ( not fqnType.startswith(self.ROOT_NS+".")):
            fqnType = self.ROOT_NS+"." + fqnType
        if ( not fqnType.endswith(TaskFactory.TASK_SUFFIX)):
            fqnType = fqnType + TaskFactory.TASK_SUFFIX

        newTask = self.createTask(task, fqnType, typeAndTaskname[1])

        taskModel = propVal
        # If propVal is a string, it means it's a filename: recursively load config file
        if (type(propVal) is unicode):
            # if it is string, it can only be load:
            configFile = propVal
            if (not configFile.startswith('/')):
                rootTask = task.getRootParent();
                pathSeparatorPos = rootTask.modelUri.rfind('/')
                directory = rootTask.modelUri[0:pathSeparatorPos+1]
                configFile = directory + configFile
            self.logger.debug("Opening: " + configFile)
            taskModel = self.loadConfig(configFile)

        # Now, the taskModel is a dictionary (i.e. representation of task)
        self.loadTask(newTask, taskModel)

        return newTask

    def loadTask(self, task, taskModel):
        #print("~~" + str(taskModel))
        if (u'@modelUri' in taskModel):
            task.modelUri = taskModel['@modelUri']
        # handle all attributes first
        for propKey, propVal in taskModel.iteritems():
            if (propKey[0] == TaskFactory.ATTR_PREFIX):
                self._handleAttribute(task, propKey[1:], propVal)

        # handle all non-attributes next
        for propKey, propVal in taskModel.iteritems():
            if (propKey[0] != TaskFactory.ATTR_PREFIX): 
                # otherwise it is a task definition
                self._handleTaskDef(task, propKey, propVal)

    def loadConfig(self, configFileName):
        """
        Main method to laod a config that contains tasks
        """
        configFile = open(configFileName, "r")
        configJson = configFile.read();
        model = json.loads(configJson, object_pairs_hook=collections.OrderedDict)
        return model

    def loadRoot(self, configFilename):
        modelRoot = self.loadConfig(configFilename)
        modelRoot[u'@modelUri'] = configFilename
        rootTask =  self.createTask(None, self.ROOT_NS + ".core.CompositeTask", "root")
        self.loadTask(rootTask, modelRoot)

        return rootTask

    def _getFqTypename(self, task, typeName):
        """
        Lookups the typeName form the alias and return the fully qualified type name
        """
        currTask = task
        # get the closest alias matching the typeName

        while currTask:
            aliases = currTask.aliases
            if (aliases):
                if (typeName in aliases):
                    return aliases[typeName]
            currTask = currTask.parent
            #print ("%%-chk alias-a:" + str(currTask))
        # Fall back to the original typeName
        return typeName

    def _getClass(self, fqClassname):
        """
        Get class given a fully qualified classname, None if not found 
        http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
        """
        self.logger.info("Loading class: " + fqClassname);

        parts = fqClassname.split('.')
        modulePart = ".".join(parts[:-1])
        #print ("*__import__ "+modulePart) 
        module = __import__( modulePart )
        for attrName in parts[1:]:
            module = getattr(module, attrName, None)
            if module == None:
                return None
        return module
