# AMI BACKUP SCRIPT to be used with AWS Lambda

***UPDATE THE BUCKET NAME AS PER YOUR NEEDS***

When setting up an EC2 instance (cc-monitor) is not possible in the client account but want to take AMI backup of the account, the following solution can be helpful.
We have made 3 lambdas to initiate, verify and retain backups for the EC2 instances.

1.  The first lambda requests for all EC2 instaces matching the filter and creates AMI and snapshots for them.
    Then it stores the list of AMI created in an intermediate S3 bucket.

2.  The second lambda reads the list of AMI created(from intermediate S3 bucket), verifies its creation, snapshots creation and
    adds necessary tags to it. Then it creates an consolidated email which contains server name, AMI, volume snapshot, creation time and status for the AMI and snapshot.

3.  The third lambda runs a retention script based on retention filter in retention.json. This will delete AMI not satisfying the
    retention days.

This is a generic script which uses the json file placed in the same folder to get the EC2 region, and details about EC2
instances using the specified filter mentioned in it.

* 'backup.json' file contains the filter and the EC2 region

The filters could be changed to meet your requirements to filter your requirements.

* Region where you want to run the backup function is placed in this.
    "region":"ec2-region"

* Backup filter is placed here which would be used to decribe the instace.
    "backupFilter":[{"Name":"Tag which you would like to filter","Values":"Value for the tag"}],

* These would be the tags which would be applied on the new AMI created.
    "tagsForTheBackup":[{"Key":"Tag which you would like to add" , "Value":"Value for the tag"}]

* We get details and update files in S3 which acts as a interface between 2 lambda
