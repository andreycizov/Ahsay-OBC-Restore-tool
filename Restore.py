#!/usr/bin/python3
'''
Ahsay incremental backup rewritten from the example of OBC.


'''
from urllib.parse import quote
from AhsayAPI.urls import *

from AhsayAPI import GZStreamRead as GZ
from AhsayAPI import XMLFileList as FL
from AhsayAPI.mt import XMLFileList_FS as FSFL, FileListerMT
from AhsayAPI import XMLFileInfo
from AhsayAPI.mt import FileThreadManager, get_file_err_count
from AhsayAPI import to_size
from SimRW import SimRW
import threading

from datetime import *

import time

import sys
import os
from AhsayAPI import conf
print (datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

restoreJobID = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
r = urlopen(startRestore({
'restorejob':restoreJobID,
#'path':"E:\\",
'path':"\\\\",
'backupjob':'Current'
#'backupjob':'2011-06-28-19-00-03'
}))
print(r.getheaders())
start = time.time()

num_failed = 0

def callback(self, event, e):  
    global num_failed
    if e.tag == 'F':
        f = XMLFileInfo(e)
        
        # Create a directory (ensure the directory exists before uploading a file there)
        if f.type == "T":
            try:
                 os.mkdir(conf.o('root')+f.unixpath)
            except OSError:
                #print("Directory already exists: {}".format(f.path))
                pass
        # Create a small file
        elif f.type == "F" and f.size < 1000000:
            self.threads.fast(f)
            pass
        # Create a large file
        # enhancement - add small files if we'll wait for thread
        elif f.type == "F":
            self.threads.slow(f)
            pass
            #print(e.tag,'|',e.attrib)
        else:
            print(f)
    e.clear()
    self.root.clear()

threads =  FileThreadManager(restoreJobID)

def endcallback(self):
    print("XML reading thread stopped, locking thread manager")
    global threads
    for i in range(0, threads.m_slow):
     threads.lock_slow.acquire()
    for i in range(0, threads.m_fast):
     threads.lock_fast.acquire()
    print("XML: Thread manager locked, exiting")
    pass    
# The XML stream is GZipped
#stream = FSFL(GZ(SimRW(r)), 16384)
stream = FSFL(GZ(r), 163840)

fileLister = FileListerMT(stream, callback, endcallback)
fileLister.threads = threads
fileLister.threadstart()

while fileLister.is_alive():
    try:
        time.sleep(0.3)
        sys.stdout.write('{}/{} Active Couunt: {} Time Passed: {}              \r'.format(*to_size([stream.current_read, stream.current, threading.active_count()])+[time.time()-start]))
    except:
        print("Restore stopped by user")
        break

r = urlopen(endRestore({'restorejob':restoreJobID}))
print(r.getheaders())
f = r
data = f.read(10000).decode('utf8')
if data == '<OK/>':
    print("Restore successfully completed")
else:
    print("Restore unsuccessful")
    print(data)

print('Time it took me to restore:',time.time()-start, 'Current file pointer:{}/{}'.format(stream.current_read, stream.current))
print('Number of failed files is: {}'.format(get_file_err_count()))
