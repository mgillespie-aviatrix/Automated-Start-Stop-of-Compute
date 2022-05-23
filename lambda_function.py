#This lambda function utilizes the boto3 python module for AWS.
# The function iterates over every available region in AWS searching for running EC2 instances that have been
# tagged by the end user for regular daily shutdown. Once found, it will simply start or stop the EC2 instance depending upon the JSON payload sent to the function.
#
# @author: Matthew Gillespie
# @date: 2021-05-10

import json 
import boto3
import time

def lambda_handler(event,context):
    ec2 = boto3.client('ec2')
    region_lookup = ec2.describe_regions()
    response_dict = {}

    #Check received JSON payload to determine requested action (start or stop ec2 instances)
    action = event.get('operation')
    
    if action is None:
        response_dict["status_code"] = 400
        response_dict["message"] = "No operation received"
        return response_dict
    elif action not in ['start', 'stop']:
        response_dict["status_code"] = 400
        response_dict["message"] = "Operation is unknown (not start or stop)"
        return response_dict

    #Next, loop through all of the available regions to ensure we address all instances.
    for r in region_lookup['Regions']:

        #Search for ec2 instances in the region for our defined tag. 
        filters=[{'Name' : 'tag:Automated-Shutdown-Enabled', 'Values': ['true']}]
        ec2_lookup = boto3.resource('ec2', region_name=r['RegionName'])
        instances = ec2_lookup.instances.filter(Filters=filters)
        
        #Loop through each instance matching the "Automated-Shutdown-Enabled = true" tag.
        for i in instances:
            #Determine name tag for this instance.
            instance_name = "Unnamed Instance"
            for tag in i.tags:
                if 'Name' in tag['Key']:
                    instance_name = tag['Value']
                    break
                
            #We establish a dict to report back to the end-user the before/after state of each VM.
            instance_dict = {}
            instance_dict["id"] = i.id
            instance_dict["name"] = instance_name
            instance_dict["previous_state"] = i.state
            
            if action == "start":
                i.start()
            else:
                i.stop()
                
            time.sleep(1)
            instance_dict["new_state"] = i.state
            response_dict[i.id] = instance_dict
            
    
    response_dict["status_code"] = 200
    return response_dict
