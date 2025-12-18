
#libraries and packages
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#data import
Bnb_data = pd.read_csv('/Users/carlospadilla25/Desktop/AB_NYC_2019.csv')
Bnb_data.columns

#Q1: What is the difference in AirBnB nightly price by Borough?
#Process: Upon initial inspection of my dataset, there appeared to be significant price outliers that would have affected my later results
#Ex: Max price is $10,000 and min price is $0. If we are looking from the perspective of an "average traveler, we would want to clean the data to a more reasonable price.

Bnb_data['price']
Bnb_data['price'].min()
Bnb_data['price'].max()
Bnb_data['price'].mean()

#I cleaned the data to set a price range of $100 to $1000. I deemd this to be a reasonable range for travelers, with a bit of variation for very frugle and less price sensitive travelers
Bnb_clean = Bnb_data.copy()
Bnb_clean = Bnb_clean[(Bnb_clean['price'] >= 100) & (Bnb_clean['price'] <= 1000)]

#I also wanted to see if there were any minium nights that exceeded what would be reasonably considered standard for a visitor, i.e. capping minium nights at 14 days (2 weeks). Anything longer would be deemd more of a long-term stay than a vacation or business visit 

Bnb_clean = Bnb_clean[(Bnb_clean['minimum_nights']<=14)]

#Now that I  cleaned my data to achieve my desired parameters, I ran a simply .groupby and summary
price_summary = (
    Bnb_clean
    .groupby(['neighbourhood_group', 'room_type'])['price']
    .median()
    .reset_index(name='median_price')
)
print(price_summary.head())

#While my work above was useful, to get a better persepctive of the data and allow myself more flexibility for visualization later on, I pivoted the cleaned data.
price_pivot = price_summary.pivot(
    index='neighbourhood_group',
    columns='room_type',
    values='median_price'
)
print(price_pivot)

#Now that my table was pivoted correctly and had better control of indivdiual columns, I wanted to visualize my finding of median price by neighborhood (borough). For simplicity, I chose to do so in seaborn. 

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

#My final graph gave me a straightfoward bar graph that grouped each type of listing in my data set (entire room, private room, shared room) by borough, while also showing me the median nightly price for each listing type. 
#My graph revealed single rooms were the most expensive, which intuitively made sense. I was surprised that a private room was less expensive than shared rooms, on average. 
#The findings from this graph led me to ask the second question of my data set. 

#Q2 If I am looking for places with short minimum stays and that have a significant amount of reviews, which neighborhoods are cheapest in each borough?
#Now that I knew the median nightly price by room type in each borough, I wanted to understand if there were specifc neighborhoods that would give me the best value. 
#However, I would not want a room that was cheap but was in a very dangerous area or had never been reviewed by other customers

#First, I took  my cleaned data set from question 1 that focused on stays no longer than 14 nights. I thehn added a second filter to extract only properties that had 10 or more reviews. 
# I felt 10 plus reviews was a strong theshold. In practice, if my choices were very limited and I was willing to be a bit more risky with my location, I could lower the review threshold.

short_reliable = Bnb_clean[
    (Bnb_clean['minimum_nights'] <= 14) &
    (Bnb_clean['number_of_reviews'] >= 10)]

#Once again, I perform a groupby and sumamrize, this time of the median price per neighborhood within each borough 
neigh_stats = (
    short_reliable
    .groupby(['neighbourhood_group', 'neighbourhood'])['price']
    .median()
    .reset_index(name='median_price'))

#I then decided to use a for loop to iterate through my updated subset, as well as my neighborhood groupby to find the top 3 cheapest and reviewed neighborhoods in each borough.
#When those results were generated, I then wanted to ensure my lists were held within a single dataFrame. To accomplish this, I performed a simple concat merge.

top_cheapest_list = []

for borough in neigh_stats['neighbourhood_group'].unique():
    subset = neigh_stats[neigh_stats['neighbourhood_group'] == borough]
    top3 = subset.sort_values('median_price').head(3)
    top_cheapest_list.append(top3)
    print(f"\n=== {borough}: 3 cheapest and reviewed neighborhoods ===")
    print(top3)

cheapest_neigh = pd.concat(top_cheapest_list, ignore_index=True)
cheapest_neigh

#After seeing my merge had proven successful, I once again plotted my findings via seaborn. To distinguish each neighborhood by borough, I placed the neighborhood_group for the hue. 

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

#The visualization gave me an easy-to-read graph that showed me the top 3 neighborhoods that fit my criteria. 
#Now that I had two large questions answered, I was curious about the different hosts types and if they affected pricing. 


#Q3 As a traveler, how do prices differ when booking with “experienced hosts” (many listings) vs one-place hosts?

#To answer my question, I first performed another group by 'host_id', then applied an aggregate function to the host_listings to count how many unique listings a host had on AirBnB.

host_summary = (
    Bnb_clean
    .groupby('host_id')
    .agg(host_listings=('id', 'nunique'))
    .reset_index()
)

# I then ran a simple if-elif to iterate through hosts. If a host has 1 listing, they were classified as 'single-host,if they have greater than 3 listing 'experienced-host', and if 2 listings ' mid-level'

def classify_host(n):
    if n == 1:
        return 'single-host'
    elif n >= 3:
        return 'experienced-host'
    else:
        return 'mid-level'

host_summary['host_type'] = host_summary['host_listings'].apply(classify_host)

print(host_summary.head())

#Afer completing this process and viewing the head of my resutls, I was able to see that I would need to combine my cleaned dataFrame and the new one I had just created. 

# I then performed a left merge between my clean Bnb dataFrame and host summary data frame, using host_id as my primary key

Bnb_with_hosts = Bnb_clean.merge(
    host_summary[['host_id', 'host_type']],
    on='host_id',
    how='left'
)

# After a successful merge, I used a simple .isin on my host_focus to see the single and experienced hosts

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

#My final results showed me there was a significant difference between experienced hosts and single-hosts. If I am a very budget-concise traveler, a single-host property would be my best option. 

