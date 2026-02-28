import json
import os
import urllib.request

class DataManager:
    def __init__(self, basePath="data"):
        self.url   = os.environ.get("UPSTASH_REDIS_REST_URL")
        self.token = os.environ.get("UPSTASH_REDIS_REST_TOKEN")

    def _request(self, command_parts):
        # Build the URL by joining command parts with /
        # e.g. ["SET", "mykey", "myvalue"] becomes /SET/mykey/myvalue
        path = "/".join(urllib.request.quote(str(p), safe="") for p in command_parts)
        full_url = self.url + "/" + path

        req = urllib.request.Request(
            full_url,
            headers={ "Authorization": "Bearer " + self.token }
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            return result.get("result")

    def load(self, fileName, default=None):
        # Use the filename as the key, e.g. "settings.json"
        result = self._request(["GET", fileName])

        if result is None:
            return default

        try:
            return json.loads(result)
        except:
            return default

    def save(self, fileName, data):
        # Convert the data to a JSON string and store it
        value = json.dumps(data)
        self._request(["SET", fileName, value])
