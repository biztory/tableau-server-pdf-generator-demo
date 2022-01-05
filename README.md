# Tableau-Server-PDF-generator
# Demo Branch
## Edited by Chris Boyles - 12/05/2021

## Methods in Python Notebook
There are currently 3 methods in this notebook:
NOTE: Currently it loops through the filters and their values and can only apply one filter at a time. having multiple filters per view is the next area of improvement.

### gen_pdf_from_view_imgs()
Iterates through the views (and filters) set in the config file, downloads them as images via REST API calls and then adds them into a single PDF file
### gen_pdf_from_view_pdfs()
Iterates through the views (and filters) set in the config file, downloads them as PDFs via REST API calls and then merges them into a single PDF file
### gen_pdf_from_workbook()
Uses the Workbook name set in the config file and downloads the workbook as a PDF via a REST API call.
NOTE: This is currently only downloading the view that was last open when saving the workbook, instead of all views. Not sure why this is happening yet.

## Connection file
To connect to the server you first need to edit the connection config file 'tableau_server_pdf_generator_connection.cfg'.
Add the Server URL, Site name (can find this by logging into the site in browser and looking at the URL).
State the login method of either 'Local' or 'PAT' - Local requires traditional hardcoded username and password, wheres PAT uses a Personal Access Token to avoid hardcoding passwords in files.
You can generate the PAT from your site in your account settings.

## Config file
### workbook_details
contains download location and workbook name which are currently used for all 3 methods.
viewnames, filternames and filtervalues are used for the gen_pdf_from_view_imgs method as well as the gen_pdf_from_view_pdfs method if no specific category key is provided.

### logging_details
log file information

### Ikea/Staples/Currys
These 3 are used for the gen_pdf_from_view_pdfs method. 
When run the method prompts the user for an input and then if it matches one of these 3 keys then it uses the viewnames, filternames and filtervalues values from that particular key.
This allows variability in filters being applied and which views are required per 'client'.
