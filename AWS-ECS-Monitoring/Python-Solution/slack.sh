#!/bin/bash
URL=$(cat /path/to/slack-url)

COLOR=${INSTANCE_COLOR:-$([[ $INSTANCE_EVENT == *"succeeded"* ]] && echo good || echo danger)}
TEXT=$(echo -e "$INSTANCE_EVENT: $INSTANCE_DESCRIPTION" | python -c "import json,sys;print(json.dumps(sys.stdin.read()))")

# Send slack alert that the ECS agent has failed
PAYLOAD="{
  \"attachments\": [
    {
      \"text\": $TEXT,
      \"color\": \"$COLOR\",
      \"mrkdwn_in\": [\"text\"],
      \"fields\": [
        { \"title\": \"Date\", \"value\": \"$INSTANCE_DATE\", \"short\": true },
        { \"title\": \"Host\", \"value\": \"$INSTANCE_HOST\", \"short\": true }
      ]
    }
  ]
}"

curl -s -X POST --data-urlencode "payload=$PAYLOAD" $URL

#Try to restart the ECS agent. If restart is successful send the successful alert else send the 2nd notification
sudo stop ecs
sleep 5
sudo start ecs
RESTART_STATUS=$?

#Check restart status
if [ $RESTART_STATUS == "0" ]
then
  PAYLOAD="{
    \"attachments\": [
      {
        \"text\": \"ECS agent restarted successfully.\",
        \"color\": \"good\",
        \"mrkdwn_in\": [\"text\"],
        \"fields\": [
          { \"title\": \"Date\", \"value\": \"$INSTANCE_DATE\", \"short\": true },
          { \"title\": \"Host\", \"value\": \"$INSTANCE_HOST\", \"short\": true }
        ]
      }
    ]
  }"
else
  PAYLOAD="{
    \"attachments\": [
      {
        \"text\": \"ECS agent could not be restarted. Please look into this and perform manual restart.\",
        \"color\": \"danger\",
        \"mrkdwn_in\": [\"text\"],
        \"fields\": [
          { \"title\": \"Date\", \"value\": \"$INSTANCE_DATE\", \"short\": true },
          { \"title\": \"Host\", \"value\": \"$INSTANCE_HOST\", \"short\": true }
        ]
      }
    ]
  }"
fi
curl -s -X POST --data-urlencode "payload=$PAYLOAD" $URL
