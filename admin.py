"""
This module extends the Django comments admin interface by adding 
an action for reporting spam comments to CloudFlare.

The following constants should be added to your Django project's settings:
  - CLOUDFLARE_API_KEY (your API key from CloudFlare)
  - CLOUDFLARE_EMAIL (the email address you use to log into CloudFlare)
  
Ensure that actual end-user IP addresses are being saved to your database and 
not the IP addresses of the CloudFlare servers through which requests are proxied. 
CloudFlare passes the user's own IP address in a HTTP_CF_CONNECTING_IP header.
"""

from django.contrib import admin
from django.contrib.comments.admin import CommentsAdmin
from django.contrib.comments.models import Comment
from django.conf import settings
import simplejson as json
import httplib2
import urllib
import sys
import traceback
import logging

logger = logging.getLogger(__name__)

class CFCommentsAdmin(CommentsAdmin):
    
    # Add comment IDs to display for reference
    list_display = ['id', 'name', 'ip_address','content_type', 'object_pk', 'content_object', 'is_public', 'is_removed']
    
    def report_spam_to_cloudflare(modeladmin, request, queryset):
        "Reports selected comments as spam to CloudFlare."
        
        def stringify_params(params):
            "Converts a dictionary of query params into a URL-encoded string."
            return '&'.join(['%s=%s' % (urllib.quote(k), urllib.quote(v)) for k, v in params.items()])
        
        def get_comment_details(comment):
            "Constructs dictionary of comment details to be reported."
            return {
                'a': obj.name,
                'am': obj.user_email,
                'ip': obj.ip_address,
                'con': obj.comment[:100]
                }
        
        def report_spam_incident(comment_info):
            "Sends spam incident to CloudFlare over HTTPS."
            
            cf_url = 'https://www.cloudflare.com/ajax/external-event.html'
            cf_event = 'CF_USER_SPAM'
            cf_token = settings.CLOUDFLARE_API_KEY
            cf_email = settings.CLOUDFLARE_EMAIL
            
            request_params = {
                'u': cf_email,
                'tkn': cf_token,
                'evnt_t': cf_event,
                'evnt_v': json.dumps(comment_info)
            }
            
            request_url = '%s?%s' % (cf_url, stringify_params(request_params))
            http = httplib2.Http(disable_ssl_certificate_validation=True)
            response = json.loads(http.request(request_url)[1])
            
            if response['result'] == 'success':
                logger.info('CloudFlare // Reported spammer: %s %s' % (comment_info['am'], comment_info['ip']))
                return True
            else:
                logger.warning('CloudFlare // Failed to report spammer: %s' % (response['msg']))
                return False
        
        try:
            reported = []
        
            for obj in queryset:
                
                comment_info = get_comment_details(obj)
                successful = report_spam_incident(comment_info)

                if successful:
                    reported.append(str(obj.id))

            modeladmin.message_user(request, '%s spam comment(s) reported to CloudFlare: %s' % (len(reported), ', '.join(reported)))
            unreported = [str(obj.id) for obj in queryset if str(obj.id) not in reported]
            if unreported:
                logger.warning('CloudFlare // Did not report comments: %s' % (', '.join(unreported)))
        except:
            logger.error("Error on line " + str(traceback.tb_lineno(sys.exc_info()[2])) + ": " + str(sys.exc_info()[1]) + ": " + str(sys.exc_info()[0]))
            modeladmin.message_user(request, 'Could not report spam to CloudFlare.')

    report_spam_to_cloudflare.short_description = 'Report spam to CloudFlare'
    actions = [report_spam_to_cloudflare]

admin.site.unregister(Comment)
admin.site.register(Comment, CFCommentsAdmin)