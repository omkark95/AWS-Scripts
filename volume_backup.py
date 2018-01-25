#HOW To Use:
# python filename.py --volume-id volumename --region regionname

#example: python volume_backup.py --volume-id vol-043c6a5065d363121 --region ap-south-1


import sys, boto3, argparse

parser = argparse.ArgumentParser(description='Parse input params.')
parser.add_argument('--volume-id', dest='volumeid', type=str, required=True,
                    help='Volume ID to backup')
parser.add_argument('--region', dest='region', type=str, required=True,
                    help='sum the integers (default: find the max)')

args = parser.parse_args()


def volumebackup():

 client = boto3.client('ec2', region_name=args.region)
 volumeResponse = client.describe_volumes(VolumeIds=[args.volumeid])

 #Parsing through the Metadata and HTTPHeaders to get the Server Date time. [Day, DD Month YYYY HH:MM:SS TIMEZONE]
 date = volumeResponse['ResponseMetadata']['HTTPHeaders']['date']

 #Parsing through Volumes list to get the Tag values for the volume to retrive its name.
 valueInTag = volumeResponse['Volumes'][0]['Tags']
 name = valueInTag[0]
 name = name['Value']

 description = name + date
 response = client.create_snapshot(Description=description, VolumeId=args.volumeid)
 print response

print "Snapshot process started for Volume ID: "+args.volumeid
volumebackup()
