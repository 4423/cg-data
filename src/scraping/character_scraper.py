from bs4 import BeautifulSoup
from entity.character import Character


class CharacterScraper:
    def get_characters(self, html: str) -> list[Character]:
        return list(self.__get_characters(html))

    def __get_characters(self, html: str) -> list[Character]:
        soup = BeautifulSoup(html, "html.parser")
        tbody = soup.find("th", text="アイドル").parent.parent
        trs = tbody.find_all("tr")
        for tr in trs[2:]:
            tds = tr.find_all("td")
            if len(tds) > 2:
                chara_name = tds[1].text.strip()
                actor = tds[2].text.strip()
                if actor != "-":
                    yield Character(chara_name, actor)
