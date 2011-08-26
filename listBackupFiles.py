#!/usr/bin/python3
from AhsayAPI import GZStreamRead as GZ
from AhsayAPI import XMLFileList as FL
from AhsayAPI import XMLFileInfo
from AhsayAPI import to_size
from AhsayAPI import salt
from AhsayAPI.urls import ls
from AhsayAPI.urls import urlopen
import sys

t = ls({'dir':sys.argv[1], 
'backupjob':'Current', 
'start_page':sys.argv[2]})
r = urlopen(t)
print(r.getheader('Content-Length'))
gz = GZ(r)
def callback(self, event, e):
    if e.tag == 'F':
        f = XMLFileInfo(e)
        type = 'F'
        if f.type == "T":
            type = 'D'
        print("{type} {name} {size} {size_enc} {salt}".format(
        type=type, name=f.path, size=to_size(f.size), 
        size_enc=to_size(f.size_enc),
        salt=salt(f.salt)
        ))
        print(e.attrib)
    #self.stdcallback(event, e)

def endcallback(self):
	pass
    
fl = FL(gz, callback=callback, endcallback=endcallback)
fl.start()
        

print('Transferred data:', to_size(gz.n_comp),'/',to_size(gz.n))
