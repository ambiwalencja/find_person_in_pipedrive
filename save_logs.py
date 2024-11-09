import os
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from datetime import date
from simple_file_checksum import get_checksum
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# get credentials
account_credentials = {
    "type": os.getenv("TYPE"),
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": os.getenv("AUTH_URI"),
    "token_uri": os.getenv("TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("UNIVERSE_DOMAIN")
}
credentials = service_account.Credentials.from_service_account_info(
    account_credentials, scopes=["https://www.googleapis.com/auth/drive"])

# construct service
service = build('drive', 'v3', credentials=credentials)

# define folder id
gdrive_folder_id = os.environ.get('GDRIVE_FOLDER_ID')

# define function for getting log files from google drive
def get_files_from_folder(service, folder_id):
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, pageSize=100, fields="nextPageToken, files(id, name, md5Checksum)").execute()
    files = results.get('files', [])
    return files

# define function for uploading file to google drive
def upload_file_to_gdrive(service, file_path, mime_type):
    file_metadata = {
        'name': file_path,  # The name of the file in Google Drive
        'parents': [gdrive_folder_id]  # The ID of the folder where the file will be uploaded
        }
    media = MediaFileUpload(file_path, mimetype=mime_type)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

# define function for downloading a file
def download_file_from_drive(service, file_id):
    request = service.files().get_media(fileId=file_id)
    file_handler = io.BytesIO()
    downloader = MediaIoBaseDownload(file_handler, request)
    done = False
    while done is False:
        _, done = downloader.next_chunk()
    file_handler.seek(0)
    text_file = file_handler.read().decode('utf-8') 
    return text_file

# define job
def save_logs_to_drive():
    filename = f'{date.today().strftime("%Y-%m-%d")}.log' # .strftime("%Y-%m-%d")

    #check if file already exists
    if not os.path.isfile(filename):
        return
    
    # find the checksum of the file on the server
    local_checksum = get_checksum(filename, algorithm="MD5")
    
    # get the list of files in google drive
    try:
        list_of_files = get_files_from_folder(service, gdrive_folder_id)
    except BrokenPipeError:
        print("BrokenPipeError - we will try next time")
        return

    # compare the content
    if not list_of_files: # if there are no files
        upload_file_to_gdrive(service, filename, 'text/plain')
    else:
        list_of_drive_names = [] # make the list of names of files in gdrive
        for file in list_of_files:
            list_of_drive_names.append(file.get('name'))
            if file.get('name') == filename: # if names are the same
                gdrive_checksum = file.get('md5Checksum') # find checksum
                if gdrive_checksum != local_checksum: # if checksums are not the same
                    gdrive_file_id = file.get('id')
                    gdrive_log_file = download_file_from_drive(service, gdrive_file_id)
                    gdrive_first_line = gdrive_log_file.split('\n')[0] # get first lines of files to compare
                    with open(filename,'r') as local_log_file:
                        local_first_line = local_log_file.readline().split('\n')[0]
                    if gdrive_first_line == local_first_line: # if first lines match
                        service.files().delete(fileId=gdrive_file_id).execute() # replace file from drive with local file
                        upload_file_to_gdrive(service, filename, 'text/plain')
                    else:
                        file_metadata = {'name': f'{filename}_old.log'} # change name of gdrive file
                        updated_file = service.files().update(fileId=gdrive_file_id, body=file_metadata, fields='id, name').execute()
                        upload_file_to_gdrive(service, filename, 'text/plain') # upload new log file                             
        if filename not in list_of_drive_names:
            upload_file_to_gdrive(service, filename, 'text/plain')
    return True


scheduler = BlockingScheduler()
scheduler.add_job(save_logs_to_drive, 'interval', seconds=10) # minutes=2
scheduler.start()
