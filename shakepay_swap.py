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
import glob
import os
import matplotlib.pyplot as plt

#Current_csv function. Goes through downloads folder and returns the transactions_summary csv with the highest version number
#should work for any user as long as the transaction_summary csv is in the downloads folder on a windows machine
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

#the filepath is where the html code is saved, file suffix doesn't matter as long as it can be read
filepath = r"Q:\Automation\Python Scripts\For GITHUB\Shakepay\shakepay_wallets_html.txt"

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

#get rid of all non-swap rows (if you get an ethereum transfer that'll have to be added)
df = df[df.shake_tag != '@shakingsats']
df = df[df.shake_tag != 'Interac e-Transfer']
df = df[df.shake_tag != 'shakepay']
df = df[df.shake_tag != 'Bitcoin Blockchain']

#import the dataframe from the transaction data and pair with webscrapped data
filepath = current_csv()
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
print("\n5 Most Frequent Swappers\n{}".format(df['shake_tag'].value_counts().head()))

#todays shakes
#df_today = df[str(datetime.date.today())]

#person lookup
#df.loc[df['shake_tag'] == '@blessed1963']

#number of unique swappers today
#len(df_today['shake_tag'].unique())

#make a bar graph for most frequent swappers with @kangarossco
counts = df['shake_tag'].value_counts()

fig, ax = plt.subplots()

plt.xticks(rotation=45, ha='right', fontsize=15)
plt.yticks(fontsize=15)

x1 = df['shake_tag'].value_counts()[:25].index
y1 = df['shake_tag'].value_counts()[:25]

ax.bar(x1,y1, color="indigo")
ax.set_yticks(y1)
ax.set_xlabel('Shake Tag', fontsize=25)
ax.set_ylabel('Swaps with @kangarossco', fontsize=25)
ax.set_title("Top 25 people that have swapped with @kangarossco", fontsize=40)

legend_string = "Swapped with {} unique people.\n{} total swaps".format(swappers,int(len(df)/2))
plt.annotate(legend_string, xy=(0.70, 0.90), xycoords='axes fraction', fontsize=25)

plt.show()
