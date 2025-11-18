import os
import pickle
import shutil
import logging
import datetime
import pandas as pd

import finlab.utils

logger = logging.getLogger(__name__)


class CacheStorage:

    def __init__(self):
        """將歷史資料儲存於快取中

          Examples:
              欲切換成以檔案方式儲存，可以用以下之方式：

              ``` py
              from finlab import data
              data.set_storage(data.CacheStorage())
              close = data.get('price:收盤價')
              ```

              可以直接調閱快取資料：

              ``` py
              close = data._storage._cache['price:收盤價']
              ```
        """

        self._cache = {}
        self._cache_time = {}
        self._cache_expiry = {}
        self._stock_names = {}

    @staticmethod
    def now():
        return datetime.datetime.now(tz=datetime.timezone.utc)

    def set_dataframe(self, name, df, expiry=None):
        self._cache[name] = df
        self._cache_time[name] = self.now()
        self._cache_expiry[name] = expiry or self.now()

    def set_stock_names(self, stock_names):
        self._stock_names = {**self._stock_names, **stock_names}

    def get_time_created(self, name):

        if name not in self._cache or name not in self._cache_time:
            return None

        return self._cache_time[name]

    def get_time_expired(self, name):

        if name in self._cache_expiry:
            return self._cache_expiry[name]

        return None
    
    def set_time_expired(self, name, expiry):
        self._cache_expiry[name] = expiry

    def get_dataframe(self, name):

        # not exists
        if name not in self._cache or name not in self._cache_time:
            return None

        return self._cache[name]

    def get_stock_names(self):
        return self._stock_names


class FileStorage:
    def __init__(self, path=None, use_cache=True):
        """將歷史資料儲存於檔案中

          Args:
                path (str): 資料儲存的路徑
                use_cache (bool): 是否額外使用快取，將資料複製一份到記憶體中。

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
        if path is None:
            path = finlab.utils.get_tmp_dir()
            
        self._path = path
        self._cache = {}
        self._stock_names = None
        self._expiry = {}
        self.use_cache = use_cache
        self._created = {}

        if not os.path.isdir(path):
            os.mkdir(path)

        f_stock_names = os.path.join(path, 'stock_names.pkl')

        if not os.path.isfile(f_stock_names):
            with open(f_stock_names, 'wb') as f:
                pickle.dump({}, f)
        else:
            with open(f_stock_names, 'rb') as f:
                self._stock_names = pickle.load(f)

        f_expiry = os.path.join(self._path, 'expiry.pkl')

        if os.path.isfile(f_expiry):
            with open(f_expiry, 'rb') as f:
                try:
                    self._expiry = pickle.load(f)
                except:
                    self._expiry = {}
        
        if self._expiry:
            res = finlab.utils.requests.get('https://asia-east1-fdata-299302.cloudfunctions.net/data_reset_time', timeout=300)
            reset_data_time = datetime.datetime.fromtimestamp(float(res.text), tz=datetime.timezone.utc)
            for k, v in self._expiry.items():
                created = self.get_time_created(k)
                if created and created  < reset_data_time:
                    logger.info(f' set {k} time expired since the system reset time: {reset_data_time} > created time: {self.get_time_created(k)}')
                    self.set_time_expired(k, reset_data_time, save=False)

        self.save_expiry()


    def set_dataframe(self, name, df, expiry=None):

        file_path = os.path.join(
            self._path, name.replace(':', '#') + '.pickle')
        try:
            df.to_pickle(file_path)
        except:
            logger.warning(f' {name} save dataframe fail please check your disk permission or memory usage')
            return

        if self.use_cache:
            self._cache[name] = df

        self._expiry[name] = expiry or CacheStorage.now()
        self._created[name] = CacheStorage.now()
        self.save_expiry()

    def get_time_created(self, name):

        if name in self._created:
            return self._created[name]

        # check existence
        file_path = os.path.join(
            self._path, name.replace(':', '#') + '.pickle')

        if not os.path.isfile(file_path):
            return None

        return datetime.datetime.fromtimestamp(
            os.path.getmtime(file_path), tz=datetime.timezone.utc)

    def get_time_expired(self, name):

        if name in self._expiry:
            return self._expiry[name]

        return None
    
    def set_time_expired(self, name, expiry, save=True):
        self._expiry[name] = expiry
        if save:
            self.save_expiry()

    def save_expiry(self):
        try:
            with open(os.path.join(self._path, 'expiry.pkl'), 'wb') as f:
                pickle.dump(self._expiry, f)
        except Exception as e:
            logger.warning(f' save expiry fail {e}')
            pass

    def get_dataframe(self, name):

        if name in self._cache:
            return self._cache[name]

        file_path = os.path.join(
            self._path, name.replace(':', '#') + '.pickle')

        if os.path.isfile(file_path):
            try:
                ret = pd.read_pickle(file_path)
                if self.use_cache:
                    self._cache[name] = ret
            except:
                return None
            return ret

        return None

    def set_stock_names(self, stock_names):
        self._stock_names = {**self._stock_names, **stock_names}

        with open(os.path.join(self._path, 'stock_names.pkl'), 'wb') as f:
            pickle.dump(self._stock_names, f)

    def get_stock_names(self):

        if self._stock_names is not None:
            return self._stock_names

        with open(os.path.join(self._path, 'stock_names.pkl'), 'rb') as f:
            stock_names = pickle.load(f)
        self._stock_names = stock_names
        return stock_names
    
    def clear(self):
        folder_path = self._path
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')





