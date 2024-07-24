"""
Sample python code for using gemini multimodal api to check the type of document that is submitted in a medical expense claim usecase
Only rest api call currently, does not use vertexai libraries.
For more quickstart samples and API and client SDK references, refer to
https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal
https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/inference#request

"""
import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Image

import base64
import requests
import google.auth
import google.auth.transport.requests
creds, project = google.auth.default()


# returns the prompt for checking type of documents that is submitted
def get_doctype_prompt():
    text = """
    Context:
    This is a document submitted as part of a medical claim process, the document may contain both English and Chinese information.
    The submitted document contains doctors' handwritten diagnostic, and itemized billing items on invoices with watermarks. 
    The document will have both English and Chinese information.
    
    Based on the information in this document please identify the type of document.
    Please describe the document, break it down into the different sections.
    Explain your decision

    Output:
    Return the information in plain text in json strictly in the following format
    Do not use markdown.
    {
    docTitle: <title of document>,
    organization: <name of organization, if available>
    docType: <doctype>,
    description: <description of docs>,
    explanation: <explain your decision>
    }
    """    
    return text

# returns the prompt extracting information from doc
# this prompt is not optimized but more for demo purposes
# TODO further refine prompt by checking doctype
def get_extractinfo_prompt():
    text = """
        this is a document submitted as part of a medical insurance expense claim. It includes a patient's clinical history , doctor's diagnosis and itemized billing items.
        It contains both handwritten and printed information
        1.  Extract the patient information
        2.  Extract the hospital admission and discharge dates; or date of visit.
        3.  Extract the diagnosis and operation / procedure performed?
        4.  Please extract all the information in the bill,  return them in table format
        5. Please extract all the information in the bill, return them in json format
        If the information is not clear or the image quality is bad, do not make things up
            """    
    return text


# returns the system instructions, this is a context / instruction for the model
def get_system_instructions():
    system_instruction_text = """
        You are an expert in recognizing handwritten and printed information in documents that are submitted for medical expenses claim.
    """
    return system_instruction_text

config = {}
model = None

# initialise configurations
# export PROJECT_ID=<your project id>
def init_config():
    config['project_id'] = os.environ['PROJECT_ID']
    config['model_id'] = "gemini-1.5-flash-001"
    config['location'] = 'us-central1'
    config['files_url'] = os.environ['FILES_URL']
    vertexai.init(project=get_config('project_id'), location=get_config('location'))
    print('configurations initialized')

def get_config(config_name):
    return config[config_name]

def get_model():
    model = GenerativeModel(get_config('model_id'),system_instruction=get_system_instructions()) 
    return model

# main method to determine the type of document that is submitted based on the contents
def check_document_type(name):
    print("checking document type for "+ name)

    pdf_file = Part.from_uri(get_config('files_url')+name, mime_type="application/pdf")

    response = get_model().generate_content(
        [
            pdf_file,
            get_doctype_prompt()
        ]
    )

    print(response.text)

    return response


# main method to extract informtion for the submitted documents
def extract_info(name):
    print(name+ ': Extract information')
    pdf_file = Part.from_uri(get_config('files_url')+name, mime_type="application/pdf")
    response = get_model().generate_content(
        [
            pdf_file,
            get_extractinfo_prompt()
        ]
    )

    # print(response.text)

    return response



## README: START HERE
# export PROJECT_ID=<your project id>
# For PDF files, the supported way is to reference it via Google Object Storage
# update your files into a GCS bucket, store the url to env , export FILES_URL=gs://my-bucket/
init_config()
# Update this file list 
# create a 'file_list.txt with a comma separated list of file names: bill 1.pdf,submission claim.pdf etc, this will be loaded into an array to be passed to the gemini api
# Load files
file = open('file_list.txt', 'r')
docs_file_name = file.read().split(',')


# comment off as needed

# uncomment this if you want to run the doctype check 
#"""
print("=========Check Document Type====================")
print("This is the prompt used to check document type")
print(get_doctype_prompt())
for file_name in docs_file_name:
    print('============================================================='+file_name)
    response = check_document_type(file_name)
    print('Output: ')
    json.loads(response.text)
    print(file_name + ' document type is: '+json.loads(response.text)['docType'])

#"""

# uncomment this if you want to extract info from the documents
"""
print("=========Extract Info====================")
print("This is the prompt used to extract document info")
print(get_extractinfo_prompt())
for file_name in docs_file_name:
    print('============================================================='+file_name)
    response = extract_info(file_name)
    print('Output: ')
    print(file_name + ' Extracted Info:')
    print(response.text)
"""

