import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import time
import pickle
import sqlite3
import matplotlib.pyplot as plt
import re


def scrap_grabber():
    try:
        with open('scrap.dat', 'rb') as file:
            scrap = pickle.load(file)
    except FileNotFoundError:
        resource = 'https://ycharts.com/companies/TSLA/revenues'
        result = requests.get(resource, time.sleep(10), headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        if result:
            with open('scrap.dat', 'wb') as file:
                pickle.dump(bs(result.text, 'html'), file)
            scrap = bs(result.text, 'html')
    finally:
        return scrap

def scrap_scrimper():
    scrap = scrap_grabber()
    data = []
    tables = scrap.find_all(class_='col-6')
    for i in tables:
        for row in i.find_all('tr'):
            row_data = []
            for cell in row.find_all('td'):
                row_data.append(cell.text)
            data.append(row_data)
    df = pd.DataFrame(data)
    df = df.dropna()
    df[1] = df[1].apply(reg_cleaner)
    return df

def reg_cleaner(x):
    base = re.search(r'[BM]', x)[0]
    num = re.search(r'\d+.\d+', x)[0]
    if base == 'M':
        return int(float(num)*1000000)
    elif base == 'B':
        return int(float(num)*1000000000)


def squeal_that_scrap():
    conn = sqlite3.connect('scrap.db')
    df = scrap_scrimper()
    df.to_sql('tsla', conn, if_exists='replace')
    conn.commit()

squeal_that_scrap()
# We could make a bar graph that displays the size of gains vs losses, a line plot that shows the history of the stock,
# or correct for standard deviation, and set everything according to it's distance from the mean

def plot_that_scrap():
    df = scrap_scrimper()
    ls = list(df[1])[::-1]
    ls2 = []
    for i in range(len(ls)):
        if i != len(ls) - 1:
            ls2.append(ls[i] - ls[i+1])
        else:
            ls2.append(0)
    x = range(1, len(ls) + 1)
    fig, axs = plt.subplots(3, 1, figsize=(5,7))
    axs[0].bar(x, ls2)
    ls = list(df[1])
    ls = [(i - df[1].mean())/df[1].std() for i in ls][::-1]
    axs[1].bar(x, ls)
    axs[2].plot(x, list(df[1])[::-1])
    plt.show()


plot_that_scrap()
