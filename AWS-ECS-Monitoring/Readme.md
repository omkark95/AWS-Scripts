## AWS ECS AGENT MONITORING
These are possible solutions created to monitor the ECS agent on a ECS cluster.

## Problem Statement:
Monitor the ECS agent on ECS cluster. Alert or drain the if the ECS agent fails/nolonger running on the ECS instance.

## Requirement Reason:
We have noticed that if a ECS cloudformation template is update it run every individual commands
in the cloudformation Metadata init of the Launch configuration.

In our case we have yum update and various other commands being executed causing the ECS agent to
lose connectivity with the ECS cluster causing the cluster to go down. This was a verify dumb mistake one which we quickly
realised and started working towards for solutions.

Also, on occasion this agent crashes, and this causes other services running on that instance to be inaccessible.

We looked at AWS Cloudwatch to setup monitor for ECS agent failure (ECS agent connected value shown in ECS cluster) but no luck there.
We were also using Datadog to monitor our infrastructure but it also did not have a monitor for the same.


## Solution:
There are 3 possible solutions which we have figured out for this issue:

## I. Python Monitoring

**OS** : Linux [Tested on AWS Linux] \n
**Requirement**
  1. Python

We fixed the issue by utilising configsets and setting up crontab for the python script to monitor the ECS agent and send slack alert.

We added slack alerts incase the ECS agent goes down. If the script detects that the ECS agent is down it would try
to restart the ECS once each min. Incase it passes it would send out slack alert stating the ECS agent has been restarted.
Incase it fails it would send the slack alert stating that the ECS agent failed.

For the script to be downloaded and placed in the crontab we need to do the following:
  1. Place all these files on a S3 folder or a remote directory from where they can be downloaded.
  2. Ideally download these files on the /tmp directory
  3. Change the type of the of slack.sh using `chmod +x /path/to/slack.sh`
  4. The script can added to crontab by either utilising cron-verification.py or by simply running the following commands \n
    4.1 To remove any existing ecsagent monitoring scripts. \n
      `crontab -l | grep -v 'ecsagent-montoring'  | crontab -` \n
    4.2 Add the new cron \n
      `(crontab -l ; echo "$(cat /path/to/cron-file)") | sort | uniq | crontab -`

Once the script is added to the crontab it will monitor ECS agent every minute and alert in case of ecs agent failure.

Both our failed and updated cloudformation template are available on this repository.

## II. Placing the instance in draining state and then terminating the same.

For this solution click [here](https://github.com/silinternational/ecs-agent-monitor).

## III. Monitor using BASH and send out SNS Alerts.

For this solution click [here](http://www.tothenew.com/blog/monitor-aws-ecs-agent-automatically-restart-agent-on-failure/)

## Ideal Solution:
We should ideally create a prebaked AMI which contains this cron to avoid the hassle and continuously monitor the ECS agent
but in our case we had to update the cloudformation to accommodate the changes for the first run atleast.
