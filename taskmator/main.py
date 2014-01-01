import sys
import argparse
import logging
from taskmator.task import factory


class MainApp:

    logger = logging.getLogger("taskmator")
    def __init__(self):
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        logger.setLevel(logging.INFO)

    def execute(self):
        # Parse arguments
        parser = argparse.ArgumentParser(description="Task executor")
        parser.add_argument('-f', help="The task file in json.", default="taskmator")
        parser.add_argument('-loglevel', help="Log level")
        args = parser.parse_args()

        #logger.setLevel()

        task_factory = factory.TaskFactory()
        root_task = task_factory.loadRoot(args.f)
        root_task.execute()


main_app = MainApp()
main_app.execute()