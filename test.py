from multiprocessing.managers import SharedMemoryManager
from multiprocessing import Process

import pickle

from bin.engine import handler

import time


def major(sm):
    sm.buf[4] = 0
    while sm.buf[0]:
        if sm.buf[2]:
            sm.buf[4] += 1
            sm.buf[3] = True
            sm.buf[2] = False
            print(sm.buf[4], "add 1")
        else:
            time.sleep(0.5)
        if sm.buf[4] > 20:
            sm.buf[0] = False
            sm.buf[1] = False
            sm.buf[2] = False


def minor(sm):
    while sm.buf[0]:
        if not sm.buf[3]:
            time.sleep(0.5)
        else:
            sm.buf[3] = False
            sm.buf[2] = True
            sm.buf[4] += 2
            print(sm.buf[4], "add 2")


if __name__ == "__main__":
    # shared mem manager
    smm = SharedMemoryManager()
    smm.start()

    # 16 byte shared memory
    s1 = smm.SharedMemory(size=16)
    # set run to True
    s1.buf[0] = True

    print(s1)

    # now create 2 processes that will wait for the other to finish
    # process 1 runs first, then process 2 will run
    # set variables
    s1.buf[2] = True
    s1.buf[3] = False

    chunk = handler.Chunk(0, 0)
    print(chunk.pos, chunk.pos_offset)
    pickled_chunk = pickle.dumps(chunk, protocol=1)
    print(len(pickled_chunk))
    s1.buf[20:20+len(pickled_chunk)] = pickled_chunk

    s1.buf[10:20] = b"0123456789"

    unpickled_chunk = pickle.loads(s1.buf[20:20+len(pickled_chunk)])
    print(unpickled_chunk, unpickled_chunk.pos, unpickled_chunk.pos_offset)

    print(", ".join([str(x) for x in s1.buf]))

    # p1 = Process(name="major", target=major, args=(s1,))
    # p2 = Process(name="minor", target=minor, args=(s1,))
    #
    # p1.start()
    # p2.start()
    #
    # p1.join()
    # p2.join()

    s1.close()
