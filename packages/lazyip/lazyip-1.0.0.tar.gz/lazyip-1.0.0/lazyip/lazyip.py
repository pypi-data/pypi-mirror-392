import subprocess

"""
https://ipw.cn/
http://ip-api.com/json/
"""

def get_public_ip(
        test: bool = True,
        ipv4: bool = False,
        ipv6: bool = False
):
    if ipv4:
        url = "4.ipw.cn"
    elif ipv6:
        url = "6.ipw.cn"
    elif test:
        url = "test.ipw.cn"
    else:
        return None
    result = subprocess.run(['curl', url], capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        return result.stdout
    else:
        return None


if __name__ == '__main__':
    print(get_public_ip(ipv6=True))