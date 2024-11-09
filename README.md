# Find Person in Pipedrive  
Effortlessly manage and organize client data in Pipedrive CRM.  

---

## Description  
**Find Person in Pipedrive** is a Python-based application designed to help sales teams efficiently manage their Pipedrive CRM client database. It automates common tasks, such as verifying new client data, checking for duplicates, and creating new contacts when necessary.  

The app also supports retrying failed tasks and maintains logs for better transparency and debugging.

---

## Features  
- **Client Verification**: Validates client contact details before processing.  
- **Duplicate Check**: Searches the Pipedrive CRM database to check for existing clients:  
  - If the client exists, their ID and details are passed to an external application.
  - If the client is new, a contact person is created in Pipedrive.
  - If contact information matches multiple clients, an email is sent to the sales manager to review and merge contacts. 
- **Execution Archiving**: aves input and output data for each operation in a PostgreSQL database.
- **Task Queueing and Retry**: Leverages Redis for scheduling, enabling simultaneous execution of tasks and easy retries for failed tasks. 
- **Logging**: Maintains log files, automatically uploaded to Google Drive.
- **External Management**: Offers API endpoints for task viewing, rerunning, and user management via an external interface. 

---


## Tech Stack
- **Languages and Frameworks**: Python, FastAPI
- **Databases**: PostgreSQL (execution logs), Redis (task queue)
- **Integrations**:
    - Pipedrive API for CRM data
    - Resend for email notifications
    - Google Drive for log storage
- **Hosting**: DigitalOcean


## Installation  

1. Clone the repository:  
   ```bash  
   git clone <repository_url>  
   cd <repository_directory>  

2. Install dependencies
   ```bash  
   pip install -r requirements.txt  

3. Set up environment variables (e.g., database URLs, API keys) in a .env file.
4. Run the application:
   ```bash  
   uvicorn app.main:app --reload  
  


## Usage
The app is customized for specific company needs, with input schemas tailored to their Pipedrive data structure. However, the codebase is modular and can be adapted for other businesses' requirements.



## Authors
@ambiwalencja

@NOcrash

## License
This project is licensed under the MIT License.

## Project Status
The project is in its initial stable version. It is actively deployed and in use. While no significant changes are planned, minor adjustments may be made based on user feedback or new requirements.

