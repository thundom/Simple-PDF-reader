"""Official OAuth 2 + PKCE. Tokens stored only in OS credential vault."""
import base64
import hashlib
import json
import secrets
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode, urlparse, parse_qs, quote
import keyring
import requests
from library import DATA_DIR

PROVIDERS = {
    'Google Drive': {
        'authorize':'https://accounts.google.com/o/oauth2/v2/auth',
        'token':'https://oauth2.googleapis.com/token',
        'scope':'https://www.googleapis.com/auth/drive.appdata',
    },
    'OneDrive': {
        'authorize':'https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize',
        'token':'https://login.microsoftonline.com/consumers/oauth2/v2.0/token',
        'scope':'offline_access Files.ReadWrite.AppFolder',
    },
}
SERVICE = 'Simple PDF reader OAuth'


class Cloud:
    def __init__(self, provider):
        self.provider = provider
        self.settings = PROVIDERS[provider]
        DATA_DIR.mkdir(parents=True,exist_ok=True)
        self.config_path = DATA_DIR/'cloud-config.json'
        try: self.config = json.loads(self.config_path.read_text('utf-8'))
        except (FileNotFoundError, ValueError): self.config = {}
        self.client = self.config.get(provider,{})
        stored = keyring.get_password(SERVICE, provider)
        self.tokens = json.loads(stored) if stored else {}

    def configure(self, client_id, client_secret=''):
        if self.client.get('client_id') != client_id.strip(): self.logout()
        self.client = {'client_id':client_id.strip()}
        self.config[self.provider] = self.client
        self.config_path.write_text(json.dumps(self.config,indent=2),encoding='utf-8')
        # Google's desktop client secret is not a password but keep it out of plain config.
        if client_secret: keyring.set_password(SERVICE,self.provider+' client',client_secret)

    def _secret(self):
        value = keyring.get_password(SERVICE,self.provider+' client')
        return {'client_secret':value} if value and self.provider=='Google Drive' else {}

    def _store(self, value):
        if 'refresh_token' not in value and self.tokens.get('refresh_token'):
            value['refresh_token'] = self.tokens['refresh_token']
        value['expires_at'] = time.time()+int(value.get('expires_in',3600))-90
        self.tokens = value
        keyring.set_password(SERVICE,self.provider,json.dumps(value))

    def login(self):
        if not self.client.get('client_id'): raise ValueError('请先配置 OAuth Client ID，参见 CLOUD_SETUP.md')
        verifier = secrets.token_urlsafe(48)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
        state = secrets.token_urlsafe(32)
        answer = {}
        class Callback(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                values = parse_qs(parsed.query)
                valid = parsed.path=='/callback' and values.get('state')==[state]
                if valid:
                    answer.update({k:v[0] for k,v in values.items()})
                self.send_response(200 if valid else 400)
                self.send_header('Content-Type','text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(('登录完成，可以关闭此页面。' if valid else '无效的登录回调').encode())
            def log_message(self,*args): pass
        # Microsoft public native apps must register http://localhost (port ignored).
        with HTTPServer(('127.0.0.1',0),Callback) as server:
            server.timeout = 1
            redirect = f'http://localhost:{server.server_port}/callback'
            params = {'client_id':self.client['client_id'],'redirect_uri':redirect,
                'response_type':'code','scope':self.settings['scope'],'state':state,
                'code_challenge':challenge,'code_challenge_method':'S256'}
            if self.provider=='Google Drive': params.update(access_type='offline',prompt='consent')
            webbrowser.open(self.settings['authorize']+'?'+urlencode(params))
            deadline = time.time()+180
            while not answer and time.time()<deadline: server.handle_request()
        if answer.get('error'): raise ValueError('云盘登录被取消或拒绝')
        if not answer.get('code'): raise ValueError('登录超时，请重试')
        response = requests.post(self.settings['token'],data={
            'client_id':self.client['client_id'],'code':answer['code'],
            'redirect_uri':redirect,'grant_type':'authorization_code','code_verifier':verifier,
            **self._secret()},timeout=30)
        self._check(response)
        self._store(response.json())

    def _check(self,response):
        if not response.ok:
            # Do not expose request headers, tokens or authorization codes in UI.
            raise ValueError(f'云盘请求失败（HTTP {response.status_code}）；检查应用配置、权限和网络')

    def _request(self,method,url,**kwargs):
        if not self.tokens: raise ValueError('请先登录云盘')
        if time.time()>=self.tokens.get('expires_at',0):
            refresh = self.tokens.get('refresh_token')
            if not refresh: raise ValueError('登录过期，请重新登录')
            response = requests.post(self.settings['token'],data={
                'client_id':self.client['client_id'],'refresh_token':refresh,
                'grant_type':'refresh_token',**self._secret()},timeout=30)
            self._check(response)
            self._store(response.json())
        headers = {'Authorization':'Bearer '+self.tokens['access_token']}
        content_type = kwargs.pop('content_type',None)
        if content_type: headers['Content-Type'] = content_type
        response = requests.request(method,url,headers=headers,timeout=120,**kwargs)
        self._check(response)
        return response

    def books(self):
        items = []
        if self.provider=='Google Drive':
            params = {'spaces':'appDataFolder','q':"trashed = false and mimeType = 'application/zip'",
                'fields':'nextPageToken,files(id,name,modifiedTime,description)','pageSize':100}
            while True:
                value = self._request('GET','https://www.googleapis.com/drive/v3/files',params=params).json()
                items += [{'id':v['id'],'name':v.get('description') or v['name'],'key':v['name'],'modified':v.get('modifiedTime','')} for v in value.get('files',[])]
                if not value.get('nextPageToken'): break
                params['pageToken'] = value['nextPageToken']
        else:
            url = 'https://graph.microsoft.com/v1.0/me/drive/special/approot/children'
            while url:
                value = self._request('GET',url).json()
                items += [{'id':v['id'],'name':v['name'],'key':v['name'],'modified':v.get('lastModifiedDateTime','')} for v in value.get('value',[]) if v['name'].endswith('.spr.zip')]
                url = value.get('@odata.nextLink')
                if url and not url.startswith('https://graph.microsoft.com/'): raise ValueError('无效的云盘分页地址')
        return sorted(items,key=lambda v:v['modified'],reverse=True)

    def upload(self,key,name,data):
        if len(data)>200*1024*1024: raise ValueError('单次同步限制 200 MB，请拆分大文件')
        if self.provider=='Google Drive':
            filename = key+'.spr.zip'
            existing = next((b for b in self.books() if b['key']==filename),None)
            metadata = {'name':filename,'description':name}
            if not existing: metadata['parents'] = ['appDataFolder']
            boundary = 'spr-'+secrets.token_hex(16)
            body = (f'--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'.encode()+json.dumps(metadata).encode()+
                f'\r\n--{boundary}\r\nContent-Type: application/zip\r\n\r\n'.encode()+data+f'\r\n--{boundary}--\r\n'.encode())
            url = 'https://www.googleapis.com/upload/drive/v3/files'+('/'+existing['id'] if existing else '')
            self._upload_multipart(url,existing,boundary,body)
        else:
            filename = quote(name[:-4][:120]+'--'+key+'.spr.zip',safe='')
            self._request('PUT','https://graph.microsoft.com/v1.0/me/drive/special/approot:/'+filename+':/content',data=data)

    def _upload_multipart(self,url,existing,boundary,body):
        self._request('PATCH' if existing else 'POST',url,params={'uploadType':'multipart'},data=body,
            content_type='multipart/related; boundary='+boundary)

    def download(self,item):
        if self.provider=='Google Drive':
            return self._request('GET','https://www.googleapis.com/drive/v3/files/'+quote(item['id'],safe=''),params={'alt':'media'}).content
        # Graph's /content redirect is handled by requests, which strips Authorization cross-host.
        return self._request('GET','https://graph.microsoft.com/v1.0/me/drive/items/'+quote(item['id'],safe='')+'/content').content

    def logout(self):
        if keyring.get_password(SERVICE,self.provider): keyring.delete_password(SERVICE,self.provider)
        self.tokens = {}
