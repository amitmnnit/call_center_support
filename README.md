Call Center Support
---------------------
users can call an agent, if agent is not  available, they will  go in a waiting   queue, if agent gets available
only  one  caller  who  is waiting from  longest time  will be  transferred to  agent.  After  caller completes 
conversation, next  caller  i  waiting  will be  forwarded to agent. Agent  also can see the callers in waiting 
queue and if required he can forward any of these calls in waiting queue to any other agent or higher authority.

demo app url : http://call-center-support.herokuapp.com/
     username: admin
     password: admin

==================================================================
INSTALLATION INSTRUCTIONS
==================================================================

visit for more detail to  see, how to deploy a flask app in heroku:
 https://devcenter.heroku.com/articles/python
 https://github.com/zachwill/flask_heroku


Instructions to install this app:
heroku login
1. $git clone git@heroku.com:call-center-support.git
2. $cd call_center_support
3. $virtualenv venv --distribute
4. $source venv/bin/activate
5. $pip install Flask gunicorn
6. 4pip install -r requirements.txt
7. $foreman start


   Make sure things are working properly curl or a web browser, then Ctrl-C to exit.

   Now Deployment part:
8, $git init
9. $git add .
10. $git commit -m "init"
11. $heroku create
12. $git push heroku master
13. $heroku ps:scale web=1
14. $heroku ps
15. $heroku open


===================================================================
USING INSTRUCTIONS
===================================================================

1. Find the url of your new created app
2. Create  an app at www.plivo.com/app/, inside your account
   Application name : {name of your app}
   Answer url :
              url_of_app/quing/?auth_id={your plivo AUTHID}&auth_token={your plivo AUTH TOKEN}&moderator={moderator_number}&conference_name={conference_room_name}
              url_of_app/DIDCallForwarding/?User={the end point user name}
                   Example:
                   http://call-center-support.herokuapp.com/quing/?auth_id=MAZWVMNMY4ZWUYYTEXAB&auth_token=OGMyOThlZDkzMzZlN2FiMzg2NzY4Zm78ZmFiMzQ4&moderator=14156121180&conference_name=conference_room
   Answer method: GET
   Hangup url: same as Answer url
   Hangup method : GET
  



Connect this app to your Plivo_DID number. (to buy a Plivo DID number:https://manage.plivo.com/number/search/ )

use the following dummy link to check the working of app without installing:
----------------------------------------------------------------------------
link to website: www.plivo.com/app

Answer url and Hangup url: 
	http://call-center-support.herokuapp.com/quing/?auth_id={your plivo AUTHID}&auth_token={your plivo AUTH TOKEN}&moderator={moderator_number}&conference_name={conference_room_name}
           



