### Calculates the slope and intercept for each year individual using seasonal mann kendall test
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
df = pd.read_csv('./output_data2/cleaned_data_perPixel.csv')

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

# Initialize lists to store slope and intercept values
slope_values = []
intercept_values = []

# Iterate over each pixel and its data grouped by pixel ID
for pixel_id, data_pixel_id in df.groupby('pixel_id'):
    print("Processing pixel_id: " + str(pixel_id))
    for year, data_year in data_pixel_id.groupby(['year']):
        # Check if there are more than one rows for the current pixel_id and year
        if data_year.shape[0] > 1:
            data_year = data_year[['date','median']].copy()
            data_year = data_year.set_index('date')

            if data_year.shape[0] >= 5:
                try:
                    # Apply Seasonal Mann-Kendall test for the specific months across each year
                    trend, h, p, z, Tau, s, var_s, slope, intercept = mk.seasonal_test(data_year, period=5, alpha=0.5)

                    # Append the slope, trend, z-value, and p-value to the slope_values list
                    slope_values.append([pixel_id, year, slope, trend, z, p])

                    # Append the intercept and trend to the intercept_values list
                    intercept_values.append([pixel_id, year, intercept, trend])
                except ZeroDivisionError:
                    print("Insufficient unique data points for pixel_id: " + str(pixel_id) + ", year: " + str(year))
        else: 
            pass

# Create dataframes from the collected slope and intercept values
df_slopes = pd.DataFrame(slope_values, columns=['pixel_id', 'year', 'slope','trend_slope', 'z_value', 'p_value'])
df_intercepts = pd.DataFrame(intercept_values, columns=['pixel_id', 'year','intercept', 'trend_intercept'])

# Display the slope and intercept dataframes
print(df_slopes)
print(df_intercepts)

# Group the slope and intercept values by year, taking the median of each group
df_slopes_grouped = df_slopes.groupby(['year'], as_index=False).median()
df_intercepts_grouped = df_intercepts.groupby(['year'], as_index=False).median()

# Merge the grouped slope and intercept dataframes into a single dataframe
df_combined = pd.merge(df_slopes_grouped, df_intercepts_grouped, on=['year'])

# Display the combined dataframe
print(df_combined)

# Select relevant columns for further analysis
df_combined = df_combined[['year','slope', 'intercept', 'z_value', 'p_value']].copy()

# Save the selected columns to a CSV file
df_combined.to_csv('results_data/mk_analyse_year.csv')

# Display the updated combined dataframe
print(df_combined)
