
# python modelm.py -u "mongodb+srv://werleja1:Md1794682350.@mdmwerleja1.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
import argparse
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle

# Parse arguments
parser = argparse.ArgumentParser(description='Create Model')
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

# Handle missing values
df.dropna(inplace=True) 

print(df.count())


# Select features and target
X = df.drop(columns=['Boxoffice in Million'])  # assuming this is your target column
y = df['Boxoffice in Million']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the linear regression model
model = LinearRegression()
model.fit(X_train, y_train)


print("X_test contents:")
print(X_test.head())


# Predictions for testing set
y_pred = model.predict(X_test)

# Plotting the regression results
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, color='blue')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
plt.xlabel('Actual')
plt.ylabel('Predicted')
plt.title('Actual vs Predicted Box Office')
plt.show()


"""

print("*** DEMO ***")
is_summer = 1
is_R_rated = 1
is_english = 1
Runtime_in_Minutes = 170

print("Downhill: " + str(downhill))
print("Uphill: " + str(uphill))
print("Length: " + str(length))
demoinput = [[downhill,uphill,length,max_elevation]]
demodf = pd.DataFrame(columns=['downhill', 'uphill', 'length_3d', 'max_elevation'], data=demoinput)
demooutput = gbr.predict(demodf)
time = demooutput[0]
"""

corr = df.corr()
print(corr)
sn.heatmap(corr, annot=True)
plt.show()


#Umcomment for use!
"""
# Save the trained model
with open('LinearRegressionModel.pkl', 'wb') as file:
    pickle.dump(model, file)

# Load the model (example)
with open('LinearRegressionModel.pkl', 'rb') as file:
    loaded_model = pickle.load(file)"""