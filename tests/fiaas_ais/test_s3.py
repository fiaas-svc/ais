#!/usr/bin/env python
# -*- coding: utf-8

from fiaas_ais import app
from moto import mock_s3
from unittest import TestCase
from datetime import datetime
import json
import boto3


@mock_s3
class S3TestCase(TestCase):
    def setUp(self):
        self.mybucket = 'fiaas-release.delivery-pro.schibsted.io'
        self.conn = boto3.resource('s3')
        self.conn.create_bucket(Bucket=self.mybucket)

        self.app = app
        self.client = app.test_client()

    def test_persist_tag_to_s3(self):
        keys = ['updated', 'image', 'commit', 'build']
        data = dict(zip(keys, keys))
        data['updated'] = datetime.now().isoformat()

        self.client.post('/channel/tag', data=json.dumps(data))

        body = json.load(self.conn.Object(self.mybucket, 'channel/tag.json').get()['Body'])

        assert body == data
