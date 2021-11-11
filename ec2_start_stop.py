import boto3
import sys
import os
import time

os.environ['AWS_SHARED_CREDENTIALS_FILE']='./cred' 
my_region='us-east-1' #region in which you lauch your instance
master_inst_id= "###############" # give your master instance id from which you launch other instances 

ec2=boto3.resource('ec2',my_region)
ec2_client=boto3.client('ec2',my_region)
security_groups=['SSH_1']

# creates r number of ec2 instances from the image ID
def create(r):
	ec2.create_instances(ImageId='ami-###############', #ami-image id
		MinCount=1,
		MaxCount=r,
         	InstanceType='t2.micro',
         	KeyName='us-east-1kp',
         	SecurityGroupIds=security_groups);
         	
def get_ec2_for_my_region():
	ec2_con_re=boto3.resource('ec2',region_name=my_region)
	return ec2_con_re
	
def list_instances_on_my_region(ec2_con_re):
	list_inst_id=[]
	for each in ec2_con_re.instances.all():
		if each.id!=master_inst_id:
			pr_st=get_instance_state(ec2_con_re,each.id)
			if pr_st !="terminated":
				list_inst_id.append(each.id)
	return list_inst_id
	
def get_instance_state(ec2_con_re,in_id):
	for each in ec2_con_re.instances.filter(Filters=[{'Name':'instance-id',"Values":[in_id]}]):
		pr_st=each.state['Name']
	return pr_st

def start_instance(ec2_con_re,in_id):
	pr_st=get_instance_state(ec2_con_re,in_id)
	if pr_st=="running":
		print ("instance is already running")
	else:
		for each in ec2_con_re.instances.filter(Filters=[{'Name':'instance-id',"Values":[in_id]}]):
			each.start()
			each.wait_until_running()
			print ("now it is running")

def get_public_ip(list_inst_id):
	list_public_ip=[]
	for instance_id in list_inst_id:
		reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")
		for reservation in reservations:
	        	for instance in reservation['Instances']:
            			list_public_ip.append(instance.get("PublicIpAddress"))
	return list_public_ip

def stop(list_inst_id):
	ec2.instances.filter(InstanceIds=list_inst_id).stop()
	
def terminate(list_inst_id):
	ec2.instances.filter(InstanceIds=list_inst_id).terminate()
	
