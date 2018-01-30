from openreview import *
import json
import pandas as pd
import argparse


## Import statements and argument handling
parser = argparse.ArgumentParser()
parser.add_argument('-o','--output', help="The directory to save the output file")
parser.add_argument('--username')
parser.add_argument('--password')
args = parser.parse_args()

## Initialize the client library with username and password
openreview = Client(baseurl='https://openreview.net', username=args.username, password=args.password)

# Get all invit for ICLR 2018
list_invit = []
for i in openreview.get_invitations():
    if i.id[0:12] == "ICLR.cc/2018":
        list_invit.append(i.id)


idx = 0 # index of the final decision invitation
with open(args.output + '/data.json', 'w', encoding='utf-8') as outfile:
    # We dump the decision and the paper info into json
    feed = []
    notes = openreview.get_notes(invitation=list_invit[idx])
    for i in notes:
        fc = i.forumContent
        fc['decision'] = i.content['decision']
        feed.append(fc)
        
    json.dump(feed, outfile)

#Lets create a dataframe from the json file
df = pd.read_json(args.output + '/data.json')

# We create empty review column
df['review_1'] = None
df['conf_1'] = None
df['review_2'] = None
df['conf_2'] = None
df['review_3'] = None
df['conf_3'] = None


# We save the review note from the openreview ICLR 
# Might take some time
review_notes = []
for i,invit in enumerate(list_invit):
    invit_split = invit.split('/')
    if invit_split[2] == 'Conference':
        if invit_split[-1] == 'Official_Review':
            
            print(i,invit_split[3:])
            idx = i
            notes = openreview.get_notes(invitation=list_invit[idx])
            review_notes.append(notes)

for notes in review_notes:
    for i in notes:
        if i.number == 1:
            df.loc[df['paperhash'] == i.forumContent['paperhash'],'review_1'] = i.to_json()['content']['rating'][0]
            df.loc[df['paperhash'] == i.forumContent['paperhash'],'conf_1'] = i.to_json()['content']['confidence'][0]

        if i.number == 2:
            df.loc[df['paperhash'] == i.forumContent['paperhash'],'review_2'] = i.to_json()['content']['rating'][0]
            df.loc[df['paperhash'] == i.forumContent['paperhash'],'conf_2'] = i.to_json()['content']['confidence'][0]
        if i.number == 3:
            df.loc[df['paperhash'] == i.forumContent['paperhash'],'review_3'] = i.to_json()['content']['rating'][0]
            df.loc[df['paperhash'] == i.forumContent['paperhash'],'conf_3'] = i.to_json()['content']['confidence'][0]

df['review'] = (pd.to_numeric(df.review_1) + pd.to_numeric(df.review_2) + pd.to_numeric(df.review_3)) / 3
print(df)
df.to_json(args.output + '/save_iclr.json')
