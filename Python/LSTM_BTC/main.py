import os
import pandas as pd
import math
import statistics
import numpy as np

# data folder ubication
data_folder = os.getcwd() + '\BTCUSDT_1hs.csv'
print(data_folder)

# load data from binance
data = pd.read_csv(data_folder)
data = data.drop(['tradecount', 'unix'], axis=1)
data = data.reset_index()
data = data.sort_values('index', ascending=False)
data = data.drop(['index'], axis=1)
data.reset_index(drop=True, inplace=True)
data = data.reset_index()
filas = len(data)
list(data.columns.values)

data['predict'] = data['close'] > data['open']


# create WaveTrend Oscillator [LazyBear]
n1 = 10  # "Channel Length"
n2 = 21  # "Average Length"
obLevel1 = 60  # "Over Bought Level 1"
obLevel2 = 53  # "Over Bought Level 2"
osLevel1 = 60  # "Over Sold Level 1"
osLevel2 = 53  # "Over Sold Level 2"

data['ap'] = (data['high'] + data['low'] + data['close']) / 3
data['esa'] = data['ap'].ewm(span=n1).mean()
data['d'] = abs(data['ap'] - data['esa']).ewm(span=n1).mean()
data['ci'] = (data['ap'] - data['esa']) / (0.015 * data['d'])

data['wavetrend_1'] = data['ci'].ewm(span=n2).mean()
data['wavetrend_2'] = data['wavetrend_1'].rolling(window=4).mean()
data['wavetrend_delta'] = data['wavetrend_1'] - data['wavetrend_2']

# Create Squeeze Momentum Indicator [LazyBear]
length = 20  # "BB Length
length_div2 = int(length / 2)
mult = 2.0  # "BB MultFactor"
length2 = 20  # title="HMA Length"
source = open  # "Source"
lengthKC = 20  # "KC Length"
multKC = 1.5  # "KC MultFactor"
useTrueRange = True  # "Use TrueRange (KC)"

data['sqzwma1'] = 0
data['sqzwma2'] = 0
data['hullma'] = 0
data['dev_std'] = 0
data['TrueRange'] = 0
data['rangewma1'] = 0
data['rangewma2'] = 0
data['rangema'] = 0

f = -1
for x in range(filas):
    f = f + 1
    if f > 0:
        data['TrueRange'][f] = max((data['high'][f] - data['low'][f]), (abs(data['high'][f] - data['close'][f - 1])),
                                   (abs(data['low'][f] - data['close'][f - 1])))

wei = 0
for x in range(length + 1):
    wei = wei + x

wei_div2 = 0
for x in range(length_div2 + 1):
    wei_div2 = wei_div2 + x

f = -1
for x in range(filas):
    f = f + 1
    if f > length - 2:
        sum = 0
        sumtr = 0
        i = length
        ff = f
        for y in range(length):
            sum = sum + i * data['open'][ff]
            sumtr = sumtr + i * data['TrueRange'][ff]
            ff = ff - 1
            i = i - 1

        sum_div2 = 0
        sumtr2 = 0
        i_div2 = length_div2
        ff = f
        for y in range(length_div2):
            sum_div2 = sum_div2 + i_div2 * data['open'][ff]
            sumtr2 = sumtr2 + i_div2 * data['TrueRange'][ff]
            ff = ff - 1
            i_div2 = i_div2 - 1

        data['sqzwma1'][f] = sum / wei
        data['sqzwma2'][f] = sum_div2 / wei_div2
        data['rangewma1'][f] = sumtr / wei
        data['rangewma2'][f] = sumtr2 / wei_div2

lengthsqrt = round(math.sqrt(length))
f = -1

weisqrt = 0
for x in range(lengthsqrt + 1):
    weisqrt = weisqrt + x

for x in range(filas):
    f = f + 1
    if f > length + lengthsqrt - 2:
        sum = 0
        sumtr = 0
        i = lengthsqrt
        ff = f
        for y in range(lengthsqrt):
            sum = sum + i * (2 * data['sqzwma1'][ff] - data['sqzwma2'][ff])
            sumtr = sumtr + i * (2 * data['rangewma1'][ff] - data['rangewma2'][ff])
            ff = ff - 1
            i = i - 1

        data['hullma'][f] = sum / weisqrt
        data['rangema'][f] = sumtr / weisqrt

f = -1
for x in range(filas):
    f = f + 1
    if f > length - 2:
        sum = []
        ff = f
        for y in range(length):
            sum.append(data['open'][ff])
            ff = ff - 1
        data['dev_std'][f] = statistics.stdev(sum)

data['upper_bb'] = data['hullma'] + data['dev_std']
data['lower_bb'] = data['hullma'] - data['dev_std']

data['upperKC'] = data['hullma'] + data['rangema'] * multKC
data['lowerKC'] = data['hullma'] - data['rangema'] * multKC

# val = linreg(source - avg(avg(highest(high, lengthKC), lowest(low, lengthKC)), hma(close, lengthKC)), lengthKC, 0)


# Creando CONVERGENCIA/DIVERGENCIA DE LA MEDIA MÓVIL (MACD)
fast_length = 12  # "Fast Length"
slow_length = 26  # "Slow Length"
signal_length = 9  # "Signal Smoothing"
src = "close"

data['fast_sma'] = data['close'].rolling(window=fast_length).mean()
data['fast_ema'] = data['close'].ewm(fast_length).mean()
data['fast_sma/ema'] = data['fast_sma'] / data['fast_ema']
data['slow_sma'] = data['close'].rolling(window=slow_length).mean()
data['slow_ema'] = data['close'].ewm(slow_length).mean()
data['slow_sma/ema'] = data['slow_sma'] / data['slow_ema']

data['macdsma'] = data['fast_sma'] - data['slow_sma']
data['macdema'] = data['fast_ema'] - data['slow_ema']
data['macd'] = data['fast_sma/ema'] - data['slow_sma/ema']

data['signalsma'] = data['macdsma'].rolling(window=signal_length).mean()
data['signalema'] = data['macdema'].rolling(window=signal_length).mean()
data['signalmacd'] = data['macd'].rolling(window=signal_length).mean()
data['signalmacdsmaema'] = data['signalsma'] / data['signalema']

data['hist'] = data['macd'] - data['signalmacd']
data['histsma'] = data['macdsma'] - data['signalsma']
data['histema'] = data['macdema'] - data['signalema']
data['histsmaema'] = data['macd'] - data['signalmacdsmaema']

# limpiar primeros 40 registros del dataset
data = data.drop(range(0, 40), axis=0)

# print dataset
print(data)
print()
print(data.columns.values)

x = data.drop('close', axis=1)
x = x.drop('predict', axis=1)
x = x.drop('date', axis=1)
x = x.drop('symbol', axis=1)
y = data['predict']
print (x)
print (y)