import os

from pexpect import EOF


import settings

def setup_sshpass(host_iden, hop=None):

    cmd = f"ssh {host_iden} < setup_sshpass.sh"
    if hop is not None:
        cmd = f"ssh {hop} ssh {host_iden} < setup_sshpass.sh"
    os.system(cmd)


for p in settings.tss:
    """ log:log@ip_address
    """
    pxe_str = p.get('ts')
    s = pxe_str.split('@')[1]
    cred = pxe_str.split('@')[0]
    user = cred.split(':')[0]
    password = cred.split(':')[1]


    # Copy the SSH pub key
    cmd = f'ssh-copy-id -o StrictHostKeyChecking= no {user}@{s}'
    if settings.hop_station is not None:
        cmd = f'ssh-copy-id -o StrictHostKeyChecking=no -o ProxyCommand=\"ssh -W %h:%p {settings.hop_station}\" {user}@{s}'
        os.system(cmd)
        cmd = f'ssh {settings.hop_station} ssh-copy-id -o StrictHostKeyChecking=no {user}@{s}'

    os.system(cmd)

    # setup the sshpass environment for webssh
    setup_sshpass(f"{user}@{s}", settings.hop_station)
