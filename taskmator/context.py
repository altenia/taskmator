import collections
import datetime
import re
import logging


class ExecutionContext:

    logger = logging.getLogger(__name__)

    def __init__(self):
        self.execStartTime = datetime.datetime.now()
        self.execStopTime = None
        self.registry = collections.OrderedDict()

    def close(self):
        """
        Mark this context as terminated
        """
        self.execStopTime = datetime.datetime.now()

    def registerTask(self, taskName, taskRef):
        self.registry[taskName] = taskRef

    def lookupTask(self, taskName):
        if (taskName in self.registry):
            return self.registry[taskName]
        else:
            return None

    def tasks(self, namePattern = None, state = None):
        """
        Returns a list of tasks that matches specified criteria
        @param name -- the name pattern to searh
        @param state -- the task state
        """
        result = []
        for task in self.registry:
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

