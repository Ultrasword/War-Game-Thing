from multiprocessing import Process
from multiprocessing.shared_memory import SharedMemory, ShareableList


import threading
import time
from queue import PriorityQueue
from collections import deque


HEAVY = 0
MEDIUM = 1
LIGHT = 2

heavy_task_queue = PriorityQueue()
medium_task_queue = PriorityQueue()
light_task_queue = PriorityQueue()
heavy_queue_size = 0
pause_update_loops = 0
pause_counter = 0
thread_handler = None
thread_lock = None
running = False
current_heavy_tasks = deque([None, None])
current_light_tasks = deque([None, None, None, None, None])

has_new_task = False


# TODO - we make lighter computations - make it so that the computer runs each process
#       in chunks compared to a bulk. This should reduce in game lag by a bit


def queue_heavy_task(task):
    global heavy_task_queue, heavy_queue_size
    heavy_task_queue.put(task)
    heavy_queue_size += 1


def queue_light_task(task):
    global light_task_queue
    light_task_queue.put(task)


def set_pause_loops(p_wait):
    global pause_update_loops
    pause_update_loops = p_wait


def run_task(task, world, dt):
    next_task = task.get_next_task()
    if next_task:
        next_task(world, dt)


def update_light_task(world, dt):
    global light_task_queue, current_light_tasks
    for i in range(5):
        if not current_light_tasks[i] and not light_task_queue.empty():
            current_light_tasks[i] = light_task_queue.get()
        if current_light_tasks[i]:
            current_light_tasks[i].get_next_task()(world, dt)
            if current_light_tasks[i].finished:
                current_light_tasks[i].post_completion(world, dt)
                current_light_tasks[i] = None


def update_heavy_task(world, dt):
    global current_heavy_tasks, heavy_task_queue, heavy_queue_size, pause_update_loops, pause_counter
    if pause_counter > pause_update_loops:
        pause_counter = 0
        if heavy_queue_size > 0:
            for i in range(2):
                if not current_heavy_tasks[i] and not heavy_task_queue.empty():
                    current_heavy_tasks[i] = heavy_task_queue.get()
                if current_heavy_tasks[i]:
                    current_heavy_tasks[i].get_next_task()(world, dt)
            for i in range(2):
                if current_heavy_tasks[i]:
                    if current_heavy_tasks[i].finished:
                        current_heavy_tasks[i].post_completion(world, dt)
                        current_heavy_tasks[i] = None
                        heavy_queue_size -= 1
    pause_counter += 1


def multiprocess_handler(shared_memory):
    print("outputting data in thread")
    print(shared_memory.buf)
    while shared_memory.buf[0]:
        print("is true")
        time.sleep(0.1)
    shared_memory.unlink()


class Task(object):
    def __init__(self, weight):
        self.weight = weight
        self.current_task = 0
        self.tasks = []
        self.finished = False

    def get_next_task(self):
        self.current_task += 1
        if len(self.tasks) > self.current_task:
            if self.current_task + 1 >= len(self.tasks):
                self.finished = True
            return self.tasks[self.current_task-1]

    def queue_task(self, task):
        self.tasks.append(task)

    def post_completion(self, world, dt):
        pass

    def __lt__(self, other):
        return self.weight < other.weight

    def __gt__(self, other):
        return self.weight > other.weight

    def __le__(self, other):
        return self.weight <= other.weight

    def __ge__(self, other):
        return self.weight >= other.weight
