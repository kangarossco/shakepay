#########################################################################################################################################
# Name:     shakepay_swap.py                                                                                                            #
# Date:     May 20, 2021                                                                                                                #
# Author:   Ross McKinnon                                                                                                               #
# email:    srossmckinnon@gmail.com                                                                                                     #
# github:   @kangarossco                                                                                                                #
#                                                                                                                                       #
# language: python 3.9.0/windows10                                                                                                      #
#                                                                                                                                       #
# Parses through locally saved shakepay wallets html code along with transaction data from their downloadable csv                       #
# to crate a dataframe with usable information. Also spits out a bar graph with top 25 most frequent traders and some interesting       #
# other statistics                                                                                                                      #
#########################################################################################################################################

#import modules, no requests library because the html is being parsed locally
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import datetime
from datetime import timedelta

import glob
import os
import matplotlib.pyplot as plt

#latest_csv function. Goes through downloads folder and returns the transactions_summary csv with the highest version number
#should work for any user as long as the transaction_summary csv is in the downloads folder on a windows machine
def latest_csv():
    
    file_string = r"C:\Users\\" + os.getlogin() + "\downloads\*.csv"
    
    search_path = os.path.join(file_string)
    all_summaries = glob.glob(search_path)
    
    only_summaries = []
    max = 0

    for csv in all_summaries:
        x = os.path.basename(csv)
        if os.path.splitext(x)[0][:20] == 'transactions_summary':
            only_summaries.append(csv)
            try:
                if int(csv.split("(")[1][:].split(")")[0]) > max:
                    max = int(csv.split("(")[1][:].split(")")[0])
                    version = " (" + str(max) + ")"
            except:
                pass
                    
    if max > 0:
        version = " (" + str(max) + ")"
    else:
        version = ""

    return r"C:\Users\Ross\downloads\transactions_summary" + version + ".csv"

def censor_namelist(series):
    pass


def top_swappers(top_people):
    fig, ax = plt.subplots()

    x1 = df2['shake_tag'].value_counts()[:top_people].index
    y1 = df2['shake_tag'].value_counts()[:top_people]
    
    y2 = result['difference'][:top_people]
    x1.values[0] = "@" + len(x1[0]) * "*"
       
    ax.bar(x1,y1, color="indigo", label="good swaps")
    ax.bar(x1,y2, bottom=y1, color="gray", label="swaps resulting in no points")

    plt.xticks(rotation=45, ha='right', fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylim(0,y1[0]+5)

    ax.set_yticks(y1)
    ax.set_xlabel('Shake Tag', fontsize=25)
    ax.set_ylabel('Swaps with @kangarossco', fontsize=25)
    ax.set_title("Top {} people that have swapped with @kangarossco".format(top_people), fontsize=40)

    legend_string = "@kangarossco\nSwapped with {} unique people.\n{} new swappers last 24 hours.\n{} total swaps.".format(swappers,len(new_recent_swappers),int(len(df)/2))
    plt.annotate(legend_string, xy=(0.25, 0.83), xycoords='axes fraction', fontsize=25)

    ax.legend(loc="upper right", prop={'size': 25})

    figure = plt.gcf()

    figure.set_size_inches(30, 15)
    figure.subplots_adjust(bottom=0.2)
    plt.savefig("top_swappers.png", dpi=100)

def top_wasters(top_people):
    fig, ax = plt.subplots()

    result.drop(result[result['difference']==0].index, inplace=True)
    top_people = len(result)

    x1 = result.sort_values('difference', ascending=False)[:top_people].index
    y1 = result.sort_values('difference', ascending=False)['difference'][:top_people]

    ax.bar(x1,y1, color="grey", label="wasted swaps")

    plt.xticks(rotation=45, ha='right', fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylim(0,y1[0]+5)

    ax.set_yticks(y1)
    ax.set_xlabel('Shake Tag', fontsize=25)
    ax.set_ylabel('Swaps with @kangarossco', fontsize=25)
    ax.set_title("{} people that send duplicates with @kangarossco".format(top_people), fontsize=40)

    ax.legend(loc="upper right", prop={'size': 25})

    figure = plt.gcf()
    figure.set_size_inches(30, 15)
    figure.subplots_adjust(bottom=0.2)
    
    plt.savefig("top_wasters.png", dpi=100)


#the filepath is where the html code is saved, file suffix doesn't matter as long as it can be read
filepath = r"Q:\Automation\Python Scripts\Github\Shakepay\shakepay_wallets_html.txt"

f = open(filepath, encoding="utf8")
soup = BeautifulSoup(f, 'html.parser')
f.close()

#the data we are after is the usernames and amount transfered, we will be discarding most of the other data along the way
#loop through unique class identifiers to find all the transactions
#every transaction has a date (we don't need), shaketag, amount, and an arrow colour used to determine if the transaction is
#either incomeing or outgoing
transactions = soup.find_all("div", class_="transaction-item")

#placeholder lists
all_transactions = []
tag_list = []
amount_list = []
message_list = []

#loop through entire transaction items list
for trans_num in range(len(transactions)):
    shake_tag = transactions[trans_num].find("p", class_="title is-5 has-text-neutral-ultra-dark").get_text()
    if shake_tag[:6] != "Bought":
        amount = float(transactions[trans_num].find("p", class_="title is-5 has-text-neutral-ultra-dark has-text-right").get_text()[:4])

        #create temporary list of all the classes to check if transaction is incoming or outgoing
        class_list = set()
        tags = {tag.name for tag in transactions[trans_num].find_all()}
        for tag in tags:
            for i in transactions[trans_num].find_all(tag):
                if i.has_attr( "class" ):
                    if len( i['class'] ) != 0:
                        class_list.add(" ".join( i['class']))

        #check list class, 1 if recieved, -1 if sent
        if 'fal fa-2x fa-arrow-to-bottom has-text-success' in class_list:
            multiplier = 1
        elif 'fal fa-2x fa-arrow-from-bottom has-text-warning-light' in class_list:
            multiplier = -1

        #code throws error if there is no message, 
        try:
            message = transactions[trans_num].find("p", class_="subtitle is-size-6 has-text-neutral-very-dark").get_text()
        except:
            message = "None"      

        #final list of names and amounts transacted
        tag_list.append(shake_tag)
        amount_list.append(amount * multiplier)
        message_list.append(message)

#create dataframe from dictionary of lists
df_dict = {"shake_tag" : tag_list, "amount" : amount_list, "message" : message_list}
df = pd.DataFrame(df_dict)

#df.index = df.index - timedelta(hours=4)

#get rid of all non-swap rows (if you get an ethereum transfer that'll have to be added)
df = df[df.shake_tag != '@shakingsats']
df = df[df.shake_tag != 'Interac e-Transfer']
df = df[df.shake_tag != 'shakepay']
df = df[df.shake_tag != 'Bitcoin Blockchain']

#import the dataframe from the transaction data and pair with webscrapped data
#if you aren't you usind windows or don't keep the filepath in the downloads folder change here
filepath = latest_csv()
df2 = pd.read_csv(filepath, parse_dates=['Date'])

#remove all rows that aren't in swaps
df2 = df2[df2['Transaction Type'] != 'fiat funding']
df2 = df2[df2['Transaction Type'] != 'purchase/sale']
df2 = df2[df2['Transaction Type'] != 'referral reward']
df2 = df2[df2['Transaction Type'] != 'crypto funding']

#remove all remaining rows with currencies other than CAD
df2 = df2[df2['Credit Currency'] != 'BTC']
df2 = df2[df2['Credit Currency'] != 'ETH']

#reverse the second dataframe so the dataframes can be combined
df2 = df2.iloc[::-1]

#bring over the time data and set index
df["Time"] = list(df2["Date"])
df = df.set_index('Time')
df.index = df.index - timedelta(hours=4)

#group all shake_tags and add them together, if all debts have been repaid it should sum to zero
group = df.groupby('shake_tag')
agg = group.aggregate({'amount': np.sum})

#how many unique shake_tags have you interacted with?
swappers = len(df['shake_tag'].unique())
print("You've traded with {} different people! {} to go till diamond paddle!".format(swappers,500 - swappers))

#and... check it:
print("\nYou owe these people:")
debts = agg[agg.amount > 0]
if debts.empty:
    print("no debts")
else:
    print(debts)

print("\nThese people owe you:")
creditors = agg[agg.amount < 0]
if creditors.empty:
    print("no credits")
else:
    print(creditors)

#total trades
print("\nTotal trades made: {}".format(int(len(df)/2)))

#who did I trade most with?
#print("\n5 Most Frequent Swappers\n{}".format(df['shake_tag'].value_counts().head()))

#todays shakes
df_today = df[str(datetime.date.today())]
todays_swappers_abc = sorted(df_today.shake_tag.unique().tolist())


print("{} different swappers today:\n{}".format(len(todays_swappers_abc), todays_swappers_abc))
#person lookup
df.loc[df['shake_tag'] == '@melystorm'].drop('message', axis=1)

#number of unique swappers today
len(df_today['shake_tag'].unique())

#from datetime import datetime, timedelta
#last 24 hours
d = str(datetime.datetime.now() - timedelta(hours=24))

new_swappers = df.loc[:d]['shake_tag'].unique() #only unique swappers from last 24 hours
old_swappers = df.loc[d:]['shake_tag'].unique() #all unique swappers up to 24 hours ago
new_recent_swappers = [x for x in new_swappers if x not in old_swappers] #unique new swappers



#make a bar graph for most frequent swappers with @kangarossco
#counts = df['shake_tag'].value_counts()

################################################################
#new graph
df2 = df.reset_index(level=0)
df2['day'] = df2['Time'].dt.date
df2.drop_duplicates(subset=['shake_tag', 'amount','day'], keep='last', inplace=True)
df2 = df2.set_index('Time')
df2.drop(['message','day'], axis=1, inplace=True)

counts = df['shake_tag'].value_counts()
counts2 = df2['shake_tag'].value_counts()
result = pd.concat([counts, counts2], axis=1)
result.columns = ['inital', 'actual']
result['difference'] = result['inital'] - result['actual']

top_swappers(30)
top_wasters(100)



