import taskmator.task.core
import json


class TaskFactory:
    ROOT_NS = "taskmator.task"
    VALID_ATTRS = [u'namespaces', u'aliases', u'version', u'tasks', u'task', 
        u'description', u'params', u'execMode', u'load', u'haltOnError', u'dependsOn'
        ]

    def createTask(self, parent, type, name):
        """
        Dynamically creates a specifc task object and returns that object.
        Returns None it the type does not match to any existing class 
        """
        TaskClass = self._getClass(type)
        if (not TaskClass):
            raise Exception('Task  ' + type + " not found")

        task = TaskClass(name)

        if (parent):
            task.setParent(parent)
            parent.addChild(task)

        return task

    def _handleAttribute(self, task, propKey, propVal):
        print ("Handling ("+ propKey + ", " + str(propVal) + ")")
        if (propKey in self.VALID_ATTRS):
            setattr(task, propKey, propVal)
        else:
            raise Exception('Invalid Property ' + propKey)


    def _handleTaskDef(self, task, propKey, propVal):
        """ 
        propKey is of format <type> <task name>
        """
        typeAndTaskname = propKey.split(" ")
        if (len(typeAndTaskname) != 2):
            raise Exception('Invalid task declaration ' + propKey)

        # lookup alias
        fqnType = self._getFqTypename(task, typeAndTaskname[0])
        if ( not fqnType.startswith(self.ROOT_NS+".")):
            fqnType = self.ROOT_NS+"." + fqnType
        if ( not fqnType.endswith("Task")):
            fqnType = fqnType + "Task"

        newTask = self.createTask(task, fqnType, typeAndTaskname[1])

        # Recursively load task
        self.loadTask(newTask, propVal)

        return newTask

    def loadTask(self, task, taskModel):
        # handle all attributes first
        for propKey, propVal in taskModel.iteritems():
            if (propKey[0] == u'@'): 
                # all property that starts with '@' is task attribute
                print ("*Handling attr: " + propKey)
                self._handleAttribute(task, propKey[1:], propVal)

        for propKey, propVal in taskModel.iteritems():
            print ("*Handling " + propKey)
            if (propKey[0] != u'@'): 
                print ("*Handling taskDef: " + propKey)
                # otherwise it is a task definition
                self._handleTaskDef(task, propKey, propVal)

    def loadConfig(self, configFileName):
        """
        Main method to laod a config that contains tasks
        """
        configFile = open(configFileName, "r")
        configJson = configFile.read();
        modelRoot = json.loads(configJson)

        rootTask =  self.createTask(None, self.ROOT_NS + ".core.CompositeTask", "root")
        self.loadTask(rootTask, modelRoot)

        return rootTask

    def _getFqTypename(self, task, typeName):
        """
        Lookups the typeName form the alias and return the fully qualified type name
        """
        currTask = task
        # get the closest alias matching the typeName

        print("*currTask: "+ str(currTask))
        while currTask:
            aliases = currTask.aliases
            print("*aliases: "+ str(aliases))
            if (aliases):
                if (typeName in aliases):
                    return aliases[typeName]
            currTask = currTask._parent
        # Fall back to the original typeName
        return typeName

    def _getClass(self, fqClassname):
        """
        Get class given a fully qualified classname, None if not found 
        http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
        """
        print("*Loading: " + fqClassname);

        parts = fqClassname.split('.')
        modulePart = ".".join(parts[:-1])
        print ("*__import__ "+modulePart) 
        module = __import__( modulePart )
        for attrName in parts[1:]:
            module = getattr(module, attrName, None)
            if module == None:
                return None
        return module

