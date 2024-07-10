import importlib

from NoiseReduction import *
import copy,requests

from harmo import http_requests, extract
from harmo.global_map import Global_Map
from urllib.parse import urlparse


class ExecScript:
    def __init__(self,scriptPath):
        data = NoiseReduction().getRules(scriptPath)
        self.rulesDoc = data['rulesDoc']
        self.rulesIgnoreExect = data['rulesIgnoreExect']
        self.rulesIgnoreContain = data['rulesIgnoreContain']
        self.rulesGet = data['rulesGet']

    def updateToken(self,data):

        return data

    def callAPI(self,flowData):
        req = http_requests.HttpRequests(flowData['url'])
        if Global_Map.get("access-token"):
            flowData['headers']['access-token'] = Global_Map.get("access-token")
        resp = req.send_request(method=flowData['method'],url=flowData['url'],payload=flowData['body'], header=flowData['headers']).get("response_obj")
        parsed_url = urlparse(flowData.get('url'))
        if parsed_url.path.endswith(Global_Map.get('Setting').get('Login').get("url")):
            token = extract.extract_by_object(resp, Global_Map.get('Setting').get('Login').get("rule"))
            Global_Map.set("access-token",token)
        return resp

