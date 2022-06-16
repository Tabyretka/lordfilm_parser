import asyncio
import random

import aiohttp
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


async def get_page_data(session, page, db, cursor):
    time.sleep(random.randint(1, 4))
    url = f"http://ae.lordfilms-s.tube/filmy/page/{page}/"
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0"
    }
    async with session.get(url=url, headers=headers) as rs:
        soup = BeautifulSoup(await rs.text(), "lxml")
        try:
            div_list = soup.find("div", class_="sect-cont sect-items clearfix").find("div", id="dle-content").findAll(
                "div", class_="th-item")
            for div in div_list:
                link = div.find("a", class_="th-in with-mask").get("href")
                link = str(link).replace("http://ae.lordfilms-s.tube/", "", 1)
                name = div.find("div", class_="th-title").text
                year = int(div.find("div", class_="th-year").text)
                cursor.execute(
                    """INSERT INTO Kino (NAME, YEAR, URL) VALUES (?, ?, ?);""",
                    (name, year, link))
                db.commit()
            print(page)
        except Exception as ex:
            logger.error(f"{ex}\n{url}\n\n")


async def gather_data():
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
    async with aiohttp.ClientSession() as session:
        rs = await session.get(url=url, headers=headers)
        soup = BeautifulSoup(await rs.text(), "lxml")
        pages_count = int(soup.find("div", class_="navigation").findAll("a")[-1].text)
        tasks = []

        for page in range(1, pages_count + 1):
            task = asyncio.create_task(get_page_data(session, page, db, cursor))
            tasks.append(task)

        await asyncio.gather(*tasks)
    db.close()
    print(f"OK")


def main():
    start_time = time.time()
    asyncio.run(gather_data())
    finish_time = time.time() - start_time
    print(f"На работу затрачено {finish_time}")


if __name__ == "__main__":
    main()
