# # Python Script to create PDF from dashboard based on parameters
# ## Importing libraries and features

#pip install PyPDF2

import os, keyring, re, configparser, warnings, urllib, requests, shutil, json
from PyPDF2 import PdfFileMerger, PdfFileReader
from fpdf import FPDF
from PIL import Image
import math
import datetime
from getpass import getpass
from pathlib import Path
warnings.filterwarnings('ignore')
config = configparser.ConfigParser()
connection = configparser.ConfigParser()
config.read(r".\tableau_server_pdf_generator_config.cfg")
connection.read(r".\tableau_server_pdf_generator_connection.cfg")
illegal_chars = config["logging_details"]["illegalchars"].split(',')

# ## Setting of  Variables
server = connection["server_connection"]["server"] # Enter site in format tableau.company.com without the https before it
site_content_url = connection["server_connection"]["site"] # This can be found from the URL of the content and if using the Default site then this will be blank
api_ver = connection["server_connection"]["api"] # This can be found from the Tableau Server REST API reference
URL = "https://{}/api/{}".format(server, api_ver)

# ## Initiate Log File
log_file_loc = r"{}\{}".format(str(Path.home()), config["logging_details"]["logfilename"])
log_file = open(log_file_loc, "a+")


# ## Functions
# ### Fn to open Log file
def open_log(log_file):
    if log_file.closed:
        log_file_loc = r"{}\{}".format(str(Path.home()), config["logging_details"]["logfilename"])
        log_file = open(log_file_loc, "a+")
        return log_file 
    else:
        return 


# ### Fn to check errors
def check_error(request, task):
    if task == "sign_in":
        if request.status_code == 200:
            print("\t\tUser signed in successfully!")
            return 1
        elif request.status_code == 404:
            print("\t\tERROR: User not found!!")
            return 0
        elif request.status_code == 401:
            print("\t\tERROR: Login error!!")
            return 0
        else:
            print("\t\tERROR: Request error check again!!")
            return 0
        
    elif task == "sign_out":
        if request.status_code == 204:
            print("\t\tUser signed out successfully!")
            return 1
        else:
            print("\t\tERROR: Request error check again!!")
            return 0
        
    elif task == "create_users":
        if request.status_code == 201:
            print("\t\tUser created successfully!")
            return 1
        elif request.status_code == 404:
            print("\t\tERROR: Site not found!!")
            return 0
        elif request.status_code == 409:
            print("\t\tERROR: User exists or license unavailable, check again!!")
            return 0
        elif request.status_code == 400:
            print("\t\tERROR: Invalid site role or bad request!!")
            return 0
        else:
            print("\t\tERROR: Request error check again!!")
            return 0
        
    elif task == "update_users":
        if request.status_code == 200:
            print("\t\tUser information updated successfully!")
            return 1
        elif request.status_code == 404:
            print("\t\tERROR: User or Site not found!!")
            return 0
        elif request.status_code == 409:
            print("\t\tERROR: User exists or license unavailable, check again!!")
            return 0
        elif request.status_code == 400:
            print("\t\tERROR: Invalid site role, email address or bad request!!")
            return 0
        elif request.status_code == 403:
            print("\t\tERROR: Licensing update on self or guest account not allowed!!")
            return 0
        else:
            print("\t\tERROR: Request error check again!!")
            return 0
        
    elif task == "find_group_id":
        if request.status_code == 200:
            print("\t\tGroup found!")
            return 1
        elif request.status_code == 404:
            print("\t\tERROR: Site not found!!")
            return 0
        else:
            print("\t\tERROR: Request error check again!!")
            return 0
        
    elif task == "add_user_group":
        if request.status_code == 200:
            print("\t\tUser added to group successfully!")
            return 1
        elif request.status_code == 404:
            print("\t\tERROR: Site or Group not found!!")
            return 0
        elif request.status_code == 409:
            print("\t\tERROR: Specified User already in group!!")
            return 0
        else:
            print("\t\tERROR: Request error check again!!")
            return 0
    elif task == "query_workbook_id":
        if request.status_code == 200:
            print("\t\tQueried workbook name successfully!")
            return 1
        elif request.status_code == 400:
            print("\t\tERROR: Pagination error!!")
            return 
        elif request.status_code == 403:
            print("\t\tERROR: Forbidden to read workbook!!")
            return 0
        elif request.status_code == 404:
            print("\t\tERROR: Site or workbook not found!!")
            return 0
        else:
            print("\t\tERROR: Request error check again!!")
            return 0
    elif task == "query_view_image":
        if request.status_code == 200:
            print("\t\tQueried view image successfully!")
            return 1
        elif request.status_code == 403:
            print("\t\tERROR: Forbidden to view image!!")
            return 0
        elif request.status_code == 404:
            print("\t\tERROR: Site, workbook or view not found!!")
            return 0
        else:
            print("\t\tERROR: Request error check again!!")
            return 0
    elif task == "query_view_pdf":
        if request.status_code == 200:
            print("\t\tQueried view pdf successfully!")
            return 1
        elif request.status_code == 400:
            print("\t\tERROR: The view ID in the URI doesn't correspond to a view available on the specified site.!!")
            return 0
        elif request.status_code == 401:
            print("\t\tERROR: Unauthorized!!")
            return 0
        elif request.status_code == 403:
            print("\t\tERROR: Forbidden to view pdf!!")
            return 0
        elif request.status_code == 404:
            print("\t\tERROR: Site, workbook or view not found!!")
            return 0
        elif request.status_code == 405:
            print("\t\tERROR: Invalid request method!!")
            return 0
        else:
            print("\t\tERROR: Request error check again!!")
            return 0
    elif task == "download_workbook":
        if request.status_code == 200:
            print("\t\tDownloaded Workbook successfully!")
            return 1
        elif request.status_code == 403:
            print("\t\tERROR: Forbidden to view workbook!!")
            return 0
        elif request.status_code == 404:
            print("\t\tERROR: Site or workbook not found!!")
            return 0
        else:
            print("\t\tERROR: Request error check again!!")
            return 0
    elif task == "query_view_data":
        if request.status_code == 200:
            print("\t\tQueried view data successfully!")
            return 1
        elif request.status_code == 401:
            print("\t\tERROR: Invalid token!!")
            return 0
        elif request.status_code == 403:
            print("\t\tERROR: Forbidden to view data!!")
            return 0
        elif request.status_code == 404:
            print("\t\tERROR: Site, workbook or view not found!!")
            return 0
        else:
            print("\t\tERROR: Request error check again!!")
            return 0


# ### Fn to sign in to Server with a password
def sign_in(username, password, site=""):
    body = {
        "credentials": {
            "name": username,
            "password": password,
            "site": {
                "contentUrl": site
            }
        }
    }
    response = requests.post(
        URL + '/auth/signin', 
        json=body, 
        verify=False, 
        headers={'Accept': 'application/json'}
    )
    
    status = check_error(response, "sign_in")
    if status:
        return response.json()['credentials']['site']['id'], response.json()['credentials']['token']
    else:
        return 0,0


# ### Fn to sign in to Server with a PAT
def sign_in_pat(username, password, site=""):
    body = {
        "credentials": {
            "personalAccessTokenName": username,
            "personalAccessTokenSecret": password,
            "site": {
                "contentUrl": site
            }
        }
    }
    response = requests.post(
        URL + '/auth/signin', 
        json=body, 
        verify=False, 
        headers={'Accept': 'application/json'}
    )
    
    status = check_error(response, "sign_in")
    if status:
        return response.json()['credentials']['site']['id'], response.json()['credentials']['token']
    else:
        return 0,0


# ### Fn to sign out from Server
def sign_out(site_id, token):
    response = requests.post(
        URL + '/auth/signout', 
        verify=False, 
        headers={'Accept': 'application/json',
                'X-Tableau-Auth': token}
    )
    status = check_error(response, "sign_out")
    #log_file.close()
    return status


# ### Fn to generate list of items from delimited string
def gen_list(orig_list):
    temp_list = orig_list.split(',')
    final_list = []
    for item in temp_list:
        item_name = (item.lstrip()).rstrip()
        final_list.append(item_name)
    return final_list


# ### Fn to find workbook id from workbook name
def query_workbook_id(site_id, token, workbook_name):
    response = requests.get(
        URL + '/sites/{}/workbooks?filter=name:eq:{}'.format(site_id, workbook_name), 
        verify=False, 
        headers={'Accept': 'application/json',
                'X-Tableau-Auth': token}
    )
    status = check_error(response, "query_workbook_id")
    return response.json()


# ### Fn to find view ids from list of view names
def query_workbook_view_ids(site_id, token, workbook_id, views_list):
    response = requests.get(
        URL + '/sites/{}/workbooks/{}'.format(site_id, workbook_id), 
        verify=False, 
        headers={'Accept': 'application/json',
                'X-Tableau-Auth': token}
    )
    view_ids = []
    for view in response.json()['workbook']['views']['view']:
        if view['name'] in views_list:
            view_ids.append(view['id'])
    status = check_error(response, "query_workbook_view_ids")
    return view_ids, status


# ### Fn to query single view and return it as an image
def query_view_image(site_id, token, view_id, filtername, filtervalue, filename, applyfilter):
    REST_URL =  URL + '/sites/{}/views/{}/image?maxAge=1'.format(site_id, view_id)
    if applyfilter:
        REST_URL += '&vf_{}={}'.format(urllib.parse.quote_plus(filtername), urllib.parse.quote_plus(filtervalue))
    
    response = requests.get(
        REST_URL, stream=True, verify=False, 
        headers={'Accept': 'application/json',
                'X-Tableau-Auth': token}
    )

    status = check_error(response, "query_view_image")
    with open(filename, 'wb') as f:
        for chunk in response:
            f.write(chunk)
    return status


# ### Fn to query single view and return it as a pdf
def query_view_pdf(site_id, token, view_id, filtername, filtervalue, filename, applyfilter):
    REST_URL =  URL + '/sites/{}/views/{}/pdf?type=A4&orientation=Landscape'.format(site_id, view_id)
    if applyfilter:
        REST_URL += '&vf_{}={}'.format(urllib.parse.quote_plus(filtername), urllib.parse.quote_plus(filtervalue))
    
    response = requests.get(
        REST_URL, stream=True, verify=False, 
        headers={'Accept': 'application/json',
                'X-Tableau-Auth': token}
    )    
        
    status = check_error(response, "query_view_pdf")
    with open(filename, 'wb') as f:
        for chunk in response:
            f.write(chunk)
    return status


# ### Fn to query view data
def query_view_data(site_id, token, view_id):
    response = requests.get(
        URL + '/sites/{}/views/{}/data'.format(site_id, view_id), 
        verify=False, 
        headers={'Accept': 'application/json',
                'X-Tableau-Auth': token}
    ).text.splitlines()
    response.remove(response[0])
    #status = check_error(response, "query_view_data")
    return response


# ### Fn to generate pdf with from queried temp pdf files
def gen_pdf_from_pdfs(file_loc, pdf_filename, num_views):
    #print("Developing PDF for {}...".format(filter_value_name))
    mergedObject = PdfFileMerger()

    for fileNumber in range(1,num_views):
        mergedObject.append(PdfFileReader(r'{}\temp_{}.pdf'.format(file_loc, fileNumber)))
        fileNumber += 1
    
    mergedObject.write(r'{}\{}.pdf'.format(file_loc, pdf_filename))
    
    print("Saved pdf")
    
    for fileNumber in range(1,num_views):
        if os.path.exists(r'{}\temp_{}.pdf'.format(file_loc, fileNumber)):
            os.remove(r'{}\temp_{}.pdf'.format(file_loc, fileNumber))
            print("File deleted!")
        else:
            print("The file does not exist")
    
    
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file.write("\n{} Saved pdf!".format(current_timestamp))


# ### Fn to generate pdf with from queried temp image files
def gen_pdf_from_imgs(file_loc, datepart_filename, num_views):
    #print("Developing PDF for {}...".format(filter_value_name))
    #for chars in illegal_chars:
    #    filter_value_name = filter_value_name.replace(chars, '#')
    pdf = FPDF(orientation = 'L', unit = 'mm', format = 'A4')
    pdf.set_left_margin(8)
    for count in range(1,num_views):
        pdf.add_page()
        pdf.image(r'{}\temp_{}.png'.format(file_loc, count), x=8, y=8, w=282)
        
    filename = r'{}\{}.pdf'.format(file_loc, datepart_filename)
    pdf.output(filename)
    print("Saved pdf {}".format(filename))
    
    for fileNumber in range(1,num_views):
        if os.path.exists(r'{}\temp_{}.png'.format(file_loc, fileNumber)):
            os.remove(r'{}\temp_{}.png'.format(file_loc, fileNumber))
            print("File deleted!")
        else:
            print("The file does not exist")
    
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file.write("\n{} Saved pdf!".format(current_timestamp))


# ### Fn to download whole workbook as pdf
def workbook_as_pdf(site_id, token, workbook_id, file_loc, pdf_filename):
    response = requests.get(
            URL + '/sites/{}/workbooks/{}/pdf?maxAge=1&type=A4&orientation=Landscape'.format(site_id, workbook_id), 
            stream=True, verify=False, 
            headers={'Accept': 'application/json',
                    'X-Tableau-Auth': token}
    )
    
    status = check_error(response, "download_workbook")
    
    filename = r'{}\{}'.format(file_loc, pdf_filename)
    
    with open(filename, 'wb') as f:
        for chunk in response:
            f.write(chunk)
    return status


# ### Fn to iterate over views in list of views and save temp pdfs, then call fn to merge pdfs 
def iterate_views_as_pdfs(site_id, token, view_ids, filter_names, filter_values, file_loc, pdf_filename):
    #print("\n\nBeginning to retrieve dashboards for {}".format(filter_value))
    run = True
    attempt = 0
    if len(filter_names) > 0:
        apply_filter = True
    else:
        apply_filter = False
        
    while (run == True):
        count = 1
        for view in view_ids:
            for filter_name in filter_names or []:
                for filter_value in filter_values or []:
                    view_code = query_view_pdf(site_id, token, view, filter_name, filter_value,r"{}\temp_{}.pdf".format(file_loc, count), True)
                    count += 1
                    if (view_code == 1):
                        run = False
                        attempt+=1
                    else:
                        if attempt > 3:
                            run = False
                        else:
                            run = True
                            attempt+=1
                            break
                        
    gen_pdf_from_pdfs(file_loc, pdf_filename, count)


# ### Fn to iterate over views in list of views and save temp imgs, then call fn to insert imgs into a pdf
def iterate_views_as_imgs(site_id, token, view_ids, filter_names, filter_values, file_loc, datepart_filename):
    #print("\n\nBeginning to retrieve dashboards for {}".format(filter_value))
    run = True
    attempt = 0
    if len(filter_names) > 0:
        apply_filter = True
    else:
        apply_filter = False
        
    while (run == True):
        count = 1
        for view in view_ids:
            for filter_name in filter_names or []:
                for filter_value in filter_values or []:
                    view_code = query_view_image(site_id, token, view, filter_name, filter_value,r"{}\temp_{}.png".format(file_loc, count), apply_filter)
                    count += 1
                    if (view_code == 1):
                        run = False
                        attempt+=1
                    else:
                        if attempt > 3:
                            run = False
                        else:
                            run = True
                            attempt+=1
                            break
                        
    gen_pdf_from_imgs(file_loc, datepart_filename, count)


# ### Fn to find year and week number
def create_date_filename():
    week = int(datetime.date.today().strftime("%V"))
    if week == 1:
        week = 52
        year = int(datetime.date.today().strftime("%Y"))-1
        date_part_filename = {}
    else:
        week-=1
        year = int(datetime.date.today().strftime("%Y"))
    return "{}{}".format(year, week)


# ### Fn to check login method and sign into Server
def server_sign_in():
    if connection["server_connection"]["loginmethod"] == 'PAT':
        username = connection["PAT_auth_details"]["token"]
        if username == "":
            print("No username mentioned in config file!! Please enter username in config file and try again")
            exit()
        password = connection["PAT_auth_details"]["token_secret"]
        if password == "":
            password = getpass("Enter your PAT for the Tableau Server: ")
        site_id, token = sign_in_pat(username, password, site_content_url)
        if token == 0:
            print("ZERO TOKEN A")
            exit()
    elif connection["server_connection"]["loginmethod"] == 'Local':
        username = connection["local_auth_details"]["username"]
        if username == "":
            print("No username mentioned in config file!! Please enter username in config file and try again")
        password = connection["local_auth_details"]["password"]
        if password == "":
            password = getpass("Enter your password for the Tableau Server: ")
        site_id, token = sign_in(username, password, site_content_url)
        if token == 0:
            print("ZERO TOKEN B")
            exit()
    else:
        print("Incorrect login method specified in config file under server_connection > loginmethod! Login method has to be Local or PAT")
        exit()
    open_log(log_file)
    return site_id, token


# ## -- Generate PDF Fns --

# ### Fn to generate PDF from queried images (Praveen's code)
def gen_pdf_from_view_imgs():
    site_id, token = server_sign_in()
    
    #Find workbook id from name
    workbook_response = query_workbook_id(site_id, token, urllib.parse.quote_plus(config["workbook_details"]["workbookname"]))
    
    if (config['workbook_details']['filtername'] == ""):
        filter_names = [""]
        filter_values = [""]
        print("Iterating over views with no filters...")
    else:
        filter_names = gen_list(config['workbook_details']['filtername'])
        filter_values = gen_list(config['workbook_details']['applyfilters'])
        print("Iterating over views with filters applied...")
    
    datepart_filename = config["workbook_details"]["workbookname"] + ' - ' + create_date_filename()

    iterate_views_as_imgs(site_id, token, query_workbook_view_ids(site_id, token, workbook_response['workbooks']['workbook'][0]['id'], gen_list(config["workbook_details"]["viewnames"]))[0], filter_names, filter_values, config["workbook_details"]["download_loc"], datepart_filename)
    
    sign_out(site_id, token)
    
    return


# ### Fn to generate PDF from queried pdfs (Chris' code)
def gen_pdf_from_view_pdfs():
    site_id, token = server_sign_in()
    
    #Find workbook id from name
    workbook_response = query_workbook_id(site_id, token, urllib.parse.quote_plus(config["workbook_details"]["workbookname"]))
    
    Category = input('Which Company set of views do you want to export? Currys/Ikea/Staples - ')

    try:
        if Category == "":
            filter_names = [""]
            filter_values = [""]
            views_list = config["workbook_details"]["viewnames"]
            print("Iterating over views with no filters...")
        else:
            filter_names = gen_list(config[Category]['filtername'])
            filter_values = gen_list(config[Category]['applyfilters'])
            views_list = gen_list(config[Category]["viewnames"])
            print("Iterating over views with filters applied...")
    except KeyError:
        print("The following Company doesn\'t exist, or hasn\'t yet been configured - " + Category)
        print("Please try running the function again.")
        return
    except:
        print('Another error has occured, please try again.')
        return 

    pdf_filename = config["workbook_details"]["workbookname"] + ' - ' + Category + ' - ' + create_date_filename() + '.pdf'

    iterate_views_as_pdfs(site_id, token, query_workbook_view_ids(site_id, token, workbook_response['workbooks']['workbook'][0]['id'], views_list)[0], filter_names, filter_values, config["workbook_details"]["download_loc"], pdf_filename)
    
    sign_out(site_id, token)
    
    return


# ### Fn to generate PDF from whole workbook (Chris' code)
def gen_pdf_from_workbook():
    site_id, token = server_sign_in()
    
    #Find workbook id from name
    workbook_response = query_workbook_id(site_id, token, urllib.parse.quote_plus(config["workbook_details"]["workbookname"]))
    
    workbook_filename = config["workbook_details"]["workbookname"] + ' - ' + create_date_filename() + '.pdf'

    workbook_as_pdf(site_id, token, workbook_response['workbooks']['workbook'][0]['id'], config["workbook_details"]["download_loc"], workbook_filename)
    
    sign_out(site_id, token)
    
    return


# ## -- Calling generate functions --

# ### Generate pdf from images
#gen_pdf_from_view_imgs()


# ### Generate pdf from pdfs
#gen_pdf_from_view_pdfs()


# ### Generate pdf from workbook
# #### *Only downloads the last saved view in the workbook currently
#gen_pdf_from_workbook()
