import requests
import os
import sys

def getKeys(user):
    keys = []
    try:
        r = requests.get('https://api.github.com/users/{}/keys'.format(user))
        r.raise_for_status()
    except ex:
        print(ex)
        return keys
    for key in r.json():
        keys.append(key["key"])
    return keys
    

if __name__ == '__main__':
    user = os.getenv('GITHUB_USER')
    if not user:
        print('Missing GITHUB_USER variable')
        sys.exit(1)

    authorizedKeysFile = os.getenv('AUTHORIZED_HOSTS', './authorized_hosts')
    
    keys = getKeys(user)
    if len(keys) == 0:
        print('No keys found')
        sys.exit(0)
    
    with open(authorizedKeysFile, 'w') as file:
        for key in keys:
            file.write('{}\n'.format(key))
    print('Saved {} keys'.format(len(keys)))