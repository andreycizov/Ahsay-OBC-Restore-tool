'''
AhsayAPI configuration file
'''

default = "login"

infos = {
    'login': {
       'password': 'password',
       'host': 'http(s)://www.example.com:555',
       # default backupset
       'backupset': 'default-backupset-id-or-name',
       'root': '/where_i_would_like_to_see_my_files'
    },
}

def set_account(user):
    global default
    if user in infos:
        default = user
    else:
        raise KeyError('No such user exists')
    
def o(name):
    '''
    returns option by it's name
    '''
    global infos
    global default
    if name == 'login':
        return default
    
    if name in infos[default]:
        return infos[default][name]
    else:
        raise KeyError('No such option was set up: '+name)
        
