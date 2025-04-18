from azure.storage.blob import BlobServiceClient
from django.conf import settings
import uuid

def get_blob_service_client():
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={settings.AZURE_ACCOUNT_NAME};AccountKey={settings.AZURE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"
    return BlobServiceClient.from_connection_string(connection_string)

# def upload_to_azure(file, user_id):
#     """Upload a file to Azure Blob Storage and return its URL"""
#     # Generate a unique filename
#     extension = file.name.split('.')[-1]
#     filename = f"{user_id}/{uuid.uuid4()}.{extension}"
    
#     # Get the blob service client
#     blob_service_client = get_blob_service_client()
#     container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER)
    
#     # Upload the file
#     blob_client = container_client.get_blob_client(filename)
#     blob_client.upload_blob(file, overwrite=True)
    
#     # Return the URL of the uploaded file
#     return blob_client.url

def upload_to_azure(file, user_id, username):
    """Upload a file to Azure Blob Storage with user-specific folder structure"""
    # Determine file type for categorization
    content_type = file.content_type
    if content_type.startswith('image/'):
        category = 'images'
    elif content_type.startswith('video/'):
        category = 'videos'
    elif content_type.startswith('audio/'):
        category = 'audio'
    elif content_type.startswith('application/pdf'):
        category = 'documents'
    else:
        category = 'others'
    
    # Generate a unique filename with folder structure: username/category/filename
    extension = file.name.split('.')[-1]
    filename = f"{username}/{category}/{uuid.uuid4()}.{extension}"
    
    # Get the blob service client
    blob_service_client = get_blob_service_client()
    container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER)
    
    # Upload the file
    blob_client = container_client.get_blob_client(filename)
    blob_client.upload_blob(file, overwrite=True)
    
    # Return the URL of the uploaded file and the category
    return blob_client.url, category

def delete_from_azure(file_url):
    """Delete a file from Azure Blob Storage"""
    # Extract the blob name from the URL
    blob_name = file_url.split(f"{settings.AZURE_CONTAINER}/")[-1]
    
    # Get the blob service client
    blob_service_client = get_blob_service_client()
    container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER)
    
    # Delete the file
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.delete_blob()