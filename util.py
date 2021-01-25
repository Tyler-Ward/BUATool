import hashlib
import os

def calculateSHA1Sum(filename):
    sha1 = hashlib.sha1()
    if(not os.path.isfile(filename)):
        raise ValueError("Provided path is not a file")
    with open(filename, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()
