#asas
import requests ,json
import csv 
import datetime as dt
import os
import os.path
from os import path
import time



#Lines to change - Line no: 13 to 18

def initialize_values(): 
 global appspot_id,app_id,cookie,application_id,final_steps,final_actions,step_id_list,action_id_list,workflow_depth_list,workflow_appspot,form_basic_info,master_meta_list,permission_list,permission_json,publish_check,admin_email,clarification_request_data,clarification_data_required,email_body,admin_webhook_check
 appspot_id=""
 app_id=""
 cookie={"sessionid":"","WSID":""}
 admin_email=""
 clarification_data_required=1
 publish_check=0
 workflow_appspot="app.kissflow.com"
 master_meta_list=[]
 permission_list=[]
 permission_json={}
 final_steps=[]
 form_basic_info=[]
 step_id_list=[]
 final_actions=[]
 action_id_list=[]
 workflow_depth_list=[]
 clarification_request_data=[] 
 email_body=[]
 admin_webhook_check="No"



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


def createFolder(folder_name):
 try:
   os.mkdir(folder_name)
   print(folder_name + "- created")
 except OSError:
  print ("Creation of the directory failed")    



def convert_unicode(val):
 if val is None:
  return None
 elif isinstance(val, float):
  return val
 elif isinstance(val, int):
  return val 
 elif str(type(val)) == "<class 'bytes'>":
  return str(val.decode('ascii'))[2:-1] 
 elif val.isascii(): 
  return str(val.encode("utf-8"))[2:-1] 
 else:
  return str(val) 




def convert_csv_data(data):
 for i in range(0,len(data)):
  data[i]=list(map(lambda x: convert_unicode(x),data[i]))
 return data



def getFIds():
 url="https://app.kissflow.com/{0}/f/process?callback=angular.callbacks._8&showAll=true".format(app_id)
 r=requests.get(url,cookies=cookie)
 print("{0} - {1}".format(r.status_code,url))
 r=r.text.replace("angular.callbacks._8(","")[0:-1]
 js=json.loads(r)
 LiveIds=list(filter(None,list(map(lambda arr: None if ("Trash" in arr.keys() or "PublishedAt" not in arr.keys()) else arr["Id"],js))))
 return LiveIds




def getLiveProcessids():
 url="https://app.kissflow.com/{0}/f/process?callback=angular.callbacks._8&showAll=true".format(app_id)
 r=requests.get(url,cookies=cookie)
 print("{0} - {1}".format(r.status_code,url))
 r=r.text.replace("angular.callbacks._8(","")[0:-1]
 js=json.loads(r)
 LiveIds=list(filter(None,list(map(lambda arr: None if ("Trash" in arr.keys() or "PublishedAt" not in arr.keys()) else arr["ModelId"],js))))
 print(str(len(LiveIds)) + " live processes found")
 return LiveIds



def readFormData(process_id):
 url="https://{0}.appspot.com/{1}/1/{2}/mobileform".format(appspot_id,app_id,process_id)
 r=requests.get(url,cookies=cookie)
 print("{0} - {1}".format(r.status_code,url))
 js=json.loads(r.text)
 return js


def readPublishPageInfo(Fid):
 url="https://{0}/{1}/1/{2}".format(workflow_appspot,app_id,Fid)
 r=requests.get(url,cookies=cookie)
 print("{0} - {1}".format(r.status_code,url))
 js=json.loads(r.text)
 return js

def xldate_to_datetime(xldate):
 temp = dt.datetime(1899,12,30) 
 delta = dt.timedelta(days=xldate)
 ist_offset=dt.timedelta(days=0.22916667)
 return temp+delta+ist_offset



def read_all_process_progress_info():
 if clarification_data_required==1: 
  url="https://{0}.appspot.com/{1}/1/appsummary/report/{2}".format(appspot_id,app_id,admin_email)
  r=requests.get(url,cookies=cookie)
  print("{0} - {1}".format(r.status_code,url))
  js=json.loads(r.text)
  inprogress_applications=list(filter(None,list(map(lambda process: process if process["Inprogress"]!=0 else None,js))))
  for application in inprogress_applications:
   read_clarification_data(application["Id"],application["Name"])
  writeToCsv([],clarification_request_data,"clarification_requests.csv") 


def read_clarification_data(model_id,process_name):
 print()  
 start_index=0
 result_length=1
 clarification_end=0
 while result_length!=0 and clarification_end!=1:
  url="https://{0}.appspot.com/{1}/1/apps/detailed/report/{2}?processId={3}&row=250&sort=-6&stage=1&start={4}&stepname=0&tagtype=appwise&totalrecord=250&type=In+Progress&usertype=normaluser".format(appspot_id,app_id,admin_email,model_id,start_index)
  r=requests.get(url,cookies=cookie)
  print("{0} - {1}".format(r.status_code,url))
  js=json.loads(r.text)
  result_length=len(js["resultset"])
  modified_result_set=list(filter(None,list(map(lambda request_list: request_list if request_list[5]=="Yes" else None,js["resultset"]))))
  if len(modified_result_set)!=result_length:
   clarification_end=1
  modified_result_set=list(map(lambda request_list: [request_list[0],request_list[1],str(xldate_to_datetime(request_list[2])),request_list[4],request_list[6],request_list[7]],modified_result_set))
  print(str(len(modified_result_set)) + " clarifications found")
  modified_result_set=list(map(attachProcess,modified_result_set,[process_name]*len(modified_result_set)))
  if len(modified_result_set)>0:
   clarification_request_data.extend(modified_result_set)
  start_index+=250
 



def getRequestCount(process_id):
 url="https://{0}.appspot.com/{1}/1/{2}/kpireport/wfsummary/split/2013-3-1/{3}".format(appspot_id,app_id,process_id,dt.datetime.now().strftime('%Y-%m-%d'))
 print(url)
 r=requests.get(url,cookies=cookie)
 js=json.loads(r.text)
 print(str(r.status_code) + " - Request count")
 return [js["Completed"],js["Open"],js["Rejected"],js["Withdrawn"],js["Total"]]



def sheetRowDefinition(fields):
 content=[]
 if fields["Widget"]=="Richtext":
  content=["RichTextField",fields["Id"],"RichText",None,None,None,None,None]
  return content
 content.append(fields["Name"])
 content.append(fields["Id"])
 if fields["Widget"]=="Singleline":
  content.append("Text")
 elif fields["Widget"]=="Multiline":
  content.append("Text Area")
 else:
  content.append(fields["Widget"])  
 if "Formula" in fields.keys():
  content.append(fields["Formula"])
 else: 
  content.append(None)
 if "MaxCharacters" in fields.keys():
  content.append(fields["MaxCharacters"])
 else: 
  content.append(None)
 if "DefaultValidation" in fields.keys():
  if "RegEx" in fields.keys():
   content.append(fields["DefaultValidation"]+ "  "+ fields["RegEx"])   
  else:
   content.append(fields["DefaultValidation"])
 else: 
  content.append(None)
  #Validation  step["SLA"] if "SLA" in step.keys() else None
 if "Validation" in fields.keys(): 
  content.append("\n".join(list(map(lambda validation: "{0}  {1}  {2}".format(validation["Operator"] if "Operator" in validation.keys() else None,validation["RHSType"]  if "RHSType" in validation.keys() else None,validation["RHS"] if "RHS" in validation.keys() else None),fields["Validation"]))))
 else: 
  content.append(None)
 if fields["Widget"]=="Dropdown" or fields["Widget"]=="Checkbox" or fields["Widget"]=="Lookup" or fields["Widget"]=="Masters":
  if fields["Widget"]=="Dropdown" or fields["Widget"]=="Checkbox":
   content.append(fields["Dropdown"] if "Dropdown" in fields.keys() else "Reference Missing")
  elif fields["Widget"]=="Lookup":
   content.append(fields["LookupProcess"] if "LookupProcess" in fields.keys() else "Reference Missing") 
  else:
   content.append(fields["LookupProcess"][3:] if "LookupProcess" in fields.keys() else "Reference Missing") 
 else: 
  content.append(None)
 return content


def readEachFormData():
 LiveIds=getLiveProcessids()
 finalContent=[]
 print("Reading Form data")
 for i in LiveIds:
  js=readFormData(i)
  print("Reading - " + (js["Label"] if js["Label"] is not None else js["Name"]))
  for sections in js["Form"]:
   #if sections["Type"]=="Section": 
   # finalContent.append([sections["Name"],sections["Id"],sections["Type"],None,None,None,None,js["Label"],sections["Type"],None,js["Id"]])
   #if sections["Type"]=="Table":
   # finalContent.append([sections["Name"],sections["Id"],sections["Type"],None,None,None,None,js["Label"],sections["Type"],None,js["Id"]])   
   sectionContent=list(map(sheetRowDefinition,sections["Fields"]))
   label_mapping=[js["Label"]]*len(sections["Fields"])
   section_type_mapping=[sections["Type"]]*len(sections["Fields"])
   model_id_mapping=[js["Id"]]*len(sections["Fields"])
   permission_mapping=[None]*len(sections["Fields"])
   newSectionContent=list(map(attachProcess,sectionContent,label_mapping))
   newSectionContent1=list(map(attachProcess,newSectionContent,section_type_mapping))
   newSectionContent2=list(map(attachProcess,newSectionContent1,permission_mapping))
   newSectionContentfinal=list(map(attachProcess,newSectionContent2,model_id_mapping))
   finalContent.extend(newSectionContentfinal)
 return finalContent
 



def writeToCsv(columns,data,filename):
 print("transforming data to unicode format....") 
 data=convert_csv_data(data)
 print("Creating File - " + filename) 
 with open("DataCsvs/"+filename, 'w') as csvfile: 
  csvwriter = csv.writer(csvfile) 
  #csvwriter.writerow(columns) 
  csvwriter.writerows(data)


def generateFormData():
 print("Generate FormData")
 data=readEachFormData()
 permissions()
 data=insertPermissioninFormData(data)
 writeToCsv(["Name","Widget Type","Formula","Max Characters","Default Validation" ,"Validation","Process Name"],data,"FormOutput.csv")




def attachProcess(arr,static_text):
 arr.append(static_text)
 return arr




def parseAssignTO(assignto):
 if "IsGroup" in assignto.keys():
  return "Group: {0}".format(assignto["EmailId"])
 else:
  return assignto["EmailId"]



def create_model_id_name_index():
 url="https://{0}/{1}/f/process?callback=angular.callbacks._8&showAll=true".format(workflow_appspot,app_id)
 r=requests.get(url,cookies=cookie)
 print("{0} - {1}".format(r.status_code,url))
 print("Creating process id & name index")
 r=r.text.replace("angular.callbacks._8(","")[0:-1]
 js=json.loads(r)
 LiveIds=list(filter(None,list(map(lambda arr: None if ("Trash" in arr.keys() or "PublishedAt" not in arr.keys()) else ({"ModelId" : arr["ModelId"],"ProcessName" : arr["ProcessName"],"Process_Id" : arr["Name"]}),js))))
 process_index_json={}
 for process in LiveIds:
  process_index_json[process["ModelId"]]=process["ProcessName"]
 return process_index_json





def kf1_webhooks():
 url="https://{0}.appspot.com/{1}/1/admin/webhooks".format(appspot_id,app_id)
 r=requests.get(url,cookies=cookie)
 print("{0} - {1}".format(r.status_code,url))
 js=json.loads(r.text)
 if len(js.keys())!=0:
  print(str(len(js.keys()))+" process's webhooks found from Kf version 1") 
  admin_webhook_check="Yes" 
  process_index_json=create_model_id_name_index()
  live_model_ids=getLiveProcessids()
  for model_id in js:
   if model_id in live_model_ids:
    for webhook in js[model_id]:
     final_actions.append(["Webhook","Kf1_webhook",model_id,process_index_json[model_id],"Kf1 webhook","Always",None,None,"-X-" + webhook + "-X-",None,None])
     
  


def stepData(step,process_name,model_id):
 
 if step["Type"]=="Start" or step["Type"]=="End":
  return None  


 final_output=[]
 if step["Type"]=="Approval" or step["Type"]=="ProvideInput":
  assignee="" 
  if "AssignTo" in step.keys():
   assignee=",".join(list(map(parseAssignTO,step["AssignTo"])))
  if "AssignFromField" in step.keys(): 
   assignee=step["AssignFromField"] 
  final_output=[step["Type"],step["Id"],model_id,process_name,step["Name"],step["SLA"] if "SLA" in step.keys() else None,step["ExecuteWhen"] if "ExecuteWhen" in step.keys() else "Always",assignee,None]   
  final_steps.append(final_output)
  step_id_list.append(step["Id"])
  return None


 if step["Type"]=="Goto":
  final_output=[step["Type"],step["Id"],model_id,process_name,step["Name"],None,step["ExecuteWhen"] if "ExecuteWhen" in step.keys() else "Always",None,step["Goto"]]
  final_steps.append(final_output)
  return None 
 

 if step["Type"]=="Webhook":
  final_output=[step["Type"],step["Id"],model_id,process_name,step["Name"],step["ExecuteWhen"] if "ExecuteWhen" in step.keys() else "Always",None,None,"-X-" + step["Webhook"][0]["Url"] + "-X-",None,None]
  final_actions.append(final_output)
  action_id_list.append(step["Id"])
  return None  
 

 if step["Type"]=="Email":
  assignee="" 
  if "To" in step["Email"][0].keys():
   assignee=",".join(list(map(parseAssignTO,step["Email"][0]["To"])))
  if "ToFromField" in step["Email"][0].keys(): 
   assignee=step["Email"][0]["ToFromField"] 
  if "Body" in (step["Email"][0]).keys():
   email_body.append([step["Id"],model_id,step["Email"][0]["Body"]])
  final_output=[step["Type"],step["Id"],model_id,process_name,step["Name"],step["ExecuteWhen"] if "ExecuteWhen" in step.keys() else "Always",assignee,None,None,None,None]
  final_actions.append(final_output)
  action_id_list.append(step["Id"])
  return None




 if step["Type"]=="StartNewItem" or step["Type"]=="StartMultipleItem":
  if "IsSubmit" in step.keys():
   if step["IsSubmit"]==1:
    final_output=[step["Type"],step["Id"],model_id,process_name,step["Name"],step["ExecuteWhen"] if "ExecuteWhen" in step.keys() else "Always",None,"Submit After Creation",None,step["ModelMapping"][0]["TargetModel"],None]
   else:  
    final_output=[step["Type"],step["Id"],model_id,process_name,step["Name"],step["ExecuteWhen"] if "ExecuteWhen" in step.keys() else "Always",None,"Create only",None,step["ModelMapping"][0]["TargetModel"],None]
  final_actions.append(final_output)
  action_id_list.append(step["Id"])  
  return None


 if step["Type"]=="UpdateItem" or step["Type"]=="UpdateMaster":
  final_output=[step["Type"],step["Id"],model_id,process_name,step["Name"],step["ExecuteWhen"] if "ExecuteWhen" in step.keys() else "Always",None,None,None,step["ModelMapping"][0]["TargetModel"],None]
  final_actions.append(final_output)
  action_id_list.append(step["Id"])
  return None  
  
 



def readWorkflow(Fid):
 url="https://{0}/{1}/1/{2}/step".format(workflow_appspot,app_id,Fid)
 r=requests.get(url,cookies=cookie)
 js=json.loads(r.text)
 print("{0} - {1}".format(r.status_code,url))
 #print(r.status_code)
 return js



def parseThroughWorkflow(steps,process_name,model_id):
 for step in steps:
  if "Branches" in step.keys():
   for branch in step["Branches"]:
    final_output=["Branch",branch["Id"],model_id,process_name,branch["Name"],None,branch["ExecuteWhen"] if "ExecuteWhen" in branch.keys() else "Always",None,None]
    final_steps.append(final_output)
    parseThroughWorkflow(branch["Steps"],process_name,model_id)
  else:   
   stepData(step,process_name,model_id) 



def generateWorkflowData():
 print("Generate Workflow") 
 ids=getFIds()
 for i in ids:
  workflowjson=readWorkflow(i)
  print("Reading - " + (workflowjson["Label"] if workflowjson["Label"] is not None else workflowjson["Name"] ))  
  parseThroughWorkflow(workflowjson["Steps"],workflowjson["Label"],workflowjson["ModelId"])
  js=readPublishPageInfo(i)
  form_basic_app=[workflowjson["ModelId"],workflowjson["Label"],flowDepth(workflowjson),js["Layout"] if "Layout" in js.keys() else False,js["IsPublicForm"] if "IsPublicForm" in js.keys() else False]
  form_basic_app.extend(getRequestCount(workflowjson["ModelId"]))
  form_basic_info.append(form_basic_app)
 findGotoPointers() 
 findSelfUpdateActions()
 kf1_webhooks()
 writeToCsv(["Type","Id","Process Name","Step Name","SLA","ExecuteWhen","AssignedTo","Goto"],final_steps,"WorkflowOutput.csv")
 writeToCsv(["Type","Id","Process Name","Action Name","ExecuteWhen","To","SubmitAfterCreation","WebhookUrl"],final_actions,"ActionOutput.csv")
 writeToCsv(["Id","App Name","Depth","One-Column Layout","Public Forms"],form_basic_info,"ProcessInfo.csv")




def findDepth(steps):
 depthlist=[]
 for step in steps:
  if "Branches" in step.keys():
   for branch in step["Branches"]:
    depthlist.append(1+findDepth(branch["Steps"]))
  else:
   depthlist.append(1)

 return max(depthlist) if depthlist else 0


def flowDepth(workflowjson):
 depth=findDepth(workflowjson["Steps"])
 return depth



def findSelfUpdateActions():
 for action in final_actions:
  target=action[9]
  if target==action[2]:
   action[10]="Yes"
 


def findGotoPointers():
 for step in final_steps:
  if step[-1] is not None:
   if step[-1] in step_id_list:
    step[-1] = step[-1] + " - Step"
   if step[-1] in action_id_list:
    step[-1] = step[-1] + " - Action"   



def generateMastersMeta():
 url="https://{0}.appspot.com/{1}/1/master".format(appspot_id,app_id)
 r=requests.get(url,cookies=cookie)
 print("{0} - {1}".format(r.status_code,url))
 js=json.loads(r.text)
 for master in js:
   master_meta_list.append([master["Id"],master["Name"],master["Columns"],"Master",read_master_data(master["Id"])])
 new_url="https://{0}.appspot.com/{1}/1/dropdown".format(appspot_id,app_id)
 new_r=requests.get(new_url,cookies=cookie)
 new_js=json.loads(new_r.text)
 for list_master in new_js:
   master_meta_list.append([list_master["Id"],list_master["Name"],None,"List",read_list_data(list_master["Id"])])  
 writeToCsv(None,master_meta_list,"masters_meta.csv") 




def read_master_data(master_id):
 url="https://{0}.appspot.com/{1}/1/master/{2}/export".format(appspot_id,app_id,master_id)
 r=requests.get(url,cookies=cookie,headers={"accept" : "application/json"})
 print("{0} - {1}".format(r.status_code,url))
 js=json.loads(r.text)
 if r.status_code==200:
  return len(js["data"])-1
 else:
  return "Error"  
 
 
def read_list_data(list_id):
 url="https://{0}.appspot.com/{1}/1/dropdown/{2}".format(appspot_id,app_id,list_id)
 r=requests.get(url,cookies=cookie)
 print("{0} - {1}".format(r.status_code,url))
 js=json.loads(r.text)
 return len(js["Values"]) if r.status_code==200 else "Error"
 



def parseThroughDefaultPermission(defaultPermissions):
 for items in defaultPermissions:
  finalpermission=[]  
  if items["Permission"]=="Conditional":
   finalpermission.append(items["For"])
   conditions=""
   for condition in items["Condition"]:
    lhs=(condition["LHS"] if ("LHS" in condition.keys() and condition["LHS"]!=None) else "MissingLHS")
    rhs=(condition["RHS"] if ("RHS" in condition.keys()  and condition["RHS"]!=None) else "MissingRHS")
    conditions+=lhs + " " + (condition["Operator"] if ("Operator" in condition.keys() and condition["Operator"]!=None)  else "MissingOperator") + " " +  (condition["RHSType"] if ("RHSType" in condition.keys() and condition["RHSType"]!=None)  else "MissingRHSType") + " " + rhs + "\n"
   finalpermission.append(conditions)
   permission_json[finalpermission[0]]=finalpermission[1]
   
  if items["Permission"]=="Invisible":  
   finalpermission=[items["For"],"Hidden"]
   permission_json[finalpermission[0]]=finalpermission[1]
  permission_list.append(finalpermission)

def readPermission(Fid):
 url="https://{0}/{1}/1/{2}/permission".format(workflow_appspot,app_id,Fid)
 r=requests.get(url,cookies=cookie)
 js=json.loads(r.text)
 print("{0} - {1}".format(r.status_code,url))
 return js


def permissions():
 ids=getFIds()
 for i in ids:
  permission=readPermission(i)
  parseThroughDefaultPermission(permission["Permission"]["Default"])


def insertPermissioninFormData(form_field_list):
 for field in form_field_list:
  if field[1] in permission_json.keys():
   field[10]=permission_json[field[1]]
 return form_field_list




def read_process_json():
 url="https://app.kissflow.com/{0}/f/process?callback=angular.callbacks._8&showAll=true".format(app_id)
 r=requests.get(url,cookies=cookie)
 r=r.text.replace("angular.callbacks._8(","")[0:-1]
 js=json.loads(r)
 LiveIds=list(filter(None,list(map(lambda arr: None if ("Trash" in arr.keys() or "PublishedAt" not in arr.keys()) else {"Id":arr["Id"], "ProcessName" : arr["ProcessName"]},js))))
 return LiveIds



def check_publish_status(callback_number,process_id):
 check_status_url="https://app.kissflow.com/ping?callback=angular.callbacks._{0}&invoke=checkProcessStatus&key={1}&wiztoken=".format(str(callback_number),process_id)
 r=requests.get(check_status_url,cookies=cookie)
 print("{0} - {1}".format(r.status_code,check_status_url))
 if r.status_code!=200:
  print("Status check Failed Retrying")
  time.sleep(2)
  check_publish_status(callback_number,process_id)



def initiate_publish(process_id):
 batch_update_url="https://app.kissflow.com/{0}/1/{1}?batchData=%7B%7D".format(app_id,process_id)
 r=requests.put(batch_update_url,cookies=cookie)
 print("{0} - {1}".format(r.status_code,batch_update_url))
 init_publish_url ="https://app.kissflow.com/{0}/1/{1}/publish?requestType=async".format(app_id,process_id)
 r=requests.post(init_publish_url,cookies=cookie,data={"WIZ_HOST":"app.kissflow.com"},headers={"content-type": "application/json"})
 print("{0} - {1}".format(r.status_code,init_publish_url))
 print(r.text)
 print("checking publish status...")
 time.sleep(3)
 for callback_number in [2,3,4,5]:
  check_publish_status(callback_number,process_id)




def app_publish():
 if publish_check==1:
  process_list=read_process_json()
  for process_json in process_list:
   print("Triggering publish for process - "+ process_json["ProcessName"])
   initiate_publish(process_json["Id"])



def email_body_table_check():
 writeToCsv([],email_body,"email_action_table.csv")  
 tables_in_email=sum(list(filter(None,list(map(lambda email: 1 if (email[2].find("<table")>-1 or email[2].find("</table>")>-1) else None ,email_body)))))
 print(tables_in_email)
 return ["Emails in Table",tables_in_email]
  



def kf2_get_holidays():
 url="https://{0}.appspot.com/{1}/1/holidays".format(appspot_id,app_id)
 r=requests.get(url,cookies=cookie)
 print("{0} - {1}".format(r.status_code,url))
 js=json.loads(r.text)
 final_list_holidays=list(filter(lambda holiday:dt.datetime.now()<dt.datetime(int(holiday["date"][0:4]),int(holiday["date"][5:7]),int(holiday["date"][8:10])),js))
 return len(final_list_holidays)


def transform_holiday_name(day):
 js={"wed": "Wednesday", "sun": "Sunday", "fri": "Friday", "tue": "Tuesday", "mon": "Monday", "thu": "Thursday", "sat": "Saturday"}
 return js[day]


def get_work_hours_info():
 url="https://{0}.appspot.com/{1}/1/worktimings".format(appspot_id,app_id)
 r=requests.get(url,cookies=cookie)
 print("{0} - {1}".format(r.status_code,url))
 js=json.loads(r.text)
 url_1="https://{0}.appspot.com/{1}/2/worktimings".format(appspot_id,app_id)
 r_1=requests.get(url_1,cookies=cookie)
 print("{0} - {1}".format(r_1.status_code,url_1))
 js_1=json.loads(r_1.text)
 return ["Work Hours",js,js_1]
 



def app_specific_notification():
 url="https://{0}.appspot.com/{1}/1/admin/mailpreference?processOrGlobal=Process".format(appspot_id,app_id)
 r=requests.get(url,cookies=cookie)
 print("{0} - {1}".format(r.status_code,url))
 js=json.loads(r.text)
 return ["App specific notifications",(len(js) if len(js)>0 else "None")]




def generate_main_sheet():
 total_output=[]
 url="https://{0}.appspot.com/{1}/1/admin/company".format(appspot_id,app_id)
 r=requests.get(url,cookies=cookie)
 print("{0} - {1}".format(r.status_code,url))
 js=json.loads(r.text)
 total_output.append(["Company Name" ,js["CompanyName"]])
 total_output.append(["Plan Type" ,js["AccountType"]])
 total_output.append(["Appspot Id" ,appspot_id])
 total_output.append(["Application Id" ,app_id])
 total_output.append(["Public Form Data" ,js["PublicForm"]])
 preference=json.loads(js["Preference"])
 total_output.append(["Locale" ,js["Locale"]])
 total_output.append(["Disable Reassign" ,"Yes" if ("user-reassign" in preference.keys() and "disable" in preference["user-reassign"].keys()) else "No"])
 total_output.append(["Disable Withdraw" ,"Yes" if ("user-withdraw" in preference.keys() and "disable" in preference["user-withdraw"].keys()) else "No"])
 total_output.append(["Google Attachments" ,"Yes" if ("attachment" in preference.keys() and "NoDrive" in preference["attachment"].keys()) else "No"])
 total_output.append(["Default Attachments" ,"Yes" if ("attachment" in preference.keys() and "disable" in preference["attachment"].keys()) else "No"])
 total_output.append(["SAML Authentication", "Yes" if ("authentication" in preference.keys() and preference["authentication"] is not None) else "No"])
 
 url="https://{0}.appspot.com/{1}/1/weekday".format(appspot_id,app_id)
 r=requests.get(url,cookies=cookie)
 print("{0} - {1}".format(r.status_code,url))
 js=json.loads(r.text)
 if "work_timings" in js.keys() and js["work_timings"]!="No data found":
  weekends=[day for day in js["work_timings"].keys() if js["work_timings"][day]==True]  
  weekends=",".join(list(map(transform_holiday_name,weekends)))
  total_output.append(["Weekends",weekends])
 else:
  total_output.append(["Weekends","Error"]) 
 total_output.append(["Future Holidays",kf2_get_holidays()])
 total_output.append(get_work_hours_info())
 total_output.append(app_specific_notification())
 total_output.append(email_body_table_check())
 total_output.append(["Admin Webhooks" ,admin_webhook_check])
 with open("DataCsvs/"+"main.csv", 'w') as csvfile: 
  csvwriter = csv.writer(csvfile) 
  csvwriter.writerows(total_output)





def main():
 initialize_values()
 app_publish()
 createFolder("DataCsvs")
 generateFormData()
 generateWorkflowData()
 generateMastersMeta()
 read_all_process_progress_info()
 generate_main_sheet()
 notification()

main()
