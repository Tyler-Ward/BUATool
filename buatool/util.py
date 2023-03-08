import hashlib
import os
import subprocess

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


def calculateMediaChecksum(filename):
    if filename.split(".")[-1] not in ["mp3","flac"]:
        return None
    process = subprocess.Popen([
        "ffmpeg",
        "-i",
        filename,
        "-map","0:a",
        "-codec","copy",
        "-hide_banner",
        "-loglevel","warning",
        "-f","md5",
        "-"
        ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode("utf8").split('=')[1].strip()


