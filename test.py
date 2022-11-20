import os

def verify_downloaded(file, path):
    for files in os.walk(path):
        print(files)
        if file in files:
            return True

verify_downloaded('test.py', 'videos/')