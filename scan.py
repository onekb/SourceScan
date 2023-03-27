import threading
import requests
import ipaddress
from tqdm import tqdm


class Scan():
    threads = []
    max_threads = 512
    ip_network = []
    url = ''
    timeout = 500
    request_options = None
    verify = None
    output_file = 'ip_response.txt'

    def __init__(self, ip):
        threading.Thread.__init__(self)
        self.setIp(ip)

    def setMaxThreads(self, max_threads):
        self.max_threads = max_threads
        return self

    def setIp(self, ip, reverse=False):
        ip_network = ipaddress.ip_network(ip)
        self.ip_network = list(ip_network)
        if reverse:
            self.ip_network.reverse()
        return self

    def setUrl(self, url):
        self.url = url
        return self

    def setTimeout(self, timeout):
        self.timeout = timeout
        return self

    def setRequestOptions(self, **request_options):
        self.request_options = request_options
        return self

    def setVerify(self, verify):
        self.verify = verify
        return self

    def getVerify(self, response):
        if self.verify is None:
            return response.json()
        else:
            return self.verify(response)

    def get_ip_response(self, ip_address):
        try:
            response = self.getRequest(ip_address)
            result = self.getVerify(response)
            with open(self.output_file, 'a') as f:
                f.write(str(ip_address) + ': ' + str(result) + '\n')
        except:
            pass

    def getRequest(self, ip_address):
        if self.request_options is None:
            return requests.request(method='GET',
                                    url=self.url,
                                    timeout=self.timeout / 1000,
                                    proxies={
                                        'http': 'http://' + str(ip_address) + ':80'
                                    },
                                    allow_redirects=False)
        else:
            return requests.request(self.url,
                                    timeout=self.timeout / 1000,
                                    proxies={
                                        'http': 'http://' + str(ip_address) + ':80'
                                    },
                                    allow_redirects=False,
                                    **self.request_options)

    def run(self):
        with tqdm(total=len(self.ip_network)) as pbar:
            for i, ip_address in enumerate(self.ip_network):
                if len(self.threads) >= self.max_threads:
                    self.threads[0].join()
                    self.threads = self.threads[1:]

                thread = threading.Thread(target=self.get_ip_response, args=(ip_address,))
                thread.start()
                self.threads.append(thread)

                pbar.update(1)
            for thread in self.threads:
                thread.join()
