from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import timedelta
from dotenv import set_key, dotenv_values
from typing import List, Dict, Any, Optional, Union, Callable
from itertools import chain
from util import shuffle_ls, convert_str_to_timedelta_obj, check_valid_email
from os import getenv, path
import argparse
import json
import math
import smtplib
import ssl


class Scheduler:
    """
    Creates full scheduling of student into different sessions given a total duration and session duration
    """

    def __init__(
        self,
        start_time: str,
        end_time: str,
        session_duration: str,
        students: List[str],
        no_per_group: Optional[str] = None,
    ):
        """
        :param start_time: start time
        :param end_time: end time
        :param session_duration: session duration
        :param students: list of students
        :param no_per_group: (Optional) number of students per group
        :return:
        """
        self.start_time: str = start_time
        self.end_time: str = end_time
        self.session_duration: str = session_duration
        self.students: List[str] = students
        self.no_per_group: str = no_per_group

    @property
    def start_time(self):
        return self.__start_time

    @start_time.setter
    def start_time(self, start_time: str):
        if type(start_time) is not str:
            raise TypeError("start_time must be string")
        timedelta_obj = convert_str_to_timedelta_obj(start_time)
        self.__start_time = timedelta_obj

    @property
    def end_time(self):
        return self.__end_time

    @end_time.setter
    def end_time(self, end_time: str):
        if type(end_time) is not str:
            raise TypeError("end_time must be string")
        timedelta_obj = convert_str_to_timedelta_obj(end_time)
        self.__end_time = timedelta_obj

    @property
    def session_duration(self):
        return self.__session_duration

    @session_duration.setter
    def session_duration(self, session_duration: str):
        if type(session_duration) is not str:
            raise TypeError("session_duration must be string")
        timedelta_obj = convert_str_to_timedelta_obj(session_duration)
        self.__session_duration = timedelta_obj

    @property
    def students(self):
        return self.__students

    @students.setter
    def students(self, students: List[str]):
        if type(students) is not list:
            raise TypeError("students must be List[str]")
        self.__students = students

    @property
    def no_per_group(self):
        return self.__no_per_group

    @no_per_group.setter
    def no_per_group(self, no_per_group: str):
        if no_per_group is not None and type(no_per_group) is not str:
            raise TypeError("no_per_group must be str or None")
        self.__no_per_group = int(no_per_group) if no_per_group else no_per_group

    def get_session_times(self):
        """
        Calculate all the possible session times
        """
        time_list = []
        current_time = self.start_time
        while current_time < self.end_time:

            time_list.append(current_time)
            current_time += self.session_duration
        return time_list

    def get_no_of_students_per_session(
        self, no_of_sessions: Optional[int] = None, no_of_students: Optional[int] = None
    ) -> int:
        """
        calculates the number of student per session. if no_per_group is specified it takes priority i.e every session
        must have multiples of the number of group only if no_of_student is > no_of_group
        :param no_of_sessions: number of session
        :param no_of_students: number of student
        :return: number of student for each group
        """

        no_of_sessions = no_of_sessions or len(self.get_session_times())
        no_of_students = no_of_students or len(self.students)
        if not self.no_per_group:
            if no_of_students < no_of_sessions:
                no_of_students_per_session = 1
            else:
                no_of_students_per_session = math.ceil(no_of_students / no_of_sessions)

        else:
            if no_of_students < no_of_sessions:
                no_of_students_per_session = self.no_per_group
            else:
                no_of_students_per_session = math.ceil(no_of_students / no_of_sessions)
                no_of_students_per_session += -(
                    no_of_students_per_session % self.no_per_group
                )

        return no_of_students_per_session

    def create_group_template(self, no_of_students: int) -> List[List[int]]:
        """
        Creates a list of list(groups) which contains the indexes of student to be grouped.
        :param no_of_students: number of student/ number of indices
        :return: a list of list which are the groupings
        """

        group_template = []
        students_index = list(range(no_of_students))

        students_grouped = 0
        if self.no_per_group:
            while students_grouped < len(students_index):
                group = students_index[
                    students_grouped : students_grouped + self.no_per_group
                ]

                group_template.append(group)

                students_grouped = students_grouped + self.no_per_group

        return group_template

    def create_group(
        self, students, grouping_template: List[List[int]]
    ) -> Dict[str, List[str]]:
        """
        Groups the students using the groups_listing
        :param grouping_template: list of how the students are to be grouped
        :return: returns the grouping of the students
        """
        if self.no_per_group is None:
            raise TypeError("Please specify number per group")

        groups: dict[str, list[str]] = {}

        if len(students) != len(list(chain(*grouping_template))):
            raise ValueError(
                "The number of students is not the same as number of students to be grouped"
            )

        for i in range(len(grouping_template)):
            group = []
            for student_index in grouping_template[i]:
                group.append(students[student_index])
            groups[f"group {i}"] = group

        return groups

    def shuffle_students(self):
        """
        Shuffles students
        """
        shuffle_ls(self.students)

    def session_scheduling(
        self, students: List[str], session_start_time: timedelta, session_index: int
    ) -> Dict[str, Any]:
        """
        creates a dictionary which contains all the necessary information for a session.
        :param students: list of all students for this session
        :param session_start_time: start time
        :param session_index: session number
        :return: a dictionary containing the start time, end_time, session_number and student for the session
        """
        if self.no_per_group:
            grouping_template = self.create_group_template(len(students))
            groups = self.create_group(students, grouping_template)
            return {
                "session_number": session_index,
                "start_time": str(session_start_time),
                "end_time": str(session_start_time + self.session_duration),
                "groups": groups,
            }
        return {
            "session_number": session_index,
            "start_time": str(session_start_time),
            "end_time": str(session_start_time + self.session_duration),
            "groups": students,
        }

    def generate_schedules(self):
        """Generates the appropriate schedule times for all students"""
        schedules = []
        session_times = self.get_session_times()
        no_of_student_per_session = self.get_no_of_students_per_session(
            len(session_times), len(self.students)
        )
        self.shuffle_students()
        for index in range(len(session_times)):
            start_slice = index * no_of_student_per_session
            end_slice = index * no_of_student_per_session + no_of_student_per_session
            if index == len(session_times) - 1:
                end_slice = len(self.students)

            schedules.append(
                self.session_scheduling(
                    self.students[start_slice:end_slice], session_times[index], index
                )
            )
        return schedules


class EmailStudents:
    def __init__(
        self,
        name_and_email: List[Dict[str, str]],
        data: Dict,
    ):
        self.name_and_email = name_and_email
        self.data = data

    def send_email(self):
        def send(body: str):
            new_body = body + "\n\nSigned\nManagement\n\n"
            # print(new_body)
            email_obj = Email(
                self.name_and_email[name], self.data.get("subject"), new_body
            )
            es = EmailSender(sender_email, sender_password)
            if name in ["Domenica Mgbe"]:
                # print("sent to Dome")
                es.send_email(email_obj)

        if getenv("SENDER_EMAIL"):
            sender_email = getenv("SENDER_EMAIL")
        else:
            sender_email = input("Please enter your email: ")

        sender_password = input(
            "Please enter your password(Google application password): "
        )
        body = Body(self.data)
        for sh in self.data["schedule"]:
            if isinstance(sh["groups"], dict):
                for group_no, names in sh["groups"].items():
                    for name in names:
                        send(
                            body(
                                name=name,
                                group_number=group_no,
                                start_time=sh.get("start_time"),
                                end_time=sh.get("end_time"),
                                session_number=sh.get("session_number"),
                            )
                        )
            elif isinstance(sh["groups"], list):
                for name in sh["groups"]:
                    send(
                        body(
                            name=name,
                            start_time=sh.get("start_time"),
                            end_time=sh.get("end_time"),
                            session_number=sh.get("session_number"),
                        )
                    )


class Body:
    def __init__(self, db_data=None):
        self.base_body = []
        self.append("Below is details of your Practical session")
        if db_data:
            ignored_keys = getenv("IGNORED_KEYS", [])
            for key, value in db_data.items():
                if key not in ignored_keys and value is not None:
                    string = f"{key}: {value}".upper()
                    self.append(string)

    def __call__(self, *args, **kwargs):
        new_body = self.base_body.copy()
        if args:
            for string in args:
                self.append(string, new_body)

        if kwargs:
            for key, value in kwargs.items():
                if key == "name":
                    self.insert(f"Hi {value},\n", new_body)
                else:
                    string = f"{key.upper()}: {value}"
                    self.append(string, new_body)

        return "\n".join(new_body)

    def insert(self, string, ls=None, index=0):
        if ls is None:
            self.base_body.insert(index, string)
        else:
            ls.insert(index, string)

    def append(self, string, ls=None):
        if ls is None:
            self.base_body.append(string)
        else:
            ls.append(string)

    def pop(self, ls=None, index=0):
        if ls is None:
            self.base_body.pop(index)
        else:
            ls.pop(index)

    def pop_by_string(self, string, ls=None):
        if ls is None:
            curr_ls = self.base_body
        else:
            curr_ls = ls
        for i in range(len(curr_ls)):
            if self.base_body[i].startswith(string):
                self.pop(i)


class Email:
    def __init__(
        self, receiver_email: str = None, subject: str = None, body: Any = None
    ) -> None:
        self.receiver_email = receiver_email
        self.subject = subject
        self.body = body

    @property
    def receiver_email(self):
        return self.__receiver_email

    @receiver_email.setter
    def receiver_email(self, email):
        if type(email) is not str:
            return TypeError("Invalid email")

        check_valid_email(email)

        self.__receiver_email = email


class EmailSender:
    def __init__(self, sender_email: str, sender_passwd: str) -> None:
        self.sender_email = sender_email
        self.sender_passwd = sender_passwd

    @property
    def sender_email(self):
        return self.__sender_email

    @sender_email.setter
    def sender_email(self, email: str):
        if type(email) is not str:
            return TypeError("Invalid email")

        check_valid_email(email)

        self.__sender_email = email

    @property
    def sender_passwd(self):
        return self.__sender_passwd

    @sender_passwd.setter
    def sender_passwd(self, passwd):
        self.__sender_passwd = passwd

    def send_email(self, email: Email):
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = email.receiver_email
        msg["Subject"] = email.subject
        msg.attach(MIMEText(email.body, "plain"))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            context = ssl.create_default_context()
            server.starttls(context=context)
            server.login(self.sender_email, self.sender_passwd)
            text = msg.as_string()
            server.sendmail(self.sender_email, email.receiver_email, text)
            server.quit()
            print("sent successfully... haha")
        except Exception as e:
            print("Failed to send email")
            raise e


class InputParser:
    def __init__(
        self,
        dbfunc: Callable[[argparse.Namespace], None],
        shfunc: Callable[[argparse.Namespace], None],
    ):
        self.parser = argparse.ArgumentParser(
            description="Process input for the application.",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        sub_parser = self.parser.add_subparsers(help="sub-command help")
        schedule_parser = sub_parser.add_parser("schedule", help="schedule --help")
        dbparser = sub_parser.add_parser("dbaccess", help="dbaccess --help")

        self.parser.add_argument(
            "--save",
            default=False,
            action="store_true",
            help="Save the results to database",
        )
        self.parser.add_argument(
            "--email",
            default=False,
            action="store_true",
            help="send email to students about their scheduded dates and time",
        )
        self.parser.add_argument(
            "--subject", help="subject for email students", default="LAB SCHEDULE"
        )
        self.parser.add_argument(
            "--course",
            help="course name (for example: MCT524)",
        )
        self.parser.add_argument(
            "--session",
            help="school session (for example: 2022)",
        )
        self.parser.add_argument(
            "--semester",
            help="school semester (for example: first)",
        )
        self.parser.add_argument(
            "--id",
            help="id for identifying data. Using system default is recommended",
        )
        self.parser.add_argument("--day", help="day of the week for the practical")
        self.parser.add_argument("--date", help="date for the practical")

        schedule_parser.add_argument(
            "-f",
            "--file",
            dest="file",
            required=True,
            help="Path to file of names and email of students",
        )
        schedule_parser.add_argument(
            "-s", "--start_time", dest="start_time", type=str, required=True
        )
        schedule_parser.add_argument(
            "-e",
            "--end_time",
            dest="end_time",
            type=str,
            required=True,
        )
        schedule_parser.add_argument(
            "-t",
            "--time_per_session",
            dest="tps",
            type=str,
            required=True,
            help="Time per session in minutes",
        )
        schedule_parser.add_argument(
            "-n",
            "--num_students_per_subgroup",
            dest="npsg",
            help="Number of students per subgroup (optional)",
        )
        schedule_parser.set_defaults(func=shfunc)

        dbparser.add_argument(
            "-r",
            "--retrive",
            type=str,
            dest="retrive",
            nargs=2,
            help="retrive data by key passed from database",
        )
        dbparser.add_argument(
            "--del",
            type=str,
            dest="delete",
            nargs=2,
            help="delete data by key passed from database",
        )
        dbparser.set_defaults(func=dbfunc)

    def parse_args(self):
        args = self.parser.parse_args()
        return args


class SchedulerFormatter:
    def __init__(self, data):
        self.data = data

    def format(self, data=None):
        if not isinstance(self.data, list):
            raise TypeError("data must be a list")
        for d in self.data:
            print(f"{'*':*^100}")
            if course := d.get("course"):
                print(f"{course:^100}")
            if date := d.get("date"):
                print(f"{date:^100}")
            if day := d.get("day"):
                print("{:^100}".format(f"DAY: {day.upper()}"))
            if semester := d.get("semester"):
                print("{:^100}".format(f"SEMESTER: {semester.upper()}"))
            if session := d.get("session"):
                print("{:^100}".format(f"SEMESTER: {session.upper()}"))
            if (start_time := d.get("start_time")) and (end_time := d.get("end_time")):
                print("{:^100}".format(f"TIME: {start_time} - {end_time}"))
            print(f"{'*':*^100}")

            schedule = d.get("schedule")
            for sh in schedule:
                session_number = sh.get("session_number")
                start_time = sh.get("start_time")
                end_time = sh.get("end_time")
                print("{:^100}".format(f"SESSION NUMBER: {session_number}"))
                print("{:^100}".format(f"TIME: {start_time} - {end_time}"))

                print(f"{'-':-^100}")

                groups = sh.get("groups")
                if isinstance(groups, list):
                    for i in range(len(groups)):
                        print("{} {}".format(i + 1, groups[i].upper()))
                    print(f"{'*':*^100}")
                else:
                    for group_no, names in sh["groups"].items():
                        print("{:^50}".format(f"{group_no.upper()}"))
                        for i in range(len(names)):
                            print("{} {}".format(i + 1, names[i].upper()))
                        print(f"{'-':-^100}")
                    print(f"{'*':*^100}")


class Database:
    def __init__(self):
        self.db_name = getenv("DB_NAME")

        if not path.exists(self.db_name):
            self.db = []
            self.write("a")
        else:
            self.db = self.load()

    def save(self, data: dict):
        if data.get("id") is None:
            current_id = getenv("CURRENT_DB_ID")
            new_id = str(int(current_id) + 1)
            data.update({"id": new_id})
            set_key(".env", "CURRENT_DB_ID", new_id)
            env_var = dotenv_values(".env")
            with open(".env", "w") as file:
                for key, value in env_var.items():
                    file.write(f"{key}={value}\n")

        self.db.append(data)
        self.write()
        return data.get("id")

    def retrieve(self, key, value):
        correspond_data = []
        for data in self.db:
            if data.get(key) == value:
                correspond_data.append(data)
        return correspond_data

    def delete(self, key, value):
        new_db = []
        for i in range(len(self.db)):
            if self.db[i].get(key) != value:
                new_db.append(self.db[i])
        self.db = new_db
        self.write()

    def read(self):
        with open(self.db_name) as fd:
            data = json.load(fd)
        return data

    def write(self, mode="w"):
        with open(self.db_name, mode) as fd:
            json.dump(self.db, fd)

    def load(self):
        return self.read()
