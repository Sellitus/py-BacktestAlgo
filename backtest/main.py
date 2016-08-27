# Ignore pandas futurewarnings
import warnings
warnings.simplefilter(action = "ignore", category = FutureWarning)

import bt
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import sys
from cStringIO import StringIO
import thread

from helper_functions import *



# sample_set = 'emc, fnfg, unm, ori, jec, ubnt, cpf, irbt, trmk, cvg, mbfi'
# portfolio_set = 'qcom, nvda, intc, amd, twtr, gpro, csco, p, aapl, io, hlx, dnr, clr, trxc, rgls, dsu, agnc, dx, enoc, cray, phys, cuz, acxm, rpai, cvlt, xel'
# full_set = sample_set + ', ' + portfolio_set

full_set = 'nvda'

filename = 'stock_results.txt'

start_date = '2014-01-01'

sma_low_bot = 10
sma_low_top = 100
sma_high_bot = 20
sma_high_top = 225



# Prints results as supplementary if within x percent of the top result
within_percentage = 4

# END USER SETTINGS


file = ""
data = ""

# Open file with data, if it doesn't exist pull new data and save it to a file
try:
    file = open(filename, 'r')
    data = pickle.load(file)
except IOError:
    # generate the file
    file = open(filename, 'w+')
    data = bt.get(full_set, start=start_date)
    pickle.dump(data, file)
    file.close()



### Finds optimal SMA cross settings and return percentage
# [best_low, best_high, best_percentage] = sma_cross_optimal_values(data, sma_low_bot, sma_low_top, sma_high_bot, sma_high_top, within_percentage)

### Get SMA based on the data
# sma_low_plot = pd.rolling_mean(data, best_low)
# sma_high_plot = pd.rolling_mean(data, best_high)
#
# plot = bt.merge(data, sma_low_plot, sma_high_plot).plot()
############################
### Finds optimal SMA value for price crossing the SMA line
# [best_sma, best_percentage] = above_sma_optimal_value(data, 5, sma_high_top, within_percentage)

### Get SMA based on the data
# sma_best_plot = pd.rolling_mean(data, best_sma)



# Do final test to print full results
test = above_sma(data, best_sma)
results = bt.run(test)


# Display graphical plot of the data
plot = bt.merge(data, sma_best_plot).plot()
results.plot()
results.display_monthly_returns()


results.display()
# Necessary to show matlibplot graphic produced with res.plot()
plt.show()



results.values()



