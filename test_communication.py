from unittest import TestCase

from communication import SmsSender


class TestSmsSender(SmsSender):
    def send(self, schedule):
        print("테스트용 SmsSender에서 send method 실행")
        self.__send_method_is_called = True

    def is_send_method_called(self):
        return self.__send_method_is_called