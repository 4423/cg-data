from bs4 import BeautifulSoup, Tag
import re
import copy
from entity.song import Song


class SongScraper:
    def get_songs(self, html: str) -> list[Song]:
        soup = self._parse(html)

        songs = []
        ids = self._get_cinderella_ids(soup)
        for id in ids:
            a = self._find_a_by_id(soup, id)
            head_tr = a.find_parent("tr")
            song_tr = head_tr.find_next("th", text="曲名").parent.find_next("tr")
            # 行の終わりまで繰り返す
            while song_tr.find("th") is None and len(song_tr.find_all("td", attrs={"colspan": "2"})) == 0:
                song = self._get_song(song_tr)
                songs.append(song)
                song_tr = song_tr.find_next("tr")

        return songs + self._other_songs()

    def _find_a_by_id(self, soup: BeautifulSoup, id: str) -> Tag | None:
        if id == "CG_sm-CQ":
            # STARLIGHT MASTER CRYSTAL QUALIA には一つ前の CG_sm-HT が間違って設定されている
            # そのため text で検索する
            return soup.find("a", text="STARLIGHT MASTER CRYSTAL QUALIA")

        a = soup.find("a", attrs={"name": id})
        if a is not None:
            return a
        return soup.find("a", attrs={"id": id})

    def _parse(self, html: str) -> BeautifulSoup:
        soup = BeautifulSoup(html, "html.parser")

        # 列の項目が行をまたがないように DOM を書き換える
        cache = None
        for tr in soup.findAll("tr"):
            # 行をまたぐ td が以前に定義されていたなら挿入する
            if cache != None:
                col, rowspan, td = cache
                tr.insert(col + 1, td)
                rowspan -= 1
                if rowspan == 1:
                    cache = None
                else:
                    cache = (col, rowspan, td)
                continue

            # rowspan 属性をもつ td を見つけて覚えておく
            tds = tr.findAll("td")
            for col, td in enumerate(tds):
                if td.has_attr("rowspan"):
                    rowspan = int(td["rowspan"])
                    del td["rowspan"]
                    cache = (col, rowspan, copy.copy(td))
        return soup

    def _get_cinderella_ids(self, soup: BeautifulSoup):
        ids = [
            "CGSS",
            "CP",
            "IS",
            "PT",
            "moiw2023",
            "GLS",
            "GLSE",
            "cg_currymeshi",
            "cg_spinoff",
            "U149AM",
            "WWG",
            "U149",
            # 手動で追加する
            # "GOUDOU_15th",
            # "GOUDOU_2021",
        ]
        mokuji = soup.find(
            "div", attrs={"style": "border: 1px solid #d1d1d1; padding-left: 5px; height: 405px; overflow: auto;"}
        )
        for li in mokuji.findAll("li"):
            # CD収録曲 - シンデレラガールズ 配下の id を取得
            if li.find("a", href="#CDCG", recursive=False) != None:
                cdcgIDs = map(lambda a: a["href"][1:], li.find("ul").findAll("a"))
                ids.extend(cdcgIDs)
                break
        return ids

    def _get_song(self, song_tr: Tag) -> Song:
        tds = song_tr.find_all("td")
        title = tds[0].text
        artists = self._get_artists(tds[1].text)
        is_covered = "#f0f8ff" in tds[0]["style"]

        if is_covered:
            match = re.search(r"(.+)（(.*?)）", title.replace("\n", ""))
            if match:
                title = match.group(1)
                original_artist = match.group(2)
            else:
                original_artist = title
            song = Song(title, artists, is_covered=True, original_artist=original_artist)
        else:
            song = Song(title, artists)

        self._pretty(song)
        return song

    def _get_artists(self, artists_text: str) -> list[str]:
        artists = []
        for artist in artists_text.split("、"):
            artists.append(re.sub(r"\*\d+", "", artist.strip()))
        return artists
    
    # immutable にしたいが大変なので引数を書き換える
    def _pretty(self, song: Song):
        # 前後にある改行文字や記号を除去
        song.title = song.title.strip().replace("\xa0", " ")
        if song.original_artist is not None:
            song.original_artist = song.original_artist.strip().replace("\xa0", " ")

        # 曲名の前にある (数字) を除去
        match = re.search(r"\([0-9]+\)\s(.+)", song.title)
        if match:
            song.title = match.group(1)

        # （蛍の光） はカバー元ではなく曲名の一部とみなす
        if song.original_artist == "蛍の光":
            song.original_artist = song.title + "（蛍の光）"
            song.title = song.original_artist

        # 注釈のための *数字 を除去
        for i in range(len(song.artists)):
            if song.artists[i][0] == "*":  # 簡易判定
                if re.search(r"(\*[0-9]+)", song.artists[i]):  # 詳細判定
                    del song.artists[i]

        # jewelries! はひとまず全員verを設定
        if song.title == "ススメ☆オトメ〜jewel parade〜":
            song.artists = [
                "渋谷凛",
                "高垣楓",
                "神崎蘭子",
                "多田李衣菜",
                "新田美波",
                "城ヶ崎莉嘉",
                "諸星きらり",
                "城ヶ崎美嘉",
                "本田未央",
                "赤城みりあ",
                "双葉杏",
                "前川みく",
                "島村卯月",
                "小日向美穂",
                "安部菜々",
            ]
        elif song.title == "ゴキゲンParty Night":
            song.artists = [
                "川島瑞樹",
                "白坂小梅",
                "アナスタシア",
                "神谷奈緒",
                "北条加蓮",
                "十時愛梨",
                "日野茜",
                "高森藍子",
                "星輝子",
                "堀裕子",
                "三村かな子",
                "輿水幸子",
                "佐久間まゆ",
                "緒方智絵里",
                "小早川紗枝",
            ]
        elif song.title == "Near to You":
            song.artists = [
                "宮本フレデリカ",
                "一ノ瀬志希",
                "櫻井桃華",
                "中野有香",
                "五十嵐響子",
                "鷺沢文香",
                "速水奏",
                "橘ありす",
                "塩見周子",
                "二宮飛鳥",
                "姫川友紀",
                "市原仁奈",
                "片桐早苗",
                "大槻唯",
                "相葉夕美",
            ]
        elif song.title == "認めてくれなくたっていいよ":
            song.artists = [
                "藤原肇",
                "松永涼",
                "三船美優",
                "黒埼ちとせ",
                "早坂美玲",
            ]

        # ユニット名の対応
        def pretty_unit(unit_name, artists):
            if unit_name in song.artists:
                song.unit_name = unit_name
                song.artists = artists

        pretty_unit(
            "CINDERELLA PROJECT",
            [
                "島村卯月",
                "渋谷凛",
                "本田未央",
                "双葉杏",
                "三村かな子",
                "城ヶ崎莉嘉",
                "神崎蘭子",
                "前川みく",
                "諸星きらり",
                "多田李衣菜",
                "赤城みりあ",
                "新田美波",
                "緒方智絵里",
                "アナスタシア",
            ],
        )
        pretty_unit("new generations", ["島村卯月", "渋谷凛", "本田未央"])
        pretty_unit("LOVE LAIKA", ["新田美波", "アナスタシア"])
        pretty_unit("Rosenburg Engel", ["神崎蘭子"])
        pretty_unit("CANDY ISLAND", ["三村かな子", "双葉杏", "緒方智絵里"])
        pretty_unit("凸レーション", ["城ヶ崎莉嘉", "諸星きらり", "赤城みりあ"])
        pretty_unit("*(Asterisk)", ["前川みく", "多田李衣菜"])
        pretty_unit("Triad Primus", ["渋谷凛", "神谷奈緒", "北条加蓮"])

        # with が含まれるユニット名の対応
        def pretty_unit_with(title, unit_name, artists):
            if title == song.title:
                song.unit_name = unit_name
                song.artists = artists

        pretty_unit_with("私色ギフト", "凸レーション with 城ヶ崎美嘉", ["城ヶ崎莉嘉", "諸星きらり", "赤城みりあ", "城ヶ崎美嘉"])
        pretty_unit_with("Heart Voice", "CANDY ISLAND with 輿水幸子", ["三村かな子", "双葉杏", "緒方智絵里", "輿水幸子"])
        pretty_unit_with("Wonder goes on!!", "*(Asterisk) with なつなな", ["前川みく", "多田李衣菜", "木村夏樹", "安部菜々"])
        pretty_unit_with("この空の下", "LOVE LAIKA with Rosenburg Engel", ["新田美波", "アナスタシア", "神崎蘭子"])

        if song.artists == ["U149"]:
            song.artists = ["橘ありす", "櫻井桃華", "赤城みりあ", "的場梨沙", "結城晴", "佐々木千枝", "龍崎薫", "市原仁奈", "古賀小春"]
            song.unit_name = "U149"

    def _other_songs(self) -> list[Song]:
        return [
            # jewelries! の属性別対応
            Song("ススメ☆オトメ〜jewel parade〜(Cool)", ["渋谷凛", "高垣楓", "神崎蘭子", "多田李衣菜", "新田美波"]),
            Song("ススメ☆オトメ〜jewel parade〜(Cute)", ["双葉杏", "前川みく", "島村卯月", "小日向美穂", "安部菜々"]),
            Song("ススメ☆オトメ〜jewel parade〜(Passion)", ["城ヶ崎莉嘉", "諸星きらり", "城ヶ崎美嘉", "本田未央", "赤城みりあ"]),
            Song("ゴキゲンParty Night(Cool)", ["川島瑞樹", "白坂小梅", "アナスタシア", "神谷奈緒", "北条加蓮"]),
            Song("ゴキゲンParty Night(Cute)", ["三村かな子", "輿水幸子", "佐久間まゆ", "緒方智絵里", "小早川紗枝"]),
            Song("ゴキゲンParty Night(Passion)", ["十時愛梨", "日野茜", "高森藍子", "星輝子", "堀裕子"]),
            Song("Near to You(Cool)", ["鷺沢文香", "速水奏", "橘ありす", "塩見周子", "二宮飛鳥"]),
            Song("Near to You(Cute)", ["宮本フレデリカ", "一ノ瀬志希", "櫻井桃華", "中野有香", "五十嵐響子"]),
            Song("Near to You(Passion)", ["姫川友紀", "市原仁奈", "片桐早苗", "大槻唯", "相葉夕美"]),
            Song("認めてくれなくたっていいよ(Cool)", ["松永涼", "三船美優", "森久保乃々", "藤原肇", "砂塚あきら"]),
            Song("認めてくれなくたっていいよ(Cute)", ["乙倉悠貴", "関裕美", "白菊ほたる", "早坂美玲", "黒埼ちとせ"]),
            # "GOUDOU_15th"
            Song(
                "なんどでも笑おう",
                [
                    "天海春香",
                    "如月千早",
                    "星井美希",
                    "島村卯月",
                    "渋谷凛",
                    "本田未央",
                    "春日未来",
                    "最上静香",
                    "伊吹翼",
                    "天道輝",
                    "桜庭薫",
                    "柏木翼",
                    "櫻木真乃",
                    "風野灯織",
                    "八宮めぐる",
                ],
                "THE IDOLM@STER FIVE STARS!!!!!",
            ),
            # "GOUDOU_2021"
            Song(
                "VOY@GER",
                [
                    "天海春香",
                    "菊地真",
                    "四条貴音",
                    "塩見周子",
                    "新田美波",
                    "久川颯",
                    "高坂海美",
                    "白石紬",
                    "望月杏奈",
                    "鷹城恭二",
                    "黒野玄武",
                    "古論クリス",
                    "有栖川夏葉",
                    "黛冬優子",
                    "浅倉透",
                ],
                "THE IDOLM@STER FIVE STARS!!!!!",
            ),
        ]
