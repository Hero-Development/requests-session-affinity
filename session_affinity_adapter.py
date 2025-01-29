
import socket
import urllib.parse

from requests import PreparedRequest, Response
from requests.adapters import HTTPAdapter
from urllib3.connectionpool import HTTPSConnectionPool


class SessionAffinityAdapter(HTTPAdapter):
    host_cache = {}

    def __init__(self, pool_connections = 10, pool_maxsize = 10, max_retries = 0, pool_block = False):
        super(SessionAffinityAdapter, self).__init__(pool_connections, pool_maxsize, max_retries, pool_block)

        self.host_ip = None
        self.host_name = None

    def cert_verify(self, conn: HTTPSConnectionPool, url, verify, cert):
        # send requests to ip instead of hostname
        conn.host = self.host_ip

        # repair the pool so that SSL can be verified
        conn.conn_kw['server_hostname'] = self.host_name

        # https://urllib3.readthedocs.io/en/stable/advanced-usage.html#verifying-tls-against-a-different-host
        # conn.assert_hostname = conn.hostname

        return super(SessionAffinityAdapter, self).cert_verify(conn, url, verify, cert)

    def send(self, request: PreparedRequest, stream = False, timeout = None, verify = True, cert = None, proxies = None) -> Response:
        request = self._rebuild_request(request)
        return super(SessionAffinityAdapter, self).send(request, stream, timeout, verify, cert, proxies)

    def _rebuild_request(self, request: PreparedRequest) -> PreparedRequest:
        parsed = urllib.parse.urlparse(request.url)
        if not SessionAffinityAdapter.host_cache.get(parsed.hostname):
            self.host_name = parsed.hostname
            self.host_ip = socket.gethostbyname(self.host_name)
            SessionAffinityAdapter.host_cache[self.host_name] = self.host_ip

        request.headers['Host'] = self.host_name
        request.url = self._rebuild_url(parsed, self.host_ip)
        return request

    @classmethod
    def _rebuild_url(cls, parsed, host_ip):
        clone = [*parsed]

        # update netloc
        if parsed.port:
            clone[1] = f"{host_ip}:{parsed.port}"
        else:
            clone[1] = host_ip

        return urllib.parse.urlunparse(tuple(clone))
