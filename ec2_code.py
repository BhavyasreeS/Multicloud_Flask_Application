# Note: This code is in EC2 instance
from flask import Flask
from flask import request
import math
import random
import json
app = Flask(__name__)

@app.route('/')
def estimate():
    s = request.args.get('shots')
    rate= request.args.get('q')
    shots=int(s)
    q=int(rate)
    value=[]
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
    result = json.dumps(data)
    return result
if __name__ == "__main__":
    app.run()



