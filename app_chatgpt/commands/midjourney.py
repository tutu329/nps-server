import requests
from bs4 import BeautifulSoup
import pandas as pd

# 存储数据的字典
data = {'标题': [], '说明': []}

# 假设www.abc.com的结构使我们可以这样获取所需的信息
# for page in range(1, 10):  # 更改范围以包含所需的页数
url = f'https://land.cmsh4.xyz/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 这里需要根据实际网页的HTML结构进行修改
items = soup.find_all('div', class_='item')

for item in items:
    data['标题'].append(item.find('div', class_='标题').text)
    data['说明'].append(item.find('div', class_='说明').text)

# 将字典转换为DataFrame并保存为Excel文件
df = pd.DataFrame(data)
df.to_excel('output.xlsx', index=False)
