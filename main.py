import requests
from bs4 import BeautifulSoup
import sqlite3
import logging
import time

Log_Format = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename="logfile.log",
                    filemode="w",
                    format=Log_Format,
                    level=logging.ERROR)

logger = logging.getLogger()


def collect_data(session: requests.Session, page: int, db, cursor) -> None:
    url = f"http://ae.lordfilms-s.tube/filmy/page/{page}/"
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0"
    }
    rs = session.get(url=url, headers=headers)
    if rs.ok:
        soup = BeautifulSoup(rs.text, "lxml")
        try:
            div_list = soup.find("div", class_="sect-cont sect-items clearfix").find("div", id="dle-content").findAll(
                "div", class_="th-item")
            for div in div_list:
                link = div.find("a", class_="th-in with-mask").get("href")
                link = str(link).replace("http://ae.lordfilms-s.tube/", "", 1)
                name = div.find("div", class_="th-title").text.lower()
                year = int(div.find("div", class_="th-year").text)
                cursor.execute(
                    """INSERT INTO Kino (NAME, YEAR, URL) VALUES (?, ?, ?);""",
                    (name, year, link))
                db.commit()
            print(page)
        except Exception as ex:
            logger.error(f"{ex}\n{url}\n\n")
    else:
        logger.error(f"{rs.status_code}\n{url}\n\n")


def main():
    db = sqlite3.connect("Kino.db")
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Kino (
        ID INTEGER PRIMARY KEY,
        NAME TEXT,
        YEAR TEXT,
        URL TEXT
    )""")
    db.commit()

    url = "http://ae.lordfilms-s.tube/filmy/"
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0"
    }
    session = requests.Session()
    rs = session.get(url=url, headers=headers)
    if rs.ok:
        soup = BeautifulSoup(rs.text, "lxml")
        pages_count = int(soup.find("div", class_="navigation").findAll("a")[-1].text)
        for page in range(1, pages_count + 1):
            collect_data(session=session, page=page, db=db, cursor=cursor)
        db.close()
        print("OK")
    else:
        print(rs.status_code)


if __name__ == "__main__":
    start_time = time.time()

    main()

    finish_time = time.time() - start_time
    print(f"???? ???????????? ?????????????????? {finish_time}")