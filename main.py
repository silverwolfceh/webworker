from flask import Flask, render_template, request, redirect, url_for, send_file
from modules.workerfactory import workerfactory, gen_worker_desc
from worker import workermonitor
import random
import signal

app = Flask("WebWorker")
max_worker = 3


@app.route("/")
def index():
	errmsg = None
	workertype = request.args.get('workertype', '')
	if workertype != '':
		# User already submit the workertype
		worker = workerfactory(workertype)
		if worker is None:
			errmsg = 'Stop it, script kiddies :)'
		else:
			wid = workermonitor.get_a_posibile_id(max_worker)
			if wid is None:
				errmsg = 'All workers are busy, please try again in some minutes'
			else:
				srvthread = worker(wid, request.args)
				srvthread.start()
				workermonitor.add_worker(srvthread)
				return redirect(url_for("status", tname = wid))
	else:
		pass
	alldesc = gen_worker_desc()
	return render_template("index.html", workerdesc = alldesc, errmsg = errmsg)

@app.route('/status')
def status():
	x = request.args.get('tname', "")
	y = request.args.get('stop', 0)
	if x == "":
		return redirect(url_for(index))

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
	app.run("0.0.0.0", 8000)
	try:
		# Wait for the termination signal (Ctrl+C)
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		#signal.pause()
	except KeyboardInterrupt:
		print("Terminate request. Please wait")
		monitor.stopall()
		monitor.safestop()