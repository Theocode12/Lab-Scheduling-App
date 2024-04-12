# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from dotenv import load_dotenv
from models import (
    InputParser,
    Scheduler,
    Database,
    EmailStudents,
    SchedulerFormatter,
)
from util import csv_parser, extract_key_values, lists_to_dictionary
import argparse
from pprint import pprint


def db_data_generator(schedule, args):
    data_template = {"schedule": schedule}
    meta = vars(args)
    for key, value in meta.items():
        if key not in ["func", "save"]:
            data_template[key] = value
    return data_template


def scheduler_function(args: argparse.Namespace):
    file_data = csv_parser(args.file)
    students = extract_key_values(file_data, "Name")
    emails = extract_key_values(file_data, "Email")
    names_email = lists_to_dictionary(students, emails)

    full_schedule = Scheduler(
        args.start_time, args.end_time, args.tps, students, args.npsg
    ).generate_schedules()
    db_data = db_data_generator(full_schedule, args)
    if args.email:
        mail = EmailStudents(names_email, db_data)
        mail.send_email()

    if args.save:
        db = Database()
        db.save(db_data)
    # pprint(db_data)
    SchedulerFormatter([db_data]).format()


def database_function(args: argparse.Namespace):
    db = Database()
    if args.retrive:
        data = db.retrieve(*args.retrive)
        # pprint(data)
        SchedulerFormatter(data)
        if args.email:
            file_data = csv_parser(data.get("file"))
            students = extract_key_values(file_data, "Name")
            emails = extract_key_values(file_data, "Email")
            names_email = lists_to_dictionary(students, emails)

            mail = EmailStudents(names_email, data)
            mail.send_email()

    if args.delete:
        data = db.delete(*args.delete)
        SchedulerFormatter(data)


def main():
    load_dotenv()
    parser = InputParser(shfunc=scheduler_function, dbfunc=database_function)
    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()
    data = [
        {
            "course": "MCT543",
            "date": None,
            "day": "Monday",
            "email": False,
            "end_time": "15:00:00",
            "file": "stub_data.csv",
            "id": "1",
            "npsg": "3",
            "schedule": [
                {
                    "end_time": "13:00:00",
                    "groups": {
                        "group 0": ["Adam Adams", "Taylor Wall", "Jason Torres"],
                        "group 1": [
                            "Cassandra Weber",
                            "Patricia Vasquez DVM",
                            "Carl Mclaughlin",
                        ],
                    },
                    "session_number": 0,
                    "start_time": "12:00:00",
                },
                {
                    "end_time": "14:00:00",
                    "groups": {
                        "group 0": ["Adam Adams", "Taylor Wall", "Jason Torres"],
                        "group 1": [
                            "Cassandra Weber",
                            "Patricia Vasquez DVM",
                            "Carl Mclaughlin",
                        ],
                    },
                    "session_number": 1,
                    "start_time": "13:00:00",
                },
                {
                    "end_time": "15:00:00",
                    "groups": {
                        "group 0": ["Adam Adams", "Taylor Wall", "Jason Torres"],
                        "group 1": [
                            "Cassandra Weber",
                            "Patricia Vasquez DVM",
                            "Carl Mclaughlin",
                        ],
                        "group 2": ["Gabriel Lee", "Jessica Brown"],
                    },
                    "session_number": 2,
                    "start_time": "14:00:00",
                },
            ],
            "semester": "first",
            "session": "2023",
            "start_time": "12:00:00",
            "subject": "LAB SCHEDULE",
            "tps": "1:00:00",
        }
    ]
    # SchedulerFormatter(data).format()
