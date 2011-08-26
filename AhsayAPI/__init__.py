#!/usr/bin/python3
import hashlib
from . import conf

import Crypto
from Crypto.Cipher import *
from Crypto.Hash import *

from lxml.etree import iterparse

import zlib
from time import strftime, gmtime

# from http://www.5dollarwhitebox.org/drupal/node/84
def to_size(bytes):
    def sizer(bytes):
        bytes = float(bytes)
        if bytes >= 1099511627776:
            terabytes = bytes / 1099511627776
            size = '%.2fTB' % terabytes
        elif bytes >= 1073741824:
            gigabytes = bytes / 1073741824
            size = '%.2fGB' % gigabytes
        elif bytes >= 1048576:
            megabytes = bytes / 1048576
            size = '%.2fMB' % megabytes
        elif bytes >= 1024:
            kilobytes = bytes / 1024
            size = '%.2fKB' % kilobytes
        else:
            size = '%d' % bytes
        return size
        
    if (isinstance(bytes, list)):
        r = []
        for b in bytes:
            r += [sizer(b)]
        return r
    else:
        return sizer(bytes)
        
'''Ahsay client version 5.8.x.x
jar function name class fsd.HId
I guess these will not be changed between versions,
because you can interchange data between different
server versions, and the encryption will be transfered as well,
so this data must be preserved''' 
def salt(s):
    '''
    @returns (encryption type, padding type, (password padding byte1, byte2), password salt)
    '''
    enc = ''
    if(s & 1):
        enc = ''
    elif(s & 0x2):
        enc = 'Twofish'
        raise ValueError('asd')
    elif(s & 0x4):
            enc = 'Blowfish'
    elif(s & 0x8):
        enc = 'DESede'
        raise ValueError('')
    elif(s & 0x10):
        enc = 'AES'
    elif(s & 0x20):
        enc = 'IDEA'
        raise ValueError('')
    pad = ''
    if(s & 0x100):
            pad = 'ECB'
    elif(s & 0x200):
            pad = 'CBC'
    elif(s & 0x1000):
            pad = 'NoPadding'
    elif(s & 0x2000):
            pad = 'PKC7Padding'

    l2 = s & 4294901760

    b1 = l2 >> 16 & 0xFF
    b2 = l2 >> 24 & 0xFF

    l = (s & 17587891077120) >> 32

    keyl = 128
    if s & 17592186044416:
            keyl = 128
    elif s & 35184372088832:
            keyl = 256
    elif s & 70368744177664:
            keyl = 512

    i = s & 281474976710656 == 0
    j = s & 281474976710656 == 0
   

    return (enc, pad, keyl, (b1, b2), l, i, j)

class GZStreamRead:
    def __init__(self, f, w=-15):
        self.f = f
        header = self.f.read(10)
        
        if header[:2] != b'\x1f\x8b':
            raise ValueError('Incorrect Header value: ', header)
            
        self.c = zlib.decompressobj(w)
        self.n = 0
        self.n_comp = 0
        
        self.bl = 256*256
        self.buffer = bytes()
    
    def _read(self, n):
        data = self.f.read(n)
        self.n_comp += len(data)
        data = self.c.decompress(data)
        self.n += len(data)
        return data
    
    def read(self, n):
        l = len(self.buffer)
        
        # if data read is completely in the buffer
        if l >= n:
            data = self.buffer[:n]
            self.buffer = self.buffer[n:]
            return data
        
        r = self.buffer
        self.buffer = bytes()
        n -= l
        if not n > self.bl:
            data = self._read(self.bl)
            r += data[:n]
            self.buffer = data[n:]
        else:
            r += self._read(n)
            
        return r
    
    def __str__(self):
        return '{}/{}'.format(*to_size([self.n_comp, self.n]))
        

class Cryptography:
    key = ''
    keyl = 128
    pad = ''
    enc = ''
    salt = (0,0)
    hashrounds = 0
    block_size = int(128/8)

    def __init__(self, key, s):
        opts = salt(s)
        self.enc = opts[0]
        self.pad = opts[1]
        self.keyl = opts[2]
        self.salt = opts[3]
        self.hashrounds = opts[4]
        self.key = self._genKey(key)
        self.alg = self.getCrypto()
        
        self.block_size = int(self.keyl/8)

    def _genKey(self, key):
        hashAlg = None
        if self.keyl == 128:
            hashAlg = MD5.new()
        elif self.keyl == 256:
            hashAlg = SHA256.new()
        elif self.keyl == 512:
            hashAlg = hashlib.sha512()
        else:
            hashAlg = MD5.new()    
    
        key = key.encode('UTF8')

        if self.hashrounds==0:
            return MD5.new(key).digest()

        paddedKey = key + bytes(self.salt)
        for i in range(0, self.hashrounds):
            hashAlg.update(paddedKey)

        return hashAlg.digest()        
    
    def decrypt(self, data):
        return self.alg.decrypt(data)
        
    def encrypt(self, data):
        return self.alg.encrypt(data)
        
    def getIV(self):
        IV = bytes()
        if self.keyl == 128:
            # MD5
            IV = MD5.new(self.key).digest()
        elif self.keyl == 256:
            IV = SHA256.new(self.key).digest()
        elif self.keyl == 512:
            # SHA512
            a = hashlib.sha512()
            a.update(self.key)
            IV = a.digest()
        else:
            #MD5
            IV = MD5.new(self.key).digest()            
            
        return IV
    
    def getCrypto(self):
        alg = None
        if self.enc == 'AES':
            alg = AES
        elif self.en == 'Blowfish':
            alg = Blowfish

        pad = None
        IV = None
        if self.pad == 'CBC':
            pad = alg.MODE_CBC
            IV = self.getIV()
        elif self.pad == 'ECB':
            pad = alg.MODE_ECB
        elif self.pad == 'NoPadding':
            raise ValueError('')
        elif self.pad == 'PKC7Padding':
            raise ValueError('')

        if not IV:
            return alg.new(self.key, pad)
        else:
            return alg.new(self.key, pad, IV)

class CryptographyStreamRead(Cryptography):
    def __init__(self, f, key, s):
        super().__init__(key, s)
        self.f = f
        self.min_read = super().block_size
        self.buffer = bytes()
        
    def read(self, n):
        l = len(self.buffer)
        # If our current buffer is longer than given
        if l >= n:
            r = self.buffer[:n]
            self.buffer = self.buffer[n:]
            return r
            
        # we have to fully return the buffer here
        r = self.buffer
        n -= l
        
        blocks_to_read = n // self.min_read
        leftover = n % self.min_read
        if leftover:
            blocks_to_read+=1
        decrypted = self.decrypt(self.f.read(blocks_to_read*self.min_read))
        return_to = blocks_to_read*self.min_read-(self.min_read-leftover)
        self.buffer = decrypted[return_to:]
        r += decrypted[:return_to]
        return r
        
class CryptoGZStreamRead():
    def __init__(self, f, key, s, w=-15):
        self.gz = GZStreamRead(CryptographyStreamRead(f, key, s), w)
        self.n = 0
    def read(self, n):
        data = self.gz.read(n)
        self.n += len(data)
        return data
        

        
class XMLFileInfo():
    type = 'Y' # F - file, T - treenode
    modified = 'E'
    created = 'T'
    path = 'N'
    permissions = 'FPMIT'

    job = 'J'


    size_enc = 'S'
    size = 'AOSIZE' # or 'O'

    seed = 0 #'C'
    
    def __init__(self, e):
        a = e.attrib
        
        self.type = a['Y']
        self.modified = int(a['E'])
        self.created = int(a['T'])
        self.path = a['N']
        self.unixpath = a['N'].replace('\\', '/')
        self.permissions = a['FPMIT']

        self.job = a['J']
        
        
        self.size_enc = int(a['S'])
        self.size = int(a['AOSIZE'])
        
        self.salt = int(a['C'])
        
    def __str__(self):
        return '{0} {1} {2} {4} ENC:{3} MOD:{5} CR:{6}'.format(self.type, self.path, self.size_enc, str(salt(self.salt)), self.size, 
               strftime("%a, %d %b %Y %H:%M:%S", gmtime(self.modified/1000)), strftime("%a, %d %b %Y %H:%M:%S", gmtime(self.created/1000)))
    
class XMLFileList():
    def __init__(self, source, callback=None, endcallback=None):
        self.source = source
        
        self.callback = self.stdcallback
        if callback:
            self.callback = callback
            
        self.endcallback = self.stdendcallback
        if endcallback:
            self.endcallback = endcallback
            
        self.n_files = 0
        self.n_size = 0
        self.n_size_enc = 0
        
        self.root = None
            
    def start(self):
        context = iterparse(self.source, ["start"])
        event, self.root = context.__next__()
        
        for (event, e) in context:
            self.callback(self, event, e)

        self.endcallback(self)
         
    def stdcallback(self, event, e):
        if e.tag == 'F':
            print(XMLFileInfo(e))
            f = XMLFileInfo(e)
            self.n_files+=1
            self.n_size += f.size
            self.n_size_enc += f.size_enc
            pass
        elif e.tag == 'ITEM_COUNT':
            print('Overall item count in dir: ', e.attrib['COUNT'])
        self.root.clear()
        
    def stdendcallback(self):
        pass
        
    def __str__(self):
        mean = 0
        if self.n_files > 0:
            mean = self.n_size/self.n_files
        r = [self.n_files] + to_size([self.n_size_enc, self.n_size, mean])
        print (r)
        return "File number: {0} [{3}] Size: {1}/{2}".format(*r)
