Folder structure
----------------
+taskmator
  +task
    +core.py
    +util.py
  +context.py
  +factory.py
  +main.py

taskmator/task:
Contains all the task definitions

tasmator/context.py
Includes the ExecutionContext class which provides information of task in execution.
E.g. registry of task that is running or has completed.

tasmator/factory.py
Includes the Factory class which is responsible of creating the root task and it's inner tasks.

taskmator/task/core.py
Includes core task classes: the base Task, CompositeTask, EchoTask, SwitchTask, IterationTask.

taskmator/task/util.py
Includes basic utility tasks: CommandLineTask, OutputReportTask.
