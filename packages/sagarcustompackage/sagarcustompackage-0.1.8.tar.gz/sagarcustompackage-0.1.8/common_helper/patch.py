import requests
import ssl
from requests.adapters import HTTPAdapter

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

def apply_patch():
    _session_init = requests.Session.__init__

    def _patched_init(self, *args, **kwargs):
        _session_init(self, *args, **kwargs)
        self.mount("https://", TLSAdapter())

    # Only patch once
    if getattr(requests.Session, "_patched_tls", False) is False:
        requests.Session.__init__ = _patched_init
        requests.Session._patched_tls = True
