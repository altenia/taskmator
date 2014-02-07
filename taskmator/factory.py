import logging
import taskmator.task.core
import json
import collections

class TaskFactory:
    ATTR_PREFIX = u'@'
    ROOT_NS = "taskmator.task."

    logger = logging.getLogger(__name__)

    def __init__(self):
        pass

    def create(self, name, spec, parent):
        """
        Instantiates and loads
        """
        type = spec[u'@type']
        instance = self.instantiate(type, name, parent)
        self.load(instance, spec)
        instance.init()
        return instance

    def instantiate(self, task_type, name, parent_task):
        """
        Dynamically instantiates a specific task and returns that instance.
        @type name: basestring
        @type task_spec: dict
        @type parent_task: Task
        """
        fq_typename = self.ROOT_NS + task_type + 'Task'
        TaskClass = self._get_class(fq_typename)
        if (not TaskClass):
            raise Exception('Nonexistent task type [' + task_type + '].')

        task_instance = TaskClass(name, parent_task)

        return task_instance

    def load(self, instance, spec, recursive=False):
        """
        Loads data to a task instance from spec
        """
        if (u'@modelUri' in spec):
            instance.modelUri = spec['@modelUri']

        # handle all attributes
        for propKey, propVal in spec.iteritems():
            if (propKey[0] == TaskFactory.ATTR_PREFIX):
                instance.setAttribute(propKey[1:], propVal)

    # Private methods
    def _get_class(self, fqClassname):
        """
        Get class given a fully qualified classname, None if not found
        http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
        """
        self.logger.info("Loading class: " + fqClassname);

        parts = fqClassname.split('.')
        modulePart = ".".join(parts[:-1])
        #print ("*__import__ "+modulePart)
        module = __import__(modulePart)
        for attrName in parts[1:]:
            module = getattr(module, attrName, None)
            if module == None:
                return None
        return module