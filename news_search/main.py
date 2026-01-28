import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

app = FastAPI(title="Naver News Search API")


# 응답 모델
class NewsArticle(BaseModel):
    title: str
    link: str
    body: str


class NewsResponse(BaseModel):
    total: int
    articles: List[NewsArticle]


# User Agent 설정
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0 Safari/537.36"
)

session = requests.Session()
session.headers.update({"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9"})

#  네이버 뉴스 페이지 전용 파서
def extract_naver_article_html(html: str):
   
    soup = BeautifulSoup(html, "lxml")
    # 모바일(mnews)에서 본문
    article = soup.select_one("#dic_area")
    # PC(news)에서 본문
    if not article:
        article = soup.select_one("#newsct_article")
    if not article:
        return None
    # 불필요 요소 제거
    for s in article.select(
        "script, style, .media_end_correction, .copyright, figure"
    ):
        s.decompose()
    for br in article.find_all("br"):
        br.replace_with("\n")
    return article.get_text("\n", strip=True)

# 뉴스 도메인 체크 함수
def fetch_article_text(url: str, timeout: int = 15):
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
    except Exception:
        return None

    html = resp.text
    final_url = resp.url

    # 네이버 뉴스 도메인 체크
    if (
        "n.news.naver.com" not in final_url
        and "news.naver.com" not in final_url
    ):
        return None

    # 네이버 뉴스 페이지 전용 파서
    txt2 = extract_naver_article_html(html)
    if txt2 and len(txt2.strip()) > 50:
        return txt2.strip()

    return None


# 네이버 뉴스 검색 API 호출 함수
def search_naver_news(query: str, display: int = 10):
    """네이버 뉴스 검색 API 호출"""

    api_key    = os.getenv("NAVER_API_KEY")  # Client ID 값
    secret_key = os.getenv("NAVER_SECRET_KEY")   # Client Secret 값 입력

    if not api_key or not secret_key:
        raise HTTPException(
            status_code=500,
            detail="NAVER_API_KEY or NAVER_SECRET_KEY not found in environment variables",
        )

    url = "https://openapi.naver.com/v1/search/news.json"

    params = {
        "query": query,
        "display": display,
        "start": 1,
        "sort": "sim",
    }

    headers = {
        "X-Naver-Client-Id": api_key,
        "X-Naver-Client-Secret": secret_key,
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        resp.encoding = "utf-8"
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Naver API error: {str(e)}"
        )


@app.get("/")
def read_root():
    return {"message": "Naver News Search API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


## 네이버 뉴스 검색 및 본문 추출 api
@app.get("/search", response_model=NewsResponse)
def search_news(query, display):

    search_result = search_naver_news(query, display)

    if "items" not in search_result:
        raise HTTPException(
            status_code=500, detail="Invalid response from Naver API"
        )

    ################################################
    ######### 필수 과제 - 문제 1: 네이버 뉴스 링크만 필터링

    
    news_list = [] # 네이버 뉴스 링크 담을 리스트

    for item in search_result["items"]:
        link = item.get("link", "")

        text = fetch_article_text(link)

        if not text:
            continue

        news_list.append(
            NewsArticle(
                title=item.get("title", ""),
                link=link,
                body=text
            )
        )

    return {"total": len(news_list), "articles": news_list}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
