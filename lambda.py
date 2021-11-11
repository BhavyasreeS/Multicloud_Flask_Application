# Note this code is in lambda
#!/usr/bin/env python3
import json
import time
import http.client
from concurrent.futures import ThreadPoolExecutor
import math
import random
import pandas as pd
import numpy as np
def lambda_handler(event, context):
    input_lambda=(event["key1"])
    input_lambda=input_lambda.split(",")
    shots=int(input_lambda[0])
    q=int(input_lambda[1])
    id=int(input_lambda[2])
    value=[]
    value_pi=[]
    incircle=0
    value_sum=[]
    j=0
    for i in range(0, shots):
        random1 = random.uniform(-1.0, 1.0)
        random2 = random.uniform(-1.0, 1.0)
        if( ( random1*random1 + random2*random2 ) < 1 ):
            incircle += 1
        if i in range (q-1,shots+1,q):
            j=j+i+1
            value.append(incircle)
            incircle=0
            value_sum.append(sum(value))
    data=value_sum

    # stores resource id and incircle values
    data_dict={id:data}
    return str(data_dict)
