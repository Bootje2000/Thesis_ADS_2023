### This script creates the data clustered per 3 years and calculates the slope and intercept per cluster. 
import pandas as pd
import matplotlib.pyplot as plt
import pymannkendall as mk
import warnings

warnings.filterwarnings("ignore")

# Set display options for pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)

# Read the data from a CSV file
df = pd.read_csv('./data/cleaned_data_perPixel.csv')
# df = df.head(1000)

# Filter the data based on conditions
df = df[(df['month'] >= 3) & (df['median'] <= 7)]

# Select relevant columns for analysis
df = df[['date','year','month','day','weekNumber', 'daysInMonth','halfOfMonth','median','coordinates']].copy()

# Assign a unique ID to each pixel based on coordinates
df['pixel_id'] = df.groupby('coordinates').ngroup()

# Drop rows with missing median values
df = df.dropna(subset=['median']).reset_index(drop=True)

# Select relevant columns for further analysis
df = df[['date','year','month','day','weekNumber', 'median','pixel_id']].copy()

# Filter out data beyond the year 2020 and remove data from the year 1984
df = df[df['year'] <= 2020]
df = df[df['year'] != 1984]

# Sort the data by year
df_cluster = df.sort_values('year')

# Assign clusters based on three-year periods starting from 1985
df_cluster['cluster'] = (df_cluster['year'] - 1985) // 3 + 1
df_cluster['cluster'] = df_cluster.groupby('cluster')['year'].transform('max')

# Only keep records for months February through July

# Initialize lists to store slope and intercept values
slope_values = []
intercept_values = []

# Iterate over each pixel and its data grouped by pixel ID
for pixel_id, data_pixel_id in df_cluster.groupby('pixel_id'):
    print("Processing pixel_id: " + str(pixel_id))
    for cluster, data_year in data_pixel_id.groupby(['cluster']):
        # Check if there are more than one rows for the current pixel_id and year
        if data_year.shape[0] > 1:
            data_year = data_year[['date','median']].copy()
            data_year = data_year.set_index('date')

            # Check if there are enough data points (adjust the value as needed)
            if data_year.shape[0] >= 6:
                try:
                    # Apply Seasonal Mann-Kendall test for the specific months across each year
                    trend, h, p, z, Tau, s, var_s, slope, intercept = mk.seasonal_test(data_year, period=6, alpha=0.5)

                    # Append the slope, trend, z-value, and p-value to the slope_values list
                    slope_values.append([pixel_id, cluster, slope, trend, z, p])

                    # Append the intercept and trend to the intercept_values list
                    intercept_values.append([pixel_id, cluster, intercept, trend])
                except ZeroDivisionError:
                    print("Insufficient unique data points for pixel_id: " + str(pixel_id) + ", cluster: " + str(cluster))
        else: 
            pass

# Create dataframes from the collected slope and intercept values
df_slopes = pd.DataFrame(slope_values, columns=['pixel_id', 'cluster', 'slope','trend_slope', 'z_value', 'p_value'])
df_intercepts = pd.DataFrame(intercept_values, columns=['pixel_id', 'cluster','intercept', 'trend_intercept'])

# Display the slope and intercept dataframes
print(df_slopes)
print(df_intercepts)

# Group the slope and intercept values by cluster, taking the median of each group
df_slopes_grouped = df_slopes.groupby(['cluster'], as_index=False).median()
df_intercepts_grouped = df_intercepts.groupby(['cluster'], as_index=False).median()

# Merge the grouped slope and intercept dataframes into a single dataframe
df_combined = pd.merge(df_slopes_grouped, df_intercepts_grouped, on=['cluster'])

# Display the combined dataframe
print(df_combined)

# Select relevant columns for further analysis
df_combined = df_combined[['cluster','slope', 'intercept', 'z_value', 'p_value']].copy()

# Save the selected columns to a CSV file
df_combined.to_csv('data/mk_seasonal_clustered_onlyYear.csv')

# Display the updated combined dataframe
print(df_combined)
