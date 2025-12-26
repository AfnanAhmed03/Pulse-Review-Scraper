import requests
import json
import argparse
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def is_within_range(review_date, start, end):
    return start <= review_date <= end


# ---------------- G2 SCRAPER ----------------
def scrape_g2(company, start_date, end_date):
    reviews = []
    page = 1

    while True:
        url = f"https://www.g2.com/products/{company}/reviews?page={page}"
        res = requests.get(url, headers=HEADERS)

        if res.status_code != 200:
            break

        soup = BeautifulSoup(res.text, "html.parser")
        review_blocks = soup.select("div.paper")

        if not review_blocks:
            break

        for block in review_blocks:
            try:
                title = block.select_one("h3").text.strip()
                body = block.select_one("div[itemprop='reviewBody']").text.strip()
                date_text = block.select_one("time")["datetime"]
                review_date = date_parser.parse(date_text)

                if is_within_range(review_date, start_date, end_date):
                    reviews.append({
                        "title": title,
                        "review": body,
                        "date": review_date.strftime("%Y-%m-%d"),
                        "source": "G2"
                    })

            except Exception:
                continue

        page += 1

    return reviews


# ---------------- CAPTERRA SCRAPER ----------------
def scrape_capterra(company, start_date, end_date):
    reviews = []
    page = 1

    while True:
        url = f"https://www.capterra.com/p/{company}/reviews/?page={page}"
        res = requests.get(url, headers=HEADERS)

        if res.status_code != 200:
            break

        soup = BeautifulSoup(res.text, "html.parser")
        review_blocks = soup.select("div.review")

        if not review_blocks:
            break

        for block in review_blocks:
            try:
                title = block.select_one("h3").text.strip()
                body = block.select_one("p").text.strip()
                date_text = block.select_one("time").text.strip()
                review_date = date_parser.parse(date_text)

                if is_within_range(review_date, start_date, end_date):
                    reviews.append({
                        "title": title,
                        "review": body,
                        "date": review_date.strftime("%Y-%m-%d"),
                        "source": "Capterra"
                    })

            except Exception:
                continue

        page += 1

    return reviews


# ---------------- TRUST RADIUS (BONUS) ----------------
def scrape_trustradius(company, start_date, end_date):
    reviews = []
    page = 1

    while True:
        url = f"https://www.trustradius.com/products/{company}/reviews?f=recent&page={page}"
        res = requests.get(url, headers=HEADERS)

        if res.status_code != 200:
            break

        soup = BeautifulSoup(res.text, "html.parser")
        review_blocks = soup.select("div.review")

        if not review_blocks:
            break

        for block in review_blocks:
            try:
                title = block.select_one("h3").text.strip()
                body = block.select_one("p").text.strip()
                date_text = block.select_one("time").text.strip()
                review_date = date_parser.parse(date_text)

                if is_within_range(review_date, start_date, end_date):
                    reviews.append({
                        "title": title,
                        "review": body,
                        "date": review_date.strftime("%Y-%m-%d"),
                        "source": "TrustRadius"
                    })

            except Exception:
                continue

        page += 1

    return reviews


# ---------------- MAIN ----------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", required=True)
    parser.add_argument("--source", required=True, choices=["g2", "capterra", "trustradius"])
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)

    args = parser.parse_args()

    start_date = datetime.strptime(args.start, "%Y-%m-%d")
    end_date = datetime.strptime(args.end, "%Y-%m-%d")

    if start_date > end_date:
        raise ValueError("Start date cannot be after end date")

    if args.source == "g2":
        data = scrape_g2(args.company, start_date, end_date)
    elif args.source == "capterra":
        data = scrape_capterra(args.company, start_date, end_date)
    else:
        data = scrape_trustradius(args.company, start_date, end_date)

    with open("reviews.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"Scraped {len(data)} reviews successfully.")


if __name__ == "__main__":
    main()
