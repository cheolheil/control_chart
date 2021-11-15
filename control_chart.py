import numpy as np
import h5py
from stats import x_bar
from chplot import ccplot


class shewhart_chart:
    def __init__(self, stat, L=3):
        assert callable(stat), 'Error: stat must be callable'
        self.stat = stat
        self.n = self.stat.n
        self.L = L

    def fit(self, X):
        self.center_line = 0
        w_ = 0
        # check X is h5py File or dict
        if isinstance(X, h5py.File) or isinstance(X, dict):
            # calculate the mean of X
            for key in list(X.keys()):
                X_ = X[key][:]
                self.stat.estimate_params(X_)
                self.center_line += self.stat.params['mu']
                w_ += self.stat.params['sigma']
            self.center_line /= len(list(X.keys()))
            w_ /= len(list(X.keys()))

        else:
            # check X is 1d array
            if len(X.shape) != 1:
                raise Exception('Error: X must be 1d array')
            else:
                pass
            self.stat.estimate_params(X)
            self.center_line = self.stat.params['mu']
            w_ = self.stat.params['sigma']
        
        # calculate the center line and upper and lower limit
        self.upper_limit = self.center_line + self.L * w_
        self.lower_limit = self.center_line - self.L * w_

    def run(self, X_new, verbose=1):
        # check X_new is 1d array
        if len(X_new.shape) != 1:
            raise Exception('Error: X_new must be 1d array')
        else:
            pass

        stat_test = self.stat(X_new)
        ooc_indices = np.where((stat_test > self.upper_limit) | (stat_test < self.lower_limit))[0]
        if not verbose:
            return stat_test, ooc_indices
        else:
            print(self.stat.__repr__() + ' Test data Result')
            print('Total Number of OOC: %i' % len(ooc_indices))
            print('OOC ratio: %.4f' % (len(ooc_indices)/len(X_new)))
            return stat_test, ooc_indices


if __name__ == '__main__':
    X = np.random.randn(500)
    X_new = np.random.normal(0, 1.2, 1000)
    my_stat = x_bar()
    my_chart = shewhart_chart(my_stat, L=3)
    my_chart.fit(X)
    my_chart.run(X_new)
    ccplot(my_chart, X_new)
    