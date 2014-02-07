import datetime
import re
import logging
from taskmator.factory import TaskFactory


class TaskContainer:
    """
    In this context a Task is an instance of a task loaded in memory.
    The task template is called task specification.
    """

    logger = logging.getLogger(__name__)

    def __init__(self, task_ast):
        """
        Constructor
        @type task_ast: dict abstract syntax tree that represents a task specification
        """
        self.task_ast = task_ast
        self.task_root = None
        self.task_factory = TaskFactory()

        # Load the root task
        self.task_root = self.task_factory.instantiate('core.Composite', 'root', None)
        if (self.task_ast):
            self.task_factory.load(self.task_root, self.task_ast)


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
                raise Exception('Nonexistent task with name [' + '.'.join(name_path) + '].')
        return (name_path[len(name_path) - 1], node)


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
        for name in name_path:
            if (task_node.hasChild(name)):
                task_node = task_node.getChild(name)
            else:
                # Cache lookup failed, create one based on the AST
                task_name, task_spec = self.get_task_spec(name_path)
                #task = self.instantiate_task(task_name, task_spec, task_node)
                task = self.task_factory.create(task_name, task_spec, task_node)

        return task_node

    def iteritems(self):
        """
        Return iteritems
        @PENDING
        """
        pass


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

    def get_task_container(self):
        """
        Returns the task container
        @rtype: TaskContainer
        """
        return self.task_container

    def lookup_task(self, task_fqn):
        return self.task_container.get_task(task_fqn)

    def register_trace(self, task_ref, context_path, start_time, end_time, exit_code, output):
        """
        Registers a task execution trace
        @param context_path -- the task call context path (e.g: root/test/)
                               remember this may differ from namespace because of branching
        """
        trace_entry = {
            "task_ref": task_ref,
            "context_path": context_path,
            "start_time": start_time,
            "end_time": end_time,
            "exit_code": exit_code,
            "output": output
        }
        self.execution_trace.append(trace_entry)

    def traces(self, namePattern=None, exit_code=None):
        """
        Returns a list of tasks that matches specified criteria
        @param namePattern -- the name pattern to search
        @param exit_code -- the task state
        """
        result = []
        for trace_entry in self.execution_trace:
            match = True
            if (exit_code):
                if (trace_entry['exit_code'] == exit_code):
                    match = True
            if (match):
                try:
                    match = True if namePattern is None else (re.search(namePattern, trace_entry['context_path']) is not None)
                except:
                    self.logger.warn("Error on pattern: " + namePattern)

            if (match):
                result.append(trace_entry)
        return result
