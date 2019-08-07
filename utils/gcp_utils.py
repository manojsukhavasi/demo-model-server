from google.cloud import storage
CONFIG_FILE='gcp_access.json'
DEFAULT_BUCKET='greensight-demo-output'

def copy_to_bucket(gcp_fname, file_path, zip_path, sport):
    storage_client = storage.Client.from_service_account_json(CONFIG_FILE)
    bucket = storage_client.get_bucket(DEFAULT_BUCKET)
    blob1 = bucket.blob(f'{sport}/{gcp_fname}.mp4')
    blob2 = bucket.blob(f'{sport}/{gcp_fname}.zip')
    blob1.upload_from_filename(file_path)
    blob2.upload_from_filename(zip_path)
    blob1.make_public()
    blob2.make_public()
    return (blob1.public_url, blob2.public_url)