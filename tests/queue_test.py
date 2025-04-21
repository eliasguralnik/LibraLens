import queue
import time

q = queue.Queue()

q.put("1")
print(q.get())
time.sleep(2)
q.put("2")
print(q.get())
