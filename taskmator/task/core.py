import abc
import copy
import logging
import json
import subprocess
import collections

#debugger
#import pudb; pu.db


'''
abstract class for all Task
'''
class Task:
    __metaclass__ = abc.ABCMeta

    __VALID_ATTRS = [u'aliases', u'description', u'dependsOn', u'version',
        u'modelUri', u'params', u'namespaces', u'load', u'haltOnError', u'precond', u'decl', u'type'
        ]

    def __init__(self, name, parent = None):
        self.init(name, parent)

        self.modelUri = None
        self.aliases = None
        self.namespaces = None
        self.description = None
        self.params = None
        self.haltOnError = False

    def __str__(self):
        return  self.getFqn() + " ["+self.__class__.__name__+"]";

    def init(self, name, parent = None):
        self.name = name
        self.parent = parent
        if (parent):
            parent.addChild(self)
        self.children = collections.OrderedDict()

    def copy(self, name, parent):
        """
        Retuns a copy of this tasks with a new name. 
        All fields are deep copied except for parent and children
        """
        nameTemp = self.name
        parentTemp = self.parent
        childrenTemp = self.children
        self.name = None
        self.parent = None
        self.children = None

        copyInstance = copy.deepcopy(self)
        copyInstance.init(name, parent)

        self.name = nameTemp
        self.parent = parentTemp
        self.children = childrenTemp

        
        parent.addChild(copyInstance)

        return copyInstance

    def setAttribute(self, attrKey, attrVal):
        if (attrKey in self.__VALID_ATTRS):
            setattr(self, attrKey, attrVal)
        else:
            raise Exception('Invalid Attribute "' + attrKey + '"')

    def getParams(self):
        #
        retval = self.params.copy()
        node = self
        #print ("**"+ str(node) + " --" + str(node.parent))
        while (node.parent):
            for key, val in node.params.items():
                if (key not in retval):
                    retval['key'] = val
            node = node.parent

        return retval

    def getParam(self, key, default=None):
        params = self.getParams()
        if (key in params):
            return params[key]
        else:
            default

    def setParams(self, params):
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

    def validateParam(self):
        return True

    @abc.abstractmethod
    def execute(self):
        '''Concrete classes muse implement this method'''
        return


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


class CompositeTask(Task):

    logger = logging.getLogger(__name__)

    # Double underscore makes unique namespace for this class
    __VALID_ATTRS = [u'default', u'tasks', u'execMode']

    def __init__(self, name, parent):
        # Group of tasks, it could be run sequentially or parallel depending on @execMode
        self.group = []
        super(CompositeTask, self).__init__(name, parent)

    def setAttribute(self, attrKey, attrVal):
        if (attrKey in self.__VALID_ATTRS):
            setattr(self, attrKey, attrVal)
        else:
            super(CompositeTask, self).setAttribute(attrKey, attrVal)


    def execute(self):
        self.logger.info ("Executing " + str(self))
        for name, child in self.getChildren():
            #print (str(child))
            child.execute()
        return 0

'''
Task that runs a Shell Command line
The param must contain "command"
The command are OS specific.
'''
class CommandLineTask(Task):

    logger = logging.getLogger(__name__)

    def validateParam(self):
        if ( not 'command' in self.params):
            return False
        return True

    def execute(self):
        self.logger.info ("Executing " + str(self))
        cmdLine = None
        if (self.getParam('ssh', False)):
            #print("@"+ str(self.getParams()))
            if ( not self.hasParam(u'remoteLogin') or not self.hasParam(u'sshKeyLocation') ):
                self.logger.warning("Cannot ssh, missing remoteLogin or sshKeyLocation.");
                return -1;
            # Wrap the command with ssn connection
            cmdLine = self._buildSshCommand(self.sshKeyLocation, self.remoteLogin, self.getParam(u'command'))
        else:
            cmdLine = self.getParam(u'command')

        code=0; out=""
        #if (self.getParam('skipExecution', False)):
        if (True):
            self.logger.info("Skipping: " + cmdLine)
        else:
            self.logger.info("Executing: " + cmdLine)
            code, out = self._runCommand(cmdLine)

        if (code != 0):
            self.logger.info("Command [" + command[0] + "] failed with code:" + str(code))
            self.logger.debug("output:" + out)
            if (haltOnError):
                self.logger.info( "Task [" + self.name + "] Halted.")
                return code
        
        self.logger.info("Task [" + self.name + "] Completed.")
        return 0

    def _buildSshCommand(self, keyLocation, host, remoteCommand):
        """
        Returns a string of an ssh command
        @param keyLocation   - the location of the key for ssh
        @param host          - the remote host to ssh
        @param remoteCommand - the command to execute in the remote host
        """
        cmd = "sudo ssh -i  " + keyLocation + " " + host + " " + "\"" +remoteCommand + "\""
        return cmd

    def _runCommand(self, shellCommand):
        """
        Runs a (shell) command. 
        @param shellCommand - the shell command to run
        """
        try:
            retval = subprocess.check_output( shellCommand, shell=True, stderr=subprocess.STDOUT)
            return (0, retval)
        except subprocess.CalledProcessError as cpe:
            return (cpe.returncode, cpe.output);



'''
Task that runs a Shell Command line
The param must contain "command"
The command are OS specific.
'''
class CronTask(Task):

    logger = logging.getLogger(__name__)

    def execute(self):
        self.logger.info ("Executing " + str(self))
        return 0


'''
Task that Does switch case
'''
class SwitchTask(Task):

    logger = logging.getLogger(__name__)

    def execute(self):
        self.logger.info ("Executing " + str(self))
        return 0

'''
Task that does Iteration
'''
class IterationTask(Task):

    logger = logging.getLogger(__name__)

    # Double underscore makes unique namespace for this class
    __VALID_ATTRS = [u'for', u'execute']

    def setAttribute(self, attrKey, attrVal):
        if (attrKey in self.__VALID_ATTRS):
            setattr(self, attrKey, attrVal)
        else:
            super(IterationTask, self).setAttribute(attrKey, attrVal)

    def execute(self):
        self.logger.info ("Executing " + str(self))
        return 0

