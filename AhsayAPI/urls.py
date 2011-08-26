'''
Url builder for AhsayAPI
'''
from . import conf
from urllib.parse import quote
import urllib.request


def quote_each(d):
    '''
    quotes every element in a dictionary and returns
    '''
    r = {}
    for k, v in d.items():
        r[k] = quote(str(v).encode('utf8'))
    return r

def get_tuple(t, args, default):
    '''
    
    '''
    default.update(credentials())
    default.update(args)
    return ((conf.o('host')+t[0]), 
        t[1].format(**quote_each(default)).encode('utf8'))
        
def urlopen(t): 
    return urllib.request.urlopen(t[0], t[1])

listBackupFile = ['/obs/restore/obm5.5/listBackupFile.do', 
'START_PT={start_point}&PWD={password}&ROWS_PER_PAGE={rows_per_page}&'
'BSET={backupset}&LOGIN={login}&BJOB={backupjob}&LIST_TYPE={list_type}&'
'DIR={dir}&ver={ver}&LIST_AMT={list_amount}&START_PAGE={start_page}']
    
def credentials():
    return {'login':    conf.o('login'), 
    'password': conf.o('password'),
    'backupset':    conf.o('backupset') }
    
def ls(args):
    default={
    'list_type':    'ALL',
    'dir':'', 
    'ver':          '8.0', 
    'amount':       50, 
    'start_page':   0,
    'start_point': 0,
    'rows_per_page':50,
    'backupjob': '',
    'list_amount': 50}
    default.update(credentials());
    global listBackupFile
    return get_tuple(listBackupFile, args, default)
    
strStartRestore = ['/obs/restore/obm5.5/startRestore.do', 
'PWD={password}&RJOB={restorejob}&BSET={backupset}'
'&LOGIN={login}&BJOB={backupjob}&'
'S1={path}{restorejob}CurrentF&ver={ver}'
]

strStartRestore = ['/obs/restore/obm5.5/startRestore.do', 
'PWD={password}&RJOB={restorejob}&BSET={backupset}'
'&LOGIN={login}&BJOB={backupjob}&'
'S1={path}{restorejob}{backupjob}F&ver={ver}'
]

def startRestore(args):
    default={
    'restorejob':    '',
    'path':'',
    'backupjob': '',
    'ver': '8.0'
    }
    
    default.update(credentials());
    global strStartRestore
    return get_tuple(strStartRestore, args, default)

strEndRestore = ['/obs/restore/obm5.5/endRestore.do',
'PWD={password}&RJOB={restorejob}'
'&LOGIN={login}'
]
def endRestore(args):
    default = {}
    default.update(credentials())
    global strEndRestore
    return get_tuple(strEndRestore, args, default)
    
strRestoreFile = ['/obs/restore/obm5.5/restoreFile.do?u={login}','PWD={password}&RJOB={restorejob}&BSET={backupset}&LOGIN={login}&BJOB=Current&PATH={path}&TYPE={type}'
]

def restoreFile(args):
    default={
    'restorejob': '',
    'path': '',
    'backupjob': '',
    'type': 'F'
    }
    default.update(args)
    global strRestoreFile
    a = strRestoreFile
    a[0] = a[0].format(**credentials())
    return get_tuple(a, args, default)
