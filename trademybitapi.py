import json
import urllib2
import urlparse

class TradeMyBitAPI(object):
    """ TradeMyBit API wrapper """
    def __init__(self, api_key = None, base_url='https://pool.trademybit.com/api/'):
        self.base_url = base_url
        self.api_key = api_key
        self.opener = urllib2.build_opener()

        self.opener.addheaders = [('User-agent', 'TradeMyBitAPI')]

    def command(self, command, arg = None):
        """ Send a command, receive the JSON response and decode it. """
        url = urlparse.urljoin(self.base_url, '%s?key=%s') % (command, self.api_key)
        obj = json.load(self.opener.open(url))
        # print obj # DEBUG
        return obj

    def __getattr__(self, attr):
        """ Allow us to make command calling methods.

        >>> tmb = TradeMyBitAPI('secret-api-key')
        >>> tmb.bestalgo()
        >>> tmb.hashinfo()

        """
        def out(arg=None):
            return self.command(attr, arg)
        return out
