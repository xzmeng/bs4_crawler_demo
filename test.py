from urllib.parse import urljoin


url = 'http://www.baidu.com/'

url2 = '/hello/index.html'

url3 = urljoin(url, url2)

print(url3)

a = [1, 2, 3]

print(a[0:3])

a = 'hello?'
print