import collections
import datetime
import re
import logging
import json

class TaskLoader:

    ATTR_PREFIX = u'@'

    def load(self, instance, spec, recursive = False):
        """
        Loads data to a task instance from spec
        """
        #print("~~" + str(taskModel))
        if (u'@modelUri' in spec):
            instance.modelUri = spec['@modelUri']

        # handle all attributes
        for propKey, propVal in spec.iteritems():
            if (propKey[0] == TaskLoader.ATTR_PREFIX):
                instance.setAttribute(propKey[1:], propVal)


class TaskContainer:
    """
    In this context a Task is an instance of a task loaded in memory.
    The task template is called task specification.
    """

    ROOT_NS = "taskmator.task"

    logger = logging.getLogger(__name__)


    def __init__(self, task_ast):
        """
        Constructor
        @type task_ast: dict abstract syntax tree that represents a task specification
        """
        self.task_ast = task_ast
        self.task_root = None
        self.task_loader = TaskLoader()

        # Load the root task
        self.task_root = self.instantiate_task('root', self.task_ast, None, self.ROOT_NS + 'CompositeTask')
        self.task_loader.load(self.task_root, self.task_ast)


    def get_task_spec(self, name_path):
        """
        Returns the task specification which is a pointer to an internal node
        in the AST
        @type name_path :array of names starting with root. E.g.: ['root', 'name1', ..]
        """
        # names represent the namespace hierarchy
        node = self.task_ast
        for name in name_path:
            if (name in node):
                node = node[name]
            else:
                raise Exception('Nonexistent task with name [' + '.'.join(name_path) + '].' )
        return (name_path[len(name_path)-1], node)

    def instantiate_task(self, name, task_spec, parent_task, task_type = None):
        """
        Dynamically instantiates a specific task and returns that instance.
        @type name: basestring
        @type task_spec: dict
        @type parent_task: Task
        """
        type = task_type if task_type else task_spec[u'@type']



        TaskClass = self._get_class(type)
        if (not TaskClass):
            raise Exception('Nonexistent task type [' + type + '].')

        task_instance = TaskClass(name, parent_task)

        self.task_loader.load(task_instance, task_spec)

        return task_instance

    def get_root(self):
        return self.task_root

    def get_task(self, task_fqn):
        """
        Returns the task given its fully qualified name.
        Instantiates tasks if not found but exists in the spec.
        @type task_fqn: basestring
        """
        name_path = task_fqn.split('.')
        if (len(name_path) == 1 and name_path[0] == u'root'):
            return self.task_root

        # traverse starting from the root's child
        name_path = name_path[1:]
        task_node = self.task_root
        for name in name_path[1:]:
            if (task_node.hasChild(name)):
                task_node = task_node.getChild(name)
            else:
                # Cache lookup failed, create one based on the AST
                task_name, task_spec = self.get_task_spec(name_path)
                task = self.instantiate_task(task_name, task_spec, task_node)
        return task_node

    def iteritems(self):
        """
        Return iteritems
        """


    # Private methods
    def _get_fq_typename(self, task, typeName):
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

    def _get_class(self, fqClassname):
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


class ExecutionContext:

    logger = logging.getLogger(__name__)

    def __init__(self, task_container):
        self.exec_start_time = None
        self.exec_stop_time = None
        self.task_container = task_container
        self.execution_trace = []

    def mark_start(self):
        self.exec_start_time = datetime.datetime.now()

    def mark_stop(self):
        """
        Mark this context as terminated
        """
        self.exec_stop_time = datetime.datetime.now()

    def lookup_task(self, task_fqn):
        return self.task_container.get_task(task_fqn)

    def register_trace(self, task_fqn, start_time, end_time, exit_code, output):
        trace_entry = {
                "start_time": start_time,
                "end_time": end_time,
                "code": exit_code,
                "output": output
            }
        self.execution_trace.append(trace_entry)

    def tasks(self, namePattern = None, state = None):
        """
        Returns a list of tasks that matches specified criteria
        @param name -- the name pattern to searh
        @param state -- the task state
        """
        result = []
        for taskname, task in self.task_container.iteritems():
            match = True
            if(state):
                if (task.getState() == state):
                    match = True
            if (match):
                try:
                    match = True if namePattern is None else (re.search(namePattern, task.getFqn()) is not None)
                except:
                    self.logger.warn("Error on pattern: "+ namePattern)

            if (match):
                result.append(task)
        return result
