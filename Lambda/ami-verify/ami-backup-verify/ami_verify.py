import boto3, datetime, sys, time, json, ast
from datetime import datetime
from datetime import timedelta

# Main function. Entrypoint for Lambda
def handler(event, context):

#Open backup file to get details for email, bucketname and html file
  configJsonString = ''
  with open('backup.json', 'r') as lines:
   for line in lines:
     configJsonString = configJsonString + line
  config = json.loads(configJsonString)

#Read file from S3 to get AMI List. Enter Bucket name.
  file_name = str(time.strftime("%d%m%y")+".txt")
  ec2client = boto3.client('ec2')
  s3Resource = boto3.client('s3')
  s3response = s3Resource.get_object(Bucket=config['bucketName'], Key=file_name)
  amiList = s3response['Body'].read().decode('utf-8')
  amiList = ast.literal_eval(amiList)


#Describe AMI to get its details store it in informationOfImagesList
  descImageResponse = ec2client.describe_images(ImageIds = amiList)
  informationOfImagesList = descImageResponse['Images']

  imageInformation = {}

#Parse the informationOfImagesList to get details for each individual AMI. Store details like Status, imageid(AMI Id), creation date, instance name and snapshot ids(List)
  for individualImage in informationOfImagesList:

   statusOfImage = individualImage['State']
   imageId = individualImage['ImageId']
   imageInformation[imageId] = {}

#Add details to the dictionary imageInformation. Convert datetime from GMT to IST.
   if statusOfImage == "available":

#Change the date from the server to IST
    creationDate = individualImage['CreationDate']
    creationDate = datetime.strptime(creationDate,'%Y-%m-%dT%H:%M:%S.%fZ')
    creationDate = creationDate + timedelta(hours=5, minutes=30)
    creationDate = creationDate.strftime('%Y-%m-%d-%H:%M:%S IST')

#Other details
    description = individualImage['Description']
    instanceName = description[(description.find('of')+2):(description.find('instanceId'))]

    snapshots = []

    imageInformation[imageId]["status"] = statusOfImage
    imageInformation[imageId]["creation_date"] = creationDate
    imageInformation[imageId]["instanceName"] = instanceName

#For loop to tag the snapshots.
    for elem in individualImage["BlockDeviceMappings"]:
     snapshots.append(elem["Ebs"]["SnapshotId"])
     createTagsResponse= ec2client.create_tags(
       Resources= [elem["Ebs"]["SnapshotId"]],
       Tags=[
        {
            'Key': 'Backup',
            'Value': 'True'
        },
        {
            'Key' : 'Retention',
            'Value': 'True'
        }
          ]
      )
    imageInformation[imageId]["snapshot_ids"] = snapshots


   else:

#Change the date from the server to IST
    creationDate = individualImage['CreationDate']
    creationDate = individualImage['CreationDate']
    creationDate = datetime.strftime(creationDate,'%Y-%m-%dT%H:%M:%S.%fZ')
    creationDate = creationDate + timedelta(hours=5, minutes=30)
    creationDate = creationDate.strptime('"%Y-%m-%d-%H:%M:%S IST"')

#Other Details
    description = individualImage['Description']
    instanceName = description[(description.find('of')+2):(description.find('instanceId'))]
    snapshots = []

    imageInformation[imageId]["status"] = statusOfImage
    imageInformation[imageId]["creation_date"] = creationDate
    imageInformation[imageId]["instanceName"] = instanceName


#Tag each snapshot_ids with given tags
    for elem in individualImage["BlockDeviceMappings"]:
     snapshots.append(elem["Ebs"]["SnapshotId"])
     createTagsResponse= ec2client.create_tags(
       Resources= [elem["Ebs"]["SnapshotId"]],
       Tags=[
        {
            'Key': 'Backup',
            'Value': 'True'
        },
        {
            'Key' : 'Retention',
            'Value': 'True'
        }
    ]
     )
    imageInformation[imageId]["snapshot_ids"] = snapshots

  email_sender(imageInformation)



def email_sender(informationOfBackups):

#Open backup file to get details for email and html file
  configJsonString = ''
  with open('backup.json', 'r') as lines:
   for line in lines:
     configJsonString = configJsonString + line
  config = json.loads(configJsonString)

#Open the HTML file to draft the email
  message = ''
  with open(config['htmlFile'],'r') as lines:
    for line in lines:
      message  = message + line


#Parse the informationOfBackups to get details to add to the email.
  for ami in informationOfBackups.keys():
    emailString = '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'%(informationOfBackups[ami]['instanceName'] , ami, informationOfBackups[ami]['snapshot_ids'] ,informationOfBackups[ami]['creation_date'], informationOfBackups[ami]['status'])
    message = message + emailString
  message = message + '</table></body></html>'


#Call the SES to send the email.
  client = boto3.client('ses',region_name= config['sesRegion'])
  response=  client.send_email(
  Source= config['sesFromAddress'],
       Destination= {
       'ToAddresses': config['sesToAdresses']
        },
       Message={
        'Subject':{
        'Data':'Backup notification.',
        'Charset':'utf-8'
        },
       'Body':{
         'Html':{
           'Data': message,
             'Charset':'utf-8'
            }
        }
      },
      ReplyToAddresses=[config['sesFromAddress']],
      ReturnPath= config['sesFromAddress'])

# Manual invocation of the script (only used for testing)
if __name__ == "__main__":
   # Test data
   test = {}
   test["config_file"] = "backup.json"
   # Test function
   handler(test, None)
