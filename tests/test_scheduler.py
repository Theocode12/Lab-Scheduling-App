from dotenv import dotenv_values
from datetime import timedelta
from models import Scheduler
from util import (
    extract_values_from_data,
    csv_parser,
    convert_str_to_timedelta_obj,
    shuffle_ls,
)
import unittest


class TestScheduler(unittest.TestCase):
    def setUp(self) -> None:
        file = dotenv_values().get("STUB_FILE", None)
        data = csv_parser(file)
        self.students = extract_values_from_data(data, "Name")

    def test_correct_start_time_initialization(self):
        sh = Scheduler("12:00:00", "1:00:00", "00:30:00", self.students)
        self.assertIsInstance(sh.start_time, timedelta)

    def test_incorrect_start_time_initialization(self):
        with self.assertRaises(ValueError):
            Scheduler("12,00,00", "1:00:00", "00:30:00", self.students)

    def test_correct_stop_time_initialization(self):
        sh = Scheduler("12:00:00", "1:00:00", "00:30:00", self.students)
        self.assertIsInstance(sh.start_time, timedelta)

    def test_incorrect_stop_time_initialization(self):
        with self.assertRaises(ValueError):
            Scheduler("12:00:00", "1,00:00", "00:30:00", self.students)

    def test_correct_session_duration_initialization(self):
        sh = Scheduler("12:00:00", "1:00:00", "00:30:00", self.students)
        self.assertIsInstance(sh.start_time, timedelta)

    def test_incorrect_session_duration_initialization(self):
        with self.assertRaises(ValueError):
            Scheduler("12:00:00", "1:00:00", "30:00", self.students)

    def test_correct_student_intialisation(self):
        sh = Scheduler("12:00:00", "1:00:00", "00:30:00", self.students)
        self.assertIsInstance(sh.students, list)

    def test_incorrect_student_intialisation(self):
        with self.assertRaises(TypeError):
            Scheduler("12:00:00", "1:00:00", "00:30:00", "lisa")
            Scheduler("12:00:00", "1:00:00", "00:30:00", 1)

    def test_correct_no_per_student_intialisation(self):
        sh = Scheduler("12:00:00", "1:00:00", "00:30:00", self.students, "4")
        self.assertIsInstance(sh.no_per_group, int)

    def test_incorrect_no_per_student_intialisation(self):
        with self.assertRaises(TypeError):
            Scheduler("12:00:00", "1:00:00", "00:30:00", "lisa")
            Scheduler("12:00:00", "1:00:00", "00:30:00", 1)

    def test_get_session_times(self):
        sh = Scheduler("12:00:00", "13:00:00", "00:30:00", self.students, "4")
        time_list = sh.get_session_times()
        self.assertEqual(len(time_list), 2)
        self.assertIsInstance(time_list[0], timedelta)

        sh = Scheduler("12:00:00", "11:00:00", "00:30:00", self.students, "4")
        self.assertListEqual(sh.get_session_times(), [])

    def test_get_no_of_students_per_session_with_sub_grouping(self):
        students = ["lisa, chin-chen, lubah, chris"]
        sh = Scheduler("10:30:00", "12:30:00", "00:30:00", students, "4")

        # Tests with objects no_of_session and no_of_student
        self.assertEqual(sh.get_no_of_students_per_session(), 4)

        # Tests with external no_of_session and no_of_student
        self.assertEqual(sh.get_no_of_students_per_session(3, 13), 4)

    def test_get_no_of_students_per_session_without_sub_grouping(self):
        students = ["lisa, chin-chen, lubah, chris"]
        sh = Scheduler("10:30:00", "12:30:00", "00:30:00", students)

        # Tests with objects no_of_session and no_of_student
        self.assertEqual(sh.get_no_of_students_per_session(), 1)

        # Tests with external no_of_session and no_of_student
        self.assertEqual(sh.get_no_of_students_per_session(3, 13), 5)

    def test_create_group_template_with_no_per_group(self):
        sh = Scheduler("10:30:00", "12:30:00", "00:30:00", self.students, "4")
        template = sh.create_group_template(3)
        self.assertSequenceEqual(template, [[0, 1, 2]])

        template = sh.create_group_template(10)
        self.assertSequenceEqual(template, [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]])

    def test_create_group_template_with_no_number_per_group(self):
        sh = Scheduler("10:30:00", "12:30:00", "00:30:00", self.students)
        template = sh.create_group_template(len(sh.students))
        self.assertEqual(template, [])

    def test_create_group(self):
        students = ["Dome", "John", "Lisa", "Tristen"]
        sh = Scheduler("10:30:00", "11:30:00", "00:30:00", students, "2")
        group_template = sh.create_group_template(len(students))
        groups = sh.create_group(students, group_template)
        self.assertIsInstance(groups, dict)
        self.assertDictEqual(
            groups, {"group 0": ["Dome", "John"], "group 1": ["Lisa", "Tristen"]}
        )

    def test_session_scheduling(self):
        pass

    def test_generate_schedules(self):
        pass


class TestUtilities(unittest.TestCase):
    def test_convert_str_to_timedelta_obj_with_correct_params(self):
        td_obj = convert_str_to_timedelta_obj("12:00:00")
        self.assertIsInstance(td_obj, timedelta)

    def test_convert_str_to_timedelta_obj_with_wrong_params(self):
        with self.assertRaises(ValueError):
            convert_str_to_timedelta_obj("12:00")
            convert_str_to_timedelta_obj("a:12:a")

    def test_shuffle_ls(self):
        ls = [3, 4, 5]
        new_ls = shuffle_ls(ls)
        self.assertNotEqual(ls, new_ls)


if __name__ == "__main__":
    unittest.main()
