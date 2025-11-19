import requests


class Http:
    def __init__(self, header):
        if (not header):
            self.__header = {}
        else:
            self.__header = header

    def get(self, url, log=False):
        if log:
            print('get请求:', url)
        res = requests.get(
            url=url,
            headers=self.__header
        )
        if log:
            print(res.text)
        return res.text

    def postForm(self, url, data):
        self.__header["Content-Type"] = "application/x-www-form-urlencoded"
        res = requests.post(url=url,
                            headers=self.__header,
                            data=data)
        print(res.text)
        return res.text

    def post(self, url, json, log=False):
        if log:
            print('post请求:', url, json)
        self.__header["Content-Type"] = "application/json"
        res = requests.post(url=url,
                            headers=self.__header,
                            json=json)
        if log:
            print(res.text)
        return res.text

    def upload(self, url, files, data, log=False):
        if log:
            print('upload请求:', url, files)
        del self.__header["Content-Type"]
        res = requests.request("POST", url, headers=self.__header, data=data, files=files)
        if log:
            print(res.text)
        return res.text

    def set_header(self, header):
        for key in header:
            self.__header[key] = header[key]

    def set_header(self, key , value):
        self.__header[key] = value