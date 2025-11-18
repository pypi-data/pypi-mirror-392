import requests
from bs4 import BeautifulSoup
import typing
import time


class LeaderboardGroup:
    def __init__(self, app_id):
        xml = requests.get(f"https://steamcommunity.com/stats/{app_id}/leaderboards/?xml=1")
        _bs = BeautifulSoup(xml.content, features="lxml-xml")
        self.leaderboards = []
        self.app_id = app_id
        for leaderboard in _bs.find_all("leaderboard"):
            self.leaderboards.append(ProtoLeaderboard(leaderboard, app_id))

    def __repr__(self):
        return f"<LeaderboardGroup for {self.app_id} with {len(self.leaderboards)} leaderboards>"

    def get(self, name=None, *, lbid=None, display_name=None, **kwargs) -> typing.Optional["Leaderboard"]:
        """Get the full leaderboard with the specified parameter."""
        if bool(lbid) + bool(name) + bool(display_name) > 1:
            raise ValueError("You can only find a leaderboard by 1 parameter.")
        if lbid is not None:
            if not isinstance(lbid, int):
                raise ValueError("lbid must be an int")
            for leaderboard in self.leaderboards:
                if leaderboard.lbid == lbid:
                    return leaderboard.full(**kwargs)
        elif name is not None:
            if not isinstance(name, str):
                raise ValueError("name must be a str")
            for leaderboard in self.leaderboards:
                if leaderboard.name == name:
                    return leaderboard.full(**kwargs)
        elif display_name is not None:
            if not isinstance(display_name, str):
                raise ValueError("display_name must be a str")
            for leaderboard in self.leaderboards:
                if leaderboard.display_name == display_name:
                    return leaderboard.full(**kwargs)
        return None


class ProtoLeaderboard:
    """Information about a leaderboard retrieved through a leaderboard"""
    def __init__(self, soup, app_id):
        self.url = soup.url.text
        self.lbid = int(soup.lbid.text)
        self.name = soup.find("name").text
        self.display_name = soup.display_name.text
        self.entries = int(soup.entries.text)
        self.sort_method = int(soup.sortmethod.text)
        self.display_type = int(soup.displaytype.text)
        self.app_id = app_id

    def full(self, **kwargs) -> "Leaderboard":
        return Leaderboard(**kwargs, protoleaderboard=self)


class Leaderboard:
    # noinspection PyMissingConstructor
    def __init__(self, app_id=None, lbid=None, *, protoleaderboard=None, limit=None, delay=None):
        if protoleaderboard:
            self.url = protoleaderboard.url
            self.lbid = protoleaderboard.lbid
            self.name = protoleaderboard.name
            self.display_name = protoleaderboard.display_name
            self.entries = protoleaderboard.entries
            self.sort_method = protoleaderboard.sort_method
            self.display_type = protoleaderboard.display_type
            self.app_id = protoleaderboard.app_id
        elif app_id and lbid:
            self.lbid = lbid
            self.app_id = app_id
            self.url = f"https://steamcommunity.com/stats/{self.app_id}/leaderboards/{self.lbid}/?xml=1"
            self.name = None
            self.display_name = None
            self.entries = None
            self.sort_method = None
            self.display_type = None
        else:
            raise ValueError("No app_id, lbid or protoleaderboard specified")
        if limit is None:
            limit = 5000
        if delay is None:
            delay = 0.5
        next_request_url = self.url
        self.entries = []
        while next_request_url:
            xml = requests.get(next_request_url)
            _bs = BeautifulSoup(xml.content, features="lxml-xml")
            for entry in _bs.find_all("entry"):
                self.entries.append(Entry(entry))
                if len(self.entries) >= limit:
                    next_request_url = None
                    self.entries = self.entries[:limit]
                    break
            else:
                try:
                    next_request_url = _bs.find_all("nextRequestURL")[0].text
                except IndexError:
                    next_request_url = None
                else:
                    time.sleep(delay)

    def __repr__(self):
        if self.name:
            return f'<Leaderboard "{self.name}" for {self.app_id} with {len(self.entries)}>'
        else:
            return f'<Leaderboard [{self.lbid}] for {self.app_id} with {len(self.entries)}>'

    def find_entry(self, steam_id=None, *, rank=None):
        if bool(steam_id) + bool(rank) > 1:
            raise ValueError("You can only find an entry by 1 parameter.")
        if steam_id is not None:
            if not isinstance(steam_id, str):
                raise ValueError("steam_id must be a str")
            for entry in self.entries:
                if entry.steam_id == steam_id:
                    return entry
            else:
                return None
        elif rank is not None:
            if not isinstance(rank, int):
                raise ValueError("steam_id must be an int")
            try:
                return self.entries[rank - 1]
            except IndexError:
                return None


class Entry:
    def __init__(self, soup):
        self.steam_id = soup.steamid.text
        self.score = int(soup.score.text)
        self.rank = int(soup.rank.text)
        self.ugcid = soup.ugcid.text
        self.details = soup.details.text

    def __repr__(self):
        return f"<Entry #{self.rank} {self.steam_id}: {self.score} pts>"
