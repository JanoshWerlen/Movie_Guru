# cd model
# python save.py -c "DefaultEndpointsProtocol=https;AccountName=werleja1;AccountKey=Lq7W5Yjdv17UBMc9UQEnUGah15qO9Uzg3qSV+uuSmNTKfPurZmgkYDadHwVzFW82V3mvvDlvkt0p+AStrOJ80A==;EndpointSuffix=core.windows.net"

import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import argparse

# https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python?tabs=managed-identity%2Croles-azure-portal%2Csign-in-azure-cli
# Erlaubnis auf eigenes Konto geben :-)

try:
    print("Azure Blob Storage Python quickstart sample")

    parser = argparse.ArgumentParser(description='Upload Model')
    parser.add_argument('-c', '--connection', required=True, help="azure storage connection string")
    args = parser.parse_args()

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(args.connection)

    exists = False
    containers = blob_service_client.list_containers(include_metadata=True)
    suffix = 0
    for container in containers:
        existingContainerName = container['name']
        print(existingContainerName, container['metadata'])
        if existingContainerName.startswith("movie-model"):
            parts = existingContainerName.split("-")
            print(parts)
            if (len(parts) == 3):
                newSuffix = int(parts[-1])
                if (newSuffix > suffix):
                    suffix = newSuffix

    suffix += 1
    container_name = str("movie-model-" + str(suffix))
    print("new container name: ")
    print(container_name)

    for container in containers:            
        print("\t" + container['name'])
        if container_name in container['name']:
            print("EXISTIERTT BEREITS!")
            exists = True

    if not exists:
        # Create the container
        container_client = blob_service_client.create_container(container_name)

    def upload_model(model_name):
        local_file_name = model_name
        upload_file_path = os.path.join(".", local_file_name)

        # Create a blob client using the local file name as the name for the blob
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)
        print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

        # Upload the created file
        with open(file=upload_file_path, mode="rb") as data:
            blob_client.upload_blob(data)
        
        print("Uploaded: " + model_name)

    upload_model("LinearRegressionModel.pkl")
    upload_model("DecisionTreeModel.pkl")
    upload_model("DataFrameAllDocs.pkl")

except Exception as ex:
    print('Exception:')
    print(ex)
    exit(1)
