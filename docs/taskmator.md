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

Task Execution
--------------
The task specification runs in the following manner:
All task specification must contain a root task which is a composite task.
When the root task is started, it executes the sub-task(s) in the following
1. If "@exec" attribute is defined, then the sub-task specified in the
attribute is executed. This is called explicit task execution.
2. If there is no "@exec" then it searches for the sub-task named "default"
and executes it.

Note that the "@exec" can contain an array of named-task declarations or calls (anonymous).

Task characteristics
--------------------
### Design Considerations ###
- Named leaf tasks should be accessible to query its state
- The output of the leaf tasks should be captured and accessible by other tasks
- The above should accomodate for branching and loops (Switch and Loop)
- The above should accomodate for nested tasks through composite tasks

### Named Leaf Tasks ###
Named leaf tasks are those which the task is named, and which the parents
composite tasks are named up to the root.
These tasks maintains state and can be referenced (executed) by other tasks.
The @params specified in the task are default parameters values that can be
overriden when executed from other task by specifying the @args.

### Execution Context: ###
The Execution Context contains three main structures:
- The Abstract Syntax Tree (AST)
- The Named-Task Registry
- The Output ExecutionTrace

#### Abstract Syntax Tree ####
Just the JSON representation as loaded by Python json module.
This structure is used by the Runtime (task) when lazily instantiating named tasks.
Also to instantiate anonymous tasks on-demand.

#### Named-Task registry ####
The named-task registry contains references to the task using the fully qualified name (FQN).
The FQN has direct one-to-one mapping to the AST hierarchical namespace.
Note that Switch and Iteration Tasks cannon contain subtask (they can only
execute) other named tasks.

#### Output Execution Trace ####
The Node Tasks (those in the core: CompositeTasks, Switch, and Loop) can
possibly hold outcome state (unless the task is anonymous)

The outcome state can be retrieved from the ExecutionContext's execution trace (an OreredDictionary)

The id used in the execution trace is the Execution stack path:
root/<ct-name>[/<ct-name>|[idx]>]/<leaf-task-name>
In case of switch
root/<case-name>[/<ct-name>|[idx]>|]/<leaf-task-name>
in case of loop
root/<iterator>[/<ct-name>|[idx]>]/<leaf-task-name>
Where
- ct-name is CompositTask's name
- <idx> is the index if the the name

Implementation
--------------

### Task Loading & Instantiation ###


### ExecutionContext structure ###

ExecutionContext: {
    task_ast: { <task-spec> }
    task_registry: {
        {<fqn>: <reference to the task>}, ...
    }
    <synchronized:OrderedDictionary> execution_trace: [
        # In the order of start time (or end time?)
        {<execution-stack-path>: {
            "start_time": <ISO-time>,
            "end_time: <ISO-time>,
            "code":<numeric exit code>,
            "output": {Output any structure}
            }
        }, ...
    ]
}