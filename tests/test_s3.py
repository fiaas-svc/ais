#!/usr/bin/env python
# -*- coding: utf-8

import ais
from moto import mock_s3
from unittest import TestCase
from datetime import datetime
import json
import boto3


@mock_s3
class S3TestCase(TestCase):
    def setUp(self):
        self.conn = boto3.resource('s3')
        self.conn.create_bucket(Bucket='mybucket')

        self.app = ais.app
        self.app.config['S3BUCKET'] = 'mybucket'
        self.client = ais.app.test_client()

    def test_persist_tag_to_s3(self):
        keys = ['updated', 'image', 'commit', 'build']
        data = dict(zip(keys, keys))
        data['updated'] = datetime.now().isoformat()

        self.client.post('/namespace/tag', data=json.dumps(data))

        body = json.load(self.conn.Object('mybucket', 'namespace/tag.json').get()['Body'])

        assert body == data
