#####################################################################################################################################################################################
# Name:     shaking_sats.py                                                                                                                                                         #
# Date:     May 20, 2021                                                                                                                                                            #
# Author:   Ross McKinnon                                                                                                                                                           #
# email:    srossmckinnon@gmail.com                                                                                                                                                 #
# github:   @kangarossco                                                                                                                                                            #
#                                                                                                                                                                                   #
# language: python 3.9.0/windows10                                                                                                                                                  #
#                                                                                                                                                                                   #
# script creates a fun graph of all your sats collected from #shaking sats as yoshi eggs!                                                                                           #                                                                                                                                                                                  #
# download all the htmlcode from https://shakepay.com/dashboard/wallets and save locally to parse                                                                                   #
#####################################################################################################################################################################################

#import modules, no requests library because the html is being parsed locally
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

#general system imports
import datetime
import os
import glob

#for chart and pictures
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

#assume the transactions_summary is in the downloads folder
#this function will return the most recent one
def current_csv():
    file_string = r"C:\Users\\" + os.getlogin() + "\downloads\*.csv"

    search_string = os.path.join(file_string)
    all_summaries = glob.glob(search_string)
    
    only_summaries = []
    max = 0

    for csv in all_summaries:
        x = os.path.basename(csv)
        if os.path.splitext(x)[0][:20] == 'transactions_summary':
            only_summaries.append(csv)
            try:
                if int(csv.split("(")[1][:1]) > max:
                    max = int(csv.split("(")[1][:1])
                    version = " (" + str(max) + ")"
            except:
                pass
                    
    if max > 0:
        version = " (" + str(max) + ")"
    else:
        version = ""

    return r"C:\Users\Ross\downloads\transactions_summary" + version + ".csv"

def plot_images(x, y, image, ax=None):
    ax = ax or plt.gca()
    for xi, yi in zip(x,y):
        im = OffsetImage(image, zoom=72/ax.figure.dpi)
        im.image.axes = ax
        ab = AnnotationBbox(im, (xi,yi), frameon=False, pad=0.0,)
        ax.add_artist(ab)

#import the dataframe from the transaction data and pair with webscrapped data
filepath = current_csv()
df = pd.read_csv(filepath, index_col=['Date'], parse_dates=['Date'])

#turn dataframe right side up
df = df.iloc[::-1]

#only keep rows without the bad data
df = df[df['Credit Currency'] == 'BTC']
df = df[df['Credit/Debit'] == 'credit']
df = df[df['Transaction Type'] == 'peer transfer']

#now only keep the columns with the satoishis transactions and btc/cad rate at the time
#satoshis reported in terms of bitcoin so mulitply by a billion to get there
df = df[['Amount Credited','Spot Rate']]
df["sats"] = df['Amount Credited'] * 100000000

#location of the egg picture
yoshi_egg = 'Yoshi_Egg.png'
image = plt.imread(yoshi_egg)

#chart and plot
fig, ax = plt.subplots()

dates = df.index[::1]
labels = dates.strftime('%D')

x1 = df.index
y1 = df['sats']
    
fontsize = 40
plt.title("@kangarossco's #ShakingSats rewards", fontsize=fontsize)    
#ax.set_xlabel('Date', fontsize=fontsize)   #obvious information
ax.set_ylabel('Satoshis', fontsize=fontsize)
plt.xticks(dates, labels, rotation=45, fontsize=fontsize*.4)

# zip joins x and y coordinates in pairs, keep the labels a little up and to the right of each point (leave room for egg picture)
for x,y in zip(x1,y1):
    label = "{:.0f}".format(y)
    plt.annotate(label,(x,y), textcoords="offset points", xytext=(-25,35), ha='center',fontsize=18)

ax.plot(x1,y1)

#add egg images to plot
plot_images(x1, y1, image, ax=ax)

#plt.show()

figure = plt.gcf()
figure.set_size_inches(30, 15)
figure.subplots_adjust(bottom=0.2)

plt.savefig("shaking_sats_eggs.png")
