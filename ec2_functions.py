#!/usr/bin/env python3
import time
import http.client
from concurrent.futures import ThreadPoolExecutor
import math
import random
import pandas as pd
import numpy as np
import json
import requests
# creates a list of values as long as the number of things we want

 
def process_ec2out(data):
    dict_list=[]
    for i in range(0,len(data)):
        temp=data[i]
        data_id=temp[-1]
        incircle_vals=temp[:-1]
        dict_data={data_id:incircle_vals}
        dict_list.append(dict_data)
    return dict_list
 
 
 
def getpage(id):
    try:
        ip=list_public_ip[id]
        time.sleep(10)
        # Connects with created ec2 instances
        r = requests.get(ip,verify=False)
        result=r.text
        results1=json.loads(result)
        results1.append(id)
        return results1
    except IOError:
        print( 'Failed to open ' ) # Is the Lambda address correct?


def getpages():
    with ThreadPoolExecutor() as executor:
        results=list(executor.map(getpage, runs))

    results=process_ec2out(results)
    return results

def main(r1,d1,s1,q1,ip1):
    global r,d,s,q,runs,list_public_ip,count,parallel,table,shots
    r=r1
    d=d1
    s=s1
    q=q1
    list_public_ip=ip1
    parallel=r
    count=1000
    threshold=10
    shots=int(s/r)
    value_pi=[]
    thresh=1
    res=[0]
    temp=[]
    list_shots=[]
    final_incircle=0
    new_dict={}
    table=pd.DataFrame(columns=['Resource','Incircle'])
    final_results=[]
    query_string='/?shots={}&q={}'.format(shots,q)
    # adding the query string to each ip to form a URL
    for i in range (0,len(list_public_ip)):
        list_public_ip[i]='http://'+list_public_ip[i]+query_string
        
    while(thresh<=threshold):
        results=[]
        runs=[value for value in range(parallel)]
        
	# this is a list of dictionary
        results_dict= getpages()
        
	# storing value of incircle to results, results contain a list of incircle values from all resources
        for k, v in [(k, v) for x in results_dict for (k, v) in x.items()]:
            results.append(v)

	# this converts the list of dictionaries into a single dictionary with resource_id as key and list of incircle values as value
        for dicti in results_dict:
            new_dict.update(dicti)
        
        # Creates a table table that stores Resource Id and Incircle values(per q)
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
            ll=ul
            ul=len(temp)

            # Adds the incircle values for the second run
            for i in range(ll,ul):
                temp[i]=temp[i-1]+temp[i]


	# Gives the value of shots for subsequent runs
        value_shots=[x for x in range (q,shots+1,q)]
        value_shots=value_shots*thresh

	# creates a list of shots across all runs
        #list_shots=list_shots+value_shots

	# Calculates pi across all resources for first 2 thresholds to plot the graph
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
    value_shots=value_shots*r
    y=value_pi
    table['shots']=value_shots
    final_results.append(y)
    final_results.append(table)
    final_results.append(estimated_pi)

    return(final_results)
