import requests,json
import base64,os
import csv
import time
import urllib.parse
import math
import sys
import os

# lines to change - 17 to 25




def initializeValues():
 global kf2_api_key,kf2_email_id,X_Access_Key_Id,X_Access_Key_Secret,kfdw_process_id,signature_field_ids,kf2_appspot_id,kfdw_domain,kfdw_account_id,root_folder,cookie,kf2_app_id,workflow_appspot,source_key_json_file,target_key_json_file
 root_folder=""
 kf2_api_key=""
 kf2_appspot_id=""
 kf2_email_id=""
 kf2_app_id=""
 cookie={"sessionid":"","WSID":""}
 X_Access_Key_Id=""
 X_Access_Key_Secret=""
 kfdw_domain=""
 kfdw_account_id=""
 zingworks=0
 workflow_appspot=("test.zingworks.com" if zingworks==1 else ("app" +".kissflow.com"))
 source_key_json_file={}
 target_key_json_file={}
 #headers={"X-Access-Key-Id" :X_Access_Key_Id,"X-Access-Key-Secret" : X_Access_Key_Secret }





def createFolder(folder_name):
 try:
   os.mkdir(folder_name)
   print(folder_name + "- created")
 except OSError:
  print ("Creation of the directory failed")    



def reduceToSignature(field):
 if field["Widget"]=="Signature":
  return field["Name"]	
 else:
  return None 


def readFormData(process_id):
 url="https://{0}.appspot.com/{1}/1/{2}/mobileform".format(kf2_appspot_id,kf2_app_id,process_id)
 print(url)
 r=requests.get(url,cookies=cookie)
 js=json.loads(r.text)
 print(r.status_code)
 return js


 
def writeToCsv(columns,data,filename):
 print("Creating File - " + filename)	
 with open(filename, 'w') as csvfile: 
  csvwriter = csv.writer(csvfile) 
  #csvwriter.writerow(columns) 
  csvwriter.writerows(data)


def createJsonFile(filename,data):
 print("Creating Json file - " + filename)		
 with open("{0}/{1}".format(root_folder,filename), 'w+') as jsonFile:
  jsonFile.write(json.dumps(data))


def getLiveProcessids():
 url="https://{0}/{1}/f/process?callback=angular.callbacks._8&showAll=true".format(workflow_appspot,kf2_app_id)
 print(url)
 r=requests.get(url,cookies=cookie)
 r=r.text.replace("angular.callbacks._8(","")[0:-1]
 js=json.loads(r)
 LiveIds=list(filter(None,list(map(lambda arr: None if ("Trash" in arr.keys() or "PublishedAt" not in arr.keys()) else ({"ModelId" : arr["ModelId"],"ProcessName" : arr["ProcessName"],"Process_Id" : arr["Name"]}),js))))
 print(str(len(LiveIds)) + " live processes found")
 return LiveIds




def getProcessInfo():
 createFolder(root_folder)	
 createFolder(root_folder+"/Kf2Signatures")	 
 process_list=getLiveProcessids()
 #print(process_list)
 print(len(process_list))
 for i in range(0,len(process_list)):
  form_data=readFormData(process_list[i]["ModelId"])
  process_list[i]["Signature_Field_ids"]=[]
  for section in form_data["Form"]:
   process_list[i]["Signature_Field_ids"].extend(list(filter(None,list(map(reduceToSignature,section["Fields"])))))
 createJsonFile("signature_meta.json",process_list)
 print("Metadata file creation completion")

 #urllib.parse.quote(process_json["ProcessName"])

def readRequests(process_json):
 if len(process_json["Signature_Field_ids"])>0:
  createFolder(root_folder+"/Kf2Signatures/" + process_json["Process_Id"])
  source_key_json_file[process_json["Process_Id"]]=[]
  length=1
  page=1
  index=0
  while length!=0:
   url="https://{0}.appspot.com/api/1/{1}/list/p{2}/200".format(kf2_appspot_id,process_json["ProcessName"].replace("/","%252F"),page)	
   headers={"api_key": kf2_api_key}
   r=requests.get(url,headers=headers)
   js=json.loads(r.text)
   print(str(r.status_code) + " - " + url)
   if r.status_code!=200:
   	print(r.text) 
   length=len(js)
   if length>0:
    page=page+1
    for request in js:
     tempJson={}
     tempJson["_id"]=request["Id"]
     for sign in process_json["Signature_Field_ids"]:
      if sign in request.keys() and request[sign][0:21]=="data:image/png;base64":	
   	   img_data=bytes(request[sign][22:],'utf-8')
   	   createFolder("{0}/Kf2Signatures/{1}/{2}".format(root_folder,process_json["Process_Id"],request["Id"]))
   	   path="{0}/Kf2Signatures/{1}/{2}/{3}.png".format(root_folder,process_json["Process_Id"],request["Id"],sign)
   	   with open(path,"wb") as fh:
   	    fh.write(base64.decodebytes(img_data))
   	    print(sign + ".png file created")
   	    tempJson[sign]=path

     if len(tempJson.keys())>1: 
      tempJson["index"]=index	
      source_key_json_file[process_json["Process_Id"]].append(tempJson)
      index=index+1
 		     


def readSignatureAndUpload():
 with open("{0}/{1}".format(root_folder,"signature_target_data.json"),"r") as target_file:
  target_key_json_file=json.loads(target_file.read()) 	
 process_list=None 
 with open("{0}/{1}".format(root_folder,"signature_source_data.json"),"r") as jsonFile:
  process_list=json.loads(jsonFile.read())
 for process in process_list.keys():
  print("Reading " + process +" Folder")
  if len(process_list[process])>0:
   if process not in target_key_json_file.keys():
    target_key_json_file[process]=[]	
   request_num=1
   total_request=len(process_list[process])
   i=total_request
   print("Found " + str(total_request) + " requests")
   while i!=-0:
    print("Reading {0} of {1} requests".format(request_num,str(total_request)))
    signature_count=1
    total_signature_fields=str(len(process_list[process][0].keys())-2)
    tempJson={}
    tempJson["_id"]=process_list[process][0]["_id"]
    for key in process_list[process][0].keys():
     if key!="_id" and key!="index":
      print("Reading {0} of {1} signature fields".format(signature_count,total_signature_fields))
      tempKey=uploadSignature(process,process_list[process][0]["_id"],key,process_list[process][0][key])
      tempJson[key]=tempKey
      signature_count=signature_count+1
    process_list[process].pop(0)
    target_key_json_file[process].append(tempJson)
    createJsonFile("signature_target_data.json",target_key_json_file)
    createJsonFile("signature_source_data.json",process_list)
    request_num=request_num+1
    i=i-1  
 


def uploadSignature(process_id,instance_id,signature_id,path):
 try:
  #time.sleep(2)
  url="https://{0}/upload/2/{1}/".format(kfdw_domain,kfdw_account_id)
  data={"name":signature_id,"size":os.stat(path).st_size,"key":"{0}/{1}/{2}.png".format(process_id,instance_id,signature_id)}
  headers={"X-Access-Key-Id" :X_Access_Key_Id,"X-Access-Key-Secret" : X_Access_Key_Secret,"content-type": "application/json"}
  r=requests.post(url,data=json.dumps(data),headers=headers)
  print(str(r.status_code) + "-" + url)
  js=json.loads(r.text)
  new_url=js["Url"]
  #time.sleep(2)
  with open(path,"rb") as fh:
   uploading_signature=fh.read()
   new_headers={"content-type": "image/png","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
   new_r=requests.put(new_url,data=uploading_signature,headers=new_headers)
   print(str(new_r.status_code)+ "-"+ new_url)
   if new_r.status_code==200 and r.status_code==200:
    return {"name": signature_id,"key":js["Key"]}
 except ConnectionError as e:
  print("Connection Terminated - Retrying.....")
  return uploadSignature(process_id,instance_id,signature_id,path) 	




def updateRequest(instance_id,key,process_id):
 url="https://{0}/process/2/{1}/admin/{2}/batch".format(kfdw_domain,kfdw_account_id,kfdw_process_id)
 headers={"X-Access-Key-Id" :X_Access_Key_Id,"X-Access-Key-Secret" : X_Access_Key_Secret,"content-type": "application/json"}
 data=[{"_id":instance_id,"Signature_1":{"name":"Signature_1","key":key}}]
 r=requests.post(url,data=json.dumps(data),headers=headers)
 print(r.text)
 print(r.status_code)



def updateBatchRequest(process_id,payload):
 url="https://{0}/process/2/{1}/admin/{2}/batch".format(kfdw_domain,kfdw_account_id,process_id)
 headers={"X-Access-Key-Id" :X_Access_Key_Id,"X-Access-Key-Secret" : X_Access_Key_Secret,"content-type": "application/json"}
 r=requests.post(url,data=json.dumps(payload),headers=headers)
 print("{0} - {1}".format(r.status_code,url))
 if r.status_code!=200: #and process_id!="Job_Order":
  print(r.text)
  print("Retrying Batch update....")
  updateBatchRequest(process_id,payload)


def readKeysandUpdate():
 with open(root_folder +"/signature_target_data.json","r") as file:
  file=json.loads(file.read())
  for process_id in file.keys():
   num=len(file[process_id])
   request_rate=100
   div=math.floor(num/request_rate)
   final=[100]*div + [num-(div*request_rate)]
   for i in range(0,len(final)):
    if i==0:
     final[i]=tuple([0,final[i]])
    else:
     final[i]=tuple([request_rate*(i),(request_rate*(i))+final[i]])  
   for custom_range in final:
    if len(file[process_id])>0:
     payload=file[process_id][custom_range[0]:custom_range[1]]
     print("Reading index {0} to {1}".format(custom_range[0],custom_range[1]))
     updateBatchRequest(process_id,payload)
  




def readAndStoreSignatures():
 process_list=[]	
 with open("{0}/{1}".format(root_folder,"signature_meta.json"),"r") as jsonFile:
  jsonFile=jsonFile.read()
  process_list=json.loads(jsonFile)	     
  for process in process_list:
   print("Reading process - " + process["ProcessName"])	
   readRequests(process)
  createJsonFile("signature_source_data.json",source_key_json_file)
  createJsonFile("signature_target_data.json",target_key_json_file)
 

def notification():
 if path.exists('data_sheet_completion_vibrate.wav') is False:  
  r=requests.get("https://soundbible.com/grab.php?id=1599&type=wav")
  with open("data_sheet_completion_vibrate.wav","wb") as file:
   file.write(r.content)
 os.system("afplay data_sheet_completion_vibrate.wav")  
 print("*********CSV files are ready to upload!!*********")  
 i=2
 while i:
  os.system("afplay data_sheet_completion_vibrate.wav")
  i-=1




def main(value):
 initializeValues()
 while(1):	
  print("-------------     Signature Upload  -------------")
  print("             1. Signature Meta download")
  print("             2. Download Signatures from 2.0")
  print("             3. Upload Signature")
  print("             4. Batch update requests")
  command=input() if value=="input" else value
  if command=="1":
   getProcessInfo()
  if command=="2":
   readAndStoreSignatures()
  if command=="3":
   readSignatureAndUpload()
   notification()
  if command=="4":
   readKeysandUpdate()  
  if command=="5":
   notification()
   sys.exit(0)
   #return "Hello"




args=sys.argv
if len(args)==1:
 main("input")
else:
 main(args[1]) 
