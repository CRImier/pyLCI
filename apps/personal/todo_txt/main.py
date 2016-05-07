menu_name = "TODO.txt"

import tasklib

from ui import Menu, Printer

import re

tasklist_filename = "/root/todo.txt"

i = None
o = None

storage = None

class TaskStorage():
    
    tasks = []
    file_contents = None
    projects = []
    contexts = []
 
    def __init__(self, filename):
        self.load_tasks(filename)

    def load_tasks(self, filename):
        f = open(filename, 'r')
        self.projects = []
        self.contexts = []
        for line in f.readlines():
            task = tasklib.Task(line.strip('\n'))
            for project in task.projects:
                self.projects.append(project)
            for context in task.contexts:
                self.contexts.append(context)
            self.tasks.append(task)
        self.projects = list(set(self.projects))
        self.contexts = list(set(self.contexts))
        f.seek(0)
        self.file_contents = f.read()
        print(self.projects)
        print(self.contexts)

def uncomplete_task(task):
    task.setPending()
    Printer("Task not complete!", i, o, 1)

def complete_task(task):
    task.setCompleted()
    Printer("Task complete!", i, o, 1)

def make_task_menu(task):
    task_contents = []
    task_contents.append(["Description", lambda: Printer(re.sub('<[^<]+?>', '', task.description), i, o)])
    if task.is_complete:
        task_contents.append(["Completed", lambda x=task: uncomplete_task(x)])
    else:
        task_contents.append(["Pending", lambda x=task: complete_task(x)])
    Menu(task_contents, i, o, "Task menu").activate()
    
def tasks_menu(uncompleted=False):
    menu_contents = []
    for task in storage.tasks:
        description = re.sub('<[^<]+?>', '', task.description)
        if uncompleted:
            if not task.is_complete:
                menu_contents.append([description, lambda x=task: make_task_menu(x)])
        else:
            menu_contents.append([description, lambda x=task: make_task_menu(x)])
    Menu(menu_contents, i, o, "Tasks menu").activate()

def projects_menu():
    menu_contents = []
    for project in storage.projects:
        description = re.sub('<[^<]+?>', '', task.description)
        menu_contents.append([description, lambda x=task: make_task_menu(x)])
    Menu(menu_contents, i, o, "Tasks menu").activate()

callback = None

def init_app(input, output):
    main_menu_contents = []
    global i, o, storage, callback
    i = input
    o = output
    storage = TaskStorage(tasklist_filename)
    main_menu_contents.append(["Uncompleted tasks", lambda: tasks_menu(uncompleted=True)])
    main_menu_contents.append(["All tasks", tasks_menu])
    main_menu_contents.append(["Projects", projects_menu])
    main_menu_contents.append(["Contexts", contexts_menu])
    callback = Menu(main_menu_contents, i, o, "Main menu").activate

#['_highest_priority', '_lowerCompleteness', '_lowest_priority', '_parseDate', '_parseWord', '_reset', 'completion_date', 'creation_date', 'decreasePriority', 'due', 'due_error', 'increasePriority', 'is_complete', 'is_future', 'keywords', 'priority', 'threshold', 'threshold_error']
