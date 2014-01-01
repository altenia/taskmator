import abc
import copy
import logging
import collections
import threading
import datetime
from string import Template

from taskmator.context import ExecutionContext


class Task:
    """
    Abstract base class for all Tasks
    """
    __metaclass__ = abc.ABCMeta

    __VALID_ATTRS = [u'aliases', u'description', u'dependsOn', u'version',
        u'modelUri', u'params', u'namespaces', u'load', u'haltOnError', u'precond', u'decl', u'type'
        ]

    SCOPE_SEPARATOR = "/"

    STATE_NEW = 0
    STATE_RUNNING = 1
    STATE_WAITING = 2
    STATE_STOPPED = 3

    def __init__(self, name, parent = None):
        self.init(name, parent)

        # A tuple where first element is the code, and second element is the result
        self.outcome = (None, None)
        self.retainOutcome = True
        self.modelUri = None
        self.aliases = None
        self.namespaces = None
        self.description = None
        self.params = None
        self.haltOnError = False

    def __str__(self):
        return self.getFqn() + " ["+self.__class__.__name__+"]";

    def init(self, name, parent = None):
        self.state = Task.STATE_NEW
        self.lastExecTimeStart = None
        self.lastExecTimeStop = None
        self.name = name
        self.parent = parent
        if (parent):
            parent.addChild(self)
        self.children = collections.OrderedDict()

    def copy(self, name, parent):
        """
        Returns a copy of this tasks with a new name.
        All fields are deep copied except for parent and children
        """
        temp_name = self.name
        temp_parent = self.parent
        temp_children = self.children
        self.name = None
        self.parent = None
        self.children = None

        copy_instance = copy.deepcopy(self)
        copy_instance.init(name, parent)

        self.name = temp_name
        self.parent = temp_parent
        self.children = temp_children

        parent.addChild(copy_instance)

        return copy_instance

    def setAttribute(self, attrKey, attrVal):
        if (attrKey in self.__VALID_ATTRS):
            setattr(self, attrKey, attrVal)
        else:
            raise Exception('Invalid Attribute "' + attrKey + '"')

    def getParams(self):
        retval = self.params.copy()
        node = self
        #print ("**"+ str(node) + " --" + str(node.parent))
        while (node.parent):
            for key, val in node.params.items():
                if (key not in retval):
                    retval['key'] = val
            node = node.parent

        return retval

    def getParam(self, key, default=None, executionContext = None, expandTemplate = True):
        params = self.getParams()
        retval = None;
        if (key in params):
            retval = params[key]
        else:
            retval = default

        # Super simplified variable match
        if (executionContext and retval[0] == u'$'):
            dotPos = retval.rfind(".")
            taskName = retval[1:dotPos]
            propName = retval[dotPos+1:]
            taskRef = executionContext.lookupTask(taskName)
            if (propName == "outcome_code"):
                retval = taskRef.getOutcome()[0]
            elif (propName == "outcome_result"):
                retval = taskRef.getOutcome()[1]

        # Expand template by replacing the placeholders with the params
        if (expandTemplate and retval):
            retval = self.applyTemplate(retval)
        return retval

    def setParams(self, params):
        if (not self.params):
            self.params = params
        else:
            self.params.update(params)

    def hasParam(self, key):
        if (key in self.params):
            return True

    def setParent(self, parent):
        self.parent = parent

    def getParent(self):
        return self.parent

    def getRootParent(self):
        node = self
        #print ("++"+ str(node) + " --" + str(node.parent))
        while node.parent is not None:
            node = node.parent
        return node

    def addChild(self, child):
        self.children[child.name] = child

    def getChildren(self):
        return self.children.items()

    def getChild(self, name):
        return self.children[name]

    def getChildAt(self, idx):
        self._children[idx]

    def traverse(self):
        self.__traverse(self)

    def __traverse(self, node):
        print (str(node) + "+" + str(len(node.getChildren())))
        if (len(node.getChildren()) > 0):
            for childName, child in node.getChildren():
                self.__traverse(child)

    def getOutcome(self):
        return self.outcome

    def setOutcome(self, code, result):
        self.outcome = (code, result)

    def getNamespace(self):
        """
        Returns fully qualified name
        """
        nampescope = []
        currTask = self.parent

        while currTask:
            nampescope.append(currTask.name)
            currTask = currTask.parent

        # Fall back to the original typeName
        return ".".join(reversed(nampescope))

    def getFqn(self):
        """
        Returns fully qualified name
        """
        nampescope = [self.name]

        currTask = self.parent
        while currTask:
            nampescope.append(currTask.name)
            currTask = currTask.parent

        # Fall back to the original typeName
        return ".".join(reversed(nampescope))

    def applyTemplate(self, templateStr):
        """
        Applies template to the argument passed
        """
        tmpl = Template(templateStr)
        return tmpl.safe_substitute(self.params)

    @abc.abstractmethod
    def executeInternal(self, executionContext):
        '''Concrete classes muse implement this method'''
        return

    def execute(self, executionContext = None):
        """
        The main execution method
        """
        context_created = False
        if (not executionContext):
            context_created = True
            executionContext = ExecutionContext()
        self.lastExecTimeStart = datetime.datetime.now()
        self.state = Task.STATE_RUNNING
        # @todo - the task registry is using static module fqn instead of runtime call path.
        executionContext.registerTask(self.getFqn(), self)

        self.executeInternal(executionContext)
        self.state = Task.STATE_STOPPED
        self.lastExecTimeStop = datetime.datetime.now()

        if (context_created):
            executionContext.close()
        return

class TaskThread(threading.Thread):
    def __init__(self, threadID, name, task, executionContext):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.task = task
        self.executionContext = executionContext

    def run(self):
        self.task.execute(self.executionContext)

class CompositeTask(Task):

    logger = logging.getLogger(__name__)

    # Double underscore makes unique namespace for this class
    __VALID_ATTRS = [u'default', u'tasks', u'execMode']

    def __init__(self, name, parent):
        # Group of tasks, it could be run sequentially or parallel depending on @execMode
        self.group = []
        self.execMode = 'sequential'
        super(CompositeTask, self).__init__(name, parent)

    def setAttribute(self, attrKey, attrVal):
        if (attrKey in self.__VALID_ATTRS):
            setattr(self, attrKey, attrVal)
        else:
            super(CompositeTask, self).setAttribute(attrKey, attrVal)


    def executeInternal(self, executionContext):
        self.logger.info ("Executing " + str(self))

        self.logger.info("Executing in " + self.execMode + " mode")
        if (self.execMode == u'parallel'):
            taskThreads = []
            for name, child in self.getChildren():
                #print (str(child))
                taskThread = TaskThread(1, "Thread-" + child.name,  child )
                taskThreads.append(taskThread)
                try:
                    taskThread.start()
                except:
                    print "Error: unable to start thread"

            self.logger.info("Joining all threads")
            for thread in taskThreads:
                try:
                    taskThread.join()
                except:
                    print "Error: unable to join thread"

        else:
            # Executing in serial
            lastChild = None
            for name, child in self.getChildren():
                lastChild = child
                child.execute(executionContext)
            # In serial mode, the last outcome is the compositeTask's outcome
            code, result = lastChild.getOutcome()
            self.setOutcome(code, result)

        return 0


'''
Task that runs a Shell Command line
The param must contain "command"
The command are OS specific.
'''
class CronTask(Task):

    logger = logging.getLogger(__name__)

    def executeInternal(self, executionContext):
        self.logger.info ("Executing " + str(self))
        return 0


class SwitchTask(Task):
    """
    Task that Does switch case
    """

    logger = logging.getLogger(__name__)

    def executeInternal(self, executionContext):
        self.logger.info ("Executing " + str(self))
        return 0


class IterationTask(Task):
    """
    Task that does Iteration
    """

    logger = logging.getLogger(__name__)

    # Double underscore makes unique namespace for this class
    __VALID_ATTRS = [u'for', u'exec']

    def setAttribute(self, attrKey, attrVal):
        if (attrKey in self.__VALID_ATTRS):
            setattr(self, attrKey, attrVal)
        else:
            super(IterationTask, self).setAttribute(attrKey, attrVal)

    def executeInternal(self, executionContext):
        self.logger.info ("Executing " + str(self))
        return 0

