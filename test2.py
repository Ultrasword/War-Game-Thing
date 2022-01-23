import numpy as np

with open("file.chk", 'rb') as file:
    data = file.read()
    file.close()

array = np.frombuffer(data, dtype=np.uint8)





