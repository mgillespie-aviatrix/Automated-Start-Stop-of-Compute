# Automated-Start-Stop-of-Compute
This repository contains a simple python script leveraging boto3 which can be deployed as a Lamba in AWS to automate the startup/shutdown of select EC2 instances on a scheduled basis. 

Included in this repository is a JSON IAM policy to apply to the lambda Execution Role (providing the requried access to describe regions and instances, as well as start/stop them)