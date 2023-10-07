from flask import Flask, render_template, request, redirect, url_for, send_file
from sms import smspool, workermonitor
import random
import signal

app = Flask("SMSPoolChecker")
max_worker = 3

def random_worker_name():
	posibles = ["Wolf", "Cat", "Dog", "Pig", 
			 "Eagle", "Ant", "Ele", "Bird", 
			 "Snake", "Human", "Panda", "Tiger", 
			 "Lion", "Fish", "Duck", "Giff" ]
	name1 =  random.choice(posibles)
	while workermonitor.get_worker(name1) is not None:
		name1 = random.choice(posibles)
	return name1

@app.route("/")
def index():
	srvid = request.args.get('srvid', "")
	if srvid == "":
		return render_template("index.html")
	apikey = request.args.get('key', "VFoCdZK4WjDeArKacB43cE1K0Intx2Vu")
	if workermonitor.num_worker() >= max_worker:
		return "Sorry, all workers are busy"
 
	thdname = random_worker_name()
	srvthread = smspool(srvid, apikey, thdname)
	srvthread.start()
	workermonitor.add_worker(thdname, srvthread)
	return redirect(url_for("status", tname = thdname))

@app.route('/status')
def status():
	x = request.args.get('tname', "")
	y = request.args.get('stop', 0)
	if x == "":
		return "API wrong"
	srvthread = workermonitor.get_worker(x)
	finalrs = workermonitor.get_result(x)
	
	if int(y) == 1 and srvthread is not None:
		srvthread.stop()
		return render_template("status.html", percent = "Send stop", msg = srvthread.get_message(), tname = x)
	elif int(y) == 1 and srvthread is None:
		return redirect(url_for('index'))
	
	if srvthread is None and finalrs is None:
		return "Your thread has end or not register"

	if srvthread is not None:
		return render_template("status.html", percent = srvthread.get_progress(), msg = srvthread.get_message(), tname = x)
	elif finalrs is not None:
		return render_template("status.html", percent = 100, msg = finalrs, tname = x)
  

if __name__ == '__main__':
	monitor = workermonitor()
	monitor.start()
	app.run("0.0.0.0", 80)
	try:
		# Wait for the termination signal (Ctrl+C)
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		#signal.pause()
	except KeyboardInterrupt:
		print("Terminate request. Please wait")
		monitor.stopall()
		monitor.safestop()