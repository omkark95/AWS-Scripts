import commands, socket

# Function to check the ECS agent status. If failed run the bash script to send slack alert.
def ecsagent_status(command_to_check_ecs_agent, hostname):
    ecs_agent_status_execute = commands.getstatusoutput(command_to_check_ecs_agent)
    if ecs_agent_status_execute[0] != 0:
        command_for_alerts = "/bin/bash -c 'INSTANCE_EVENT=\"ECS agent is not running\" \
        INSTANCE_DESCRIPTION=\"Trying to restart ECS agent.\" INSTANCE_HOST=" + hostname + " INSTANCE_DATE=`date -R` \
        /path/to/slack.sh\'"
        output = commands.getstatusoutput(command_for_alerts)
        print output
    else:
        pass

# Hostname would consist of the IP(for our case) you can modify the same as per your requirement
hostname = socket.gethostname()
command_to_check_ecs_agent = 'docker top ecs-agent'


try:
    ecsagent_status(command_to_check_ecs_agent, hostname)
except Exception as e:
    print e
