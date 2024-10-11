import pandas as pd
import matplotlib.pyplot as plt

# Load the .tsv file
file_path = '/home/ubuntu/landscape-aesthetics/data/external/scenicornot/votes.tsv'  # Replace with your actual file path
df = pd.read_csv(file_path, sep='\t')

# Split the 'Votes' column and explode it into separate rows
df['Votes'] = df['Votes'].str.split(',')
df_votes = df.explode('Votes')

# Convert 'Votes' column to integer type
df_votes['Votes'] = df_votes['Votes'].astype(int)

# Display the distribution of votes
vote_counts = df_votes['Votes'].value_counts().sort_index()

# Plot the histogram of raw "Votes" feature
plt.figure(figsize=(8, 6))
vote_counts.plot(kind='bar', color='#1E90FF', width=0.8)  

plt.xlabel('Vote Value')
plt.ylabel('Frequency')
# plt.title('Distribution of Votes')
plt.xticks(rotation=0)

plt.grid(axis='y')

plt.show()
