# python -m flask --debug --app service run (works also in PowerShell)
# $env:AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=werleja1;AccountKey=Lq7W5Yjdv17UBMc9UQEnUGah15qO9Uzg3qSV+uuSmNTKfPurZmgkYDadHwVzFW82V3mvvDlvkt0p+AStrOJ80A==;EndpointSuffix=core.windows.net"

from flask_cors import CORS
from flask import Flask, jsonify, request, send_file
from azure.storage.blob import BlobServiceClient
import pandas as pd
from pathlib import Path
import pickle
import datetime
import os
from flask.cli import load_dotenv



#load_dotenv()
#AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
model_files = ["LinearRegressionModel.pkl", "DecisionTreeModel.pkl", "DataFrameAllDocs.pkl"]
model_in_use = "DecisionTreeModel.pkl"

# init app, load model from storage
print("*** Init and load model ***")
if 'AZURE_STORAGE_CONNECTION_STRING' in os.environ:
    azureStorageConnectionString = os.environ['AZURE_STORAGE_CONNECTION_STRING']
    blob_service_client = BlobServiceClient.from_connection_string(
        azureStorageConnectionString)

    print("fetching blob containers...")
    containers = blob_service_client.list_containers(include_metadata=True)
    for container in containers:
        existingContainerName = container['name']
        print("checking container " + existingContainerName)
        if existingContainerName.startswith("movie-model"):
            parts = existingContainerName.split("-")
            print(parts)
            suffix = 1
            if (len(parts) == 3):
                newSuffix = int(parts[-1])
                if (newSuffix > suffix):
                    suffix = newSuffix

    container_client = blob_service_client.get_container_client(
        "movie-model-" + str(suffix))
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        print("\t" + blob.name)
        print(suffix)

    # Download the blob to a local file
    Path("../model").mkdir(parents=True, exist_ok=True)
    for model_file in model_files:
        download_file_path = os.path.join("../model", model_file)
        print("\nDownloading blob to \n\t" + download_file_path)

        with open(file=download_file_path, mode="wb") as download_file:
            download_file.write(container_client.download_blob(model_file).readall())
        print("Downloaded: " + model_file)

else:
    print("CANNOT ACCESS AZURE BLOB STORAGE - Please set connection string as env variable")
    print(os.environ)
    print("AZURE_STORAGE_CONNECTION_STRING not set")


file_path = Path(".", "../model/", "LinearRegressionModel.pkl")
with open(file_path, 'rb') as fid:
    model_lr = pickle.load(fid)

file_path = Path(".", "../model/", "DecisionTreeModel.pkl")
with open(file_path, 'rb') as fid:
    model_dt = pickle.load(fid)

file_path = Path(".", "../model/", "DataFrameAllDocs.pkl")
with open(file_path, 'rb') as fid:
    df_all_docs = pickle.load(fid)

print("*** Init Flask App ***")
app = Flask(__name__)
cors = CORS(app)
app = Flask(__name__, static_url_path='/', static_folder='../frontend/build')


@app.route("/")
def indexPage():
    return send_file("../frontend/build/index.html")


@app.route("/api/predict")
def predict():
    try:
        # Extracting features from the query parameters
        is_summer = request.args.get('is_summer', default=0, type=int)
        is_R_rated = request.args.get('is_R_rated', default=0, type=int)
        is_english = request.args.get('is_english', default=0, type=int)
        Runtime_in_Minutes = request.args.get(
            'Runtime_in_Minutes', default=0, type=int)
        Director_is_PeterJackson = request.args.get(
            'Director_is_PeterJackson', default=0, type=int)
        audience_score = request.args.get(
            'audience_score', default=0, type=int)
        tomato_score = request.args.get('tomato_score', default=0, type=int)


# ['is_summer','is_R_rated','is_english',"Runtime in Minutes","Director_is_PeterJackson", "audience_score", "tomato_score"]
        # Creating the input DataFrame
        input = [[Runtime_in_Minutes,audience_score,tomato_score, is_summer, is_R_rated, is_english,Director_is_PeterJackson]]
        df = pd.DataFrame(columns=['Runtime in Minutes','audience_score', 'tomato_score', 'is_summer', 'is_R_rated', 'is_english','Director_is_PeterJackson'], data=input)



        # Making prediction
        output_lr = model_lr.predict(df)
        output_dr = model_dt.predict(df)
        print(output_lr)
        print(output_dr)

        avg_prediction = (output_dr + output_lr) / 2
        print(avg_prediction)
        predicted_box_office = round(avg_prediction[0], 2)

        target_boxoffice = predicted_box_office  # Example target value in millions
        boxoffice_range = 5    # Example range in millions (+/- 5 in this case)

        filtered_df = df_all_docs[(df_all_docs['Boxoffice in Million'] >= target_boxoffice - boxoffice_range) & 
                 (df_all_docs['Boxoffice in Million'] <= target_boxoffice + boxoffice_range)]

        filtered_df = filtered_df['Title']
        filtered_df_head = filtered_df.head().tolist()
        print("Filteres DF")
        print(filtered_df.head())


        print(predicted_box_office)
        return jsonify({"predicted_box_office": predicted_box_office ,"similar_movies": filtered_df_head})
    except Exception as e:
        return jsonify({"error": str(e)})
    
    

