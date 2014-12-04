import urllib

from django.conf import settings


from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import requests

from http_signature.requests_auth import HTTPSignatureAuth

import json
#from django.utils.http import unquote
from copy import deepcopy
from models import Post


class AssessmentRequests(object):


    def __init__(self, username='taaccct_instructor'):
        self._pub_key = settings.PUBLIC_KEY
        self._pri_key = settings.PRIVATE_KEY
        self._assessments_host = settings.ASSESSMENTS_HOST
        self._service = settings.URL_ASSESSMENTS
        self._headers = {
                'Host'          : self._assessments_host,
                'Accept'        : 'application/json',
                'content-type'  : 'application/json',
                'X-Api-Key'     : self._pub_key,
                'X-Api-Proxy'   : username
            }
        # print self._pub_key
        # print self._pri_key
        # print self._assessments_host
        # print self._service
        # print self._headers


        if 'instructor' in username:
            self._sig_headers = ['request-line','accept','date','host','x-api-proxy']
            self._auth = HTTPSignatureAuth(key_id=self._pub_key,
                                           secret=self._pri_key,
                                           algorithm='hmac-sha256',
                                           headers=self._sig_headers)
        else:


            lti_headers = ['request-line', 'accept', 'date', 'host', 'x-api-proxy',
                           'lti-user-id', 'lti-tool-consumer-instance-guid', 'lti-user-role', 'lti-bank']
            params = {}
            for g in Post.objects.all():
                params[g.key] = g.value
            #print params
            self._headers['LTI-User-ID'] =                     str(params['user_id'])
            self._headers['LTI-Tool-Consumer-Instance-GUID'] = str(params['tool_consumer_instance_guid'])
            self._headers['LTI-User-Role'] =                   str(params['roles'])
            self._headers['LTI-Bank'] ='assessment.Bank%3A53cec85833bb72730f66da92%40birdland.mit.edu'

            # print params['user_id']
            # print params['tool_consumer_instance_guid']
            # print params['roles']
            # print json.dumps(self._headers)

            self._auth = HTTPSignatureAuth(key_id=settings.PUBLIC_KEY,
                                     secret=settings.PRIVATE_KEY,
                                     algorithm='hmac-sha256',
                                     headers=lti_headers)

        self.url = self._service + '/assessment/banks/'


    def post(self, url, data=None, files=None):

        url = urllib.unquote(url)
        now_headers = deepcopy(self._headers)
        now_headers['Date'] = get_now()

        # print self._auth
        req = requests.post(url, data=data,
                            auth=self._auth, headers=now_headers)#, verify=False)
        print "status code: " + str(req.status_code)
        return req.json()



    def get(self, url):
        url = urllib.unquote(url)
        now_headers = deepcopy(self._headers)
        now_headers['Date'] = get_now()
        req = requests.get(url, auth=self._auth, headers=now_headers)#, verify=False)
        #print req.text
        return req

    def delete(self, url, data=None):
        url = urllib.unquote(url)
        now_headers = deepcopy(self._headers)
        now_headers['Date'] = get_now()
        req = requests.delete(url, auth=self._auth, headers=now_headers)
        return req
    '''
    Detele does not return json object
    '''

    def put(self, url, data):
        url = urllib.unquote(url)
        now_headers = deepcopy(self._headers)
        now_headers['Date'] = get_now()

        req = requests.put(url, data=data, auth=self._auth, headers=now_headers)
        return req


def get_now():
    return format_date_time(mktime(datetime.now().timetuple()))
