import numpy as np
import pandas as pd


class Stat:
    # base class of stat objects
    def get_constant(self, name, n):
        factor = pd.read_csv('factor_table.csv')
        return factor[name][factor['n']==n].to_numpy()[0]

    def get_params(self):
        print(self.params)

    def set_params(self, params):
        assert len(params) == len(self.params), 'param length must be equal to the length of stat params'
        for i, key in enumerate(self.params.keys()):
            self.params[key] = params[i]


class x_bar(Stat):
    # x_bar stat
    def __init__(self, n=30):
        self.n = n
        self.ddof = 1 if self.n > 1 else 0
        self.params = {'mu': np.nan, 'sigma': np.nan}
        if self.n <= 25:
            self.factor = {'c4': super().get_constant('c4', self.n)}
        else:
            self.factor = {'c4': 4 * (self.n - 1) / (4 * self.n - 3)}

    def estimate_params(self, x):
        assert np.ndim(x) == 1, 'x must be 1-d array'
        self.params['mu'] = np.mean(x)
        if len(x) % self.n == 0:
            m_ = len(x) // self.n
        else:
            x = np.append(x, np.nan * np.ones(self.n - len(x) % self.n))
            m_ = len(x) // self.n
        s_bar_ = np.nan_to_num(np.nanstd(x.reshape(m_, self.n), axis=1, ddof=self.ddof)).mean()
        self.params['sigma'] =  s_bar_.mean() / (self.factor['c4'] * np.sqrt(self.n))

    def __call__(self, x):
        assert np.ndim(x) == 1, 'x must be 1-d array'
        if len(x) % self.n == 0:
            m_ = len(x) // self.n
        else:
            x = np.append(x, np.nan * np.ones(self.n - len(x) % self.n))
            m_ = len(x) // self.n
        return np.nanmean(x.reshape(m_, self.n), axis=1)
    
    def __repr__(self):
        return 'x bar (w={})'.format(self.n)

class S(Stat):
    # S stat
    def __init__(self, n=30):
        # n is subsample size
        self.n = n
        self.ddof = 1 if self.n > 1 else 0
        self.params = {'mu': np.nan, 'sigma': np.nan}
        if self.n <= 25:
            self.factor = {'c4': super().get_constant('c4', self.n)}
        else:
            self.factor = {'c4': 4 * (self.n - 1) / (4 * self.n - 3)}

    def estimate_params(self, x):
        s_bar_ = self(x).mean()
        sigma_hat_ = s_bar_ / self.factor['c4']
        self.params['mu'] = s_bar_
        self.params['sigma'] = sigma_hat_ * np.sqrt(1 - np.square(self.factor['c4']))

    def __call__(self, x):
        assert np.ndim(x) == 1, 'x must be 1-d array'
        if len(x) % self.n == 0:
            m_ = len(x) // self.n
        else:
            x = np.append(x, np.nan * np.ones(self.n - len(x) % self.n))
            m_ = len(x) // self.n
        return np.nan_to_num(np.nanstd(x.reshape(m_, self.n), axis=1, ddof=self.ddof))
    
    def __repr__(self):
        return 'S (w={})'.format(self.n)

class ma(Stat):
    # moving average stat
    def __init__(self, n=30):
        # n is the window size
        self.n = n
        self.params = {'mu': np.nan, 'sigma': np.nan}

    def estimate_params(self, x):
        assert np.ndim(x) == 1, 'x must be 1-d array'
        self.params['mu'] = np.mean(x)
        self.params['sigma'] = np.nanmean(pd.Series(x).rolling(self.n).std())

    def __call__(self, x):
        assert np.ndim(x) == 1, 'x must be 1-d array'
        mav = np.cumsum(x)
        mav[self.n:] = mav[self.n:] - mav[:-self.n]
        return mav[self.n - 1:] / self.n
    
    def __repr__(self):
        return 'MA (w={})'.format(self.n)

class R(Stat):
    # R stat
    def __init__(self, n=30):
        # n is subsample size
        self.n = n
        self.factor = {'d2': super().get_constant('d2', self.n), 'd3': super().get_constant('d3', self.n)}

    def estimate_params(self, x):
        R_ = self(x)
        self.params['mu'] = np.mean(R_)
        self.params['sigma'] = np.mean(R_) * self.factor['d3'] / self.factor['d2']

    def __call__(self, x):
        assert np.ndim(x) == 1, 'x must be 1-d array'
        if len(x) % self.n == 0:
            m_ = len(x) // self.n
        else:
            x = np.append(x, np.nan * np.ones(self.n - len(x) % self.n))
            m_ = len(x) // self.n
        return np.nanmax(x.reshape(m_, self.n), axis=1) - np.nanmin(x.reshape(m_, self.n), axis=1)