import os
import json
import uuid
from flask import Flask, redirect, render_template, request, send_from_directory, send_file, make_response, url_for
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

app = Flask(__name__)
connect_str = "DefaultEndpointsProtocol=https;AccountName=csg100320023229a661;AccountKey=VSrOGSmbrNE8uCa+53ZF5zPPVbfvjYGtJHaa3rG5trg9TeHdQQUp44DZoB4pm6CRuY9LFApSl6/B+AStxLwB+g==;EndpointSuffix=core.windows.net"
container_name = "blobber"
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Retrieve the uploaded file from the request
        file = request.files['file']

        # Create a BlobServiceClient object
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        # Create a BlobClient object for the uploaded file
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file.filename)

        # Upload the file to Azure Blob Storage
        blob_client.upload_blob(file)

        return "File uploaded successfully"

    return render_template('upload.html')

@app.route('/download/<filename>')
def download(filename):
    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Create a BlobClient object for the requested file
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

    # Download the file from Azure Blob Storage
    file_data = blob_client.download_blob()

    # Set the content type and disposition headers
    content_type = blob_client.get_blob_properties().content_settings.content_type
    content_disposition = 'attachment; filename="{}"'.format(filename)

    # Create a Flask response object with the blob content
    response = make_response(file_data.readall())

    # Set the content type and disposition headers on the response
    response.headers.set('Content-Type', content_type)
    response.headers.set('Content-Disposition', content_disposition)

    return response


@app.route('/about')
def aboutus():
    return render_template('About.html')
@app.route('/privacy-policy')
def privacy():
    return render_template('Privacy.html')
@app.route('/search', methods=['POST'])
def search_files():
    search_query = request.form['search_query']
    results = []

    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client(container_name)

    # Search for blobs that match the search query
    for blob in container_client.list_blobs():
        if blob.name.lower().startswith(search_query.lower()):
            size = blob.size
            date_modified = blob.last_modified
            link = container_client.get_blob_client(blob).url
            results.append({
                'name': blob.name,
                'link': link,
                'size': f"{size / 1024:.1f} KB",
                'date_modified': date_modified.strftime('%Y-%m-%d')
            })

    # If no exact match is found, search for partial matches
    if not results:
        for blob in container_client.list_blobs():
            if blob.name.lower().find(search_query.lower()) != -1:
                size = blob.size
                date_modified = blob.last_modified
                link = container_client.get_blob_client(blob).url
                results.append({
                    'name': blob.name,
                    'link': link,
                    'size': f"{size / 1024:.1f} KB",
                    'date_modified': date_modified.strftime('%Y-%m-%d')
                })

    return render_template('file_search_results.html', results=results)

@app.route('/files')
def files():
    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Get a reference to the container
    container_client = blob_service_client.get_container_client(container_name)

    # Get a list of blobs in the container
    blobs = container_client.list_blobs()

    return render_template('files.html', blobs=blobs)
@app.route('/save_code', methods=['POST'])
def save_code():
    code = request.form['code']

    # Save code to local file system
    with open('saved_code.txt', 'w') as f:
        f.write(code)

    # Save code to Azure Storage account
    blob_client = container_client.get_blob_client('saved_code.txt')
    blob_client.upload_blob(code, overwrite=True)

    return 'OK'

@app.route('/get_code', methods=['GET'])
def get_code():
    try:
        # Try to read code from local file system
        with open('saved_code.txt', 'r') as f:
            code = f.read()
    except FileNotFoundError:
        # If local file is not found, read code from Azure Storage account
        blob_client = container_client.get_blob_client('saved_code.txt')
        code = blob_client.download_blob().content_as_text()

    return code
@app.route('/ads.txt')
def serve_ads_txt():
    print('Serving ads.txt')
    return send_from_directory(app.root_path, 'ads.txt')

if __name__ == '__main__':
    app.run(debug=True)