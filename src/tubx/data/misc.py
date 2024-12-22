import pandas as pd
from qubx.pandaz.utils import scols, srows
from qubx.utils.marketdata.binance import load_binance_markets_info


class BinanceMarketsHelper:
    """
    Simple helper for Binance markets
    """

    markets: pd.DataFrame
    sectors: dict[str, pd.DataFrame]

    def __init__(self) -> None:
        m, s = load_binance_markets_info()
        self.markets = m
        self.sectors = s

    def ls_sectors(self, not_include=[]) -> list[str]:
        return [s for s in list(self.sectors.keys()) if s not in not_include]

    def find(
        self,
        coin: str | list[str] | None = None,
        sector: str | None = None,
        quoted: str | list[str] | None = None,
        min_mkt_cap=0,
    ) -> pd.DataFrame:
        if quoted and isinstance(quoted, (list, set, tuple)):
            return srows(*[self.find(coin, sector, q, min_mkt_cap) for q in quoted])

        if isinstance(coin, (list, set, tuple)):
            return srows(*[self.find(c, sector, quoted, min_mkt_cap) for c in coin])

        r = self.sectors.get(sector, self.markets)  # type: ignore

        # r = r[r['Coin'] == coin] if coin else r
        # r = r[r['Quoted'] == quoted] if quoted else r

        cond = r["Coin"] != None
        if coin and quoted:
            cond = (r["Coin"] == coin) & (r["Quoted"] == quoted)
        else:
            if coin:
                cond = (r["Coin"] == coin) | (r["Quoted"] == coin)
            elif quoted:
                cond = r["Quoted"] == quoted

        r = r[cond]
        r = r[r["MarketCap"] >= min_mkt_cap]
        return r.reset_index(drop=True)

    def select(
        self,
        quoted,
        sectors=None,
        exclude_coins=[],
        add_coins=[],
        min_mkt_cap=0,
        limit_per_sector=-1,
    ) -> pd.DataFrame:
        n_per_sector = 1_000_000 if limit_per_sector < 0 else limit_per_sector
        rs = pd.DataFrame()
        sectors = self.ls_sectors() if sectors is None else sectors
        for s in sectors:
            r = self.find(sector=s, quoted=quoted, min_mkt_cap=min_mkt_cap)
            r = r[:n_per_sector]
            rs = srows(rs, r[~r["Coin"].isin(exclude_coins)])

        for ac in add_coins:
            if ac not in exclude_coins:
                rs = srows(rs, self.find(ac, quoted=quoted, min_mkt_cap=min_mkt_cap))

        rs = rs.drop_duplicates("Symbol").sort_values("MarketCap", ascending=False).reset_index(drop=True)

        return rs

    def get_all_stablecoins(self):
        return set(self.find(sector="stablecoin")["Coin"])

    def listings_by_sector(
        self, quoted=None, exclude=[], coins=[], min_mkt_cap=0, limit_per_sector=100000, fillna="", as_frame=True
    ) -> pd.DataFrame | dict:
        sec_rep = {}
        for s in self.ls_sectors(not_include=exclude):
            pres = self.select(quoted, sectors=[s], limit_per_sector=limit_per_sector, min_mkt_cap=min_mkt_cap)
            pres = pres[pres["Coin"].isin(coins)] if coins else pres
            sec_rep[s] = pres[["Symbol", "MarketCap"]]
        if as_frame:
            data = scols(*sec_rep.values(), keys=sec_rep.keys())
            return data.fillna("") if fillna else data
        return sec_rep
