import abc
import logging
import json

'''
abstract class for all Task
'''
class Task:
    __metaclass__ = abc.ABCMeta

    __VALID_ATTRS = [u'aliases', u'description', u'dependsOn', u'version',
        u'modelUri', u'params', u'namespaces', u'load', u'haltOnError', u'type'
        ]

    modelUri = None
    aliases = None
    namespaces = None
    description = None
    params = None
    haltOnError = False

    _parent = None
    _children = []

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.__class__.__name__ + ":" + self.name;

    def setAttribute(self, attrKey, attrVal):
        if (attrKey in self.__VALID_ATTRS):
            setattr(self, attrKey, attrVal)
        else:
            raise Exception('Invalid Attribute "' + attrKey + '"')

    def getParam(self, key, default=None):
        if (key in self.params):
            return self.params[key]
        else:
            default

    def hasParam(self, key):
        if (key in self.params):
            return True

    def setParent(self, parent):
        self._parent = parent

    def getParent(self):
        return self._parent

    def getRootParent(self):
        node = self
        while node._parent is not None:
            node = node._parent
        return node

    def addChild(self, child):
        self._children.append(child)

    def getChildren(self):
        return self._children

    def getChildAt(self, idx):
        self._children[idx]

    def validateParam(self):
        return True

    @abc.abstractmethod
    def execute(self):
        '''Concrete classes muse implement this method'''
        return

class CompositeTask(Task):

    logger = logging.getLogger(__name__)

    # Double underscore makes unique namespace for this class
    __VALID_ATTRS = [u'tasks', u'task', u'execMode']

    def __init__(self, name):
        super(CompositeTask, self).__init__(name)

    def setAttribute(self, attrKey, attrVal):
        if (attrKey in self.__VALID_ATTRS):
            setattr(self, attrKey, attrVal)
        else:
            super(CompositeTask, self).setAttribute(attrKey, attrVal)

    def traverse(self):
        self.__traverse(self)

    def __traverse(self, node):
        print (str(node) + "+" + str(len(node.getChildren())))
        if (len(node.getChildren()) > 0):
            for child in node.getChildren():
                self.__traverse(child)

    def execute(self):
        self.logger.info ("Executing " + str(self))
        for child in self.getChildren():
            print (str(child))
            #child.execute()
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
        self.logger.info ("Executing " + __name__)
        cmdLine = None
        if (self.getParam('ssh', False)):
            if ( not self.hasParam('remoteLogin') or not self.hasParam('sshKeyLocation') ):
                self.logger.warning("Cannot ssh, missing remoteLogin or sshKeyLocation.");
                return -1;
            # Wrap the command with ssn connection
            cmdLine = self._buildSshCommand(self.sshKeyLocation, self.remoteLogin, self.getParam('command'))
        else:
            cmdLine = self.getParam('command')

        code=0; out=""
        if (self.getParam('skipExecution', False)):
            self.logger.debug("Skipping: " + cmdLine)
        else:
            self.logger.debug("Executing: " + cmdLine)
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

    def validateParam(self):
        if ( not 'command' in self.params):
            return False
        return True

    def execute(self):
        self.logger.info ("Executing " + self.__class__.__name__)
        return 0


