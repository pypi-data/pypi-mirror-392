"""
import all dependencies
"""

import os
import re
import ephem
import locale
import requests
import warnings
import calendar
from bs4 import BeautifulSoup
from tqdm.notebook import trange

#import notebook
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from platform import python_version
import catboost
import graphviz
from datetime import time
from datetime import datetime
from datetime import timedelta
import sklearn
from sklearn.metrics import mean_absolute_error as MAE
from sklearn.metrics import mean_absolute_percentage_error as MAPE
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import TimeSeriesSplit
from sklearn.model_selection import LearningCurveDisplay

def print_dependency():
    print(f"python: v {python_version()}")
    #print(f"Jupyter Notebook: v {notebook.__version__}")
    print(f"numpy: v {np.__version__}")
    print(f"pandas: v {pd.__version__}")
    print(f"seaborn: v {sns.__version__}")
    print(f"graphviz: v {graphviz.__version__}")
    print(f"matplotlib: v {matplotlib.__version__}")
    print(f"sklearn: v {sklearn.__version__}")
    print(f"CatBoost: v {catboost.__version__}")