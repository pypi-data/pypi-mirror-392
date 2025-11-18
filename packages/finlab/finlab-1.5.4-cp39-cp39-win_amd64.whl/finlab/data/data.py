import gc
import re
import sys
import json
import time
import math
import logging
import hashlib
import datetime
import numpy as np
import pandas as pd
from io import BytesIO
from functools import lru_cache

import finlab.utils
import finlab.dataframe
from finlab import config
from .storage import CacheStorage, FileStorage
from .universe import universe, set_universe, us_universe, set_us_universe, refine_stock_id

logger = logging.getLogger(__name__)

_has_print_free_user_warning = False
_role = None
use_local_data_only = False
force_cloud_download = False
truncate_start = None
truncate_end = None
prefer_local_if_exists = False

_storage = FileStorage()

 

def clear():
    """清除本地端儲存的歷史資料，並還原初始設定。
    Examples:
        ``` py
        from finlab import data
        data.clear()
        ```
    """
    global _storage
    if isinstance(_storage, FileStorage):
        _storage.clear()
    _storage = FileStorage()



def set_storage(storage):
    """設定本地端儲存歷史資料的方式
    假設使用 `data.get` 獲取歷史資料則，在預設情況下，程式會自動在本地複製一份，以避免重複下載大量數據。
    storage 就是用來儲存歷史資料的接口。我們提供兩種 `storage` 接口，分別是 `finlab.data.CacheStorage` (預設) 以及
    `finlab.data.FileStorage`。前者是直接存在記憶體中，後者是存在檔案中。詳情請參考 `CacheStorage` 和 `FileStorage` 來獲得更詳細的資訊。
    在預設情況下，程式會自動使用 `finlab.data.FileStorage` 並將重複索取之歷史資料存在作業系統預設「暫時資料夾」。

    Args:
        storage (data.Storage): The interface of storage

    Examples:
        欲切換成以檔案方式儲存，可以用以下之方式：

        ``` py
        from finlab import data
        data.set_storage(data.FileStorage())
        close = data.get('price:收盤價')
        ```

        可以在本地端的 `./finlab_db/price#收盤價.pickle` 中，看到下載的資料，
        可以使用 `pickle` 調閱歷史資料：
        ``` py
        import pickle
        close = pickle.load(open('finlab_db/price#收盤價.pickle', 'rb'))
        ```
    """

    global _storage
    _storage = storage



def fetch_data(dataset: str, time_saved=None):
    """
    Fetches data from a specified dataset.

    Args:
        dataset (str): The name of the dataset to fetch.
        time_saved (datetime, optional): The time to fetch the data from. Defaults to None.

    Returns:
        dict: A dictionary containing the fetched data and other information.
    """

    url = 'https://asia-east2-fdata-299302.cloudfunctions.net/auth_generate_data_url'
    params = {
        'api_token': finlab.get_token(),
        'bucket_name': 'finlab_tw_stock_item',
        'blob_name': dataset.replace(':', '#') \
                + ('.pickle' if "pyodide" in sys.modules else '.feather'),
        'pyodide': 'pyodide' in sys.modules
    }
    if time_saved:
        params['time_saved'] = time_saved.strftime('%Y%m%d%H%M%S')

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',}
    try:
        res = finlab.utils.requests.post(url, params, headers=headers, timeout=300)
    except Exception as e:
        time.sleep(3)
        res = finlab.utils.requests.post(url, params, headers=headers, timeout=300)

    ret = res.json()

    if 'error' in ret:

        if ret['error'] in [
            'request not valid',
            'User not found',
            'api_token not valid',
            'api_token not match', ]:
            finlab.login()
            return fetch_data(dataset, time_saved)
        
        if ret['error'] == 'Usage exceed 500 MB/day. Please consider upgrade to VIP program.':
            raise Exception(f"**Error: {ret['error']}")

        if ret['error'] == 'Usage exceed 5000 MB/day. Please consider upgrade to VIP program.':
            raise Exception(f"**Error: Usage exceed 5000 MB/day. Please consider reaching out to us at https://discord.gg/tAr4ysPqvR to reset your usage.")

        return None

    _role = ret.get('role', None)
    # print free user warning
    global _has_print_free_user_warning
    if not _has_print_free_user_warning \
            and _role in ret \
            and _role == 'free':
        print('Due to your status as a free user, '
            'the most recent data has been shortened or limited.')
        _has_print_free_user_warning = True

    if 'quota' in ret and '.recent' not in dataset:
        print(f'Daily usage: {ret["quota"]:.1f} / {ret["limit_size"]} MB - {dataset}')

    ret['expiry'] = datetime.datetime.strptime(
        ret['time_scheduled'], '%Y%m%d%H%M%S').replace(tzinfo=datetime.timezone.utc)\
        if 'time_scheduled' in ret else None
    
    # download data if server return an url
    if 'url' in ret and len(ret['url']) > 0:

        if 'pyodide' in sys.modules:
            if hasattr(finlab.utils.requests, 'getBytes'):
                res = finlab.utils.requests.getBytes(ret['url'])
                df = pd.read_pickle(BytesIO(res), compression='gzip')
            else:
                res = finlab.utils.requests.get(ret['url'], timeout=300)
                df = pd.read_pickle(BytesIO(res.content), compression='gzip')
        else:
            res = finlab.utils.requests.get(ret['url'], headers=headers, timeout=300)
            df = pd.read_feather(BytesIO(res.content))

        ret['data'] = df#process_data(dataset, df)
    return ret



def has_index_name(df, name):
    # Check if the DataFrame has a single index
    if df.index.name == name:
        return True
    # Check if the DataFrame has a MultiIndex
    elif isinstance(df.index, pd.MultiIndex):
        if name in df.index.names:
            return True
    return False


def process_data(dataset, df):

    if 'stock_id' in df.columns and 'date' in df.columns:
        df.set_index(['stock_id', 'date'], inplace=True)
    elif 'date' in df.columns:
        df.set_index('date', inplace=True)
    elif 'stock_id' in df.columns:
        df.set_index('stock_id', inplace=True)

    # special case (to align with tutorial)
    if dataset == 'broker_transactions':
        df = df.reset_index().set_index('date')

    # the column name is stock id, and index is date
    if ':' in dataset:
        df.columns.name = 'symbol'

    # table format
    if ':' not in dataset:
        df = df.reset_index()

    if not has_index_name(df, 'date'):
        return df

    table_name = dataset.split(':')[0]
    if table_name in ['tw_total_pmi', 'tw_total_nmi', 'tw_industry_nmi', 'tw_industry_pmi']:
        if isinstance(df.index[0], pd.Timestamp):
            close = get('price:收盤價')
            df.index = df.index.map(
                lambda d: d if len(close.loc[d:]) == 0 or d < close.index[0] else close.loc[d:].index[0])

    # if column is stock name
    if (df.columns.str.find(' ') != -1).all():

        # remove stock names
        df.columns = df.columns.str.split(' ').str[0]

        # combine same stock history according to sid
        check_numeric_dtype = pd.api.types.is_numeric_dtype(df.values)
        if check_numeric_dtype:
            df = df.transpose().groupby(level=0).mean().transpose()
        else:
            df = df.fillna(np.nan).transpose().groupby(
                level=0).last().transpose()

    df = finlab.dataframe.FinlabDataFrame(df)

    if isinstance(df.index, pd.DatetimeIndex):
        # Read truncate window from the package module if set via `from finlab import data; data.truncate_start = ...`
        package_module = sys.modules.get('finlab.data')
        effective_truncate_start = truncate_start
        effective_truncate_end = truncate_end
        if package_module is not None:
            effective_truncate_start = getattr(package_module, 'truncate_start', effective_truncate_start)
            effective_truncate_end = getattr(package_module, 'truncate_end', effective_truncate_end)
        df = df.loc[effective_truncate_start:effective_truncate_end]

    if table_name in ['monthly_revenue', 'rotc_monthly_revenue']:
        df = df._index_to_business_day()
    elif table_name in ['financial_statement', 'fundamental_features',]:
        df = df._index_date_to_str_season()
    elif table_name in ['us_fundamental', 'us_fundamental_ART']:
        df = df._index_date_to_str_season('-US')
    elif table_name in ['us_fundamental_all', 'us_fundamental_all_ART']:
        df = df._index_date_to_str_season('-US-ALL')

    return df



def _apply_truncate_if_any(df):
    package_module = sys.modules.get('finlab.data')
    effective_truncate_start = truncate_start
    effective_truncate_end = truncate_end
    if package_module is not None:
        effective_truncate_start = getattr(package_module, 'truncate_start', effective_truncate_start)
        effective_truncate_end = getattr(package_module, 'truncate_end', effective_truncate_end)
    if isinstance(df.index, pd.DatetimeIndex):
        return df.loc[effective_truncate_start:effective_truncate_end]
    return df


def _finalize(dataset, df):
    df = _apply_truncate_if_any(df)
    return refine_stock_id(dataset, finlab.dataframe.FinlabDataFrame(df))


def hash(df):
    return hashlib.md5(pd.util.hash_pandas_object(df, index=True).values).hexdigest()[:7]



def get(dataset: str, save_to_storage: bool = True, force_download=False) -> finlab.dataframe.FinlabDataFrame:
    """下載歷史資料

    請至[歷史資料目錄](https://ai.finlab.tw/database) 來獲得所有歷史資料的名稱，即可使用此函式來獲取歷史資料。
    假設 `save_to_storage` 為 `True` 則，程式會自動在本地複製一份，以避免重複下載大量數據。

    Args:
        dataset (str): The name of dataset.
        save_to_storage (bool): Whether to save the dataset to storage for later use. Default is True. The argument will be removed in the future. Please use data.set_storage(FileStorage(use_cache=True)) instead.
        force_download (bool): Whether to force download the dataset from cloud. Default is False.

    Returns:
        (pd.DataFrame): financial data

    Examples:
        欲下載所有上市上櫃之收盤價歷史資料，只需要使用此函式即可:

        ``` py
        from finlab import data
        close = data.get('price:收盤價')
        close
        ```

        | date       |   0015 |   0050 |   0051 |   0052 |   0053 |
        |:-----------|-------:|-------:|-------:|-------:|-------:|
        | 2007-04-23 |   9.54 |  57.85 |  32.83 |  38.4  |    nan |
        | 2007-04-24 |   9.54 |  58.1  |  32.99 |  38.65 |    nan |
        | 2007-04-25 |   9.52 |  57.6  |  32.8  |  38.59 |    nan |
        | 2007-04-26 |   9.59 |  57.7  |  32.8  |  38.6  |    nan |
        | 2007-04-27 |   9.55 |  57.5  |  32.72 |  38.4  |    nan |

        !!!note
            使用 `data.get` 時，會預設優先下載近期資料，並與本地資料合併，以避免重複下載大量數據。

            假如想要強制下載所有資料，可以在下載資料前，使用
            ```py
            data.force_cloud_download = True
            ```
            假如想要強制使用本地資料，不額外下載，可以在下載資料前，使用
            ```py
            data.use_local_data_only = True
            ```

    """
    finlab.utils.check_version()

    global _storage
    global force_cloud_download
    global use_local_data_only

    if not save_to_storage:
        logger.warning('save_to_storage will be deprecated after 2024/06/01. Please use data.set_storage(CacheStorage()) to disable data saved to local storage')
    
    # Read flags from the package module if users set them via `from finlab import data; data.use_local_data_only = True`
    # This avoids the issue where re-exported booleans in package __init__ are decoupled from this module's globals.
    package_module = sys.modules.get('finlab.data')
    effective_force_cloud_download = force_cloud_download
    effective_use_local_data_only = use_local_data_only
    effective_prefer_local_if_exists = prefer_local_if_exists
    if package_module is not None:
        effective_force_cloud_download = getattr(package_module, 'force_cloud_download', effective_force_cloud_download)
        effective_use_local_data_only = getattr(package_module, 'use_local_data_only', effective_use_local_data_only)
        effective_prefer_local_if_exists = getattr(package_module, 'prefer_local_if_exists', effective_prefer_local_if_exists)

    force_download |= effective_force_cloud_download

    if effective_use_local_data_only and force_download:
        raise Exception('data.use_local_data_only and data.force_download cannot be both True')
    
    if effective_use_local_data_only:
        df = _storage.get_dataframe(dataset)
        if df is not None and len(df) != 0:
            return _finalize(dataset, df)
        raise Exception(f"**Error: {dataset} not exists at local storage. Please set data.use_local_data_only = False to download data from cloud.")

    # Prefer local cache if present without checking for updates/expiry, but allow fallback to cloud
    if effective_prefer_local_if_exists and not force_download:
        df = _storage.get_dataframe(dataset)
        if df is not None and len(df) != 0:
            logger.debug(f'{dataset} prefer_local_if_exists enabled -> get data from local without update check')
            return _finalize(dataset, df)


    # not expired
    time_expired = _storage.get_time_expired(dataset)
    df = _storage.get_dataframe(dataset)
    if time_expired and time_expired > CacheStorage.now() and not force_download and df is not None and len(df) != 0:
        logger.debug(f'{dataset} not expired -> get data from local')
        return _finalize(dataset, df)
    
    # free user can only use historical data without merge
    global _role
    if _role == 'free' and df is not None:
        return _finalize(dataset, df)
    
    ############################
    # try to merge short data
    ############################
    if df is not None and len(df) != 0:
        url_data = fetch_data(dataset + '.recent', time_saved=_storage.get_time_created(dataset))
        if url_data is not None and df is not None and len(df) != 0 and not force_download:
            if 'data' not in url_data:
                _storage.set_time_expired(dataset, url_data['expiry'])
                logger.debug(f'{dataset} get recent, server says not expired -> get data from local')
                return _finalize(dataset, df)

            short_df = url_data['data']
            merge_success = False
            try:
                compare_cols = df.columns.intersection(['stock_id', 'date', '持股分級', 'broker'])
                df = pd.concat([df, short_df])\
                    .pipe(lambda df: df[~df.duplicated(subset=compare_cols, keep='last')])\
                    [short_df.columns]\
                    .reset_index(drop=True)
                merge_success = True
            except Exception as e:
                # logger.warning(f'{dataset} get recent, merge fail -> cancel merge recent to local data')
                pass

            if merge_success:
                hash_df = hash(df)
                logger.debug(f'hash df: {hash_df} url: {url_data.get("hash", None)}')

                if url_data.get('hash', None) == hash_df and len(df) != 0:
                    _storage.set_dataframe(dataset, df, expiry=url_data['expiry'])
                    logger.debug('get recent, is valid -> and merge recent to local data')
                    return _finalize(dataset, df)
                else:
                    pass
                    # logger.warning(f' {dataset} get recent, shape not valid -> cancel merge recent to local data')
        del url_data

    ###################
    # all data download
    ###################
    del df
    gc.collect()
    
    # expired at local but may not expired at server
    url_data = fetch_data(dataset)

    if url_data is None:
        raise Exception(f"**Error: {dataset} not exists")

    df = url_data['data']

    # fallback to cache storage if user is free user
    if url_data is not None and _role is None:
        if url_data['role'] == 'free':
            _role = 'free'
            _storage = CacheStorage()

    if len(df) > 0:
        _storage.set_dataframe(dataset, df, expiry=url_data['expiry'])
    
    if len(df) == 0:
        raise Exception(f"**Error: {dataset} download fail")

    logger.debug(f' {dataset} get recent, merge fail -> get whole data from cloud')
    return _finalize(dataset, df)



def get_input_args(attr):
    input_names = attr.input_names
    refine_input_names = []
    for key, val in input_names.items():
        if 'price' in key:
            if isinstance(val, list):
                refine_input_names += val
            elif isinstance(val, str):
                refine_input_names.append(val)

    return refine_input_names


def indicator(indname, adjust_price=False, resample='D', **kwargs):
    """支援 Talib 和 pandas_ta 上百種技術指標，計算 2000 檔股票、10年的所有資訊。

    在使用這個函式前，需要安裝計算技術指標的 Packages

    * [Ta-Lib](https://github.com/mrjbq7/ta-lib)
    * [Pandas-ta](https://github.com/twopirllc/pandas-ta)

    Args:
        indname (str): 指標名稱，
            以 TA-Lib 舉例，例如 SMA, STOCH, RSI 等，可以參考 [talib 文件](https://mrjbq7.github.io/ta-lib/doc_index.html)。

            以 Pandas-ta 舉例，例如 supertrend, ssf 等，可以參考 [Pandas-ta 文件](https://twopirllc.github.io/pandas-ta/#indicators-by-category)。
        adjust_price (bool): 是否使用還原股價計算。
        resample (str): 技術指標價格週期，ex: `D` 代表日線, `W` 代表週線, `M` 代表月線。
        market (str): 市場選擇，ex: `TW_STOCK` 代表台股, `US_STOCK` 代表美股。
        **kwargs (dict): 技術指標的參數設定，TA-Lib 中的 RSI 為例，調整項為計算週期 `timeperiod=14`。
    建議使用者可以先參考以下範例，並且搭配 talib官方文件，就可以掌握製作技術指標的方法了。
    """
    package = None

    if not isinstance(adjust_price, bool):
        usage_str = f'data.indicator({indname}, adjust_price={adjust_price}, resample={resample}, **kwargs)'
        example_str = 'k, d = data.indicator("STOCH", adjust_price=True, resample="D", fastk_period=14, fastd_period=3)'
        raise ValueError(f'`adjust_price` must be a bool, e.g. `True`, `False`. Usage: {usage_str}, Example: {example_str}')

    try:
        from talib import abstract
        import talib
        attr = getattr(abstract, indname)
        package = 'talib'
    except:
        try:
            import pandas_ta
            # test df.ta has attribute
            getattr(pd.DataFrame().ta, indname)
            attr = lambda df, **kwargs: getattr(df.ta, indname)(**kwargs)
            package = 'pandas_ta'
        except:
            raise Exception(
                "Please install TA-Lib or pandas_ta to get indicators.")

    market = config.get_market()

    close = market.get_price('close', adj=adjust_price)
    open_ = market.get_price('open', adj=adjust_price)
    high = market.get_price('high', adj=adjust_price)
    low = market.get_price('low', adj=adjust_price)
    volume = market.get_price('volume', adj=adjust_price)


    # check if the dataframes above are same shape
    shape_is_same = all([close.shape == open_.shape, close.shape == high.shape, close.shape == low.shape, close.shape == volume.shape])

    if not shape_is_same:

        logger.warning(f'indicator: {indname} market: {market} has different end date, '
                       'cut to {latest_date}. This is due to server updating data. '
                       'If you want to get the latest data, please try again 3 minutes later.')

        common_idx = close.index.intersection(open_.index).intersection(high.index).intersection(low.index).intersection(volume.index)
        common_cols = close.columns.intersection(open_.columns).intersection(high.columns).intersection(low.columns).intersection(volume.columns)
        
        close = close.loc[common_idx, common_cols]
        open_ = open_.loc[common_idx, common_cols]
        high = high.loc[common_idx, common_cols]
        low = low.loc[common_idx, common_cols]
        volume = volume.loc[common_idx, common_cols]
        

    if resample.upper() != 'D':
        close = close.resample(resample).last()
        open_ = open_.resample(resample).first()
        high = high.resample(resample).max()
        low = low.resample(resample).min()
        volume = volume.resample(resample).sum()
        
    dfs = {}
    default_output_columns = None
    for key in close.columns:

        prices = {'open': open_[key].ffill(),
                  'high': high[key].ffill(),
                  'low': low[key].ffill(),
                  'close': close[key].ffill(),
                  'volume': volume[key].ffill()}

        if prices['close'].iloc[-1] != prices['close'].iloc[-1]:
            continue

        if package == 'pandas_ta':
            prices = pd.DataFrame(prices)
            s = attr(prices, **kwargs)

        elif package == 'talib':
            abstract_input = list(attr.input_names.values())[0]
            abstract_input = get_input_args(attr)

            # quick fix talib bug
            if indname == 'OBV':
                abstract_input = ['close', 'volume']

            if indname == 'BETA':
                abstract_input = ['high', 'low']

            if isinstance(abstract_input, str):
                abstract_input = [abstract_input]
            paras = [prices[k] for k in abstract_input]
            s = attr(*paras, **kwargs)
        else:
            raise Exception("Cannot determine technical package from indname")

        if isinstance(s, list):
            s = {i: series for i, series in enumerate(s)}

        if isinstance(s, np.ndarray):
            s = {0: s}

        if isinstance(s, pd.Series):
            s = {0: s.values}

        if isinstance(s, pd.DataFrame):
            s = {i: series.values for i, series in s.items()}

        if default_output_columns is None:
            default_output_columns = list(s.keys())

        for colname, series in s.items():
            if colname not in dfs:
                dfs[colname] = {}
            dfs[colname][key] = series if isinstance(
                series, pd.Series) else series

    newdic = {}
    for key, df in dfs.items():
        newdic[key] = pd.DataFrame(df, index=close.index)

    ret = [newdic[n] for n in default_output_columns]
    ret = [d.apply(lambda s:pd.to_numeric(s, errors='coerce')) for d in ret]

    if len(ret) == 1:
        return finlab.dataframe.FinlabDataFrame(ret[0])

    return tuple([finlab.dataframe.FinlabDataFrame(df) for df in ret])


indicator.us_stock = lambda *args, **kwargs: indicator(*args, **{**kwargs, **{'market': 'US_STOCK'}})
indicator.tw_stock = lambda *args, **kwargs: indicator(*args, **{**kwargs, **{'market': 'TW_STOCK'}})


def get_strategies(api_token=None):
    """取得已上傳量化平台的策略回傳資料。

    可取得自己策略儀表板上的數據，例如每個策略的報酬率曲線、報酬率統計、夏普率、近期部位、近期換股日...，
    這些數據可以用來進行多策略彙整的應用喔！


    Args:
        api_token (str): 若未帶入finlab模組的api_token，會自動跳出[GUI](https://ai.finlab.tw/api_token/)頁面，
                         複製網頁內的api_token貼至輸入欄位即可。
    Returns:
        (dict): strategies data
    Response detail:

        ``` py
        {
          strategy1:{
            'asset_type': '',
            'drawdown_details': {
               '2015-06-04': {
                 'End': '2015-11-03',
                 'Length': 152,
                 'drawdown': -0.19879090089478024
                 },
                 ...
              },
            'fee_ratio': 0.000475,
            'last_trading_date': '2022-06-10',
            'last_updated': 'Sun, 03 Jul 2022 12:02:27 GMT',
            'ndays_return': {
              '1': -0.01132480035770611,
              '10': -0.0014737286933147464,
              '20': -0.06658015749110646,
              '5': -0.002292995729485159,
              '60': -0.010108700314771735
              },
            'next_trading_date': '2022-06-10',
            'positions': {
              '1413 宏洲': {
                'entry_date': '2022-05-10',
                'entry_price': 10.05,
                'exit_date': '',
                'next_weight': 0.1,
                'return': -0.010945273631840613,
                'status': '買進',
                'weight': 0.1479332345384493
                },
              'last_updated': 'Sun, 03 Jul 2022 12:02:27 GMT',
              'next_trading_date': '2022-06-10',
              'trade_at': 'open',
              'update_date': '2022-06-10'
              },
            'return_table': {
              '2014': {
                'Apr': 0.0,
                'Aug': 0.06315180932606546,
                'Dec': 0.0537589857541485,
                'Feb': 0.0,
                'Jan': 0.0,
                'Jul': 0.02937490104459939,
                'Jun': 0.01367930162104769,
                'Mar': 0.0,
                'May': 0.0,
                'Nov': -0.0014734320286596825,
                'Oct': -0.045082529665408266,
                'Sep': 0.04630906972509852,
                'YTD': 0.16626214846456966
                },
                ...
              },
            'returns': {
              'time': [
                '2014-06-10',
                '2014-06-11',
                '2014-06-12',
                ...
                ],
              'value': [
                100,
                99.9,
                100.2,
                ...
                ]
              },
            'stats': {
              'avg_down_month': -0.03304015302646822,
              'avg_drawdown': -0.0238021414698247,
              'avg_drawdown_days': 19.77952755905512,
              'avg_up_month': 0.05293384465715908,
              'cagr': 0.33236021285588846,
              'calmar': 1.65261094975066,
              'daily_kurt': 4.008888367138843,
              'daily_mean': 0.3090784769257415,
              'daily_sharpe': 1.747909002374217,
              'daily_skew': -0.6966018726321078,
              'daily_sortino': 2.8300677082214034,
              ...
              },
            'tax_ratio': 0.003,
            'trade_at': 'open',
            'update_date': '2022-06-10'
            },
          strategy2:{...},
          ...}
        ```
    """
    if api_token is None:
        api_token = finlab.get_token()

    request_args = {
        'api_token': api_token,
    }

    url = 'https://asia-east2-fdata-299302.cloudfunctions.net/auth_get_strategies'
    response = finlab.utils.requests.get(url, request_args, timeout=300)
    status_code = response.status_code
    if status_code in [400, 401]:
        logger.error("The authentication code is wrong or the account is not existed."
                     "Please input right authentication code or register account ")
        return {}
    try:
        return json.loads(response.text)
    except:
        pass

    return response.text



def search(keyword=".*", display_info=['name', 'description', 'items']):
    """查詢與取得資料庫目錄資訊。

    查詢FinLab資料庫目錄中的資料表名稱或項目欄位名稱是否包含關鍵字，方便搜尋資料庫是否存在目標資料。

    Args:
        keyword (str): 欲查詢關鍵字，預設列舉全部。
        display_info (list):指定顯示的資訊項目，預設只顯示「資料表英文代稱、資料表的中文描述、資料表欄位名稱」，若設定為None，則顯示全部資訊。

    Returns:
        (list): database information

    Response detail:
        ``` py
        [{'name': 'financial_statement',
          'description': '財報',
          'items': {'存貨': {'type': 'float', 'description': '資產負債表(仟元)'},
                    '存貨_增加_減少': {'type': 'float', 'description': '單季現金流量表(仟元)'}}},
         {'name': 'fundamental_features',
          'description': '財務指標',
          'items': {'存貨週轉率': {'type': 'float', 'description': '(%)'}}},...]

        ```
    Examples:
        ``` py

        # 查詢各資料表的欄位名稱含有'存貨'關鍵字資料表的基本資訊
        ex1 = data.search(keyword='存貨')
        # 取得含有'存貨'關鍵字相關資料表的所有資訊
        ex2 = data.search(keyword='存貨', display_info=None)
        ```
    """
    if not hasattr(search, 'db_info'):
        res = finlab.utils.requests.get('https://asia-east2-fdata-299302.cloudfunctions.net/get_data_info', timeout=300)
        search.db_info = json.loads(res.text)['data']

    db_info = search.db_info

    if display_info:
        db_info = [{i: table[i] for i in display_info} for table in db_info]

    result = []
    if keyword:
        result = [table for table in db_info if (re.search(keyword, table['description'], re.IGNORECASE)) or (
            re.search(keyword, table['name'], re.IGNORECASE))]
        result_tables = [table['name'] for table in result]

    def check_column_contains_keyword(table, keyword):
        table = table.copy()
        keyword_exist = {
            k: v for k, v in table["items"].items() if re.search(keyword, k, re.IGNORECASE)
        }
        if len(keyword_exist) > 0:
            table["items"] = keyword_exist
            return table

    checked_table = None  # 初始化 checked_table 
    if keyword:
        for table in db_info:
            if table["name"] not in result_tables:
                checked_table = check_column_contains_keyword(table, keyword=keyword)
            if checked_table is not None:
                result.append(checked_table)
    return result
