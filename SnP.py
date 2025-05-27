import pandas as pd
import FinanceDataReader as fdr

spy = fdr.DataReader('SPY')
spy.head()