import sys
sys.path.append("/Users/louyk/miniconda2/lib/python2.7/site-packages")

import urllib
import urlparse
import json
import time
import httplib

class Profiles:
    _PROFILE_ID = "identificationProfileId"

    def __init__(self, response):
        self._profile_id = response.get(self._PROFILE_ID, None)

    def get_profile_id(self):
        return self._profile_id


class SpeakerRecognitionClient:
    _STATUS_OK = 200
    _BASE_URI = "westus.api.cognitive.microsoft.com"
    _CREATE_ENROLLMENT_URI = "/spid/v1.0/identificationProfiles"
    _CREATE_PROFILES_URI = "/spid/v1.0/identificationProfiles"
    _VERIFICATION_PROFILES_URI = "/spid/v1.0/verificationProfiles"
    _VERIFICATION_URI = "/spid/v1.0/verify"
    _SUBSCRIPTION_KEY_HEADER = "Ocp-Apim-Subscription-Key"
    _CONTENT_TYPE_HEADER = "Content-Type"
    _JSON_CONTENT_HEADER_VALUE = "application/json"
    _STREAM_CONTENT_HEADER_VALUE = "application/octet-stream"

    subscription_key = ""
    profilelist = []
    profiledict = {}
    index = 0

    def __init__(self, subscription_key):
        self.subscription_key = subscription_key

    def create_profile(self, locale):
        """locale: en-US or zh-CN"""
        #        try:
        headers = {self._CONTENT_TYPE_HEADER: self._JSON_CONTENT_HEADER_VALUE,
                   self._SUBSCRIPTION_KEY_HEADER: self.subscription_key}

        body = json.dumps({"locale": "{0}".format(locale)})

        conn = httplib.HTTPSConnection("westus.api.cognitive.microsoft.com")

        conn.request("POST", "/spid/v1.0/identificationProfiles", body, headers)
        response = conn.getresponse()
        data = response.read()
        p = Profiles(json.loads(data))
        pid = p.get_profile_id()
        self.profilelist.append(pid)
        self.profiledict[pid] = self.index
        self.index = self.index + 1
        conn.close()

        return pid

    #        except:
    #            logging.error("Error resetting profile")

    def delete_profile(self, profile_id):
        request_url = "/spid/v1.0/identificationProfiles/{0}".format(profile_id)

        headers = {self._CONTENT_TYPE_HEADER: self._JSON_CONTENT_HEADER_VALUE,
                   self._SUBSCRIPTION_KEY_HEADER: self.subscription_key}

        conn = httplib.HTTPSConnection("westus.api.cognitive.microsoft.com")

        conn.request("DELETE", request_url, None, headers)
        response = conn.getresponse()
        print(response.status)

        if response.status == 200:
            self.profilelist.remove(profile_id)
            self.profiledict.pop(profile_id)
        elif response.status == 202:
            self.profilelist.remove(profile_id)
            self.profiledict.pop(profile_id)
            operation_url = response.getheader("Operation-Location")
            ans = self.poll_operation(operation_url)
            return
        else:
            data = response.read()
            reason = response.reason if not data else data
            print(reason)

    def enroll_profile(self, profile_id, file_path):
        #        try:
        request_url = "/spid/v1.0/identificationProfiles/{0}/enroll?{1}={2}".format(
            urllib.quote(profile_id),
            "shortAudio",
            True)

        headers = {self._CONTENT_TYPE_HEADER: self._STREAM_CONTENT_HEADER_VALUE,
                   self._SUBSCRIPTION_KEY_HEADER: self.subscription_key}

        with open(file_path, "rb") as body:
            conn = httplib.HTTPSConnection("westus.api.cognitive.microsoft.com")
            conn.request("POST", request_url, body, headers)
            response = conn.getresponse()
            print(response.status)

            if response.status == 200:
                data = response.read()
                print(response.status)
                print(data["enrollmentStatus"])
            elif response.status == 202:
                operation_url = response.getheader("Operation-Location")
                ans = self.poll_operation(operation_url)
                print(ans)
            else:
                data = response.read()
                reason = response.reason if not data else data
                print(reason)
            conn.close()
            #        except:
            #            logging.error("Error")

    def reset_enrollment(self, profile_id):
        request_url = "/spid/v1.0/identificationProfiles/{0}/reset".format(profile_id)

        headers = {self._CONTENT_TYPE_HEADER: self._JSON_CONTENT_HEADER_VALUE,
                   self._SUBSCRIPTION_KEY_HEADER: self.subscription_key}

        conn = httplib.HTTPSConnection("westus.api.cognitive.microsoft.com")

        conn.request("POST", request_url, None, headers)
        response = conn.getresponse()
        print(response.status)

        if response.status == 200:
            return
        elif response.status == 202:
            operation_url = response.getheader("Operation-Location")
            ans = self.poll_operation(operation_url)
            return
        else:
            data = response.read()
            reason = response.reason if not data else data
            print(reason)

    def identify_speaker(self, voice):
        #        try:
        ids_str = ",".join(self.profilelist)
        request_url = "/spid/v1.0/identify?identificationProfileIds={0}&{1}={2}".format(
            urllib.quote(ids_str),
            "shortAudio",
            True)

        headers = {self._CONTENT_TYPE_HEADER: self._STREAM_CONTENT_HEADER_VALUE,
                   self._SUBSCRIPTION_KEY_HEADER: self.subscription_key}

        body = voice
        conn = httplib.HTTPSConnection("westus.api.cognitive.microsoft.com")

        conn.request("POST", request_url, body, headers)
        response = conn.getresponse()
        print(response.status)

        if response.status == 200:
            data = json.loads(response.read())
            ans = data.get("identifiedProfileId", None)
            print(ans)
            return ans
        elif response.status == 202:
            operation_url = response.getheader("Operation-Location")
            ans = self.poll_operation(operation_url)
            res = ans.get("identifiedProfileId", None)
            print(res)
            return res
        else:
            data = response.read()
            reason = response.reason if not data else data
            print(reason)

        conn.close()

    #        except:
    #            logging.error("Error")

    def poll_operation(self, operation_url):
        parsed_url = urlparse.urlparse(operation_url)
        print(parsed_url)

        headers = {self._CONTENT_TYPE_HEADER: self._JSON_CONTENT_HEADER_VALUE,
                   self._SUBSCRIPTION_KEY_HEADER: self.subscription_key}

        conn = httplib.HTTPSConnection(parsed_url.netloc)

        while True:
            conn.request("GET", parsed_url.path, None, headers)
            response = conn.getresponse()

            if response.status != 200:
                raise Exception("Operation Error: ")

            data = response.read()
            operation_response = json.loads(data)

            if operation_response["status"] == "succeeded":
                return operation_response["processingResult"]
            elif operation_response["status"] == "failed":
                raise Exception("Operation Error")
            else:
                time.sleep(5)
