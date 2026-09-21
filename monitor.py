import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

URL = "https://m.wilsonbaseball.co.kr/"
SEEN_FILE = "seen_products.txt"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
        "AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1"
    )
}

# 1. 이미 확인한 상품번호 불러오기
with open(SEEN_FILE, "r", encoding="utf-8") as f:
    seen_products = {
        line.strip()
        for line in f
        if line.strip()
    }

print("기존 상품 수:", len(seen_products))

# 2. Wilson 페이지 가져오기
response = requests.get(
    URL,
    headers=headers,
    timeout=20
)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# 3. 현재 상품 추출
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

    if product_no in products:
        continue

    name = " ".join(a.stripped_strings).strip()

    if not name:
        continue

    products[product_no] = {
        "name": name,
        "url": full_url
    }

print("현재 상품 수:", len(products))

# 4. 기존 목록에 없는 상품 찾기
new_product_ids = [
    product_no
    for product_no in products
    if product_no not in seen_products
]

if not new_product_ids:
    print("새 상품 없음")
    raise SystemExit(0)

print("새 상품 발견:", len(new_product_ids))

# 5. ntfy Topic 불러오기
ntfy_topic = os.environ.get("NTFY_TOPIC")

if not ntfy_topic:
    raise RuntimeError("NTFY_TOPIC이 설정되어 있지 않습니다.")

# 6. 새 상품마다 알림 보내기
for product_no in sorted(
    new_product_ids,
    key=int,
    reverse=True
):
    product = products[product_no]

    print("NEW:", product_no, product["name"])

    notification_headers = {
        "Title": "Wilson 신상품 발견!",
        "Priority": "high",
        "Tags": "baseball",
        "Click": product["url"]
    }

    message = (
        f"{product['name']}\n"
        f"상품번호: {product_no}\n"
        f"알림을 눌러 상품 페이지로 이동"
    )

    notify_response = requests.post(
        f"https://ntfy.sh/{ntfy_topic}",
        data=message.encode("utf-8"),
        headers=notification_headers,
        timeout=20
    )

    notify_response.raise_for_status()

print("알림 전송 완료")
