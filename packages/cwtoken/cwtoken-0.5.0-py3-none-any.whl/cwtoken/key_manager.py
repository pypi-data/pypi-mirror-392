import requests
import pandas as pd
from urllib.parse import urlencode
import warnings
from .exceptions import *

class RawQuery:
    def __init__(self, base_url, full_query, headers):
        self.query_type = "Raw"
        self.base_url = base_url.rstrip('/')
        self.full_query = full_query.strip('/')
        self.headers = headers
        self.response = None
    
    def last_response(self):
        if self.response is None:
            return None
        try:
            return self.response.json()
        except Exception:
            return self.response.text
    
    def get_columns(self):
        full_url = f"{self.base_url}/{self.endpoint}?limit=1"
        response = requests.get(full_url, headers=self.headers)
        self.response = response
        data = response.json()
        columns = list(data[0].keys() if data else [])
        return columns
    
    def fetch(self, to_df=False):
        full_url = f"{self.base_url}/{self.full_query}"
        try:
            response = requests.get(full_url, headers=self.headers)
            self.response = response
            response.raise_for_status()
        except Exception as ex:
            resp = getattr(ex, 'response', None)
            raise FetchError(f"Request failed for URL:\n{full_url}", resp)

        return pd.DataFrame(response.json()) if to_df else response.json()


class Query:
    def __init__(self, base_url, endpoint, headers=None):
        self.query_type = "Constructor"
        self.base_url = base_url.rstrip('/')
        self.endpoint = endpoint.strip('/')
        self.headers = headers or {}
        self._params = {}
        self._filters = []
        self._orders = []
        self.response = None
    
    def select(self, *columns):
        existing = self._params.get('select', '').split(',')
        combined = [c for c in existing + list(columns) if c]
        self._params['select'] = ','.join(combined)
        return self

    def filters(self, *filter_strings):
        self._filters.extend(filter_strings)
        return self

    def order(self, *columns, desc=False):
        direction = 'desc' if desc else 'asc'
        for col in columns:
            for c in col.split(','):
                c = c.strip()
                if c:
                    self._orders.append(f"{c}.{direction}")
        return self

    def limit(self, n):
        self._params['limit'] = str(n)
        return self

    def clear_filters(self):
        self._filters = []
        return self

    def clear_orders(self):
        self._params.pop("order", None)
        self._orders = []
        return self

    def clear_params(self):
        self._params = {}
        return self

    def clear_select(self):
        self._params.pop("select", None)
        return self

    def clear_limit(self):
        self._params.pop("limit", None)
        return self
    
    def last_response(self):
        if self.response is None:
            return None
        try:
            return self.response.json()
        except Exception:
            return self.response.text
    
    def get_columns(self):
        full_url = f"{self.base_url}/{self.endpoint}?limit=1"
        response = requests.get(full_url, headers=self.headers)
        self.response = response
        data = response.json()
        columns = list(data[0].keys() if data else [])
        return columns
    
    def compose_url(self):
        full_url = f"{self.endpoint}"
        if self._orders:
            self._params['order'] = ','.join(self._orders)

        query_str = urlencode(self._params, safe=',()')
        filter_str = '&'.join(self._filters)

        if query_str or filter_str:
            full_url += '?' + '&'.join(filter(None, [query_str, filter_str]))
        return full_url

    def fetch(self,to_df=False):
        full_url = f"{self.base_url}/{self.compose_url()}"
 
        def safe_response(e):
            return getattr(e, 'response', None)

        try:
            response = requests.get(full_url, headers=self.headers)
            self.response = response
            response.raise_for_status()
        except Exception as e:
            resp = safe_response(e)
            raise FetchError("Query failed", resp)
            
        return pd.DataFrame(response.json()) if to_df else response.json()




class CWClient:
    def __init__(self, api_token, clubcode=None, access_token=None, base_url='https://atukpostgrest.clubwise.com/'):
        self.base_url = base_url.rstrip('/')
        self.headers = {}
        self.clubcode = clubcode
        self.api_token = api_token
        self.access_token = access_token
        self.response = None

        if not self.access_token:
            if not self.clubcode:
                raise ValueError("clubcode is required if access_token is not provided.")
            # Fetch the token
            self.get_access_token()
            
    def get_access_token(self):
        if not self.clubcode:
            raise ValueError("clubcode is required to generate access_token.")

        # Fetch the token
        request_url = f'{self.base_url}/access-token'
        request_header = {
            'CW-API-Token': self.api_token,
            'Content-Type': 'application/json'
        }
        try:
            payload = {'sClubCode': self.clubcode}
            response = requests.post(request_url, json=payload, headers=request_header, timeout=10)
            self.response = response
            response.raise_for_status()
        except Exception as e:
            resp = getattr(e, 'response', None)
            raise AuthenticationError( "Failed to authenticate. Check your clubcode, API token, and network connection.",resp)
        
        self.access_token = response.json().get('access-token')
        if not self.access_token:
            raise AuthenticationError("Access token not found in response.", response)
        self.headers = {
            'CW-API-Token': self.api_token,
            'Authorization': f'Bearer {self.access_token}'
        }
        
        return self
    
    def last_response(self):
        if self.response is None:
            return None
        try:
            return self.response.json()
        except Exception:
            return self.response.text
    
    def get_endpoints(self):
        response = requests.get(self.base_url, headers=self.headers)
        spec = response.json()
        endpoints = list(spec["paths"].keys())
        tables = []
        for endpoint in endpoints:
            tables.append(endpoint.lstrip("/"))
        return tables
        
    def table(self, endpoint):
        return Query(self.base_url, endpoint, self.headers)
    def raw_query(self, full_query):
        return RawQuery(self.base_url, full_query, self.headers)
    
