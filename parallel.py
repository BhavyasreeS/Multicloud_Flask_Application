#!/usr/bin/env python3
import time
import http.client
from concurrent.futures import ThreadPoolExecutor
import math
import random
import pandas as pd
import numpy as np
import json
# creates a list of values as long as the number of things we want
 #https://##############################.us-east-1.amazonaws.com/default
 
# This function writes to s3
def toS3(choice,s,q,d,r,pi,cost,service):
    try:
        host = "############.us-east-1.amazonaws.com" # S3 address
        c = http.client.HTTPSConnection(host)
        input_S3=str(1)+","+str(s)+","+str(q)+","+str(d)+","+str(r)+","+str(pi)+","+str(cost)+","+service
        json='{ "key1":"'+input_S3+'"}'
        c.request("POST", "/default/bucketaccess", json)
        response = c.getresponse()
        data = response.read().decode('utf-8')
    except IOError:
        print( 'Failed to open ' ) # Is the Lambda address correct?

# this fucntionb retrieves history from s3
def fromS3():
    try:
        host = "############.execute-api.us-east-1.amazonaws.com" # S3 address
        c = http.client.HTTPSConnection(host)
        input_S3=str(2)
        json='{ "key1":"'+input_S3+'"}'
        c.request("POST", "/default/bucketaccess", json)
        response = c.getresponse()
        data = response.read().decode('utf-8')
        return data
    except IOError:
        print( 'Failed to open ' ) # Is the Lambda address correct?

def cost_estimate_lambda(time_taken,thresh):
    total_secs=time_taken
    total_GBsecs=time_taken*(128/1024)
    cost_GBsec=total_GBsecs*0.00001667
    req_charge=(r*thresh)*(0.2/1000000)
    total_cost=cost_GBsec+req_charge
    return total_cost

def cost_estimate_EC2(total_time):
    time_in_hrs=total_time/(60*60)
    total_cost=time_in_hrs*0.0116
    return total_cost

def process_lambdaout(data):
    data_list=[]
    for i in data:
        item=i
        items=item.split(":")
        data_id=items[0]
        data_id=data_id[2:]
        data_id=int(data_id)
        incircle_vals=items[1]
        incircle_vals=incircle_vals[2:-3]
        incircle_vals=incircle_vals.split(",")
        incircle_vals = list(map(int, incircle_vals))
        dict_data={data_id:incircle_vals}
        data_list.append(dict_data)
    return data_list
 
def getpage(id):
    try:
        host = "#########.us-east-1.amazonaws.com" # lambda function
        c = http.client.HTTPSConnection(host)
        input_lambda=str(shots)+","+str(q)+","+str(id)
        json='{ "key1":"'+input_lambda+'"}'
        c.request("POST", "/default/pi_estimation", json)
        response = c.getresponse()
        data = response.read().decode('utf-8')
        return data
    except IOError:
        print( 'Failed to open ' ) # Is the Lambda address correct?

def getpages():
    
    with ThreadPoolExecutor() as executor:
        results=list(executor.map(getpage, runs))
    return results

def main(r1,d1,s1,q1):
    global r,d,s,q,runs,count,parallel,table,shots,start_time,elapsed_time
    r=r1
    d=d1
    s=s1
    q=q1
    parallel=r
    count=1000
    threshold=10
    st=q
    shots=int(s/r)
    value_pi=[]
    thresh=1
    res=[0]
    temp=[]
    #list_shots=[]
    final_incircle=0
    new_dict={}
    table=pd.DataFrame()
    final_results=[]
    elapsed_time=0
    start_time=0
    final_time=0
    table=pd.DataFrame(columns=['Resource','Incircle'])
    while(thresh<=threshold):
        results=[]
        runs=[value for value in range(parallel)]
        start_time=time.time()
        lambda_out= getpages()
        elapsed_time=time.time()-start_time
        final_time=final_time+elapsed_time
        results_dict=process_lambdaout(lambda_out)

	# storing value of incircle to results, results contain a list of incircle values from all resources
        for k, v in [(k, v) for x in results_dict for (k, v) in x.items()]:
            results.append(v)

	# this converts the list of dictionaries into a single dictionary with key as id and value the list of incircle values
        for dicti in results_dict:
            new_dict.update(dicti)
        
        for k,v in new_dict.items():
            for value in v:
                table=table.append({'Resource':k,'Incircle':value},ignore_index=True)

	# We calculate the sum of incircle values across all resources
        res=[sum(i) for i in zip(*results)]
        final_incircle=final_incircle+res[-1]
        if(thresh==1):
            temp=res
        else:
            # This creates a single list of all incircle values across the runs, this is used to plot the final graph
            ul=len(temp)
            temp=temp+res
            #print(temp)
            ll=ul
            ul=len(temp)

            # Adds the incircle values for the second run
            for i in range(ll,ul):
                temp[i]=temp[i-1]+temp[i]


	# Gives the value of shots for subsequent runs
        value_shots=[x for x in range (q,shots+1,q)]
        value_shots=value_shots*thresh



        # Calculates pi across all resources for first 2 runs to plot the graph
        if(thresh<3):
            for i in range (0,len(res)):
                pi=(res[i]/(value_shots[i]*r))*4
                pi=math.floor(pi * 10 ** (d-1) )/ 10 ** (d-1)
                value_pi.append(pi)

        real_pi=math.floor(math.pi * 10 ** (d-1))/ 10 ** (d-1)
        estimated_pi=(final_incircle/(s*thresh))*4
        estimated_pi=math.floor(estimated_pi * 10 ** (d-1) )/ 10 ** (d-1)

        thresh=thresh+1

	# Checks whether d is met
        if(estimated_pi==real_pi):
            break;

    #This is for drawing graph
    #list_shots=[x for x in range(q,(len(value_shots)*q)+1,q)]
    value_shots=value_shots*r
    y=value_pi    
    # printing the table of values, add the q rate column
    table['shots']=value_shots
    final_results.append(y)
    final_results.append(table)
    final_results.append(thresh)
    final_results.append(final_time)
    final_results.append(estimated_pi)

    return(final_results)
