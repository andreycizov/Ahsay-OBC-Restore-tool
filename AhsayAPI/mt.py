'''
Multithreaded classes for file IO
'''
from threading import *
import gc
from . import XMLFileList as FL, XMLFileInfo as XF, CryptoGZStreamRead
from . import urls
from . import conf
import time
import sys
import os
import io
from urllib.error import URLError


file_err_count = 0

def get_file_err_count():
 global file_err_count
 return file_err_count

class DifThread(Thread):
    def __init__(self, rjob, file, semaphore):
        self.file = file
        self.lock = semaphore
        super().__init__()
        self.daemon = True
        self.rjob = rjob
        
    def path(self, file):
        return conf.o('root') + file.unixpath    
        
    def checkifexists(self, file):
        path = self.path(file)
        # use file modification date here instead
        try:
            if os.stat(path).st_mtime  == file.modified // 1000:
                 return False
            else:
                 print("File modification time is different:", path)
                 return True
        except OSError as e:
            print('File does not exist', path)
            return True
    
    def afterwrite(self, file):
        # update file modification date here
        os.utime(self.path(file), (file.created//1000, file.modified//1000))
        
    def filewrite(self, file):
        path = self.path(file)
        try:
            #path = self.path(file)
            if not self.checkifexists(file):
                return
            r = None
            while True:
             try:
               r = urls.urlopen(urls.restoreFile({
               'restorejob': self.rjob,
               'path': file.path
               }))
               break
             except URLError as e:
                print("URLError while openning file:", path, ":", e)
                time.sleep(0)
            
            data = r.read(2)
            if data != b'00':
                data += r.read(100)
                raise ValueError('Invalid file type: {}'.format(data))
            
            r = CryptoGZStreamRead(r, conf.o('password'), file.salt)
            f = open(path, 'w+b')
            while True:
                data = r.read(262144)
                if not len(data):
                    f.close()
                    break
                f.write(data)
            # should do that after file close, since the system should update the modification date after.
            self.afterwrite(file) 
            return True
        except:
            print('Exception raised:',sys.exc_info(),'at file:', file, 'unixpath', path)
            global file_err_count
            file_err_count += 1
            return False

class FastThread(DifThread):
    def run(self):
        i = 0
        for f in self.file:
            if not self.filewrite(f):
               i+=1
        self.lock.release()
        return i
     
class SlowThread(DifThread):
    def run(self):
        i = 0
        if not self.filewrite(self.file):
           i = 1
        self.lock.release()
        return i
        #print("Slow file downloaded", self.file.unixpath)

class FileListerMT(FL):
    def threadstart(self):
        class Reader(Thread):
            def run(self):
                self.filelister.start()
        self.t = Reader()
        self.t.filelister = self
        self.t.daemon = True
        self.t.start()
        
    def is_alive(self):
        return self.t.is_alive()
        
class FileThreadManager():
    def __init__(self, rjob, fast_number=200, slow_threads=50, fast_threads=60):
        self.lock_fast = Semaphore(fast_threads)
        self.lock_slow = Semaphore(slow_threads)
        self.fast_buffer = []
        self.fast_max = fast_number
 
        self.m_slow = slow_threads        
        self.m_fast = fast_threads

        self.rjob = rjob
        
    def fast(self, f):
        '''
        takes a list of nodes as a parameter
        '''
        self.fast_buffer += [f]
        if len(self.fast_buffer) == self.fast_max:
            self.lock_fast.acquire()
            FastThread(self.rjob, self.fast_buffer, self.lock_fast).start()
            self.fast_buffer = []
            
        
    def slow(self, file):
        self.lock_slow.acquire()
        SlowThread(self.rjob, file, self.lock_slow).start()
        #print("Added new slow thread")
    

class XMLFileList_FS():
    def __init__(self, f, buffer_size=16384,filename='./tmp.tmp'):
        self.lock = Semaphore()
        self.completed = False
        
        self.f = f
        
        self.w = open(filename, 'w+b')
        self.r = open(filename, 'rb')
        
        self.buffer = buffer_size
        self.rw = io.BufferedRWPair(self.r,self.w, buffer_size=buffer_size)
        
        self.current = 0
        self.current_read = 0
        
        class Reader(Thread):
            daemon = True
            def run(self):
                print('Writing to local file thread started')
                while True:
                    data = self.inst.f.read(self.inst.buffer)
                    self.inst.current += len(data)
                    self.inst.rw.write(data)
                    self.inst.rw.flush()
                    self.inst.lock.release()
                    if len(data) == 0:
                        break
                self.inst.w.close()
                self.inst.completed = True
		
                print('Writing to local file thread stopped')
                    
        self.thread_reader = Reader()
        self.thread_reader.inst = self
        
        self.thread_reader.start()
        
    def read(self, size):
        r = bytes()
        while size:
            data = self.rw.read(size)
            r += data
            l = len(data)
            self.current_read += l
            if l < size and not self.completed:
                self.lock.acquire()
            else:
                break
            size -= l
        return r
        
    def join(self):
        self.thread_reader.join()
        
    def is_alive(self):
        return self.thread_reader.is_alive()
