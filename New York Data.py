#libraries and packages
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#data imported
Bnb_data = pd.read_csv('/Users/carlospadilla25/Desktop/AB_NYC_2019.csv')
Bnb_data.columns

#Q1: What is the difference in AirBnB nightly price by Borough?
#Process: There appear to be significant price outliers that would affect my results
#Ex: Max price is $10,000 and min price is $0. If we are looking from the perspective of an "average traveler, we would want to clean
# the data to a more reasonable price."

Bnb_data['price']
Bnb_data['price'].min()
Bnb_data['price'].max()
Bnb_data['price'].mean()

#clean the data to set a price range of $100 to $1000
Bnb_clean = Bnb_data.copy()
Bnb_clean = Bnb_clean[(Bnb_clean['price'] >= 100) & (Bnb_clean['price'] <= 1000)]

#Also wanted to see if there were any minium nights that exceeded what would be reasonably considered standard for a visitor,
#i.e. capping minium nights at 28 days (4 weeks). Anything longer would be deemd more of a long-term stay than a vacation 

Bnb_clean = Bnb_clean[(Bnb_clean['minimum_nights']<=28)]

#Now that I have cleaned my data for the parameters I am looking for, I ran a simply .groupby and summary
price_summary = (
    Bnb_clean
    .groupby(['neighbourhood_group', 'room_type'])['price']
    .median()
    .reset_index(name='median_price')
)
print(price_summary.head())

#To get a different view of the data and allow myself more flexibility for visualizing, I pivote the data 
price_pivot = price_summary.pivot(
    index='neighbourhood_group',
    columns='room_type',
    values='median_price'
)
print(price_pivot)

#Now that my table was pivoted correctly, I wanted to visualize my finding of median price by neighborhood (borough)

plt.figure(figsize=(9, 6))
sns.barplot(
    data=price_summary,
    x='neighbourhood_group', 
    y='median_price',
    hue='room_type',
    errorbar=None,
    dodge=True
)
plt.title('Median Nightly Price by Borough and Room Type')
plt.xlabel('Borough')
plt.ylabel('Median Price (USD)')
plt.legend(title='Room Type', loc='upper left')
plt.tight_layout()
plt.show()

#Q2 If I am looking for places with short minimum stays and that have plenty of reviews, which neighborhoods are cheapest in each borough.”
#Approaching this more from the perpsecitve of a business travel or long-weekend getaway 

#First, I took a subsample of my cleaned data set from question 1 that focused on stays no longer than 5 nights and had at least 10 reviews 

short_reliable = Bnb_clean[
    (Bnb_clean['minimum_nights'] <= 4) &
    (Bnb_clean['number_of_reviews'] >= 10)]

#once again, I perform a groupby and sumamrize, this time of the median price per neighborhood within each borough 
neigh_stats = (
    short_reliable
    .groupby(['neighbourhood_group', 'neighbourhood'])['price']
    .median()
    .reset_index(name='median_price'))

#I then decided to use a for loop to iterate through my subset and neighborhood group to find the top 3 cheapest and reviewed neighborhoods
#I then did a concat merge between my top_cheapest_list

top_cheapest_list = []

for borough in neigh_stats['neighbourhood_group'].unique():
    subset = neigh_stats[neigh_stats['neighbourhood_group'] == borough]
    top3 = subset.sort_values('median_price').head(3)
    top_cheapest_list.append(top3)
    print(f"\n=== {borough}: 3 cheapest and reviewed neighborhoods ===")
    print(top3)

cheapest_neigh = pd.concat(top_cheapest_list, ignore_index=True)

#I then visualized my findings
plt.figure(figsize=(9, 6))
sns.barplot(
    data=cheapest_neigh,
    y='neighbourhood',
    x='median_price',
    hue='neighbourhood_group'
)
plt.title('Cheapest Reliable Neighborhoods (Short Stays, ≥10 Reviews)')
plt.xlabel('Median Nightly Price (USD)')
plt.ylabel('Neighborhood')
plt.legend(title='Borough', bbox_to_anchor=(1, 1), loc='upper left')
plt.tight_layout()
plt.show()


#Q3 As a traveler, how do prices differ when booking with “experienced hosts” (many listings) vs one-place hosts?
#This question is aimed to help decipher as a traveler, if it is better to go with an experienced host or someone with one location 

#First, I performed a group by 'host_id', then applied an aggregate function to the host_listings to count how many unique listings a host,
#identified by id, has on Air_Bnb
host_summary = (
    Bnb_clean
    .groupby('host_id')
    .agg(host_listings=('id', 'nunique'))
    .reset_index()
)

# 2. I then ran a simple if-elif to iterate through hosts. If a host has 1 listing, they were classified as 'single-host,
# if they have greater than 3 listing 'experienced-host', and if 2 listings ' mid-level'
def classify_host(n):
    if n == 1:
        return 'single-host'
    elif n >= 3:
        return 'experienced-host'
    else:
        return 'mid-level'

host_summary['host_type'] = host_summary['host_listings'].apply(classify_host)

print(host_summary.head())

# 3. I then performed a left merge between my clean Bnb dataFrame and host summary data frame, using host_id as my primary key
Bnb_with_hosts = Bnb_clean.merge(
    host_summary[['host_id', 'host_type']],
    on='host_id',
    how='left'
)

# After a successful merge, I used a simple .isin on my host_type to see the single and experienced hosts
Bnb_host_focus = Bnb_with_hosts[
    Bnb_with_hosts['host_type'].isin(['single-host', 'experienced-host'])
]

# 5. I then performed another groupby of neighbourhood, host_type, and price and looked for the mean of all of this groupby function.

host_price_stats = (
    Bnb_host_focus
    .groupby(['neighbourhood_group', 'host_type'])['price']
    .mean()
    .reset_index(name='avg_price')
)

print(host_price_stats)

#Upon receiving my results from my groupby function, I made a simple bar chart to visualize findings
plt.figure(figsize=(8, 5))
sns.barplot(
    data=host_price_stats,
    x='neighbourhood_group',
    y='avg_price',
    hue='host_type'
)
plt.title('Average Price by Host Experience Level and Borough')
plt.xlabel('Borough')
plt.ylabel('Average Nightly Price (USD)')
plt.legend(title='Host Type', bbox_to_anchor=(1, 1), loc='upper right')
plt.tight_layout()
plt.show()



