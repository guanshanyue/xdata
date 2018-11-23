from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import AuthenticationException
from paramiko.rsakey import RSAKey
# from apps.setting import Setting
from io import StringIO

ssh_public_key = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDkVpFkJQEXvifnr889aNTcsaqVxHycsEHilKoUYF1/dlkgJ6a8wCq0P3tfj8zTK7YCdKP0/pY80haPyLonCMNftdoRo7G9/X/lM7x/JKGrplZ3KzIjF15oLsH4aazqFGPUU6ejVFW3rimLSIV3aPYAUJuOSxMPco9rcgyJH/aTw98FVGpcUw+MWYjYITr3QXNUzlAO52YSHx+stzzoaSCgyt2MCICJK5N6hL71t4mcSZbe4UB5lt3sxifuGFq3nQ8EwOl/xjfqoc7owltdkM3Dog01qiUDM2uzeCDVgc63Lx6IbrrnaFQV9gfLngeGeA0K/Ca6vW3eJJcQA0ExqZXZ'
ssh_private_key = '''
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA5FaRZCUBF74n56/PPWjU3LGqlcR8nLBB4pSqFGBdf3ZZICem
vMAqtD97X4/M0yu2AnSj9P6WPNIWj8i6JwjDX7XaEaOxvf1/5TO8fyShq6ZWdysy
IxdeaC7B+Gms6hRj1FOno1RVt64pi0iFd2j2AFCbjksTD3KPa3IMiR/2k8PfBVRq
XFMPjFmI2CE690FzVM5QDudmEh8frLc86GkgoMrdjAiAiSuTeoS+9beJnEmW3uFA
eZbd7MYn7hhat50PBMDpf8Y36qHO6MJbXZDNw6INNaolAzNrs3gg1YHOty8eiG66
52hUFfYHy54HhngNCvwmur1t3iSXEANBMamV2QIDAQABAoIBACXPP9v5VKj9z9XJ
guOETFsPAFQ0aP35Ia/HNjKRkmncyv1ME4wFtgyKxn8YbK46+rSFY/DZhz8i+qFs
d4anKNLcZfOty2zOYTMu0fOruSmXLZImEPNGl1dhBrV/qiZIog8ymvusp1T2/eIW
bCNNug5rSpbRT6KrMZx1EiZSqJ3m7RpzxYTLEYdl8lHvpHfclB5qq8AlHEInEBND
FPbmEoHEUkpIfDDSK7breGo0ituRppT7xRK4g8wFpOHo4p1sayVrNHlqQsl5MOYO
2ddYVPPZ1C0lcpFQyM3DSJLm3350b1P5p5LxhpC4hvT08DfDjGYsNgn+E4JvTE0l
9t2/hRECgYEA+Ax3kXBq9OHipwjAvC3hI/Dw19YjbtviP0TQi3GpiMMhGeUNqEXF
zGsBSd1An24XRG5MfdXMZS+uCUrINKi5PPK8yWgoJa40kOujGwkn6oj2X1GZZTjY
TvpYzd3HACfZGktCjh16nMZDFNPP3raPFucAyC1GlSlKRI++uONWD6MCgYEA66ha
QMyQq+w++umoPzMJBvHn/KMvDiiqeI3yxBm7UFgrsoL2ikprPOQgfSvJLAqcVR00
jvdDMZQDbvMBiLRrx9YKr5mU6dskPtsQWD7YIbEHBQKBbB8zhnDvPU6+Pd+7mcpo
Muh5tiBB0YeE0EkTCtv4cG3Zy5QLIu7OA+zLrFMCgYBTdcZpbjzepn5fm2dWKc2+
DRzMUqXbcCqhBSNyN81GUfl6QAKnYsqZ7EsjsklDG4TCpqYgFObQCQny4HGankat
hjMVRXF0tDfFpzNbLmp61JipG8iUMVs+v6dPpVaG6+F1omsDbFHMHD2H7Xjcw+pD
V3iA4hMErz7o8MDIbt2PJwKBgGZWGbuCGmFOmpsD1Rh85TKq4n+HreuMJVts6TvX
oMxnPbKrxLyRTLiIqMMyvI3vnawonqZnIjrpeAQ6azQehZ+mh8VyAIT9sWPKZfKs
d9dJtS6rw+BcPFfpuzr4cw0Tl7hVeaKB6jj5ERwYqch5s1dH5z+LtMT/aUamRbjW
oCwZAoGBAL0nQL+riTXUTCNrUZ7gWO6RnnXJnxiWuA87uTxn1yNqN3yDIjMgMEZA
zu7+xZtCkjFm0MIaU/hnl7mJxnooMXCXt/9zv19RkcWky8tL3+zx9wupVkiHNz1h
fTtS0NjksgyJV8ohXRPYYUGKuVyRj/XqDXdh1hEIXPoAgLWSS+Ib
-----END RSA PRIVATE KEY-----
'''

def generate_ssh_key():
    key_obj = StringIO()
    key = RSAKey.generate(2048)
    key.write_private_key(key_obj)
    return key_obj.getvalue(), 'ssh-rsa ' + key.get_base64()


def add_public_key(hostname, port, password):
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy)
    ssh_client.connect(
        hostname=hostname,
        port=port,
        username='root',
        password=password
    )
    try:
        _, stdout, stderr = ssh_client.exec_command('mkdir -p -m 700 /root/.ssh && \
        echo %r >> /root/.ssh/authorized_keys && \
        chmod 600 /root/.ssh/authorized_keys' % ssh_public_key)
        if stdout.channel.recv_exit_status() != 0:
            raise Exception('Add public key error: ' + ''.join(x for x in stderr))
    finally:
        ssh_client.close()


def get_ssh_client(hostname, port):
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy)
    ssh_client.connect(
        hostname,
        port=port,
        username='root',
        pkey=RSAKey.from_private_key(StringIO(ssh_private_key)))
    return ssh_client


def ssh_exec_command(hostname, port, command):
    ssh_client = get_ssh_client(hostname, port)
    try:
        _, stdout, stderr = ssh_client.exec_command(command)
        return stdout.channel.recv_exit_status(), ''.join(x for x in stdout), ''.join(x for x in stderr)
    except Exception as e:
        return 256, e, None
    finally:
        ssh_client.close()


def ssh_exec_command_with_stream(ssh_client, command):
    try:
        _, stdout, _ = ssh_client.exec_command(command, get_pty=True)
    except Exception as e:
        ssh_client.close()
        raise e
    while True:
        message = stdout.readline()
        if not message:
            break
        yield message
    ssh_client.close()


def ssh_ping(hostname, port):
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy)
    try:
        ssh_client.connect(
            hostname,
            port=port,
            username='root',
            #pkey=RSAKey.from_private_key(StringIO(Setting.ssh_private_key)))
            pkey=RSAKey.from_private_key(StringIO(ssh_private_key)))

    except AuthenticationException:
        return False
    ssh_client.close()
    return True
if __name__ == '__main__':
    # private_key, public_key = generate_ssh_key()
    # print(private_key,public_key)
    # add_public_key('192.168.1.91',22,'oracle')
    print(ssh_exec_command('192.168.1.91',22,"ifconfig | egrep -A 1 '(enp0s3|eth0)' | egrep 'inet' | awk '{print $2}'"))
    # print(ssh_ping('192.168.1.91',22))
    # print(ssh_exec_command_with_stream(get_ssh_client('192.168.1.91',22),'df -hT'))
