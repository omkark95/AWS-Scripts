import boto3, datetime, sys, time, json, re

# Main function. Entrypoint for Lambda
def handler(event, context):
 configJsonString = ''

#open the json file to get the parameters like region, backupFilter, tags for backup, sesRegion, sesFromAddress and sesToAdresses
 with open('backup.json', 'r') as lines:
   for line in lines:
     configJsonString = configJsonString + line
 config = json.loads(configJsonString)
 client = boto3.client(
     'ec2',
     region_name= config['region']
 )


#Getting details for all running Instances in a region
 response= client.describe_instances(Filters=config['backupFilter'])

#Parsing through JSON response to get details for InstanceId, Tag values
 for i in range(len(response['Reservations'])):

   #extract instanceid
   for j in range(len(response['Reservations'][i]['Instances'])):
     startTime = str(datetime.datetime.now())
     instanceId= response['Reservations'][i]['Instances'][j]['InstanceId']

     #extract Instance name
     for k in range(len(response['Reservations'][i]['Instances'][j]['Tags'])):
       if(response['Reservations'][i]['Instances'][j]['Tags'][k]['Key']=='Name'):
         nameTagValue = response['Reservations'][i]['Instances'][j]['Tags'][k]['Value']
         nameTagValue = re.sub(r'[\!\@\#\$\%\^\&\*\{\}\|\:\;\"\'\<\>\?\[\] ]', r'-', nameTagValue)

     #give amiName and remove special charaters and limit the length
     amiName= str(nameTagValue + "-" + time.strftime("%d%m%y-%H-%M-%S"))
     amiName = re.sub(r'[\!\@\#\$\%\^\&\*\{\}\|\:\;\"\'\<\>\?\[\] ]', r'-', amiName)
     if len(amiName) > 127:
         amiName = amiName[:127]
     createImageResponse= client.create_image(
         InstanceId= instanceId,
         NoReboot= True,
         Name= amiName,
         Description= "Backup of " + nameTagValue + " instanceId : " + instanceId
     )

     imageId= createImageResponse['ImageId']
     imageList.append(imageId)
     resourcesToBeTagged= []
     resourcesToBeTagged.append(imageId)
     tags = response['Reservations'][i]['Instances'][j]['Tags']
     for k in range(len(config['tagsForTheBackup'])):
       tags.append(config['tagsForTheBackup'][k])
     createTagsResponse= client.create_tags(
       Resources= resourcesToBeTagged,
       Tags= tags
     )
 imageList = str(imageList)
 s3Resource = boto3.resource('s3')
 file_name = str(time.strftime("%d%m%y")+".txt")
 object = s3Resource.Object(config['bucketName'], file_name)
 object.put(Body=imageList)

# Manual invocation of the script (only used for testing)
if __name__ == "__main__":
   # Test data
   test = {}
   test["config_file"] = "backup.json"
   # Test function
   handler(test, None)
