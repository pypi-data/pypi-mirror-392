from flask import Flask, Response, jsonify
from flask_cors import CORS
import threading
import time
from .exceptions import *


class Endpoints:
    def __init__(self, client, default_interval=300):
        self.client = client
        self.default_interval = default_interval
        self._endpoints = []

    def add(self, func, interval=None, name=None):
        if name is None:
            name = func.__name__
        if interval is None:
            interval = self.default_interval
        self._endpoints.append((name, func, interval))
        return self  # allows chaining

    def run(self, host=None, port=None, debug=True):
        backend = CWBackend(self.client, self._endpoints)
        backend.run(host=host, port=port, debug=debug)


class CWBackend:
    def __init__(self, client, endpoints, default_interval=300):
        self.client = client
        self.functions = {}
        self.intervals = {}
        self.data = {}
        self.last_update = {}

        for name, func, interval in endpoints:
            # allow None or missing interval -> default
            if interval is None:
                interval = default_interval

            self.functions[name] = func
            self.intervals[name] = interval
            self.data[name] = None
            self.last_update[name] = 0
        self.app = Flask(__name__)
        CORS(self.app)
        for key in self.functions.keys():
            endpoint = f"/{key}"
            def make_route(k):
                def route():
                    return jsonify(self.data[k])
                return route
            self.app.route(endpoint,endpoint=f"route_{key}")(make_route(key))
       
        @self.app.route("/overview")   
        def overview():
            return jsonify(self.data)
        
    def update_data(self):
        update_times = {key: time.time() for key in self.intervals}
        while True:
            for key, func in self.functions.items():
                now = time.time()
                if now - self.last_update[key] >= self.intervals[key]:
                    self.last_update[key] = now
                    update_times[key] = now + self.intervals[key]
                    try:
                        self.data[key] = func(self.client)
                    except FetchError as e:
                        if e.status_code() == 401: # Not authorised so token expired or wrong
                            self.client.get_access_token()
                            self.data[key] = func(self.client)
                        else:
                            self.data[key] = f"Error fetching data"
            next_update = min(update_times.values())
            sleep_time = max(1, next_update - time.time())
            time.sleep(sleep_time)

    def run(self,host=None,port=None,debug=True):
        threading.Thread(target=self.update_data, daemon=True).start() 
        self.app.run(debug=debug, use_reloader=False)