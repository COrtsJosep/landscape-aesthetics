import pandas as pd

# get the votes data
file_path = "landscape-aesthetics/data/external/scenicornot/votes.tsv"
df = pd.read_csv(file_path, delimiter = '\t')

# n means that we don't want data whose number of votes is less than n
# set an value to n
n = 3

# function to filter
def filter_votes(votes, n):
    vote_list = votes.split(',')
    return len(vote_list) >= n

# filtering
df_filtered = df[df['Votes'].apply(filter_votes, n=n)]

# 