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

# returns the system instructions, this is a context / instruction for the model
def get_system_instructions():
    system_instruction_text = """
        You are an expert in recognizing handwritten and printed information in documents that are submitted for medical expenses claim.
    """
    return system_instruction_text

# construct a json request object for the rest api call
def construct_request_object(name):
    request_json = {}
    inlineData = {}
    # TODO, detect mime type using filename
    inlineData['mimeType'] = 'application/pdf'
    inlineData['data'] = get_document_bytes(name) # encoded pdf or image
    parts = []
    parts_object = {}
    parts_object['inlineData'] = inlineData
    parts_object_text = {}
    parts_object_text['text'] = get_doctype_prompt()
    parts.append(parts_object)
    parts.append(parts_object_text)

    contents = []
    contents_object = {}
    contents_object['role'] = 'user'
    contents_object['parts'] = parts
    contents.append(contents_object)

    system_instruction = {}
    system_instruction_parts = []
    system_instruction_parts_text = {}
    system_instruction_parts_text['text'] = get_system_instructions()
    system_instruction_parts.append(system_instruction_parts_text)

    system_instruction['parts'] = system_instruction_parts
    safety_settings = {}
    safety_settings['threshold'] = 'BLOCK_NONE'
    generation_config = {} # use default for now
    generation_config['responseMimeType'] = "text/plain"
    generation_config["maxOutputTokens"] = 2048 # 8192
    generation_config["temperature"] = 1
    generation_config["top_p"] =0.95
    request_json['contents'] = contents
    request_json['systemInstruction'] = system_instruction
    request_json['safety_settings'] = safety_settings
    request_json['generation_config'] = generation_config
    request = json.dumps(request_json)
    return request

config = {}
# initialise configurations
# export PROJECT_ID=<your project id>
def init_config():
    config['project_id'] = os.environ['PROJECT_ID']
    config['model_id'] = "gemini-1.5-flash-001"
    config['api_url'] = "https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/google/models/{model_id}:generateContent"
    print('configurations initialized')

def get_config(config_name):
    return config[config_name]

# main method to determine the type of document that is submitted based on the contents
def check_document_type(name):
    print("checking document type for "+ name)
    request = construct_request_object(name)
    # print(request)

    project_id = get_config('project_id')
    model_id = get_config('model_id')
    api_url = get_config('api_url')
    api_url = api_url.format(project_id=project_id, model_id=model_id)
    # print(api_url)
    # getting bearer token for REST API, if using SDK this is not needed
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    # print(creds.token)
    # Now you can use creds.token
    headers = {
        "Authorization": "Bearer " + creds.token,
        "Content-Type":"application/json"
    }
    response = requests.post(api_url, data=request, headers=headers)
    json_object = response.json()
    # print(response.json())
    # uncomment below if you wants to save the output json files
    """
    # save json output to a local file
    with open(name.replace(".","_").replace(" ","_")+'_gemini_'+model_id+'.json', 'w') as f:
        json.dump(response.json(), f, ensure_ascii=False)
    print("written json response to file")    
    """
    # printout results
    output = json_object['candidates'][0]['content']['parts'][0]['text']
    print(output)
    j = json.loads(output)
    # print(j['docType'])
    return j

# returns the bytes of the PDF file, for passing as parameter to the api
def get_document_bytes(name):
    with open(path + name, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read()).decode('UTF-8')
    return encoded_string

# main method to extract informtion for the submitted documents
def extract_info(name):
    print(name+ ' Extract information')
    # TODO 



## Main => START HERE
# export PROJECT_ID=<your project id>

init_config()
print("=========Check Document Type====================")
print("This is the prompt used to check document type")
print(get_doctype_prompt())
# Update this file list 
# create a 'file_list.txt with a comma separated list of file names: bill 1.pdf,submission claim.pdf etc
file = open('file_list.txt', 'r')
# this sample assumes all are pdf files, if there are different file types, change construct_request_object() to handle the mime_type
docs_file_name = file.read().split(',')

# Update this for your environment
path = "docs/"

for file_name in docs_file_name:
    print('============================================================='+file_name)
    response = check_document_type(file_name)
    print('Output: ')
    print(file_name + ' document type is: '+response['docType'])


