
# python modelm.py -u "mongodb+srv://werleja1:Md1794682350.@mdmwerleja1.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
import argparse
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt
from pymongo import MongoClient

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

# Fetch documents
documents = list(collection.find({}))

# Create DataFrame
df = pd.DataFrame(documents)

# Transformations
summer_months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"]
df['is_summer'] = df['release_month'].apply(lambda x: 1 if x in summer_months else 0)
df['is_R_rated'] = df['rating'].apply(lambda x: 1 if x == "R" else 0)
df['is_english'] = df['Original Language'].apply(lambda x: 1 if x == "English" else 0)
df["Boxoffice in Million"] = pd.to_numeric(df["Boxoffice in Million"], errors='coerce')
df["Runtime in Minutes"] = pd.to_numeric(df["Runtime in Minutes"], errors='coerce')

# Keep only numeric columns
df = df.select_dtypes(include=['number'])

# Handle missing values
df.dropna(inplace=True)  # or df.fillna(0) if you prefer to fill with zeros

# Correlation Analysis
corr = df.corr()
print(corr)
sn.heatmap(corr, annot=True)
plt.show()
