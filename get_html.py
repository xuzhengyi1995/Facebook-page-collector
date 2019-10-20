# use urllib to get resources
# XU,Zhengyi 23/08/2017

import socket
import urllib.error
import urllib.request


class GetHtml:
    '''
    Ggeneric class for request a web resource.
    Can set header and use proxy.
    Can get data and cookies from the server.
    Method:
        set(url=String,header=Dict,retryTimes=int)
        get(getcookie=Boolean,t_out=int,use_proxy=boolean)
    PROXY are in proxy.txt
    You can also make it get some proxy from a database.
    '''

    def __init__(self, Proxy=False):
        self._url = 'http://www.google.com'
        if(Proxy):
            proxy_file = open("./proxy.txt")
            x = proxy_file.readline()
            self.proxy = []
            while(x):
                self.proxy.append(x[:-1])
                x = proxy_file.readline()

    def set(self, url, header=None, retryTimes=10, data=None):
        '''
        url: url to get
        header: as {'Accept':'application/json'}
        '''
        self._url = url
        self._header = header
        self._retryTimes = retryTimes
        self._data = data.encode('utf-8') if data else None

    def get(self, getcookie=False, t_out=15, use_proxy=False, method=None):
        req = urllib.request.Request(self._url, method=method, data=self._data)
        if(self._header):
            for key in self._header:
                req.add_header(key, self._header[key])

        is_error = True
        s_retry = 0
        r_data = None
        cookies = ""
        while(is_error and s_retry < 10):
            try:
                if(not use_proxy):
                    r = urllib.request.urlopen(req, timeout=t_out)
                    r_data = r.read()
                    cookies = ""
                    for name, content in r.getheaders():
                        if(name == 'Set-Cookie'):
                            cookies += content.split(";")[0] + '; '
                    cookies = cookies[:-2]
                else:
                    is_proxy_ok = False
                    for i in range(len(self.proxy)):
                        try:
                            p_i = (hash(self._url) + i) % len(self.proxy)
                            req.set_proxy(host=self.proxy[p_i], type="http")
                            req.set_proxy(host=self.proxy[p_i], type="http")
                            print("Proxy", req.has_proxy())
                            if(req.has_proxy()):
                                r = urllib.request.urlopen(req, timeout=t_out)
                                r_data = r.read()

                                cookies = ""
                                for name, content in r.getheaders():
                                    if(name == 'Set-Cookie'):
                                        cookies += content.split(";")[0] + '; '
                                cookies = cookies[:-2]

                                is_proxy_ok = True
                                break
                        except urllib.error.HTTPError as err:
                            print("PROXY %s" % str(err))
                            if(err.code == 404):
                                if(getcookie):
                                    return (None, "")
                                return None
                        except:
                            print("PROXY %d ERROR, CHANGE PROXY..." % p_i)
                    if(not is_proxy_ok):
                        req = urllib.request.Request(self._url)
                        if(self._header):
                            for key in self._header:
                                req.add_header(key, self._header[key])
                        r = urllib.request.urlopen(req, timeout=t_out)
                        r_data = r.read()
                        cookies = ""
                        for name, content in r.getheaders():
                            if(name == 'Set-Cookie'):
                                cookies += content.split(";")[0] + '; '
                        cookies = cookies[:-2]
                is_error = False
            except urllib.error.HTTPError as err:
                print("LOCAL %s" % str(err))
                if(err.code == 404):
                    if(getcookie):
                        return (None, "")
                    return None
                is_error = True
                s_retry += 1
                print('HTTPError Retry %d times' % s_retry)
            except urllib.error.URLError as err:
                is_error = True
                s_retry += 1
                print('URLError Retry %d times' % s_retry)
                print(err.reason)
            except socket.timeout:
                is_error = True
                s_retry += 1
                print('SOCKETError Retry %d times' % s_retry)
            except:
                is_error = True
                s_retry += 1
                print('ConnectionError Retry %d times' % s_retry)
        if(getcookie):
            return (r_data, cookies)
        return r_data
