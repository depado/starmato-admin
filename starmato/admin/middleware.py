import re
#
from django import http
from django.http import Http404

# based on http://code.djangoproject.com/ticket/3777#comment:4
class FilterPersistMiddleware(object):

    def process_request(self, request):

        if '/argamato/' not in request.path:
            return None

        if not request.META.has_key('HTTP_REFERER'):
            return None
        
        popup = 'pop=1' in request.META['QUERY_STRING']
        path = request.path[request.path.find('/argamato'):len(request.path)]
        query_string = request.META['QUERY_STRING']
        session = request.session

        if session.get('redirected', False):#so that we dont loop once redirected
            del session['redirected']
            return None

        referrer = request.META['HTTP_REFERER'].split('?')[0]
        referrer = referrer[referrer.find('/argamato'):len(referrer)]
        key = 'key'+path.replace('/','_')

        if popup:
            key = 'popup'+path.replace('/','_')

        if path == referrer or "arlist_id" in query_string:
        #We are in same page as before or requesting a saved list
            if query_string == '': #Filter is empty, delete it
                if session.get(key, False):
                    del session[key]
                return None
            request.session[key] = query_string
        else: #We are are coming from another page, restore filter if available
            if session.get(key, False):
                if query_string == '': #Filter is empty, retrieve it
                    sub = re.search("q=[^&]+&?", request.session.get(key))
                    if sub is not None:
                        query_string = request.session.get(key).replace(sub.group(0), "")
                    else:
                        query_string = request.session.get(key)
                redirect_to = request.path+'?'+query_string
                request.session['redirected'] = True
                return http.HttpResponseRedirect(redirect_to)
        return None
