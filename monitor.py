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

# 2. Wilson 모바일 홈페이지 가져오기
response = requests.get(
    URL,
    headers=headers,
    timeout=20
)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# 3. NEW ARRIVALS 영역 찾기
new_arrivals_heading = None

for h2 in soup.find_all("h2"):
    if "NEW ARRIVALS" in h2.get_text(" ", strip=True).upper():
        new_arrivals_heading = h2
        break

if new_arrivals_heading is None:
    raise RuntimeError(
        "NEW ARRIVALS 영역을 찾지 못했습니다. 사이트 구조를 확인하세요."
    )

# 검사 결과 확인된 NEW ARRIVALS 상품 컨테이너
new_arrivals_section = new_arrivals_heading.find_parent(
    "div",
    class_=lambda classes:
        classes and "xans-product-listmain-2" in classes
)

if new_arrivals_section is None:
    raise RuntimeError(
        "NEW ARRIVALS 상품 컨테이너를 찾지 못했습니다."
    )

print("NEW ARRIVALS 영역 확인 완료")

# 4. NEW ARRIVALS 안의 상품만 추출
products = {}

for a in new_arrivals_section.find_all("a", href=True):
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

    # 이미지 링크와 상품명 링크가 중복되므로
    # 같은 product_no는 한 번만 처리
    if product_no in products:
        continue

    # 상품명은 해당 상품의 li 영역에서 가져옴
    product_li = a.find_parent("li")

    if product_li is None:
        continue

    name_tag = product_li.select_one("strong.name a")

    if name_tag is None:
        continue

    name = " ".join(name_tag.stripped_strings).strip()

    if not name:
        continue

    products[product_no] = {
        "name": name,
        "url": full_url
    }

print("현재 NEW ARRIVALS 상품 수:", len(products))

# 사이트 구조가 바뀌어 상품을 하나도 못 찾았는데
# 정상으로 오인하는 상황 방지
if not products:
    raise RuntimeError(
        "NEW ARRIVALS 상품을 하나도 찾지 못했습니다."
    )

# 5. 기존 목록에 없는 상품 찾기
new_product_ids = [
    product_no
    for product_no in products
    if product_no not in seen_products
]

if not new_product_ids:
    print("새 상품 없음")
    raise SystemExit(0)

print("새 상품 발견:", len(new_product_ids))

# 6. ntfy Topic 불러오기
ntfy_topic = os.environ.get("NTFY_TOPIC")

if not ntfy_topic:
    raise RuntimeError(
        "NTFY_TOPIC이 설정되어 있지 않습니다."
    )

# 7. 새 상품 알림 보내기
successfully_notified = []

for product_no in sorted(
    new_product_ids,
    key=int,
    reverse=True
):
    product = products[product_no]

    print("NEW:", product_no, product["name"])

    notification_headers = {
        "Title": "Wilson New Arrival!",
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

    successfully_notified.append(product_no)

    print("알림 전송 성공:", product_no)

# 8. 알림 전송에 성공한 상품만 저장
if successfully_notified:
    updated_products = seen_products.union(
        successfully_notified
    )

    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        for product_no in sorted(
            updated_products,
            key=int,
            reverse=True
        ):
            f.write(product_no + "\n")

    print(
        "seen_products.txt 업데이트 완료:",
        len(updated_products)
    )
