# AirBnB Final Data Project

## Executive Summary

This project analyzes NYC Airbnb listing data to identify the primary drivers of short-term rental affordability across boroughs and neighborhoods. Using Python-based data cleaning and visualization, I examine how location, room type, and listing density influence nightly prices, with implications for travelers seeking cost-efficient accommodations.

## Key Findings
- Manhattan listings exhibit a significant price premium relative to outer boroughs
- Entire-home listings drive the majority of affordability variance
- Neighborhood density has a stronger effect on price than review scores

![NYC Airbnb Price Distribution](outputs/figures/new%20viz%201.png)


## The Project

As I visited New York City over fall break, I was forced to spend hours
shifting through websites and listing to try and find a reasonable hotel
room. After the experience, I was left wondering if I could have used my
data analytics skills to have found an AirBnB listing that met my
criteria faster than scrolling through the app or looking at websites.

As I knew I had a data project coming up, I decided that this would be a
perfect time to answer my own question and perhaps save myself time and
frustration for future trips

## The Data Used

I landed on a dataset I found on Kaggle. I opted to use this set due to
its relatively clean nature, the amount of columns and rows, and the
fact the data had all the variables I was most interested in. My only
complaint about the data was its 2019 date. Since the pandemic, prices
for tourist related activities have had significant shifts. However, I
still decided to move forward with the dataset, knowing the prices would
not likely reflect today’s reality.

## Getting Started

I began my data work by importing all libraries and packages I felt
would be necessary to have a smooth process

``` python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
```

### Loading the dataset

I then proceeded to load in my data from my desktop, where I like to
have my files live. After a successful import, I did a quick check of my
columns to ensure everything I needed to complete my task was present,
as shown on Kaggle.

``` python
Bnb_data = pd.read_csv('data/AB_NYC_2019.csv')
Bnb_data.columns
```

    Index(['id', 'name', 'host_id', 'host_name', 'neighbourhood_group',
           'neighbourhood', 'latitude', 'longitude', 'room_type', 'price',
           'minimum_nights', 'number_of_reviews', 'last_review',
           'reviews_per_month', 'calculated_host_listings_count',
           'availability_365'],
          dtype='object')

## Question 1: What is the difference in AirBnB nightly price by Borough?

The first question I wanted to address centered around the boroughs
themselves. Out of the 5, which borough offered the most affordable
median price on a per night basis?

Upon initial inspection of my dataset, there appeared to be significant
price outliers that would have affected my later results. For example,
after looking at the maximum and miniumm prices, I saw the prices ranged
from \$0 to \$10,000.

    np.float64(152.7206871868289)

If I was looking from the perspective of an “average traveler”, \$10,000
a night would not be in my price range.

### Fixing the range

To remedy the pricing outlier issue, I cleaned the data to a price range
of \$100 to \$1000. I deemd this to be a reasonable range for travelers,
with a bit of variation for very frugle and less price sensitive
travelers

``` python
Bnb_clean = Bnb_data.copy()
Bnb_clean = Bnb_clean[(Bnb_clean['price'] >= 100) & (Bnb_clean['price'] <= 1000)]
```

### Minimum Nights

I also wanted to see if there were any minium nights that exceeded what
would be reasonably considered standard for a visitor (i.e. capping
minium nights at 14 nights). I felt that any stay longer than this would
be deemd a long-term stay than a vacation or business visit.

I performed a similar filter as the price, just setting the threshold to
less than or equal to 14 for ‘minimum_nights’.

``` python
Bnb_clean = Bnb_clean[(Bnb_clean['minimum_nights']<=14)]
```

### Grouping and summarizing

Now that I filtered my data and set my desired parameters, I ran a
simply .groupby. I grouped ‘neighbourhood_group’ and ‘room_type’ by
price. I then ensured that the results only showed the median price of
each reach room type.

      neighbourhood_group        room_type  median_price
    0               Bronx  Entire home/apt         135.0
    1               Bronx     Private room         125.0
    2               Bronx      Shared room         150.0
    3            Brooklyn  Entire home/apt         155.0
    4            Brooklyn     Private room         120.0

### Data Pivot

While my groupby was useful, I wanted to have a more workable dataFrame,
especially for later visualization. To accomplish this, I did a wide
data pivot, ensuring each variable had its own column.

``` python
price_pivot = price_summary.pivot(
    index='neighbourhood_group',
    columns='room_type',
    values='median_price'
)
print(price_pivot)
```

    room_type            Entire home/apt  Private room  Shared room
    neighbourhood_group                                            
    Bronx                          135.0         125.0        150.0
    Brooklyn                       155.0         120.0        149.5
    Manhattan                      199.0         130.0        150.0
    Queens                         150.0         120.0        115.0
    Staten Island                  150.0         110.0        150.0

### First Visualization

After ensuring my pivot had executed correctly, I wanted to create a
simple visualization that showed each room type, grouped by each
borough, while also showing the median price of each listing type.

My final graph gave me a straightfoward bar graph that grouped each type
of listing in my data set (entire room, private room, shared room) by
borough, while also showing me the median nightly price for each listing
type. My graph revealed single rooms were the most expensive, which
intuitively made sense. I was surprised that a private room was less
expensive than shared rooms, on average. \#The findings from this graph
led me to ask the second question of my data set.

``` python
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
```

![](README_files/figure-commonmark/cell-9-output-1.png)

## Q2: If I am looking for places with short minimum stays and that have a significant amount of reviews, which neighborhoods are cheapest in each borough?

Now that I knew the median nightly price by room type in each borough, I
wanted to understand if there were specifc neighborhoods that would give
me the best value. However, I would not want a room that was cheap but
was in a very dangerous area or had never been reviewed by other
customers.

### Setting up the new data work

To begin the new process, I took my cleaned data set from question 1
that focused on stays no longer than 14 nights. I thehn added a second
filter to extract only properties that had 10 or more reviews. I felt 10
or more reviews was a strong theshold. In practice, if my choices were
very limited and I was willing to be a bit more risky with my location,
I could lower the review threshold.

``` python
short_reliable = Bnb_clean[
    (Bnb_clean['minimum_nights'] <= 14) &
    (Bnb_clean['number_of_reviews'] >= 10)]
```

### More Grouping and Summarizing

Once again, I perform a groupby and sumamrize, this time of the median
price per neighborhood within each borough.

``` python
neigh_stats = (
    short_reliable
    .groupby(['neighbourhood_group', 'neighbourhood'])['price']
    .median()
    .reset_index(name='median_price'))
```

### Iterating

I decided to use a for loop to iterate through my updated subset, as
well as my neighborhood groupby to find the top 3 cheapest and reviewed
neighborhoods in each borough. I decided to only generate 3 in each, as
I felt this would give me a good amount of choice wihtout paralyzing my
ability to make a decision with too many choices.


    === Bronx: 3 cheapest and reviewed neighborhoods ===
       neighbourhood_group neighbourhood  median_price
    32               Bronx     Unionport         100.0
    1                Bronx    Baychester         101.0
    12               Bronx    Highbridge         103.0

    === Brooklyn: 3 cheapest and reviewed neighborhoods ===
       neighbourhood_group  neighbourhood  median_price
    53            Brooklyn   Coney Island         110.0
    40            Brooklyn    Bensonhurst         113.0
    59            Brooklyn  East Flatbush         125.0

    === Manhattan: 3 cheapest and reviewed neighborhoods ===
        neighbourhood_group     neighbourhood  median_price
    104           Manhattan  Roosevelt Island         120.0
    98            Manhattan       Marble Hill         120.5
    94            Manhattan            Inwood         123.5

    === Queens: 3 cheapest and reviewed neighborhoods ===
        neighbourhood_group neighbourhood  median_price
    141              Queens   Kew Gardens         100.0
    154              Queens      Rosedale         100.0
    120              Queens     Briarwood         110.0

    === Staten Island: 3 cheapest and reviewed neighborhoods ===
        neighbourhood_group  neighbourhood  median_price
    168       Staten Island   Howland Hook         100.0
    172       Staten Island  Midland Beach         105.0
    167       Staten Island    Grymes Hill         110.0

### Merging

After looking at my top 3 neighboorhoods in the new dataframe I created
(top_cheapest_list), I knew I had to merge this new dataFrame with the
previously existing neigh_stats to have the ability to visualize an
answer to my overall problem. To stack these smaller dataFrames
together, I elected to utilize a concat merge to complete this

``` python
cheapest_neigh = pd.concat(top_cheapest_list, ignore_index=True)
cheapest_neigh
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead th {
        text-align: right;
    }
</style>

|     | neighbourhood_group | neighbourhood    | median_price |
|-----|---------------------|------------------|--------------|
| 0   | Bronx               | Unionport        | 100.0        |
| 1   | Bronx               | Baychester       | 101.0        |
| 2   | Bronx               | Highbridge       | 103.0        |
| 3   | Brooklyn            | Coney Island     | 110.0        |
| 4   | Brooklyn            | Bensonhurst      | 113.0        |
| 5   | Brooklyn            | East Flatbush    | 125.0        |
| 6   | Manhattan           | Roosevelt Island | 120.0        |
| 7   | Manhattan           | Marble Hill      | 120.5        |
| 8   | Manhattan           | Inwood           | 123.5        |
| 9   | Queens              | Kew Gardens      | 100.0        |
| 10  | Queens              | Rosedale         | 100.0        |
| 11  | Queens              | Briarwood        | 110.0        |
| 12  | Staten Island       | Howland Hook     | 100.0        |
| 13  | Staten Island       | Midland Beach    | 105.0        |
| 14  | Staten Island       | Grymes Hill      | 110.0        |

</div>

### Vizualisation 2

After ensuring my merge had executed correctly, I had all the data
necessary to create my second visualization. I ran another simple box
plot for clarity. To make it easier to distinguish neighborhoods within
each borough, I placed ‘neighborhood_group’ in the ‘hue’. The result is
as seen below.

``` python
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
```

![](README_files/figure-commonmark/cell-14-output-1.png)

My graph was very useful as it not only validated that my first graph of
the Bronx and Queens having the lower cost on average, but it also
showed me which neighborhoods within these boroughs offered the most
affordable listings. While the neighborhoods between these boroughs were
fairly similar, it appeared that Queens had the overall cheapest
neighborhods.

## Q3: As a traveler, how do prices differ when booking with “experienced hosts” (many listings) vs one-property hosts?

I have now answered two of my most pressing questions. However, as I am
dealing with AirBnB, I must also address the reality of the different
hosts who run the listings. My data set contained experienced hosts and
single hosts. Experienced hosts have multiple listings, where
single-hosts only have one listing registered to them.

As I am trying to maximize my savings, I wanted to find out if there was
a significant price difference between properties for experienced hosts
compared to single-listing.

### Grouping and Summarizing

To answer my question, I first performed another groupby. I used the
‘host_id’ to identify individiual hosts, with an aggregate function that
counted the number of unique listings that were linked to the host id.
This served to ensure hosts would be categorized properly and avoid
duplicates skewing my output.

``` python
host_summary = (
    Bnb_clean
    .groupby('host_id')
    .agg(host_listings=('id', 'nunique'))
    .reset_index()
)
```

### IF-ELIF

I then ran a simple if-elif to iterate through my new host_summary
dataFrame. If a host has 1 listing, they were classified as
‘single-host,if they have greater than 3 listing ’experienced-host’, and
if 2 listings ’ mid-level’

       host_id  host_listings    host_type
    0     2571              1  single-host
    1     2787              2    mid-level
    2     2845              1  single-host
    3     4632              1  single-host
    4     5089              1  single-host

### New Merge

\#Afer completing this process and viewing the head of my resutls, I was
able to see that I would need to combine my cleaned dataFrame and the
new one I had just created.

# 3. I then performed a left merge between my pre-existing, clean Bnb dataFrame and the new host summary data frame, using host_id as my primary key

``` python
Bnb_with_hosts = Bnb_clean.merge(
    host_summary[['host_id', 'host_type']],
    on='host_id',
    how='left'
)
```

### Using .isin

After ensuring a successful merge had occured, I used a simple .isin on
new BnB_with_hosts dataframe to quickly extract the classficiation that
I was interested in.

``` python
Bnb_host_focus = Bnb_with_hosts[
    Bnb_with_hosts['host_type'].isin(['single-host', 'experienced-host'])
]
```

### Another Merge

After I had successfuly extracted my desired classifications, I then
performed another groupby of neighbourhood, host_type, and price and
looked for the mean price broken down between experienced and
single-hosts.

``` python
host_price_stats = (
    Bnb_host_focus
    .groupby(['neighbourhood_group', 'host_type'])['price']
    .mean()
    .reset_index(name='avg_price')
)

print(host_price_stats)
```

      neighbourhood_group         host_type   avg_price
    0               Bronx  experienced-host  222.100000
    1               Bronx       single-host  159.680412
    2            Brooklyn  experienced-host  235.173077
    3            Brooklyn       single-host  180.367495
    4           Manhattan  experienced-host  260.369376
    5           Manhattan       single-host  216.899334
    6              Queens  experienced-host  201.954545
    7              Queens       single-host  164.063166
    8       Staten Island  experienced-host  333.333333
    9       Staten Island       single-host  178.447917

### Final Visualization

After I checked to ensure this had executed succesfully, it was time to
create my final visualization. In keeping with my theme of simple, clean
graphics, I created another simple bar plot that demonstrated the
pricing difference between experienced host listing and single-host
listings.

``` python
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
```

![](README_files/figure-commonmark/cell-20-output-1.png)

My final graph demonstrated a very clear distinction. Experienced hosts
were significantly more expensive, regardless of borough. This was
pertinent information, as this showed me that if I am looking to truly
maximize my budget as a traveler, I should be looking at single-listing
hosts. While experienced hosts may have more listings and time on
AirBnB, I could likely find a deal with a single-lister.

## Discussion and takeaways

Overall, this projected demonstrated how useful data analysis can be for
determining optimal pricing for travel. As a fairly frequent traveler, I
found this extremely insightful. Although many of these apps and website
listings have filters that accomplish similar aims as my project, if I
have very stringent parameters when it comes to price and geographic
location, I can narrow my options with much more specificty and in a
shorter amount of time than worrying about clicking 10 differnt filters
in often subpar user interfaces.

### Future Work

While I found this project very fun, I couldn’t help wonder what these
numbers would look like in today’s market. These prices were all
pre-pandemic. I would be interested in repeating the task with more
updated information and see if my findings hold up.

I would also be interested in looking at other major cities and travel
destinations. I chose New York as I recently visited. However, I would
be interested in looking at locations in other countries or compare the
prices in New York to somewhere like Hawaii.
