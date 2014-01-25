import abc
import copy
import logging
import collections
import threading
import datetime
import re
import string

class ParamTemplate(string.Template):
    """
    Templating for the param: accepts dots
    for replacing ExecutionContext values
    """
    idpattern = r"[\._a-z][\._a-z0-9]*"


class TemplateModelAdapter:
    def __init__(self, fallback_dic, execution_context=None):
        self.fallback_dic = fallback_dic
        self.execution_context = execution_context

    def __getitem__(self, key):
        retval = None
        # If the key referes to an outcome from the ExecutionContext
        if (".outcome_" in key):
            if (self.execution_context):
                dotPos = key.rfind(".")
                taskName = key[0:dotPos]
                propName = key[dotPos + 1:]
                taskRef = self.execution_context.lookup_task(taskName)
                if (taskRef):
                    if (propName == "outcome_code"):
                        retval = taskRef.getOutcome()[0]
                    elif (propName == "outcome_result"):
                        retval = taskRef.getOutcome()[1]
        if (retval == None):
            retval = self.fallback_dic[key]
        return retval


class Task:
    """
    Abstract base class for all Tasks
    """
    __metaclass__ = abc.ABCMeta

    ATTR_PARAMS = u'params'

    __VALID_ATTRS = [u'aliases', u'description', u'dependsOn', u'version',
                     u'modelUri', ATTR_PARAMS, u'namespaces', u'load', u'haltOnError', u'precond', u'decl', u'type'
    ]

    SCOPE_SEPARATOR = "/"

    STATE_NEW = 0
    STATE_RUNNING = 1
    STATE_WAITING = 2
    STATE_STOPPED = 3

    CODE_OK = 0
    CODE_SKIPPED = -1

    def __init__(self, name, parent=None):
        self._init_internal(name, parent)

        # A tuple where first element is the code, and second element is the result
        self.retainResult = True
        self.outcome_code = None
        self.outcome_result = None
        self.retainOutcome = True
        self.modelUri = None
        self.aliases = None
        self.namespaces = None
        self.description = None
        # attributes are local data that cannot be overriden
        self.attribs = {}
        # params are used in input for template. It can also be overriden
        self.params = {}
        self.haltOnError = False
        self.precond = None

    def __str__(self):
        return self.getFqn() + " [" + self.__class__.__name__ + "]";

    def _init_internal(self, name, parent=None):
        """
        Initialization that is run after deep copying a task instance
        I.e. All other variables are copied over.
        """
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
        copy_instance._init_internal(name, parent)

        self.name = temp_name
        self.parent = temp_parent
        self.children = temp_children

        parent.addChild(copy_instance)

        return copy_instance

    def init(self):
        """
        Task initialization.
        Inheriting Task class may implement any initialization here.
        This is called after all attributes are set
        """
        self.setParam('TASK_TYPE_NAME', self.__class__.__name__ )

    def setAttribute(self, attrKey, attrVal):
        if (attrKey == self.ATTR_PARAMS):
            self.params = attrVal
        elif (attrKey in self.__VALID_ATTRS):
            #setattr(self, attrKey, attrVal)
            self.attribs[attrKey] = attrVal;
        else:
            raise Exception('Invalid Attribute "' + attrKey + '"')

    def getAttribute(self, attrKey, default=None, executionContext=None, expandTemplate=True):

        if (attrKey in self.attribs):
            retval = self.attribs[attrKey]

            # Expand template by replacing the placeholders with the params
            if expandTemplate and isinstance(retval, basestring):
                retval = self.applyTemplate(retval, self.getParams(), executionContext)
            return retval

        else:
            return default

    def getParams(self):
        """
        Returns a copy of the param
        Goes up to the scope hierarchy to add entries which the key does not conflict
        """
        if (not self.params):
            return {}
        retval = self.params.copy()
        node = self.parent
        while (node and node.params):
            for key, val in node.params.items():
                if (key not in retval):
                    retval[key] = val
            node = node.parent

        return retval

    def applyTemplate(self, templateStr, params, executionContext=None):
        """
        Applies template to the argument passed
        """
        # Expand template by replacing the placeholders with the params
        tpl = ParamTemplate(templateStr)
        model = TemplateModelAdapter(params, executionContext)
        retval = tpl.safe_substitute(model)
        return retval


    def getParam(self, key, default=None, executionContext=None, expandTemplate=True):
        params = self.getParams()
        retval = None
        if (key in params):
            retval = params[key]
        else:
            retval = default

        # Expand template by replacing the placeholders with the params
        if expandTemplate and isinstance(retval, basestring):
            retval = self.applyTemplate(retval, params, executionContext)

        return retval

    def setParams(self, params):
        if (not self.params):
            self.params = params
        else:
            self.params.update(params)
    def setParam(self, key, value):
        self.params[key] = value

    def hasParam(self, key):
        if (key in self.params):
            return True

        node = self.parent
        while (node):
            if (key in node.params):
                return True
            node = node.parent

        return False

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

    def hasChild(self, name):
        return name in self.children

    def getChildren(self):
        return self.children.items()

    def getChild(self, name):
        return self.children[name]

    def getChildAt(self, idx):
        self._children[idx]

    def get_subtask(self, name_path):
        """
        @param name_path array of names to resolve the descendant (sub) task
        """
        node = self
        for name in name_path:
            if (node.hasChild(name)):
                node = node.getChild(name)
            else:
                raise Exception('Nonexistent task with name [' + '.'.join(name_path) + ']' )
        return node


    def traverse(self):
        self.__traverse(self)

    def __traverse(self, node):
        """
        Pending pass function as parameter
        """
        print (str(node) + "+" + str(len(node.getChildren())))
        if (len(node.getChildren()) > 0):
            for childName, child in node.getChildren():
                self.__traverse(child)

    def getOutcome(self):
        return (self.outcome_code, self.outcome_result)

    def setOutcome(self, code, result):
        self.outcome_code = code
        if (self.retainResult):
            self.outcome_result = result

    def getResult(self):
        return self.outcome_result

    def setResult(self, result):
        self.outcome_result = result

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

    def getTypename(self):
        return self.__class__.__name__


    def validate(self):
        """
        Concrete classes must implement this method
        It should return true if valid, false otherwise
        """
        return True

    def eval(self, expression):
        return eval(expression, {"__builtins__": {}})

    @abc.abstractmethod
    def executeInternal(self, executionContext):
        """
        Concrete classes must implement this method
        """
        return

    def execute(self, execution_context):
        """
        The main execution method.
        It internally calls executeInternal following the Template Method pattern
        @type execution_context ExecutionContext
        """
        precondEval = True
        if (self.precond):
            params = self.getParams()
            precond = self.applyTemplate(self.precond, params, execution_context)
            precondEval = self.eval(precond)
        if (not precondEval):
            # Precondition evaluated to false, return
            return Task.CODE_SKIPPED, None

        self.lastExecTimeStart = datetime.datetime.now()
        self.state = Task.STATE_RUNNING

        exit_code, output = self.executeInternal(execution_context)
        self.state = Task.STATE_STOPPED
        self.lastExecTimeStop = datetime.datetime.now()

        # @todo - the task registry is using static module fqn instead of runtime call path.
        #         shall we keep as is? What is is already registered?
        execution_context.register_trace(self, self.getFqn(),
                                         self.lastExecTimeStart, self.lastExecTimeStop,
                                         exit_code, output
        )

        return exit_code, output


class TaskThread(threading.Thread):
    """
    Class that encapsulates a task in thread
    This thread is executed from CompositeTask
    """

    def __init__(self, thread_id, name, task, executionContext):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.task = task
        self.code = None
        self.output = None
        self.executionContext = executionContext

    def run(self):
        self.code, self.output = self.task.execute(self.executionContext)


class CompositeTask(Task):
    """
    Task that is a grouping of tasks
    """
    logger = logging.getLogger(__name__)

    ATTR_INIT_MODE = u'initMode'
    ATTR_EXEC = u'exec'
    ATTR_EXEC_MODE = u'execMode'

    # Double underscore makes unique namespace for this class
    __VALID_ATTRS = [ATTR_INIT_MODE, ATTR_EXEC, ATTR_EXEC_MODE]

    def __init__(self, name, parent):
        super(CompositeTask, self).__init__(name, parent)
        self._exec = [] # Array of string of task names

    def setAttribute(self, attrKey, attrVal):
        if (attrKey == self.ATTR_EXEC):
            # There is two possibilities: a string that contains the fqn of
            # the task to execute, or a string array of task names to execute
            # either in sequentially or in parallel depending of the execMode
            if (isinstance(attrVal, basestring)):
                self._exec.append(attrVal)
            elif (isinstance(attrVal, list)):
                for item in attrVal:
                    if (isinstance(item, basestring)):
                        self._exec.append(item)
                    else:
                        raise Exception('Element in @exec must be a string')
            else:
                raise Exception('The value of @exec has invalid type ' + str(type(attrVal)) + ', only string or array of string is allowed.')

        if (attrKey in self.__VALID_ATTRS):
            self.attribs[attrKey] = attrVal
        else:
            super(CompositeTask, self).setAttribute(attrKey, attrVal)


    def executeInternal(self, executionContext):
        """
        Executes task(s) specified in the @exec attribute
        """
        self.logger.info("Executing " + str(self))

        # Find which task(s) to execute.
        task_names_to_exec = self._exec if len(self._exec) > 0 else [u'default']

        tasks_to_exec = []
        for task_name_to_exec in task_names_to_exec:
            task_fqn = task_name_to_exec if task_name_to_exec.startswith('root') \
                else self.getFqn() + '.' + task_name_to_exec
            tasks_to_exec.append(executionContext.get_task_container().get_task(task_fqn))

        exec_mode = self.getAttribute(u'execMode', u'sequential')
        self.logger.info("ExecMode: " + exec_mode)

        code, output = (Task.CODE_OK, None)
        if (exec_mode == u'parallel'):
            taskThreads = []
            for task_to_exec in tasks_to_exec:
                #print (str(child))
                taskThread = TaskThread(1, "Thread-" + task_to_exec.name, task_to_exec, executionContext)
                taskThreads.append(taskThread)
                try:
                    taskThread.start()
                except:
                    self.logger.error("Error: unable to start thread")

            self.logger.info("Joining all threads")
            for thread in taskThreads:
                try:
                    taskThread.join()
                except:
                    self.logger.error("Error: unable to join thread")
            # @todo Assign the result value

        else:
            # Executing in serial
            for task_to_exec in tasks_to_exec:
                code, output = task_to_exec.execute(executionContext)
            # In serial mode, the last outcome is the compositeTask's outcome

        # Composite returns None as output
        return (code, None)

class EchoTask(Task):
    """
    Task that simply echoes the message
    """
    logger = logging.getLogger(__name__)

    def executeInternal(self, executionContext):
        message = self.getParam('message', False)
        self.logger.info("Echo '" + message+ "'")
        self.setOutcome(Task.CODE_OK, message)
        return (Task.CODE_OK, message)


class SwitchTask(Task):
    """
    Task that Does switch case.
    Notice: first matching case is the one that is executed.
    """

    logger = logging.getLogger(__name__)

    def executeInternal(self, executionContext):
        self.logger.info("Executing " + str(self))
        cases = self.getAttribute(u'cases')

        # case is the boolean statement, body is the task to execute.
        code, out = (Task.CODE_OK, None)
        for case, body in cases:
            if self.eval(case):
                if (body[0] == u'#'):
                    task_fqname = body[1:]
                    task = executionContext.lookupTask(task_fqname)
                    code, out = task.execute(executionContext)
                break
        return (code, out)


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
        self.logger.info("Executing " + str(self))
        return (Task.CODE_OK, None)

