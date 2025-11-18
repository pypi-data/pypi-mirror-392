class AllHeadres:

    def set_token( self, token:str):
        self.token = token


    def header_phone_has_app(self):
    # header check_number
        header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fa",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "Referer": "https://my.irancell.ir/invite",
        "x-app-version": "9.62.0",
        "Origin": "https://my.irancell.ir",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Authorization": self.token,
        "Connection": "keep-alive",
        "Priority": "u=0",
    }
        
        return header



    def header_invite_to_MyIransell(self):
    # header invite to MyIransell
        header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fa",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "Referer": "https://my.irancell.ir/invite/confirm",
        "x-app-version": "9.62.0",
        "Origin": "https://my.irancell.ir",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Authorization": self.token,
        "Connection": "keep-alive",
        "Priority": "u=0",
        }
        
        return header



    def header_my_info(self):
        header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fa",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://my.irancell.ir/sim/profile",
        "x-app-version": "9.62.0",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Authorization": self.token,
        "Connection": "keep-alive"
    }
    
        return header
    


    def header_View_Internet_packages(self):
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fa",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://my.irancell.ir/",
        "x-app-version": "9.62.0",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Authorization": self.token,
        "Connection": "keep-alive"
    }
        return headers
    

    @staticmethod
    def header_View_music_default():
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://my.irancell.ir/",
        "Origin": "https://my.irancell.ir",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Connection": "keep-alive"
    }
        
        return headers


    @staticmethod
    def header_Viewing_command_codes():
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://my.irancell.ir/",
        "Origin": "https://my.irancell.ir",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Connection": "keep-alive"
    }
        
        return headers