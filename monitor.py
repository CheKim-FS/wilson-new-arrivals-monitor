import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://m.wilsonbaseball.co.kr/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
        "AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1"
    )
}

response = requests.get(URL, headers=headers, timeout=20)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

print("=== NEW ARRIVALS LINK TEST ===")

found = False

for a in soup.find_all("a", href=True):
    text = " ".join(a.stripped_strings)

    if "이정후" in text:
        found = True
        print("TEXT:", text)
        print("LINK:", urljoin(URL, a["href"]))
        print("HTML:", str(a)[:1500])
        print("-----")

if not found:
    print("ERROR: 이정후 상품 링크를 찾지 못했습니다.")
