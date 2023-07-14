### this script calculates for each year month combination the intercept and slope using Seasonal Mann Kendall test.
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import pymannkendall as mk
import statsmodels.api as sm
import warnings

warnings.filterwarnings("ignore")

pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)

# Read the CSV file into a DataFrame
df = pd.read_csv('./data/cleaned_data_perPixel.csv')

# Filter the DataFrame to include only relevant months and median values
df = df[(df['month'] >= 3) & (df['median'] <= 7)]

# Select required columns
df = df[['date', 'year', 'month', 'day', 'weekNumber', 'daysInMonth', 'halfOfMonth', 'median', 'coordinates']].copy()

# Assign a unique ID to each pixel based on coordinates
df['pixel_id'] = df.groupby('coordinates').ngroup()

# Drop rows with missing median values
df = df.dropna(subset=['median']).reset_index(drop=True)

# Select required columns
df = df[['date', 'year', 'month', 'day', 'weekNumber', 'median', 'pixel_id']].copy()

# Filter out years beyond 2020 and the year 1984
df = df[df['year'] <= 2020]
df = df[df['year'] != 1984]

# Sort the DataFrame by year and assign clusters
df_cluster = df.sort_values('year')
df_cluster['cluster'] = (df_cluster['year'] - 1985) // 3 + 1
df_cluster['cluster'] = df_cluster.groupby('cluster')['year'].transform('max')

slope_values = []
intercept_values = []

for pixel_id, data_pixel_id in df_cluster.groupby('pixel_id'):
    print("Processing pixel_id: " + str(pixel_id))
    for (cluster, month), data_year_month in data_pixel_id.groupby(['cluster', 'month']):
        if data_year_month.shape[0] > 1:
            data_year_month = data_year_month[['date', 'median']].copy()
            data_year_month = data_year_month.set_index('date')

            # Apply Seasonal Mann-Kendall test for the specific months across each cluster
            if data_year_month.shape[0] >= 4:
                try:
                    trend, h, p, z, Tau, s, var_s, slope, intercept = mk.seasonal_test(data_year_month, period=4, alpha=0.5)
                    slope_values.append([pixel_id, cluster, month, slope, trend, z])
                    intercept_values.append([pixel_id, cluster, month, intercept, trend, p])
                except ZeroDivisionError:
                    print("Insufficient unique data points for pixel_id: " + str(pixel_id) + ", cluster: " + str(cluster))
            else:
                pass
        else:
            pass

# Create DataFrames for slope and intercept values
df_slopes = pd.DataFrame(slope_values, columns=['pixel_id', 'cluster', 'month', 'slope', 'trend_slope', 'z_score'])
df_intercepts = pd.DataFrame(intercept_values, columns=['pixel_id', 'cluster', 'month', 'intercept', 'trend_intercept', 'p_value'])

# Group the slope and intercept DataFrames by cluster and month and calculate the medians
df_slopes_grouped = df_slopes.groupby(['cluster', 'month'], as_index=False).median()
df_intercepts_grouped = df_intercepts.groupby(['cluster', 'month'], as_index=False).median()

# Merge the slope and intercept DataFrames
df_combined = pd.merge(df_slopes_grouped, df_intercepts_grouped, on=['cluster', 'month'])
df_combined.to_csv('results_data/mk_analyse_alldata_notMerged_clustered_2.csv')

# Print the combined DataFrame
print(df_combined)

# Select specific columns from the combined DataFrame and save to a new CSV file
df_combined = df_combined[['cluster', 'month', 'slope', 'intercept', 'z_score', 'p_value']].copy()
df_combined.to_csv('data/mk_analysis_clustered_YearMonth.csv')

# Print the final combined DataFrame
print(df_combined)
