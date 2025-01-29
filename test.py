
import requests
import time

from session_affinity_adapter import SessionAffinityAdapter

def main():
    base_url = 'https://google.com'
    adapter = SessionAffinityAdapter()
    session = requests.Session()
    session.mount(base_url, adapter)

    for i in range(600):
        '''
        google.com
        60s
        142.250.69.228
        142.250.72.36
        142.250.72.46
        '''
        res = session.post(f"{base_url}/search?q=pizza", stream=True)
        host, port = res.raw._connection.sock.getpeername()
        assert host == adapter.host_ip
        print(f"{i}: {host}:{port}")
        time.sleep(1.000)


if __name__ == '__main__':
    main()
