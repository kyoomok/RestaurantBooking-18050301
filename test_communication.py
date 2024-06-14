from unittest import TestCase

from communication import SmsSender, MailSender


class TestSmsSender(SmsSender):
    def send(self, schedule):
        print("테스트용 SmsSender에서 send method 실행")
        self.__send_method_is_called = True

    def is_send_method_called(self):
        return self.__send_method_is_called


class TestMailSender(MailSender):
    def __init__(self):
        self.__count_send_mail_called = 0

    def send(self):
        self.__count_send_mail_called += 1

    def get_count_send_mail_called(self):
        return self.__count_send_mail_called
