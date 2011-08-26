import threading

class SimRW(threading.Thread):
    stream_out = bytes()
    
    size = None
    lock = None
    lock_out = None
    f = None
    daemon = True
    
    EOF = False
    
    def __init__(self, f, size=256*256*16):
        super().__init__()
        self.lock = threading.Lock()
        self.lock_out = threading.Lock()
        
        self.f = f
        self.size = size
        
        self.lock.acquire()
        self.lock_out.acquire()
        
        self.start()
        
    def read(self, n):
        #print('SimRW: reading {} bytes in MAIN'.format(n))
        data = bytes()
        while n > 0:
            if not len(self.stream_out) and self.EOF:
                break
            elif not len(self.stream_out):
                self.lock_out.release()
                self.lock.acquire()
            
            if len(self.stream_out) >= n:
                data += self.stream_out[:n]
                self.stream_out = self.stream_out[n:]
                n = 0
            else:
                nread = len(self.stream_out)
                n -= nread
                data += self.stream_out
                self.stream_out = bytes()
        return data
        
        
    def run(self):
        # This object's activity
        while True:
            #print('SimRW: reading {} bytes in READER'.format(self.size))
            stream_tmp = self.f.read(self.size)
            if not len(stream_tmp):
                self.EOF = True
                try:
                    self.lock.release()
                except threading.ThreadError:
                    pass
                break
            self.lock_out.acquire()
            self.stream_out = stream_tmp
            self.lock.release()
            
        print('SimRW: simureader stopped')