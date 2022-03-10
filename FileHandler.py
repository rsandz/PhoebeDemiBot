import random
import os

def randomFile(filename, n):
    output = []
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f]
        choice = random.randint(0, (len(lines) / n) - 1)
        for x in range(n):
            output.append(lines[(choice * n) + x])
    return output

def writeFile(filename, lines):
    f = open(filename, "a")
    for line in lines:
        f.write("\n" + line)
    f.close()

def deleteFile(filename, n):
    with open(filename, "r+", encoding="utf-8") as file:
        for i in range(n):
            file.seek(0, os.SEEK_END)
            pos = file.tell() - 1
            while pos > 0 and file.read(1) != "\n":
                pos -= 1
                file.seek(pos, os.SEEK_SET)
            if pos > 0:
                file.seek(pos, os.SEEK_SET)
                file.truncate()