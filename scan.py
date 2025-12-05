import threading
import requests
import ipaddress
from urllib.parse import urlparse
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
        # 解析URL，提取域名和路径
        parsed_url = urlparse(self.url)
        domain = parsed_url.netloc
        path = parsed_url.path
        if parsed_url.query:
            path += '?' + parsed_url.query

        # 准备headers，添加Host头
        # 先创建默认的Host头
        default_headers = {'Host': domain}

        # 准备请求参数（默认值）
        request_kwargs = {
            'method': 'GET',
            'url': f"http://{ip_address}{path}",
            'timeout': self.timeout / 1000,
            'headers': default_headers,
            'allow_redirects': False
        }

        # 如果有额外的请求选项，让它们覆盖默认值
        if self.request_options:
            # 创建副本以避免修改原始选项
            options_copy = self.request_options.copy()

            # 处理headers：需要合并而不是覆盖
            if 'headers' in options_copy:
                # 将默认的Host头合并到用户设置的headers中
                # 用户设置的headers优先，但如果用户没有设置Host，则保留默认的
                user_headers = options_copy['headers']
                if 'Host' not in user_headers:
                    user_headers['Host'] = domain
                # 移除headers，因为我们已经在下面处理了
                options_copy.pop('headers')
                # 将合并后的headers设置为最终值
                request_kwargs['headers'] = user_headers

            # 更新其他所有参数（用户设置的会覆盖默认值）
            request_kwargs.update(options_copy)

        return requests.request(**request_kwargs)

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
