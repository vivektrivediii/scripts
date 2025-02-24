###ec2-aler gui

import boto3
from datetime import datetime, timedelta, timezone
import requests
import pytz

# AWS and Slack configurations
REGION_NAME = 'us-east-1'  # Replace with your AWS region
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/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'

# Initialize Boto3 clients
ec2 = boto3.client('ec2', region_name=REGION_NAME)
cloudtrail = boto3.client('cloudtrail', region_name=REGION_NAME)

# Timezone configuration
IST = pytz.timezone('Asia/Kolkata')

# List of tag prefixes to whitelist
WHITELIST_TAG_PREFIXES = ['projectkraft', 'whitelist']

def get_running_instances():
    response = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            tags = instance.get('Tags', [])
            skip_instance = False
            for tag in tags:
                if tag['Key'] == 'projectname_personname_datecreated' and any(tag['Value'].startswith(prefix) for prefix in WHITELIST_TAG_PREFIXES):
                    skip_instance = True
                    break
            if not skip_instance:
                instances.append(instance)
    return instances

def check_instance_uptime(instance):
    launch_time = instance['LaunchTime']
    current_time = datetime.now(timezone.utc)
    uptime = current_time - launch_time
    return uptime

def get_user_from_event(instance_id, event_name):
    response = cloudtrail.lookup_events(
        LookupAttributes=[
            {'AttributeKey': 'ResourceName', 'AttributeValue': instance_id}
        ],
        MaxResults=5,
        StartTime=datetime.now(timezone.utc) - timedelta(days=90)
    )
    
    for event in response['Events']:
        if event_name in event['EventName']:
            return event['Username']
    return None

def get_instance_name(tags):
    for tag in tags:
        if tag['Key'].lower() == 'name':
            return tag['Value']
    return "Unknown"

def format_tags(tags):
    return ', '.join([f"{tag['Key']}: {tag['Value']}" for tag in tags]) if tags else "No tags"

# def send_slack_notification(instance_id, instance_name, instance_type, created_by, last_started_by, uptime_hours, tags):
#     tag_info = "\n".join([f"- {tag['Key']}: {tag['Value']}" for tag in tags]) if tags else "No tags available"
    
#     message = (
#         f"*AWS Instance Alert 🚨*\n"
#         f"> *Instance Name:* {instance_name}\n"
#         f"> *Instance ID:* `{instance_id}`\n"
#         f"> *Instance Type:* {instance_type}\n"
#         f"> *Uptime:* {uptime_hours} hours ⏳\n"
#     )
    
#     if created_by:
#         message += f"> *Created By:* {created_by} 👤\n"
#     if last_started_by:
#         message += f"> *Last Started By:* {last_started_by} 🔄\n"
    
#     message += f"> *Tags:*\n{tag_info}"
    
#     payload = {"text": message}
#     requests.post(SLACK_WEBHOOK_URL, json=payload)

def send_slack_notification(instance_id, instance_name, instance_type, created_by, last_started_by, uptime_hours, tags):
    message = (
         f"*AWS Instance Alert 🚨*\n"
        f"> *Instance Name:* {instance_name}\n"
        f"> *Instance ID:* `{instance_id}`\n"
        f"> *Instance Type:* {instance_type}\n"
        f"> *Uptime:* {uptime_hours} hours ⏳\n"
        # f"AWS Instance '{instance_name}' (ID: {instance_id}, Type: {instance_type}) has been running for more than 4 hours "
        # f"(Exact uptime: {uptime_hours} hours)."
    )
    if created_by:
        message += f"\nCreated by: {created_by}"
    if last_started_by:
        message += f"\nLast started by: {last_started_by}"
    message += f"\nTags: {tags}"
    
    payload = {"text": message}
    requests.post(SLACK_WEBHOOK_URL, json=payload)

def stop_instance(instance_id, instance_name):
    ec2.stop_instances(InstanceIds=[instance_id])
    print(f"Instance '{instance_name}' (ID: {instance_id}) has been stopped.")
    send_slack_notification(instance_id, instance_name, "Unknown", None, None, "Stopped by Administrator", "No tags")

def lambda_handler(event, context):
    instances = get_running_instances()
    for instance in instances:
        uptime = check_instance_uptime(instance)
        uptime_hours = uptime.total_seconds() // 3600
        if uptime >= timedelta(hours=4):
            instance_id = instance['InstanceId']
            instance_name = get_instance_name(instance.get('Tags', []))
            instance_type = instance['InstanceType']
            created_by = get_user_from_event(instance_id, 'RunInstances')
            last_started_by = get_user_from_event(instance_id, 'StartInstances')
            tags = format_tags(instance.get('Tags', []))
            send_slack_notification(instance_id, instance_name, instance_type, created_by, last_started_by, uptime_hours, tags)
            
            current_time_ist = datetime.now(IST).time()
            stop_time = datetime.strptime('22:00:00', '%H:%M:%S').time()
            if current_time_ist >= stop_time:
                should_stop = not any(
                    tag['Key'] == 'projectname_personname_datecreated' and any(tag['Value'].startswith(prefix) for prefix in WHITELIST_TAG_PREFIXES)
                    for tag in instance.get('Tags', [])
                )
                if should_stop:
                    stop_instance(instance_id, instance_name)

if __name__ == "__main__":
    lambda_handler(None, None)
