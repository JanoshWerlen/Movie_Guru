import pandas as pd
import argparse
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor, plot_tree
import matplotlib.pyplot as plt
import pickle

# python modelm.py -u "mongodb+srv://werleja1:Md1794682350.@mdmwerleja1.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"


def get_df():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Create model_lr')
    parser.add_argument('-u', '--uri', required=True,
                        help="mongodb uri with username/password")
    args = parser.parse_args()

    # MongoDB setup
    mongo_uri = args.uri
    mongo_db = "movies"
    mongo_collection = "movies"

    client = MongoClient(mongo_uri)
    db = client[mongo_db]
    collection = db[mongo_collection]

    documents = list(collection.find({}))

    df = pd.DataFrame(documents)
    df_all_docs = pd.DataFrame(documents)

    return df, df_all_docs


# Get dataframes
df, df_all_docs = get_df()

# Transformations
df['is_summer'] = df['release_month'].apply(
    lambda x: 1 if x in ["Apr", "May", "Jun", "Jul", "Aug", "Sep"] else 0)
df['is_R_rated'] = df['rating'].apply(lambda x: 1 if x == "R" else 0)
df['is_english'] = df['Original Language'].apply(
    lambda x: 1 if x == "English" else 0)
df['Director_is_PeterJackson'] = df['Director'].apply(
    lambda x: 1 if x == "PeterJackson" else 0)

# Converting to numeric
cols_to_numeric = ['Boxoffice in Million',
                   'Runtime in Minutes', 'audience_score', 'tomato_score']
df[cols_to_numeric] = df[cols_to_numeric].apply(pd.to_numeric, errors='coerce')

df = df.drop(columns=['audience_score', 'is_summer',
             'Director_is_PeterJackson'])

# Drop non-numeric columns
df = df.select_dtypes(include=['number'])

# Drop null values
df.dropna(inplace=True)

# Drop duplicates
df.drop_duplicates(inplace=True)
df_all_docs.drop_duplicates(inplace=True)

print(df.head())

print(f"DF before quantiles: {len(df)}")

# Handling Outliers for 'Boxoffice in Million'
Q1 = df['Boxoffice in Million'].quantile(0.25)
Q3 = df['Boxoffice in Million'].quantile(0.75)
IQR = Q3 - Q1

# Define limits for outlier
lower_limit = Q1 - 1.5 * IQR
upper_limit = Q3 + 1.5 * IQR

# Filter out outliers
filtered_df = df[(df['Boxoffice in Million'] >= lower_limit)
                 & (df['Boxoffice in Million'] <= upper_limit)]

print(f"DF after quantiles: {len(filtered_df)}")

# Select features and target
features = df.columns.drop('Boxoffice in Million')
X = filtered_df[features]
y = filtered_df['Boxoffice in Million']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

if not list(X_train.columns) == list(X_test.columns):
    print("Warning: Mismatch in feature names or order between training and test sets")


# Initialize and train models
model_lr = LinearRegression()
model_lr.fit(X_train, y_train)

model_dr = DecisionTreeRegressor()
model_dr.fit(X_train, y_train)

# Plot Decision Tree
plt.figure(figsize=(20, 10))
plot_tree(model_dr, feature_names=features, filled=True)
# plt.show()

# Predictions and Plotting for Linear Regression
y_pred_lr = model_lr.predict(X_test)
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred_lr, color='blue')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
plt.xlabel('Actual')
plt.ylabel('Predicted')
plt.title('Linear Regression: Actual vs Predicted Box Office')
# plt.show()

# Predictions and Plotting for Decision Tree Regressor
y_pred_dr = model_dr.predict(X_test)
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred_dr, color='red')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
plt.xlabel('Actual')
plt.ylabel('Predicted')
plt.title('Decision Tree: Actual vs Predicted Box Office')
# plt.show()

demo_input_data = [[180, 89, 0, 0]]  # Example input data
demo_input_df = pd.DataFrame(demo_input_data, columns=features)

# Predictions
prediction_lr = model_lr.predict(demo_input_df)
print(f"LR Prediction: {prediction_lr[0]}")

prediction_dt = model_dr.predict(demo_input_df)
print(f"Decision Tree Prediction: {prediction_dt[0]}")

prediction_avg = (prediction_lr[0] + prediction_dt[0]) / 2
print(f"Average Prediction: {prediction_avg}")


def save_model(model_filename, model):
    with open(model_filename, 'wb') as file:
        pickle.dump(model, file)


def load_model(model_filename):
    with open(model_filename, 'rb') as file:
        loaded_model = pickle.load(file)
    return loaded_model

# Uncomment to save models


save_model('LinearRegressionModel.pkl', model_lr)
save_model('DecisionTreeModel.pkl', model_dr)
save_model('DataFrameAllDocs.pkl', df_all_docs)

# Example to load and use a saved model
# loaded_model_lr = load_model('LinearRegressionModel.pkl')
# loaded_model_dt = load_model('DecisionTreeModel.pkl')
# loaded_df_all_docs = load_model('DataFrameAllDocs.pkl')
