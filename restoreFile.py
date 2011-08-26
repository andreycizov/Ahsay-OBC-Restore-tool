#!/usr/bin/python3
from urllib.request import urlopen
import gzip

from AhsayAPI import CryptoGZStreamRead
import binascii
import sys
import zlib
r = urlopen('https://example.com:5999/obs/restore/obm5.5/restoreFile.do?u=login', 'PWD=password&RJOB=restore_job_id&BSET=backup_set&LOGIN=login&BJOB=Current&PATH=path_to_file.sh&TYPE=F'.encode())

f = open('output', 'bw+')

data = r.read(2)
if data != b'00':
    raise ValueError('Invalid file type')
    
stream = CryptoGZStreamRead(r, "user_encryption_password", 'ahsay_integer_salt')
while True:
    data = stream.read(256*256)
    print(len(data))
    print(data)
    if not len(data):
        break
    f.write(data)

f.close()        




