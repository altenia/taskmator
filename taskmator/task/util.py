__author__ = 'ysahn'
import logging
from taskmator.task.core import Task
import subprocess
import sys
import string



class CommandLineTask(Task):
    """
    Task that runs a Shell Command line
    The param must contain "command"
    The command are OS specific.
    """
    logger = logging.getLogger(__name__)

    def validateParam(self):
        if ( not 'command' in self.params):
            return False
        return True

    def executeInternal(self, executionContext):
        #print ("***"+__name__)
        self.logger.info ("Executing " + str(self))
        cmdLine = None
        if (self.getParam('ssh', False)):
            #print("@"+ str(self.getParams()))
            if ( not self.hasParam(u'remoteLogin') or not self.hasParam(u'sshKeyLocation') ):
                self.logger.warning("Cannot ssh, missing remoteLogin or sshKeyLocation.");
                return -1;
            # Wrap the command with ssn connection
            sshKeyLocation = self.getParam('sshKeyLocation')
            remoteLogin = self.getParam('remoteLogin')
            command = self.getParam(u'command')
            cmdLine = self._buildSshCommand(sshKeyLocation, remoteLogin, command)
        else:
            cmdLine = self.getParam(u'command', None, executionContext)

        code = Task.CODE_OK; out = ""
        #if (self.getParam('skipExecution', False)):
        if (self.getParam('skip', False)):
            self.logger.info("Skipping: " + cmdLine)
            code = Task.CODE_SKIPPED
        else:
            self.logger.info("Running: " + cmdLine)
            code, out = self._runCommand(cmdLine)

        # Save the outcome
        self.setResult(out)

        if (code != 0):
            self.logger.info("Command [" + cmdLine + "] failed with code:" + str(code))
            self.logger.debug("output:" + out)
            if (self.haltOnError):
                self.logger.info( "Task [" + self.name + "] Halted.")
                return code

        self.logger.info("Task [" + self.name + "] Completed.")
        return code

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
            # debug
            #retval = shellCommand
            return (0, retval.strip())
        except subprocess.CalledProcessError as cpe:
            return (cpe.returncode, cpe.output);


class OutputReportTask(Task):
    """
    Task that prints out the output of all other tasks.
    This task is usually run at the end
    """
    logger = logging.getLogger(__name__)

    def executeInternal(self, executionContext):
        stream_type = self.getParam('stream', False)
        format = self.getParam('format', "[${type}] ${name} (${outcome_code}) ${outcome_result}")
        writer = None
        is_file = False
        if (stream_type == "console"):
            writer = sys.stdout
        elif (stream_type.startswith("file")):
            is_file = False
            filename = stream_type[5:]
            writer = open(filename, "w")

        tasks = executionContext.tasks()
        for task in tasks:
            entry = {"type": task.getTypename(),
                     "name": task.getFqn(),
                     "outcome_code": task.getOutcome()[0],
                     "outcome_result": task.getOutcome()[1]
            }
            tpl = string.Template(format)
            reportrow = tpl.safe_substitute(entry)
            writer.write(reportrow + "\n")

        if (is_file):
            writer.close()

        self.setResult(None)

        return Task.CODE_OK

class CronTask(Task):
    """
    Task that runs a Shell Command line
    The param must contain "command"
    The command are OS specific.
    """

    logger = logging.getLogger(__name__)

    def executeInternal(self, executionContext):
        self.logger.info("Executing " + str(self))
        return Task.CODE_OK
