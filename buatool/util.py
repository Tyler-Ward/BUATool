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
    output_split = stdout.decode("utf8").strip().split('=')

    if len(output_split)==2:
        return output_split[1]
    else:
        return None


