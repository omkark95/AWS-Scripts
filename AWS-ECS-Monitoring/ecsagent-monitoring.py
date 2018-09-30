import commands, socket


def ecsagent_status(command_to_check_ecs_agent, hostname):
    ecs_agent_status_execute = commands.getstatusoutput(command_to_check_ecs_agent)
    if ecs_agent_status_execute[0] != 0:
        command_for_alerts = "/bin/bash -c 'INSTANCE_EVENT=\"ECS agent is not running\" \
        INSTANCE_DESCRIPTION=\"Trying to restart ECS agent.\" INSTANCE_HOST=" + hostname + " INSTANCE_DATE=`date -R` \
        /tmp/slack.sh\'"
        output = commands.getstatusoutput(command_for_alerts)
        print output

hostname = socket.gethostname()
command_to_check_ecs_agent = 'docker top ecs-agent'

try:
    ecsagent_status(command_to_check_ecs_agent, hostname)
except Exception as e:
    print e
