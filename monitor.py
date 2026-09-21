import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

URL = "https://m.wilsonbaseball.co.kr/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
        "AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1"
    )
}

response = requests.get(
    URL,
    headers=headers,
    timeout=20
)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

products = {}

for a in soup.find_all("a", href=True):

    href = a["href"]

    if "product/detail.html" not in href:
        continue

    full_url = urljoin(URL, href)

    parsed = urlparse(full_url)
    query = parse_qs(parsed.query)

    product_no = query.get("product_no")

    if not product_no:
        continue

    product_no = product_no[0]

    # 같은 상품이 여러 영역에 노출되어도 한 번만 저장
    if product_no in products:
        continue

    name = " ".join(a.stripped_strings).strip()

    # 상품명이 링크 내부에 없는 항목 제외
    if not name:
        continue

    products[product_no] = {
        "name": name,
        "url": full_url
    }

print("=== WILSON PRODUCT MONITOR ===")
print("총 상품 수:", len(products))
print()

for product_no, product in sorted(
    products.items(),
    key=lambda x: int(x[0]),
    reverse=True
):

    print("PRODUCT NO:", product_no)
    print("NAME:", product["name"])
    print("LINK:", product["url"])
    print("-----")
