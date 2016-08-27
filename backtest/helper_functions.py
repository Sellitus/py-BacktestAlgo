import bt
import pandas as pd
import sys
from cStringIO import StringIO



################ CLASSES ################

class SelectWhere(bt.Algo):

    """
    Selects securities based on an indicator DataFrame.

    Selects securities where the value is True on the current date (target.now).

    Args:
        * signal (DataFrame): DataFrame containing the signal (boolean DataFrame)

    Sets:
        * selected

    """
    def __init__(self, signal):
        self.signal = signal

    def __call__(self, target):
        # get signal on target.now
        if target.now in self.signal.index:
            sig = self.signal.ix[target.now]

            # get indices where true as list
            selected = list(sig.index[sig])

            # save in temp - this will be used by the weighing algo
            target.temp['selected'] = selected

        # return True because we want to keep on moving down the stack
        return True



class WeighTarget(bt.Algo):
    """
    Sets target weights based on a target weight DataFrame.

    Args:
        * target_weights (DataFrame): DataFrame containing the target weights

    Sets:
        * weights

    """

    def __init__(self, target_weights):
        self.tw = target_weights

    def __call__(self, target):
        # get target weights on date target.now
        if target.now in self.tw.index:
            w = self.tw.ix[target.now]

            # save in temp - this will be used by the weighing algo
            # also dropping any na's just in case they pop up
            target.temp['weights'] = w.dropna()

        # return True because we want to keep on moving down the stack
        return True







################ STRATEGIES ################

# first let's create a helper function to create a ma cross backtest
def ma_cross(data, short_ma=50, long_ma=200, name='ma_cross'):
    # these are all the same steps as above
    short_sma = pd.rolling_mean(data, short_ma)
    long_sma  = pd.rolling_mean(data, long_ma)

    # target weights
    tw = long_sma.copy()
    tw[short_sma > long_sma] = 1.0
    tw[short_sma <= long_sma] = -1.0
    tw[long_sma.isnull()] = 0.0

    # here we specify the children (3rd) arguemnt to make sure the strategy
    # has the proper universe. This is necessary in strategies of strategies
    s = bt.Strategy(name, [WeighTarget(tw), bt.algos.Rebalance()])

    return bt.Backtest(s, data)


# Original trading strategy with decent results
def test_strat(data, sma_per=50, name='test_strat'):
    # calc sma
    sma = pd.rolling_mean(data, sma_per)

    s = bt.Strategy(name, [bt.algos.RunWeekly(),
                           bt.algos.SelectAll(),
                           SelectWhere(data > sma),
                           bt.algos.SelectMomentum(n=1, lookback=pd.DateOffset(months=1)),
                           bt.algos.WeighEqually(),
                           bt.algos.Rebalance()])

    return bt.Backtest(s, data)



def above_sma(data, sma_per=50, name='above_sma'):
    # calc sma
    sma = pd.rolling_mean(data, sma_per)

    # create strategy
    s = bt.Strategy(name, [bt.algos.RunWeekly(),
                           SelectWhere(data > sma),
                           bt.algos.WeighEqually(),
                           bt.algos.Rebalance()])

    # now we create the backtest
    return bt.Backtest(s, data)



# Original trading strategy with decent results
def original_backtest(data, name='original_backtest'):
    s = bt.Strategy(name, [bt.algos.RunWeekly(),
                           bt.algos.SelectAll(),
                           bt.algos.SelectMomentum(n=1, lookback=pd.DateOffset(days=1)),
                           bt.algos.WeighEqually(),
                           bt.algos.Rebalance()])

    return bt.Backtest(s, data)













################ Testers ################

# Finds optimal SMA length values and end result for the SMA cross strategy
# Also prints results within 4% of the top value for analysis purposes (like finding SMA value 'hotspots' between stocks)
def sma_cross_optimal_values(data, sma_low_bot, sma_low_top, sma_high_bot, sma_high_top, within_percentage=4):
    best_low = 1
    best_high = 1
    best_percentage = 1

    for i in range(sma_low_bot, sma_low_top):
        j_iter = iter(range(sma_high_bot, sma_high_top))
        for j in j_iter:
            if i < j:
                # ok now let's create a few backtests and gather the results.
                # these will later become our "synthetic securities"
                test = ma_cross(data, i, j)

                # let's run these strategies now
                results = bt.run(test)

                # now that we have run the strategies, let's extract
                # the data to create "synthetic securities"
                prices = results.prices

                # Redirect standard out to a string for the display function
                stdout = sys.stdout
                sys.stdout = mystdout = StringIO()

                # 'Print' the results, which actually copies the output string to mystdout
                results.display()

                percentage = 0.0

                for item in mystdout.getvalue().split("\n"):
                    if "Total Return" in item:
                        percentage = float(item.split()[2].replace("%", ""))


                # Revert to regular output
                sys.stdout = stdout

                if percentage > best_percentage:
                    best_low = i
                    best_high = j
                    best_percentage = percentage

                    print "!!!!!!!!!!!! -SMA Low: " + str(i) + "  -SMA High: " + str(j) + "  -Best Percentage: " + str(percentage) + " !!!!!!!!!!!!"
                elif ((percentage / best_percentage) > (1 - (within_percentage * .01))):
                    print "From Best: " + str(round(100 - ((percentage / best_percentage) * 100), 2)) + "%: " + "-L: " + str(i) + " -H: " + str(j) + " -P: " + str(
                        best_percentage)
                elif (j+5 < sma_high_top):
                    next(j_iter)
                    next(j_iter)
                    next(j_iter)
                    next(j_iter)
                    next(j_iter)

    return [best_low, best_high, best_percentage]


def above_sma_optimal_value(data, sma_high_bot, sma_high_top, within_percentage=4):
    best_sma = 1
    best_percentage = 1

    for i in range(sma_high_bot, sma_high_top):
        # ok now let's create a few backtests and gather the results.
        # these will later become our "synthetic securities"
        test = above_sma(data, i)

        # let's run these strategies now
        results = bt.run(test)

        # now that we have run the strategies, let's extract
        # the data to create "synthetic securities"
        prices = results.prices

        # Redirect standard out to a string for the display function
        stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

        # 'Print' the results, which actually copies the output string to mystdout
        results.display()

        percentage = 0.0

        for item in mystdout.getvalue().split("\n"):
            if "Total Return" in item:
                percentage = float(item.split()[2].replace("%", ""))


        # Revert to regular output
        sys.stdout = stdout

        if percentage > best_percentage:
            best_sma = i
            best_percentage = percentage

            print "!!!!!!!!!!!! -SMA Value: " + str(i) + "  -Best Percentage: " + str(percentage) + " !!!!!!!!!!!!"
        elif ((percentage / best_percentage) > (1 - (within_percentage * .01))):
            print "From Best: " + str(round(100 - ((percentage / best_percentage) * 100), 2)) + "%: " + "-L: " + str(i) + " -H: " + str(j) + " -P: " + str(
                best_percentage)

    return [best_sma, best_percentage]