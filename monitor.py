import requests
from bs4 import BeautifulSoup

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

# 페이지의 상품명 텍스트 확인
text = soup.get_text(" ", strip=True)

print("Wilson page loaded successfully.")
print(text[:3000])
