import os

from file_append import write_mode



def court_complex_dir(main, name_complex):
    # makes separate directory particular court complex
    court_complex_directory = os.path.join(
        main, name_complex)  # create new
    if not os.path.exists(court_complex_directory):  # if not directory exists, create one
        os.mkdir(court_complex_directory)
    return court_complex_directory

def history_direcotry(complex_dir):
    court_complex_history = os.path.join(
        complex_dir, 'history')  # create new
    if not os.path.exists(court_complex_history):  # if not directory exists, create one
        os.mkdir(court_complex_history)
    return court_complex_history


def district_summary(district, district_name):
    district_summary_directory = os.path.join(district)
    if not os.path.exists(district_summary_directory):  # if not directory exists, create one
        os.mkdir(district_summary_directory)
    summary_file = os.path.join(district, f'{district_name}_summary.txt')
    district_opening = f':       {district_name} Records             :\n'
    write_mode(summary_file, district_opening)
    return summary_file


def complex_record_details(court_complex, complex_name):
    details_of_cases = os.path.join(court_complex, f'{complex_name}_case_details.csv')
    return details_of_cases


def complex_records_poa(district, complex_name):
    details_of_poa_cases = os.path.join(district,
                                        f'{complex_name}_poa_cases.csv')
    return details_of_poa_cases


def complex_summary(complex_directory,
                    name_of_the_complex, registration_number="blank", i=0):
    complex_summary_directory = os.path.join(complex_directory, 'summary')
    if not os.path.exists(complex_summary_directory):  # if not directory exists, create one
        os.mkdir(complex_summary_directory)
    complex_summary_file = os.path.join(complex_summary_directory, f'{name_of_the_complex}_summary.txt')
    complex_opening = f':    {name_of_the_complex} - Summary Records    :\n'
    write_mode(complex_summary_file, complex_opening)
    orders_downloaded = os.path.join(complex_summary_directory,
                                     f'case_{str(registration_number)}_2020_{i}.txt')
    return complex_summary_file, orders_downloaded


def errors_file(directory, district, complex_name=None):
    error_file = os.path.join(directory, f'error_{district}_{complex_name}.txt')
    error_message = f":              registering errors            :"
    write_mode(error_file, error_message)
    return error_file
