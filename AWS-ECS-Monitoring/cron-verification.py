import commands, re

all_current_cron=[]
new_crons=[]

def check_cron_file():
    try:
        #Get current cron list and strip it for comparision.
        current_cron_list = commands.getstatusoutput('crontab -l')
        current_crons=current_cron_list[1].split('\n')
        current_cron = filter(None, current_crons)
        for i in current_cron:
          all_current_cron.append(re.sub(r'\**\/*\d*\**', r'',i).lstrip())
        print all_current_cron



        #Get new cron file from s3 and copy it to a list
        new_cron_file = open('/tmp/cron-file', 'r')
        new_cron_file = new_cron_file.read()
        new_cron_file_crons = new_cron_file.split('\n')
        new_cron_file_crons = filter(None, new_cron_file_crons)

        for i in new_cron_file_crons:
          new_crons.append(re.sub(r'\**\/*\d*\**', r'',i).lstrip())
        print new_crons

        #Convert it to set and add the new
        new_crons_to_add = set(all_current_cron)
        old_len=len(new_crons_to_add)
        for new in new_crons:
            new_crons_to_add.add(new)

        new_len=len(new_crons_to_add)

        if old_len == new_len:
            pass
        else:
            adding_to_cron = "echo \"$(cat /tmp/cron-file; crontab -l)\" | crontab -"
            commands.getstatusoutput(adding_to_cron)

    except Exception as e:
        print e

check_cron_file()
