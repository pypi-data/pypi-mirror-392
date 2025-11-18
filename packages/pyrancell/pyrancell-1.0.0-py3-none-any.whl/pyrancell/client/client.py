from ..headers.header import AllHeadres
from ..methods.method import Methods
from ..apis.api import *


class Client:
    def __init__(self , token:str , platform:str="web"):
        if bool(token):
            self.token = token
            self.platform = platform
            self.methods = Methods()
            self.haedrs = AllHeadres()
            self.haedrs.set_token(self.token)


    def __str__(self):
        return f"{self.__class__.__name__}({self.token} , {self.platform})"


    def phone_has_app(self , phone:str) -> bool:
        if phone.startswith("0"):
            phone = phone[1:]
        return self.methods.phone_has_app(api=api_phone_has_app ,phone=phone , header=self.haedrs.header_phone_has_app())


    def send_invite(self, phone:str) -> dict:
        if phone.startswith("0"):
            phone = phone[1:]
        return self.methods.send_invite(api=api_send_invite ,phone=phone , header=self.haedrs.header_invite_to_MyIransell())


    def my_info(self) -> dict:
        return self.methods.my_info(api=api_my_info,header=self.haedrs.header_my_info())


    def first_name(self) -> str:
        return self.methods.first_name(api=api_my_info,header=self.haedrs.header_my_info())


    def last_name(self) -> str:
        return self.methods.last_name(api=api_my_info,header=self.haedrs.header_my_info())


    def get_email(self) -> str:
        return self.methods.get_email(api=api_my_info,header=self.haedrs.header_my_info())


    def get_address_home(self) -> str:
        return self.methods.get_address_home(api=api_my_info,header=self.haedrs.header_my_info())


    def activation_date(self) -> str:
        return self.methods.activation_date(api=api_my_info,header=self.haedrs.header_my_info())


    def get_phone_home(self) -> str:
        return self.methods.get_phone_home(api=api_my_info,header=self.haedrs.header_my_info())


    def sim_card_serial_number(self) -> str:
        return self.methods.sim_card_serial_number(api=api_my_info,header=self.haedrs.header_my_info())


    def state_simcard(self) -> str:
        return self.methods.state_simcard(api=api_my_info,header=self.haedrs.header_my_info())


    def View_Internet_packages(self) -> dict:
        return self.methods.View_Internet_packages(api=api_View_Internet_packages,header=self.haedrs.header_View_Internet_packages())


    def View_music_default(self) -> dict:
        return self.methods.View_music_default(api=api_View_music_default,header=self.haedrs.header_View_music_default())


    def Viewing_command_codes(self) -> dict:
        return self.methods.Viewing_command_codes(api=api_Viewing_command_codes,header=self.haedrs.header_Viewing_command_codes())