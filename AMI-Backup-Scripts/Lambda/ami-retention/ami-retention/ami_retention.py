import boto3, datetime, sys, time, json
from datetime import datetime
from datetime import timedelta


def handler(event, context):

#Open the retention file to get the retention filter
	configJsonString = ''
	with open('retention.json', 'r') as lines:
		for line in lines:
			configJsonString = configJsonString + line
	config = json.loads(configJsonString)

#Get an EC2 Client
	client = boto3.client(
		'ec2',
		region_name=config['region']
	)

	snapshotsToBeDeleted = []

#Get a list of images based on the filter
	response = client.describe_images(Filters=config['retentionFilter'])
	
#Parse the response to get the creation date, AMI id, snapshot id	
	for i in range(len(response['Images'])):
		name = response['Images'][i]['Name']
		timeNow = datetime.now()
		timeOfCreation = response['Images'][i]['CreationDate']
		timeOfCreation = datetime.strptime(timeOfCreation,'%Y-%m-%dT%H:%M:%S.%fZ')
		
		if (timeNow - timeOfCreation).days >= config['retentionDays']:
			deregisterImageResponse = client.deregister_image(ImageId=response['Images'][i]['ImageId'])
			
			# Each AMI can have multiple snapshots 	
			for k in range(len(response['Images'][i]['BlockDeviceMappings'])):
				try:
					deleteSnapshotResponse = client.delete_snapshot(SnapshotId=response['Images'][i]['BlockDeviceMappings'][k]['Ebs']['SnapshotId'])
					
				except KeyError:
					print "Error : Invalid key error"



if __name__ == "__main__":
# Test data
	test = {}
	test["config_file"] = "retention.json"
# Test function
	handler(test, None)
	