import requests
from bs4 import BeautifulSoup

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

print("=== NEW ARRIVALS STRUCTURE INSPECTION ===")

found = False

# NEW ARRIVALS라는 텍스트가 들어 있는 요소를 모두 찾음
for element in soup.find_all(string=True):

    text = " ".join(element.split())

    if "NEW ARRIVALS" not in text.upper():
        continue

    found = True

    print()
    print("========================================")
    print("FOUND TEXT:", text)
    print("TAG:", element.parent.name)
    print("----------------------------------------")

    # NEW ARRIVALS 텍스트가 속한 요소부터
    # 상위 구조를 단계별로 출력
    current = element.parent

    for level in range(6):

        if current is None:
            break

        print()
        print(f"=== PARENT LEVEL {level} ===")
        print(str(current)[:8000])

        current = current.parent

if not found:
    print("ERROR: NEW ARRIVALS 텍스트를 찾지 못했습니다.")
