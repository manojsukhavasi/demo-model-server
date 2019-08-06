from google.cloud import storage
CONFIG_FILE='gcp_access.json'
DEFAULT_BUCKET='greensight-demo-output'

def copy_to_bucket(gcp_fname, file_path, sport):
    storage_client = storage.Client.from_service_account_json(CONFIG_FILE)
    bucket = storage_client.get_bucket(DEFAULT_BUCKET)
    blob = bucket.blob(f'{sport}/{gcp_fname}')  
    blob.upload_from_filename(file_path)
    blob.make_public()
    return blob.public_url