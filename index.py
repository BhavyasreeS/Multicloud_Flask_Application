import os
import logging
import math
import random
import http.client
import pandas as pd
import json
import parallel
import ec2_functions
import ec2_start_stop
import ast
import time


from flask import Flask, request, render_template

app = Flask(__name__)
# invoke url:  https:##################.us-east-1.amazonaws.com/default
# various Flask explanations available at: https://flask.palletsprojects.com/en/1.1.x/quickstart/

def doRender(tname, values={}):
	if not os.path.isfile( os.path.join(os.getcwd(), 'templates/'+tname) ): #No such file
		return render_template('index.htm')
	return render_template(tname, **values) 


# Defines a POST supporting estimate route
@app.route('/estimate', methods=['POST'])
def estimateHandler():
	if request.method == 'POST':
		scale= request.form.get('service')
		r = request.form.get('parallel-resources')
		d = request.form.get('digits')
		s = request.form.get('shots')
		q = request.form.get('q')
		if scale == '' or r == '' or d=='' or s=='' or q=='':
			return doRender('index.htm',{'note': 'Please specify a number for each group!'})
		else:
			r=int(r)
			d=int(d)
			s=int(s)
			q=int(q)
			if scale=="lambda":
				service="lambda"
				results=parallel.main(r,d,s,q)
				thresh=results[2]
				time_taken=results[3]
				total_cost=parallel.cost_estimate_lambda(time_taken,thresh)
				print("time taken:",time_taken)
			if scale=="ec2":
				service="EC2"

				# We start r instances from the ami image
				start=time.time()
				instances=ec2_start_stop.create(r)

				# Getting all the instance-ids of the newly created instances
				ec2_con_re=ec2_start_stop.get_ec2_for_my_region()
				list_inst_id=ec2_start_stop.list_instances_on_my_region(ec2_con_re)
				#print(list_inst_id)

				# Now we need to get the public ip address of all the instance after they have started

				# Waiting for all instances to be running
				for in_id in list_inst_id:
					ec2_start_stop.start_instance(ec2_con_re,in_id)

				#getting public ip of all instances
				list_public_ip=ec2_start_stop.get_public_ip(list_inst_id)
				
				results=ec2_functions.main(r,d,s,q,list_public_ip)

				# terminating all instances
				ec2_start_stop.stop(list_inst_id)
				total_time=time.time()-start
				total_cost=parallel.cost_estimate_EC2(total_time)
				#print("time taken:",total_time)
			y=results[0]
			pivalue=[]
			for val in y:
				pivalue.append(str(val))
			pivalue=','.join(pivalue)
			pi=math.floor(math.pi * 10 ** (d-1))/ 10 ** (d-1)
			y1=[]
			for i in range(0,len(y)):
				y1.append(str(pi))
			y1=','.join(y1)
			data1=results[1]
			parallel.toS3(1,s,q,d,r,results[-1],total_cost,service)
			return render_template('chart.htm',tables=[data1.to_html(classes='data', header="true")],y=pivalue,y1=y1,pi=results[-1],cost=total_cost)
	return 'Should not ever get here'

@app.route('/history',methods=['POST'])
def history_handler():
    data=parallel.fromS3()
    result=json.loads(data)
    data=[]
    for each in result:
        data.append(json.loads(each))
    tab = pd.DataFrame.from_dict(data)
    return render_template('history.htm',tables=[tab.to_html(classes='data', header="true")])
    
@app.route('/terminate',methods=['POST'])    
def terminate_handler():
    ec2_con_re=ec2_start_stop.get_ec2_for_my_region()
    list_inst_id=ec2_start_stop.list_instances_on_my_region(ec2_con_re)
    #print(list_inst_id)
    ec2_start_stop.terminate(list_inst_id)
    return doRender('index.htm',{'note1': 'Instances now terminated'})
    

# catch all other page requests - doRender checks if a page is available (shows it) or not (index)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def mainPage(path):
	return doRender(path)

@app.errorhandler(500)
# A small bit of error handling
def server_error(e):
	logging.exception('ERROR!')
	return """
	An error occurred: <pre>{}</pre>
	""".format(e), 500

if __name__ == '__main__':
	# Entry point for running on the local machine
	# On GAE, endpoints (e.g. /) would be called.
	# Called as: gunicorn -b :$PORT index:app,
	# host is localhost; port is 8080; this file is index (.py)
	app.run(host='127.0.0.1', port=8080, debug=True)
