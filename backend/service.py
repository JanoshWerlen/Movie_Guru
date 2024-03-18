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


load_dotenv()
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")


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
    download_file_path = os.path.join("../model", "LinearRegressionModel.pkl")
    print("\nDownloading blob to \n\t" + download_file_path)

    with open(file=download_file_path, mode="wb") as download_file:
        download_file.write(
            container_client.download_blob(blob.name).readall())

else:
    print("CANNOT ACCESS AZURE BLOB STORAGE - Please set connection string as env variable")
    print(os.environ)
    print("AZURE_STORAGE_CONNECTION_STRING not set")

file_path = Path(".", "../model/", "LinearRegressionModel.pkl")
with open(file_path, 'rb') as fid:
    model = pickle.load(fid)

"""

feature_names = ['Runtime in Minutes', 'is_summer', 'is_R_rated', 'is_english']

# Create a demo input matching the training features
demo_input = {
    'is_summer': [1],  # Example values
    'is_R_rated': [1],
    'is_english': [1],
    'Runtime in Minutes': [200]
}

# Create the DataFrame using the feature names
demo_df = pd.DataFrame(demo_input, columns=feature_names)

# Now you can use demo_df for prediction
demo_output = model.predict(demo_df)
print("Predicted Box Office (in Million):", demo_output[0])

"""

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
        demo_input = [[Runtime_in_Minutes,audience_score,tomato_score, is_summer, is_R_rated, is_english,Director_is_PeterJackson]]
        demo_df = pd.DataFrame(columns=['Runtime in Minutes','audience_score', 'tomato_score', 'is_summer', 'is_R_rated', 'is_english','Director_is_PeterJackson'], data=demo_input)

        # Making prediction
        demo_output = model.predict(demo_df)
        predicted_box_office = round(demo_output[0], 2)
        print(predicted_box_office)
        return jsonify({"predicted_box_office": predicted_box_office})
    except Exception as e:
        return jsonify({"error": str(e)})


"""

print("*** Sample calculation with model ***")
def din33466(uphill, downhill, distance):
    km = distance / 1000.0
    print(km)
    vertical = downhill / 500.0 + uphill / 300.0
    print(vertical)
    horizontal = km / 4.0
    print(horizontal)
    return 3600.0 * (min(vertical, horizontal) / 2 + max(vertical, horizontal))

def sac(uphill, downhill, distance):
    km = distance / 1000.0
    return 3600.0 * (uphill/400.0 + km /4.0)

downhill = 300
uphill = 700
length = 10000
max_elevation = 1200
print("Downhill: " + str(downhill))
print("Uphill: " + str(uphill))
print("Length: " + str(length))
demoinput = [[downhill,uphill,length,max_elevation]]
demodf = pd.DataFrame(columns=['downhill', 'uphill', 'length_3d', 'max_elevation'], data=demoinput)
demooutput = model.predict(demodf)
time = demooutput[0]
print("Our Model: " + str(datetime.timedelta(seconds=time)))
print("DIN33466: " + str(datetime.timedelta(seconds=din33466(uphill=uphill, downhill=downhill, distance=length))))
print("SAC: " + str(datetime.timedelta(seconds=sac(uphill=uphill, downhill=downhill, distance=length))))

 return jsonify({
        'time': str(datetime.timedelta(seconds=time)),
        'din33466': str(datetime.timedelta(seconds=din33466(uphill=uphill, downhill=downhill, distance=length))),
        'sac': str(datetime.timedelta(seconds=sac(uphill=uphill, downhill=downhill, distance=length)))
        })

"""
