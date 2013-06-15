from flask import Flask, url_for, Response, request, make_response, session, g, redirect, abort, render_template, flash
import plivo
import os
import random
import time
from Queue import Queue

#configuration
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'admin'

app = Flask(__name__)
app.config.from_object(__name__)

global q 
q= Queue(maxsize=0)

@app.route('/',methods=['POST','GET'])
def show_entries():
    global q
    #global agent
    print "inside  show entries functio==============================>"
    p = plivo.RestAPI(auth_id, auth_token)
    qsize = q.qsize()
    print qsize
    waiting_callers = {}
    qq = Queue(maxsize=0)
    while q.qsize() > 0:
	calluuid = q.get()
        caller = p.get_live_call({'call_uuid':calluuid})
	if caller[0] == 200 : 
	    caller_name = caller[1]['caller_name']
	    waiting_callers[caller_name] = calluuid
	    qq.put(calluuid)
    q=qq
    callers = waiting_callers.keys()
    print waiting_callers
    if request.method == "POST":
	caller = request.form.get('caller','')
	global agent
        agent = request.form.get('agent','')
        print caller
        print agent
	print waiting_callers
	caller_uuid = waiting_callers[caller]
	callers.remove(caller)
	del waiting_callers[caller]
	print caller_uuid
        params = {
                    'call_uuid' : caller_uuid,
                    'legs' : 'aleg',
                    'aleg_url' : 'http://call-center-support.herokuapp.com/?action=true',
                    'aleg_method' : 'GET'
        }
        response = p.transfer_call(params)
	print "call tranfer by agent has taken place , details:\n",response
        rq =  Queue(maxsize=0)
	while q.qsize() > 0 :
	    uuid = q.get()
    	    if caller_uuid != uuid:
       		rq.put(uuid)
	q = rq 	
        print "call transferred to executive"
        flash('call has been successfully transferred.')
        return redirect(url_for('show_entries'))
    if request.method == "GET":
	action = request.args.get('action', None)
	if action == 'true':
	    print "call being tranferred to agent:",agent
            r = plivo.Response()
            dial = r.addDial()
            body = agent
            dial.addNumber(body)
            mod_response = make_response(r.to_xml())
            mod_response.headers['Content-Type'] = 'text/xml'
            return mod_response	
    print waiting_callers
    print qsize
    return render_template('show_entries.html', entries=callers) 

@app.route('/quing/', methods=['POST', 'GET'])
def index():
    print "inside quing=======================================>"
    auth_id = request.args.get('auth_id', None)
    auth_token = request.args.get('auth_token', None)
    global p
    p = plivo.RestAPI(auth_id, auth_token)
    calluuid = request.args.get('CallUUID', None)
    print calluuid
    moderator = request.args.get('moderator', None)
    print "Moderator: ",moderator
    From = request.args.get('From', None)
    print "From: ",From
    event = request.args.get('Event', None)
    global conference_name
    conference_name = request.args.get('conference_name', None)
    if moderator == From and event == 'StartApp':
        r = plivo.Response()
        body = conference_name
        params = { 'startConferenceOnEnter' : 'true', 'endConferenceOnExit' : 'true', 'callbackUrl' : 'http://call-center-support.herokuapp.com/action/'}
        r.addConference(body, **params)
        mod_response = make_response(r.to_xml())
        mod_response.headers['Content-Type'] = 'text/xml'
        return mod_response
    if event == 'StartApp':
        q.put(calluuid)

    qsize = q.qsize()
    print "++++++++ qsize= ",qsize
    conference_status = p.get_live_conference({"conference_name": "amit3"})
    print conference_status[0]
    if event == 'StartApp' and qsize == 1 and conference_status[0] == 200 :
        r = plivo.Response()
        body = conference_name
        params = { 'callbackUrl' : 'http://call-center-support.herokuapp.com/action/'}
        r.addConference(body, **params)
        mod_response = make_response(r.to_xml())
        mod_response.headers['Content-Type'] = 'text/xml'
        return mod_response
    if event == 'StartApp':
        print "more then 1 customer in wating list"
        r = plivo.Response()
        body = "Dear customer, Still our all executive are busy, please wait, we will be happy to help you."
        params = {'loop':'0'}
        r.addSpeak(body,**params)
        response = make_response(r.to_xml())
        response.headers['Content-Type'] = 'text/xml'
        return response
    return str(qsize)


@app.route('/action/',methods=['POST','GET'])
def conference_action():
    print "\ninside action part.====================================================>"
    values = request.form.items()
    print values
    calluuid =  request.form.get('CallUUID','')
    print calluuid
    moderator_in = request.form.get('ConferenceFirstMember','')
    print moderator_in
    moderator_out = request.form.get('ConferenceLastMember','')
    print moderator_out
    conference_action = request.form.get('ConferenceAction','')
    print conference_action
    qsize = q.qsize()
    if moderator_in =='true'and qsize > 0:
        response = p.get_live_calls()
        res = response[1]
        call_uuids = res['calls']
        print "live calls", call_uuids
        caller = q.get()
        while caller not in call_uuids and q.qsize() > 0:
                caller = q.get()
        if caller in call_uuids:
            print "call with call uuid: ",caller," is being connected to moderator "
            params = {
                    'call_uuid' : caller,
                    'legs' : 'aleg',
                    'aleg_url' : 'http://call-center-support.herokuapp.com/conference/',
                    'aleg_method' : 'POST'
            }
            response = p.transfer_call(params)
            print "call transferred to executive"
            return "OK"
    if conference_action == 'exit' and qsize > 0 and  moderator_out == 'false':
        time.sleep(1)
        response = p.get_live_calls()
        res = response[1]
        call_uuids = res['calls']
        print "live calls", call_uuids
        caller = q.get()
        while caller not in call_uuids and q.qsize() > 0:
                caller = q.get()
        if caller in call_uuids:
            print "call with call uuid: ",caller," is being connected to conference "
            params = {
                    'call_uuid' : caller,
                    'legs' : 'aleg',
                    'aleg_url' : 'http://call-center-support.herokuapp.com/conference/',
                    'aleg_method' : 'POST'
            }
            response = p.transfer_call(params)
            print "call transferred to executive"
            return "OK"
    return "action"


@app.route('/conference/',methods=['POST','GET'])
def conference():
    print "\ncaller transfeered from action to conference=================================>"
    r = plivo.Response()
    body = conference_name
    params = {'callbackUrl' : 'http://call-center-support.herokuapp.com/action/'}
    print "new customer entered in conference"
    r.addConference(body, **params)
    mod_response = make_response(r.to_xml())
    mod_response.headers['Content-Type'] = 'text/xml'
    return mod_response


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9191))
    app.debug = True
    app.run(host='0.0.0.0', port=port)


