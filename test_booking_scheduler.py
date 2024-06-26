from datetime import datetime, timedelta
import unittest

from booking_scheduler import BookingScheduler
from schedule import Customer, Schedule
from test_communication import TestSmsSender, TestMailSender

CAPACITY_PER_HOUR = 3
UNDER_CAPACITY = 1
OVER_CAPACITY = 4


class TestableBookingScheduler(BookingScheduler):
    def __init__(self, capacity_per_hour, datetime):
        super().__init__(capacity_per_hour)
        self._date_time = datetime

    def get_now(self):
        return datetime.strptime(self._date_time, "%Y/%m/%d %H:%M")



class TestBookingScheduler(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.booking_scheduler = BookingScheduler(CAPACITY_PER_HOUR)
        self.test_sms_sender = TestSmsSender()
        self.booking_scheduler.set_sms_sender(self.test_sms_sender)
        self.test_mail_sender = TestMailSender()
        self.booking_scheduler.set_mail_sender(self.test_mail_sender)

    def test_예약은_정시에만_가능하다_정시가_아닌경우_예약불가(self):
        schedule = Schedule(NOT_ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)

        with self.assertRaises(ValueError):
            self.booking_scheduler.add_schedule(schedule)

    def test_예약은_정시에만_가능하다_정시인_경우_예약가능(self):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)
        self.booking_scheduler.add_schedule(schedule)

        self.assertEqual(True, self.booking_scheduler.has_schedule(schedule))

    def test_시간대별_인원제한이_있다_같은_시간대에_Capacity_초과할_경우_예외발생(self):
        schedule = Schedule(ON_THE_HOUR, CAPACITY_PER_HOUR, CUSTOMER)
        self.booking_scheduler.add_schedule(schedule)

        new_schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)
        with self.assertRaises(ValueError) as context:
            self.booking_scheduler.add_schedule(new_schedule)

        self.assertEqual('Number of people is over restaurant capacity per hour', str(context.exception))

    def test_시간대별_인원제한이_있다_같은_시간대가_다르면_Capacity_차있어도_스케쥴_추가_성공(self):
        schedule = Schedule(ON_THE_HOUR, CAPACITY_PER_HOUR, CUSTOMER)
        self.booking_scheduler.add_schedule(schedule)

        diff_time = ON_THE_HOUR + timedelta(hours=1)
        new_schedule = Schedule(diff_time, CAPACITY_PER_HOUR, CUSTOMER)
        self.booking_scheduler.add_schedule(new_schedule)

        self.assertEqual(True, self.booking_scheduler.has_schedule(new_schedule))

    def test_예약완료시_SMS는_무조건_발송(self):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)
        self.booking_scheduler.add_schedule(schedule)

        self.assertEqual(True, self.test_sms_sender.is_send_method_called())

    def test_이메일이_없는_경우에는_이메일_미발송(self):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)
        self.booking_scheduler.add_schedule(schedule)

        self.assertEqual(0, self.test_mail_sender.get_count_send_mail_called())

    def test_이메일이_있는_경우에는_이메일_발송(self):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER_WITH_MAIL)
        self.booking_scheduler.add_schedule(schedule)

        self.assertEqual(1, self.test_mail_sender.get_count_send_mail_called())

    def test_현재날짜가_일요일인_경우_예약불가_예외처리(self):
        self.booking_scheduler = TestableBookingScheduler(CAPACITY_PER_HOUR, "2024/06/09 11:00")
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER_WITH_MAIL)
        with self.assertRaises(ValueError) as context:
            self.booking_scheduler.add_schedule(schedule)
        self.assertEqual("Booking system is not available on Sunday", str(context.exception))

    def test_현재날짜가_일요일이_아닌경우_예약가능(self):
        self.booking_scheduler = TestableBookingScheduler(CAPACITY_PER_HOUR, "2024/06/10 11:00")
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER_WITH_MAIL)

        self.booking_scheduler.add_schedule(schedule)

        self.assertEqual(True, self.booking_scheduler.has_schedule(schedule))


NOT_ON_THE_HOUR = datetime.strptime("2024/06/14 11:20", "%Y/%m/%d %H:%M")
ON_THE_HOUR = datetime.strptime("2024/06/14 11:00", "%Y/%m/%d %H:%M")

CUSTOMER = Customer(name="no_name", phone_number="010-1234-1111")

CUSTOMER_WITH_MAIL = Customer("no_name", "010-1234-1111", "abcd@naver.com")

if __name__ == '__main__':
    unittest.main()
