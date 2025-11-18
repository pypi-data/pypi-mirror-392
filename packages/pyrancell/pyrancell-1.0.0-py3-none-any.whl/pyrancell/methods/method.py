import requests
import json

class Methods:
    
    def phone_has_app(self ,api:str , phone:str , header:dict) ->bool:
        
        data = {
        "application_name": "NGMI",
        "friend_number": "98"+phone
        }
        respance = requests.post(url=api , json=data , headers=header)
        if respance.status_code == 200 and json.loads(respance.text)['message'] == "done":
            return False
        return True



    def send_invite(self,api:str, phone: str , header:dict) ->dict:
        data = {
        "application_name": "NGMI",
        "friend_number": "98"+phone
        }
        respance = requests.post(url=api , json=data , headers=header)
        if respance.status_code == 200:
            return json.loads(respance.text)



    def my_info(self ,api:str, header:dict) ->dict:
        respance = requests.get(url=api , headers=header)
        if respance.status_code == 200:
            return json.loads(respance.text)


    def first_name(self,api:str, header:dict) ->str:
        respance = self.my_info(api=api,header=header)
        return respance["first_name"]


    def last_name(self ,api:str, header:dict) ->str:
        respance = self.my_info(api=api,header=header)
        return respance["last_name"]


    def get_email(self,api:str, header:dict) ->str:
        respance = self.my_info(api=api,header=header)
        return respance["email"]


    def get_address_home(self,api:str, header:dict) ->str:
        respance = self.my_info(api=api,header=header)
        return respance["address"]


    def activation_date(self,api:str, header:dict) ->str:
        respance = self.my_info(api=api,header=header)
        return respance["activation_date"]


    def get_phone_home(self,api:str, header:dict) ->str:
        respance = self.my_info(api=api,header=header)
        return respance["contact_number"]


    def sim_card_serial_number(self,api:str, header:dict) ->str:
        respance = self.my_info(api=api,header=header)
        return respance["kit_number"]


    def state_simcard(self,api:str, header:dict) ->str:
        respance = self.my_info(api=api,header=header)
        return respance["operation_status"]


    def View_Internet_packages(self,api:str, header:dict) ->dict:
        params = {
        "type": "data",
        "category": "normal"
        }
        respance = requests.get(url=api, headers=header , params=params)
        if respance.status_code == 200:
            return json.loads(respance.text)
    


    def View_music_default(self,api:str, header:dict) ->dict:
        params = {
        "v": "20250831171938970372"
        }
        respance = requests.get(url=api , headers=header , params=params)
        if respance.status_code == 200:
            return json.loads(respance.text)



    def off_sim_card(self) -> bool:
        """غیرفعال کردن سیم‌کارت (اگر ممکن است). برمی‌گرداند True در صورت موفقیت."""


    def get_device(self) -> dict:
        """اطلاعات دستگاه (مدل، OS، آخرین لاگین و...) به صورت دیکشنری."""



    def Viewing_command_codes(self,api:str, header:dict) ->dict:
        params = {
            "v": "20250203124237193931"
            }
        respance = requests.get("https://cdn-ngmy.irancell.ir/config/ussd.json" , headers=header , params=params)
        if respance.status_code == 200:
            return json.loads(respance.text)