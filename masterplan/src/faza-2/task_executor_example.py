# Task Executor Example

from litecrewai.task import Task, TaskExecutor

task1 = Task("Research Python trends")
task2 = Task("Write summary", dependencies=[task1])
task3 = Task("Create presentation", dependencies=[task2])

executor = TaskExecutor()
results = executor.run([task1, task2, task3])