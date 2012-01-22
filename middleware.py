"""
This middleware class updates REMOTE_ADDR request metadata 
with the HTTP_CF_CONNECTING_IP value added by CloudFlare in order
to make the end-user's actual IP address available to the application.

Activate by adding the module to MIDDLEWARE_CLASSES in your Django project's settings.
"""

import netaddr

class CFMiddleware(object):
    "Updates REMOTE_ADDR for requests proxied through CloudFlare."
    
    def __init__(self):
        self.cloudflare_ip_header = 'HTTP_CF_CONNECTING_IP'

    def has_cf_header(self, request):
        "Checks whether request has recognized CloudFlare header."
        return self.cloudflare_ip_header in request.META

    def process_request(self, request):
        "Overwwrites REMOTE_ADDR with user's real IP from CloudFlare header."
        if self.has_cf_header(request):
            request.META['REMOTE_ADDR'] = request.META[self.cloudflare_ip_header]