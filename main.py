from scan import Scan

# 初始化 设置扫描的IP段
s = Scan('47.0.0.0/16')
# 设置最大线程数为512 设置访问GET URL 设置超时时间为500毫秒
s.setMaxThreads(512).setUrl('http://www.xxx.com/api/news/list').setTimeout(500).run()

# 设置最大线程数为512 机器好的、带宽大的可以上调，不是说只能最大512
s.setMaxThreads(512)
# 设置扫描的IP段
s.setIp('47.112.0.0/16')
# 设置扫描的URL
s.setUrl('http://www.xxx.com/api/news/list')
# 设置超时时间为500毫秒
s.setTimeout(500)
# 请求设置-控制反转 和 requests.request 参数一致
s.setRequestOptions(allow_redirects=False)
# 验证函数 返回值会被存储
s.setVerify(lambda response: response.json())
# 设置输出文件
s.output_file = 'ip_response.txt'
# 运行扫描
s.run()
