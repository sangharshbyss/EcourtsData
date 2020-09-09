# open file in append mode
from csv import DictWriter


def write_mode(file, message=None):
    with open(file, 'w') as f:
        f.close()


def append_file(file, message):
    with open(file, 'a') as f:
        f.write(message)
        f.close()


def append_dict_as_row(output_file, dict_of_elem, field_names):
    # Open file in append mode
    with open(output_file, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        dict_writer = DictWriter(write_obj, fieldnames=field_names)
        # Add dictionary as wor in the csv
        dict_writer.writerow(dict_of_elem)
        write_obj.close()
