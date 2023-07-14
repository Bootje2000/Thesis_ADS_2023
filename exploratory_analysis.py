import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import warnings
import datetime as dt
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.seasonal import STL, seasonal_decompose
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

warnings.filterwarnings("ignore")

# Set display options for pandas
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)

# Read the data from a CSV file
df = pd.read_csv('./output_data2/cleaned_data_perPixel.csv')

# Group the data by various time-related columns and calculate the median
df = df.groupby(['date', 'year', 'month', 'day', 'weekNumber', 'daysInMonth', 'halfOfMonth'], as_index=False).median()

# Filter the data to include only years between 1985 and 2020 and median values between -1 and 1
df = df[(df['year'] >= 1985) & (df['year'] <= 2020)]
df = df[(df['median'] >= -1) & (df['median'] <= 1)]

# Prepare the training data by selecting the relevant columns
train_data = df[['median', 'year', 'month', 'day']].copy()
train_data2 = df[['year', 'month', 'day','median', 'date']].copy()

# Extract the target variable
y = train_data['median']

# Extract the features for polynomial regression
test_data_all = train_data[['year', 'month', 'day']]

# Create polynomial features
poly_features = PolynomialFeatures(degree=2)
X_poly = poly_features.fit_transform(test_data_all)

# Train a linear regression model on the polynomial features
model = LinearRegression()
model.fit(X_poly, y)

# Transform the test data with polynomial features and make predictions
test_data_poly = poly_features.transform(test_data_all)
predictions = model.predict(test_data_poly)
test_data_all['predictions'] = predictions

# Combine the predicted values and additional data columns into a single dataframe
test_data_all = pd.concat([test_data_all, train_data2], axis=1)
test_data_all = test_data_all.loc[:,~test_data_all.columns.duplicated()].copy()

# Extract the predicted and actual values for evaluation
predicted_values = test_data_all['predictions']
actual_values = test_data_all['median']

# Calculate the mean squared error (MSE) between the predicted and actual values
mse = mean_squared_error(actual_values, predicted_values)
print(mse)

# Plot the original data
plt.plot(df['date'], df['median'], color='#EEA47F', label='Data')
plt.title("NDVI value per date")
plt.xlabel('Date')
plt.ylabel('Median of the NDVI per date')
plt.legend()

# Save the plot to a file
plt.savefig('./plots/exploratory_analysis.png')

# Display the plot
plt.show()
