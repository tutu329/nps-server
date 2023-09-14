import requests
from bs4 import BeautifulSoup

# 设置请求头参数，模拟浏览器访问以防止被反爬虫机制拦截
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.'
}

def search_taobao(keyword):
    url = f'https://s.taobao.com/search?q={keyword}'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        parse_html(response.text)
    else:
        print('Request failed:', response.status_code)


def parse_html(html):
    soup = BeautifulSoup(html, 'lxml')

    items_list = soup.find_all('div', class_='item J_MouserOnverReq')
    print("items: ", items_list)

    for item in items_list[:10]:
        title_element = item.find('img')['alt']
        sales_count_element = item.find("span", class_="deal-cnt")
        evaluate_count_element = item.find_next_sibling().find("td").select(".evaluate-count")[1]

        title = title_element.string.strip()
        sales_count = sales_count_element.string.strip()[:-3]

        try:

            evaluate_count = evaluate_count_element.string.strip()

        except AttributeError:

            evaluate_count = "无评价"

        print(f"商品名称: {title}\n销量: {sales_count}\n评价数：{evaluate_num}\n")

if __name__ == '__main__':
    search_taobao('鞋子')