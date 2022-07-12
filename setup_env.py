import os


import settings

for p in settings.tss:
    pxe_str = p.get('ts')
    s = pxe_str.split('@')[1]
    cred = pxe_str.split('@')[0]
    user = cred.split(':')[0]
    password = cred.split(':')[1]

    cmd = f'ssh-copy-id -o StrictHostKeyChecking= no {user}@{s}'
    if settings.hop_station is not None:
        cmd = f'ssh-copy-id -o StrictHostKeyChecking=no -o ProxyCommand=\"ssh -W %h:%p {settings.hop_station}\" {user}@{s}'
        os.system(cmd)
        cmd = f'ssh {settings.hop_station} ssh-copy-id -o StrictHostKeyChecking=no {user}@{s}'

    os.system(cmd)
