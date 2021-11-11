# Note: This code is lambda function B, and is used for read/write to s3
import json
import boto3

def lambda_handler(event, context):
    s3=boto3.client('s3')
    bucket='bucketcoursework' #name of s3 bucket
    input=(event['key1'])
    input=input.split(",")
    choice=int(input[0])
    #choice=1, then write to S3    
    if(choice==1):
        shots=int(input[1])
        q=int(input[2])
        digits=int(input[3])
        r=int(input[4])
        estimated_pi=float(input[5])
        cost=float(input[6])
        service=str(input[7])
        json_string={"Shots":shots,"Reporting_Rate":q,"Digits":digits,"Resources":r,"Estimated_pi":estimated_pi,"Cost":cost,"Service":service}
        file_name="Pi_est"+"_"+str(shots)+"_"+str(q)+"_"+str(digits)+"_"+str(r)+"_"+str(service)+".json"
        json_data=bytes(json.dumps(json_string).encode('UTF-8'))
        s3.put_object(Bucket=bucket,Key=file_name,Body=json_data)
    #if choice=2, then read from S3 
    if(choice==2):
        s3=boto3.resource('s3')
        bucket=s3.Bucket('bucketcoursework')
        result=[]
        for obj in bucket.objects.all():
            key=obj.key
            b=obj.get()['Body'].read().decode()
            result.append(b)
        return result

