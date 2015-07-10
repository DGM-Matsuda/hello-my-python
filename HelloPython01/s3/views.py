from pprint import pprint
import io
import os
from boto.resultset import ResultSet

from boto.s3.connection import OrdinaryCallingFormat
from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView
import boto
import uuid
from pprint import pprint


class S3:

    def __init__(self):
        region = boto.s3.connect_to_region(
            boto.s3.connection.Location.APNortheast,
            calling_format=OrdinaryCallingFormat()
        )
        self.bucket = region.get_bucket("staticrosso.mydigimo.com")

    def get_all_keys(self, ext=None):
        _keys = self.bucket.get_all_keys(prefix="data/")
        _res = ResultSet()
        if ext:
            for key in _keys:
                if ext in key.name:
                    _res.append(key)
        else:
            return _keys
        return _res

    def download(self, file_key, name):
        # file_key = "/data/23XKCTZHGDHS/23XKCTZHGDHS.json"
        _key = self.bucket.get_key(file_key)
        pprint(_key)

        fp = io.BytesIO()
        _key.get_contents_to_file(fp)
        fp.seek(0)

        outfile = open(os.path.join(os.path.dirname(__file__), name), 'wb')
        outfile.write(fp.getvalue())
        outfile.close()

    def replace(self, file_key):
        fp = open(file_key, 'r')
        text = fp.read()
        fp.close()

        if "digimo3D" in text:
            if "\"digimo3D\"" in text:
                print("NO")
                return
            print("YES")
            fp = open(file_key, 'w+')
            name = file_key.replace("userdata/", "").replace(".json", "")

            text = text.replace("digimo3D", "\"digimo3D\"")
            text = text.replace(name + ".png\",", name + ".png\"")
            fp.write(text)
            fp.close()

        else:
            print("NO")


if __name__ == '__main__':
    # print("main")
    s3 = S3()
    keys = s3.get_all_keys(ext=".json")
    # keys = s3.get_all_keys(ext="2E94GF4HMETM.json")
    pprint(len(keys))

    for key in keys:
        pprint(key.name.split("/"))
        s3.download(key.name, "userdata/" + key.name.split("/")[2])
        s3.replace("userdata/" + key.name.split("/")[2])
        key.set_contents_from_filename(os.path.join(os.path.dirname(__file__), "userdata/" + key.name.split("/")[2]))

else:
    print(__name__)