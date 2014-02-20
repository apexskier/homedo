#!/usr/bin/env python
#
#
# Regenerate files in example_conf

from datetime import datetime
from cork import Cork

def populate_conf_directory():
    cork = Cork('conf', initialize=True)

    cork._store.roles['admin'] = 100
    cork._store.roles['user'] = 50
    cork._store.save_roles()

    tstamp = str(datetime.utcnow())
    username = password = 'admin'
    cork._store.users[username] = {
        'role': 'admin',
        'hash': cork._hash(username, password),
        'email_addr': username + '@localhost.local',
        'desc': username + ' test user',
        'creation_date': tstamp
    }
    cork._store.save_users()
    print("Login with the username '{}' and the password '{}'. Then go to /admin, add a new admin, and delete this one.".format(username, password))

if __name__ == '__main__':
    populate_conf_directory()

