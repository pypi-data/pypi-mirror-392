import re
import pandas as pd
from typing import Optional, Union, List, Type, cast
from types import TracebackType

# Shared universe state used to filter datasets
universe_stocks = set()


class universe():
    """Context manager to set a global stock universe filter for data retrieval.

    This context manager limits the set of stocks returned by functions such as
    `finlab.data.get(...)` and `finlab.data.indicator(...)` to a specific market
    and category selection. The filter is applied globally within the context and
    is restored after the context exits.

    Parameters
    ----------
    market : str, default 'ALL'
        Market scope to include. Supported values:
        - 'ALL': no market filter
        - 'TSE': TWSE (sii)
        - 'OTC': TPEx (otc)
        - 'TSE_OTC': include both TWSE and TPEx
        - 'ETF': exchange-traded funds
        - 'STOCK_FUTURE': underlying of single-stock futures/equity options

    category : str | list[str], default 'ALL'
        Category name(s) to include. Supports regex-like substring matching.
        For example, '電子' will match '電子工業', '電子通路業', etc. When a list is
        provided, the union of all matched categories is included.

    exclude_category : str | list[str] | None, default None
        Category name(s) to exclude from the resulting universe. Also supports
        regex-like substring matching. When None, no exclusion is applied.

    Notes
    -----
    - The filter is applied to the internal `universe_stocks` set, which is then
      used by the data processing pipeline to select columns/rows corresponding to
      the chosen stocks.
    - Inside the context, calls to `data.get(...)` will return data limited to the
      specified universe whenever applicable.
    - After exiting the `with` block, the previous universe is restored.

    Examples
    --------
    Limit to TSE/OTC and include only specific categories:

    >>> from finlab import data
    >>> with data.universe(market='TSE_OTC', category=['鋼鐵工業', '航運業']):
    ...     close = data.get('price:收盤價')

    Include categories but exclude financial-related stocks:

    >>> from finlab import data
    >>> with data.universe('TSE_OTC', ['鋼鐵工業', '航運業'], exclude_category=['金融']):
    ...     close = data.get('price:收盤價')

    Equivalent global (non-context) usage:

    >>> from finlab import data
    >>> data.set_universe(market='TSE_OTC', category='水泥', exclude_category='ETF')
    >>> close = data.get('price:收盤價')
    """
    def __init__(
        self,
        market: str = 'ALL',
        category: Union[str, List[str]] = 'ALL',
        exclude_category: Optional[Union[str, List[str]]] = None,
    ) -> None:
        self._market = market
        self._category = category
        self._exclude_category = exclude_category
        self._previous_stocks = set()

    def __enter__(self):
        global universe_stocks
        self._previous_stocks = universe_stocks
        set_universe(self._market, self._category, self._exclude_category)
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        global universe_stocks
        universe_stocks = self._previous_stocks


def set_universe(
    market: str = 'ALL',
    category: Union[str, List[str]] = 'ALL',
    exclude_category: Optional[Union[str, List[str]]] = None,
) -> None:
    from . import data as data_module

    categories = data_module.get('security_categories').reset_index().set_index('stock_id')

    market_match = pd.Series(True, categories.index)

    if 'TSE' in market and 'OTC' in market:
        market = 'TSE_OTC'

    if market == 'ALL':
        pass
    elif market == 'TSE':
        market_match = categories.market == 'sii'
    elif market == 'OTC':
        market_match = categories.market == 'otc'
    elif market == 'TSE_OTC':
        market_match = (categories.market == 'sii') | (categories.market == 'otc')
    elif market == 'ETF':
        market_match = categories.market == 'etf'
    elif market == 'STOCK_FUTURE':
        market_match = data_module.get('single_stock_futures_and_equity_options_underlying')\
            .pipe(lambda df: df[df['是否為股票期貨標的'] == 'Y'])\
            .pipe(lambda df: pd.Series(True, set(df.stock_id)).reindex(categories.index).fillna(False))

    category_match = pd.Series(True, categories.index)

    if category == 'ALL':
        pass
    else:
        if isinstance(category, str):
            category = [category]

        matched_categories = set()
        all_categories = set(categories.category)
        for ca in category:
            matched_categories |= set([c for c in all_categories if isinstance(c, str) and re.search(ca, c)])
        category_match = categories.category.isin(list(matched_categories))

    exclude_match = pd.Series(True, categories.index)
    if exclude_category is not None:
        if isinstance(exclude_category, str):
            exclude_category = [exclude_category]
        matched_excluded = set()
        all_categories = set(categories.category)
        for ca in exclude_category:
            matched_excluded |= set([c for c in all_categories if isinstance(c, str) and re.search(ca, c)])
        # Exclude by category names
        exclude_by_category = ~categories.category.isin(list(matched_excluded))
        # Special-case: if excluding 'ETF', also exclude market == 'etf'
        exclude_by_market = pd.Series(True, categories.index)
        if any(isinstance(ca, str) and ca.strip().lower() == 'etf' for ca in exclude_category):
            exclude_by_market = categories.market != 'etf'
        exclude_match = exclude_by_category & exclude_by_market

    global universe_stocks
    universe_stocks = set(categories.index[market_match & category_match & exclude_match])


class us_universe:
    def __init__(
        self,
        market: str = 'ALL',
        sector: Union[str, List[str]] = 'ALL',
        industry: Union[str, List[str]] = 'ALL',
        exchange: Union[str, List[str]] = 'ALL',
    ) -> None:
        self._market = market
        self._sector = sector
        self._industry = industry
        self._exchange = exchange
        self._previous_stocks = set()

    def __enter__(self):
        global universe_stocks
        self._previous_stocks = universe_stocks
        set_us_universe(self._market, self._sector, self._industry, self._exchange)
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        global universe_stocks
        universe_stocks = self._previous_stocks


def set_us_universe(
    market: str = 'ALL',
    sector: Union[str, List[str]] = 'ALL',
    industry: Union[str, List[str]] = 'ALL',
    exchange: Union[str, List[str]] = 'ALL',
) -> None:
    from . import data as data_module

    categories = data_module.get('us_tickers').reset_index().set_index('stock_id')
    market_range = [
        'ADR Common Stock',
        'ADR Common Stock Primary Class',
        'ADR Common Stock Secondary Class',
        'ADR Preferred Stock',
        'Domestic Common Stock',
        'Domestic Common Stock Primary Class',
        'Domestic Common Stock Secondary Class',
        'Domestic Preferred Stock',
    ]

    if market == 'ALL':
        market_match = categories.category.isin(market_range)
    else:
        market_match = categories.category.isin([m for m in market_range if market in m])

    def match_ids(column: str, item: Union[str, List[str]]) -> pd.Series:
        category_match: pd.Series = pd.Series(True, categories.index)
        if item == 'ALL':
            pass
        else:
            if isinstance(item, str):
                item = [item]
            matched_categories = set()
            all_categories = set(categories[column])
            for ca in item:
                matched_categories |= set([c for c in all_categories if isinstance(c, str) and re.search(ca, c)])
            category_match = cast(pd.Series, categories[column].isin(list(matched_categories)))
        return category_match

    sector_match = match_ids('sector', sector)
    industry_match = match_ids('industry', industry)

    exchange_match = pd.Series(True, categories.index)
    if exchange == 'ALL':
        pass
    else:
        if isinstance(exchange, str):
            exchange = [exchange]
        exchange_match = categories.exchange.isin(exchange)

    global universe_stocks
    universe_stocks = set(categories.index[market_match & sector_match & industry_match & exchange_match])


not_available_universe_stocks = [
    'benchmark_return', 'institutional_investors_trading_all_market_summary',
    'margin_balance', 'intraday_trading_stat',
    'stock_index_price', 'stock_index_vol',
    'taiex_total_index', 'broker_info',
    'rotc_monthly_revenue', 'rotc_price',
    'world_index', 'rotc_broker_trade_record',
    'security_categories', 'finlab_tw_stock_market_ind',
    'tw_industry_pmi', 'tw_industry_nmi',
    'tw_total_pmi', 'tw_total_nmi',
    'tw_business_indicators', 'tw_business_indicators_details',
    'tw_monetary_aggregates', 'us_unemployment_rate_seasonally_adjusted',
    'us_tickers',
]


def refine_stock_id(dataset: str, ret: pd.DataFrame) -> pd.DataFrame:
    from .data import process_data  # lazy import to avoid circular dependency

    ret = process_data(dataset, ret)

    if dataset in not_available_universe_stocks:
        return ret

    if not universe_stocks:
        return ret

    if ':' in dataset:
        subset_stocks = [c for c in ret.columns if c in universe_stocks]
        if len(subset_stocks) > 0:
            return ret.loc[:, subset_stocks]

    if 'stock_id' in ret.columns:
        subset_stocks = ret['stock_id'].isin(list(universe_stocks))
        if bool(subset_stocks.any()):
            return ret.loc[subset_stocks]

    return ret



