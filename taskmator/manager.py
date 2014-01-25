import collections
import logging
import json
from taskmator.context import TaskContainer, ExecutionContext

class TaskManager:
    """
    The class that manages tasks.
    There could be multiple specification loaded.
    """

    def __init__(self):
        self.task_containers = {}

    def start_task(self, spec_uri):
        """
        Starts a task
        """
        task_container = None
        if (spec_uri in self.task_containers):
            task_container = self.task_containers[spec_uri]
        else:
            spec = self.load_spec(spec_uri)
            task_container = TaskContainer(spec)
            self.task_containers[spec_uri] = task_container

        task_root = task_container.get_root()
        context = self.create_context(task_container)
        context.mark_start()
        task_root.execute(context)
        context.mark_stop()
        return context

    def create_context(self, task_container):
        return ExecutionContext(task_container)

    def load_spec(self, spec_uri):
        """
        Method to load a tasks specification
        """
        spec = None
        with open(spec_uri, "r") as spec_file:
        #spec_file = open(spec_uri, "r")
            spec_json = spec_file.read()
            spec = json.loads(spec_json, object_pairs_hook=collections.OrderedDict)
        return spec
