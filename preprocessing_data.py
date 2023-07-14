### This script executes the basic data processing stpes. It prepares it for the exploratory analysis
import pandas as pd
import plotly.express as px
import datetime 
import warnings
import matplotlib.pyplot as plt
import numpy as np

warnings.filterwarnings("ignore")

# Set display options for pandas
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)

# Read the data from a CSV file
# df = pd.read_csv('./NDVI_data/NDVI_withoutCloudCover_QaPixel.csv')
df = pd.read_csv('./NDVI_data/NDVI_Gargano.csv')

# Extract satellite information from the system:index column
df['sat'] = df['system:index'].str.split('_').str[1]  

# Extract date information from the system:index column
df['date'] = df['system:index'].str.split('_').str[3]  

# Extract latitude and longitude coordinates from the .geo column
df['coordinates'] = df['.geo'].str.split(':').str[2]  
df['coordinates'] = df['coordinates'].map(lambda x: x.strip('[]{}'))

# Extract latitude and longitude values from the coordinates
df['latitude (x)'] = df['coordinates'].str.split(',').str[0]  
df['longitude (y)'] = df['coordinates'].str.split(',').str[1] 

# Drop unnecessary columns
df = df.drop(['system:index'], axis=1)
df = df.drop(['.geo'], axis=1)

# Format the date column
df['date'] = df['date'].apply(lambda x: x[:6] + '-' + x[6:])
df['date'] = df['date'].apply(lambda x: x[:4] + '-' + x[4:])
df['date'] = pd.to_datetime(df['date'])

# Extract year, month, and day from the date column
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day

# Calculate week number, days in month, and half of month
df['weekNumber'] = df['date'].dt.week
df['daysInMonth'] = df['date'].dt.days_in_month
df['halfOfMonth'] = ['First' if day <= days_in_month / 2 else 'Second' for day, days_in_month in zip(df['day'], df['daysInMonth'])]

# Select relevant columns for further analysis
df = df[['date', 'year', 'month', 'day', 'weekNumber', 'daysInMonth', 'halfOfMonth', 'sat', 'median', 'coordinates', 'latitude (x)', 'longitude (y)']].copy()

# Drop rows with missing median values
df = df.dropna(subset=['median']).reset_index(drop=True)

# Save the cleaned data to a new CSV file
df.to_csv('./output_data2/cleaned_data_perPixel.csv')

# Aggregate the data by year, month, and half of month
df_aggr = df.groupby(['year', 'month', 'halfOfMonth'], as_index=False).median()

# Format the date column for aggregation
df_aggr['yyyymmdd'] = pd.to_datetime(df_aggr['year'].astype(str) + '-' + df_aggr['month'].astype(str), format='%Y-%m')

# Adjust the dates for the second half of the month
df_aggr.loc[df_aggr['halfOfMonth'] == 'Second', 'yyyymmdd'] = df_aggr['yyyymmdd'] + pd.offsets.MonthEnd()

# Adjust the dates for the first half of the month
df_aggr.loc[(df_aggr['halfOfMonth'] == 'First') & (df_aggr['yyyymmdd'].dt.month == 2), 'yyyymmdd'] = df_aggr['yyyymmdd'].dt.strftime('%Y-%m') + '-14'
df_aggr.loc[(df_aggr['halfOfMonth'] == 'First') & (df_aggr['yyyymmdd'].dt.month != 2), 'yyyymmdd'] = df_aggr['yyyymmdd'].dt.strftime('%Y-%m') + '-15'

# Select columns for further analysis
selected_columns = ['month', 'year', 'median', 'halfOfMonth']
selected_data = df_aggr[selected_columns]

# Select rows for the specific month and half of the month
selected_rows = selected_data[(selected_data['month'] == 5) & (selected_data['halfOfMonth'] == 'First')]

# Group the data by month and year, and store the median values as lists
grouped_data = selected_rows.groupby(['month', 'year'])['median'].apply(list)
df_aggr.to_csv('./data/clean_data_per_HalfMonth.csv')

# Print the aggregated data
print(df_aggr)

# Select relevant columns for visualization
df_aggr = df_aggr[['date', 'median']].copy()

# Plot a histogram of the data
plt.hist(df_aggr, bins=30, edgecolor='black')
plt.xlabel('Data')
plt.ylabel('Frequency')
plt.title('Histogram of Data')
plt.show()
