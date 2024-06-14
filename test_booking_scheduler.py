from datetime import datetime, timedelta
import unittest

from booking_scheduler import BookingScheduler
from schedule import Customer, Schedule
from test_communication import TestSmsSender

CAPACITY_PER_HOUR = 3
UNDER_CAPACITY = 1
OVER_CAPACITY = 4

NOT_ON_THE_HOUR = datetime.strptime("2024/06/14 11:20", "%Y/%m/%d %H:%M")
ON_THE_HOUR = datetime.strptime("2024/06/14 11:00", "%Y/%m/%d %H:%M")
CUSTOMER = Customer(name="no_name", phone_number="010-1234-1111")


class TestBookingScheduler(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.booking_scheduler = BookingScheduler(CAPACITY_PER_HOUR)
        self.test_sms_sender = TestSmsSender()

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
        self.booking_scheduler.set_sms_sender(self.test_sms_sender)
        self.booking_scheduler.add_schedule(schedule)

        self.assertEqual(True, self.test_sms_sender.is_send_method_called())

    def test_이메일이_없는_경우에는_이메일_미발송(self):
        pass

    def test_이메일이_있는_경우에는_이메일_발송(self):
        pass

    def test_현재날짜가_일요일인_경우_예약불가_예외처리(self):
        pass

    def test_현재날짜가_일요일이_아닌경우_예약가능(self):
        pass


if __name__ == '__main__':
    unittest.main()
