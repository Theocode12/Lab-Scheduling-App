from typing import List, Any, Union
from datetime import timedelta
import csv
import faker
import random
import re
import io


def shuffle_ls(ls):
    random.shuffle(ls)


def csv_parser(file: Union[str, io.TextIOWrapper]) -> List[Any]:
    # Initialize an empty list to store the data
    def reader(file_obj):
        reader = csv.DictReader(file_obj)
        for row in reader:
            data.append(row)

    data = []
    if isinstance(file, io.TextIOWrapper):
        reader(file)
    elif isinstance(file, str):
        with open(file, newline="") as file_obj:
            reader(file_obj)
    return data


def generate_fake_data():
    # Initialize Faker to generate fake data
    fake = faker.Faker()

    # Generate fake names and emails
    fake_data = [(fake.name(), fake.email()) for _ in range(20)]
    print(fake_data)

    # Write fake data to CSV file
    with open("stub_data.csv", "w", newline="") as csvfile:
        fieldnames = ["Name", "Email"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for name, email in fake_data:
            writer.writerow({"Name": name, "Email": email})

    print("Fake names and emails have been saved to stub_data.csv")


def convert_str_to_timedelta_obj(time: str):
    """
    convert time from string to time delta object. Must be in the format: "hour:minute:second"
    :param time:
    :return: time delta object
    """
    if len(time.split(":")) == 3:
        hours, minutes, seconds = [int(_) for _ in time.split(":")]
    else:
        raise ValueError("wrong format. Format should be 'hour:minute:second' ")
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def extract_key_values(data: List[dict], key: str):
    """
    Give a list of dictionaries, it finds the values of the all key present
    :param data:
    :param key:
    :return:
    """
    values = []
    for datum in data:
        if (value := datum.get(key, None)) is not None:  # remember check mechanisms
            values.append(value)
    return values


def check_valid_email(email):
    if not re.match(r"^[\w\.-]+@[\w\.-]+(\.[\w]+)+$", email):
        raise ValueError("Invalid email format")


def lists_to_dictionary(keys: List[str], values: List[str]):
    """
    Converts two lists into a dictionary.
    :param keys: List of keys
    :param values: List of values
    :return: Dictionary
    """
    if len(keys) != len(values):
        raise ValueError("Keys and values must be the same length")
    return {keys[i]: values[i] for i in range(min(len(keys), len(values)))}


if __name__ == "__main__":
    print(csv_parser("../tests/stub_data.csv"))
