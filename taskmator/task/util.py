__author__ = 'ysahn'
import logging
from taskmator.task.core import Task
import subprocess


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

    def executeInternal(self, executionContext):
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
        if (self.getParam('skip', False)):
            self.logger.info("Skipping: " + cmdLine)
        else:
            self.logger.info("Running: " + cmdLine)
            code, out = self._runCommand(cmdLine)

        # Save the outcome
        if (self.retainOutcome):
            self.setOutcome(code, out)

        if (code != 0):
            self.logger.info("Command [" + cmdLine + "] failed with code:" + str(code))
            self.logger.debug("output:" + out)
            if (self.haltOnError):
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
            return (0, retval.strip())
        except subprocess.CalledProcessError as cpe:
            return (cpe.returncode, cpe.output);

'''
Task that runs a Shell Command line
The param must contain "command"
The command are OS specific.
'''
class OutputReportTask(Task):

    logger = logging.getLogger(__name__)

    def executeInternal(self, executionContext):
        self.logger.info ("Executing " + str(self))
        return 0
