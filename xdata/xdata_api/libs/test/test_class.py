# from libs.tools import AttrDict
# from docker import APIClient
# from docker.errors import APIError, DockerException
import json
import requests
import os
import subprocess
import datetime
import base64
import uuid
import pymysql

class Registry(object):
    def __init__(self, base_url):
        self.api = base_url
        self.auth = ('admin','KY@693dp')
        # self.auth = (
        #     app.config['DOCKER_REGISTRY_AUTH'].get('username'),
        #     app.config['DOCKER_REGISTRY_AUTH'].get('password')
        # )

    def list_tags(self, name):
        req_url = 'http://%s/v2/%s/tags/list' % (self.api, name)
        tags = requests.get(req_url, auth=self.auth).json().get('tags', [])
        tags = tags or []
        tags.reverse()
        return tags

    def delete(self, name, digest):
        req_url = 'http://%s/v2/%s/manifests/%s' % (self.api, name, digest)
        res = requests.delete(req_url, auth=self.auth)
        if res.status_code not in [202, 404]:
            raise Exception('Delete image error, code: %d content: %s' % (res.status_code, res.content))

    def list_images(self):
        req_url = 'http://%s/v2/_catalog' % self.api
        res = requests.get(req_url, auth=self.auth).json()
        return res.get('repositories', [])

    def get_tag_digest(self, name, tag):
        req_url = 'http://%s/v2/%s/manifests/%s' % (self.api, name, tag)
        res = requests.head(req_url, headers={'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}, auth=self.auth)
        return res.headers.get('Docker-Content-Digest')

    def get_last_modify_date(self, name, tag):
        req_url = 'http://%s/v2/%s/manifests/%s' % (self.api, name, tag)
        res = requests.get(req_url, auth=self.auth).json()
        last_history_date = json.loads(res['history'][0]['v1Compatibility'])['created'].split('.')[0]
        created = datetime.datetime.strptime(last_history_date, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
        return created.astimezone(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')

    def __repr__(self):
        return '<Registry %r>' % self.api

if __name__ == '__main__':
    reg = Registry(base_url='172.16.6.101')
    images = reg.list_images()
    print(reg.list_tags('pol'))