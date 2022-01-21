import time
import pickle


# -------------------------------- task handling method --------------------- #
def handle_tasks(shared, data, i):
    # access results - results.shm[x] = value - use pickled strings
    # access shared - shared.buf[x] = value
    try:
        while shared.buf[0]:
            # set has room to False
            shared.buf[i] = True
            # now we pause as we wait
            shared.buf[i + data.thread_count] = True
            task, args = data.rec.recv()
            print("process ", i, task)
            task = task(shared, args)
            # finished task - has room = True
            shared.buf[i] = False
            # run task
            task.run(data.send, i)
            while shared.buf[i+data.thread_count]:
                # check if there is a task every 0.1 seconds
                time.sleep(0.1)
    except Exception as e:
        print("There was an error, abort!")
        print(e)
        # maybe send an error to thread
        # data.send("EROR"!)
    finally:
        print("Closed process ", i)


def test(active, world, receive_port):
    try:
        while active.active:
            complete_func = receive_port.recv()
            complete_func[0](world, complete_func[1:])
    except Exception as e:
        print(e)
    finally:
        print("Closed thread whatever")

# -------------------------------- -------------------- --------------------- #


class Task(object):
    def __init__(self, shared_memory, args=None):
        self.shared = shared_memory
        self.finished = False

    def run(self, host, uid):
        pass

    def post_completion(self, world):
        pass
