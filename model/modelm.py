
# python modelm.py -u "mongodb+srv://werleja1:Md1794682350.@mdmwerleja1.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
import argparse
import sys
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import tree
from sklearn.tree import DecisionTreeRegressor, plot_tree
import pickle

def get_df():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Create model_lr')
    parser.add_argument('-u', '--uri', required=True, help="mongodb uri with username/password")
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


df, df_all_docs = get_df()

# Transformations
summer_months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"]
df['is_summer'] = df['release_month'].apply(lambda x: 1 if x in summer_months else 0)
df['is_R_rated'] = df['rating'].apply(lambda x: 1 if x == "R" else 0)
df['is_english'] = df['Original Language'].apply(lambda x: 1 if x == "English" else 0)
df["Boxoffice in Million"] = pd.to_numeric(df["Boxoffice in Million"], errors='coerce')
df["Runtime in Minutes"] = pd.to_numeric(df["Runtime in Minutes"], errors='coerce')
df["Director_is_PeterJackson"] = df["Director"].apply(lambda x: 1 if x=="PeterJackson" else 0)
df["audience_score"] = pd.to_numeric(df["audience_score"], errors = "coerce")
df["tomato_score"] = pd.to_numeric(df["tomato_score"], errors = "coerce")

df = df.select_dtypes(include=['number'])

features = ['Runtime in Minutes','audience_score', 'tomato_score', 'is_summer', 'is_R_rated', 'is_english','Director_is_PeterJackson']

print(df.head())


#['is_summer','is_R_rated','is_english',"Boxoffice in Million","Runtime in Minutes","Director_is_PeterJackson", "audience_score", "tomato_score"]

df.dropna(inplace=True) 

print(df.count())


# Select features and target
X = df.drop(columns=['Boxoffice in Million'])  # assuming this is your target column
y = df['Boxoffice in Million']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the linear regression model_lr
model_lr = LinearRegression()
model_lr.fit(X_train, y_train)

model_dr = DecisionTreeRegressor()
model_dr.fit(X_train, y_train)

plt.figure(figsize=(20,10))  # Set the size of the figure
plot_tree(model_dr, feature_names=features, filled=True)
#plt.show()




print("LR Test:")
print(X_test.head())

y_pred = model_lr.predict(X_test)

# Plotting the regression results
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, color='blue')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
plt.xlabel('Actual')
plt.ylabel('Predicted')
plt.title('Actual vs Predicted Box Office')
#plt.show()

print("DT Test")

y_pred = model_dr.predict(X_test)

"""
# Plotting the regression results
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, color='blue')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
plt.xlabel('Actual')
plt.ylabel('Predicted')
plt.title('Actual vs Predicted Box Office')
plt.show()
"""

#"Zombieland", "Boxoffice in Million": 75.6, "Runtime in Minutes": 87, "Original Language": "English", "Director": "RubenFleischer", "release_month": "Oct", "rating": "R", "audience_score": 86.0, "tomato_score": 89.0, "files": []}

print("*** DEMO ***")
is_summer = 0
is_R_rated = 1
is_english = 1
Runtime_in_Minutes = 87
Director_is_PeterJackson = 0
audience_score = 86
tomato_score = 89

demo_input = [[Runtime_in_Minutes,audience_score,tomato_score, is_summer, is_R_rated, is_english,Director_is_PeterJackson]]
demo_df = pd.DataFrame(columns=features, data=demo_input)
demooutput = model_lr.predict(demo_df)
prediction_lr = demooutput[0]
print(f"LR Prediction: {prediction_lr}")

prediction_dt = model_dr.predict(demo_input)

print(f"desicion Tree Prediction: {prediction_dt}")

corr = df.corr()
print(corr)
sn.heatmap(corr, annot=True)
#plt.show()

target_boxoffice = prediction_lr  # Example target value in millions
boxoffice_range = 5    # Example range in millions (+/- 5 in this case)

# Filter the DataFrame for entries within the specified boxoffice range
filtered_df = df_all_docs[(df_all_docs['Boxoffice in Million'] >= target_boxoffice - boxoffice_range) & 
                 (df_all_docs['Boxoffice in Million'] <= target_boxoffice + boxoffice_range)]

filtered_df = filtered_df['Title']

print("Filteres DF")
print(filtered_df.head())

#Umcomment for use!

# Save the trained models

def safe_model(model, model_lr): 

    with open(model, 'wb') as file:
        pickle.dump(model_lr, file)


def load_model(model):

    with open(model, 'rb') as file:
        loaded_model = pickle.load(file)
    return loaded_model

safe_model('LinearRegressionModel.pkl', model_lr)
safe_model('DecisionTreeModel.pkl', model_dr)
safe_model('DataFrameAllDocs.pkl', df_all_docs)

"""
loaded_model_lr = load_model('LinearRegressionModel.pkl')
loaded_model_dt= load_model('DecisionTreeModel.pkl')
loaded_df_all_docs= load_model('DataFrameAllDocs.pkl')

prediction_dt = loaded_model_lr.predict(demo_input)

print(f"Loaded Prediction: {prediction_dt}")
"""

