import os
from bs4 import BeautifulSoup as bs
import glob
import datetime
import csv
import multiprocessing as mp

csv_header = ['Case Type', 'CNR Number', 'Filing Number', 'Filing Date', 
              'First Hearing', 'Next Hearing', 'Stage of Case', 'Registration Number',
              'Year', 'FIR Number', 'Police Station', 'Court Number and Judge',  'PoA',
              'IPC', 'PCR', 'PCSO', 'Any Other Act', 'Name of the Petitioner', 
              'Name of the Advocate', 'Name of the Respondent']

root_dir = r'/home/sangharshmanuski/Documents/e_courts/mha/downloads4/Pune'

def convert_html_case_files_to_csv():

    output_filename = os.path.join(
        '/home/sangharshmanuski/Documents/e_courts/mha/csvFiles2/file_' + str(
        datetime.datetime.now().day) + '_' + str(datetime.datetime.now().month) + '_' + str(
        datetime.datetime.now().year) + '.csv')

    with open(output_filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, csv_header)
        writer.writeheader()
        for newFile in glob.glob(os.path.join(root_dir, '**/*.html'), recursive=True):
            writer.writerow(process_case_file(newFile))

def process_case_file(filename):
    """Read and parse html file, return csv row as dict"""
    dictionary = {}
    # create soup.
    openFile = open(filename)
    soup = bs(openFile, 'html.parser')
    # section 1: Case Details
    try:
        case_details_table = soup.findAll(attrs={'class': 'case_details_table'})
        caseType1 = case_details_table[0].contents[1]
        caseType = soup.find('span', {'class': 'case_details_table'})
        caseTypeChild = caseType.findChild()
        sessionsCase = caseTypeChild.next.next.next
        filing = sessionsCase.next.next
        filingNumberHeading = filing.find('label')
        filingNumber = filingNumberHeading.next.next
        filingDate = filingNumber.next.next.next.next
        registration = filingDate.next.next
        registrationNumberHeading = registration.find('label')
        registrationNumber = registrationNumberHeading.next.next.next
        cnrNumber = case_details_table[3].contents[1]
        dictionary['Case Type'] = caseType1
        dictionary['Filing Number'] = filingNumber
        dictionary['Filing Date'] = filingDate
        dictionary['Registration Number'] = registrationNumber
        dictionary['CNR Number'] = cnrNumber
    except:
        pass

    # section 2: Case Status
    try:
        firstHearing = soup.find('strong')
        firstHearingDate = firstHearing.next_sibling.text
        dictionary['First Hearing'] = firstHearingDate
        nextHearing = soup.find('strong', text='Next Hearing Date')
        nextHearingDate = nextHearing.next_sibling.text
        dictionary['Next Hearing'] = nextHearingDate
        stageOfCase = soup.find('strong', text='Stage of Case')
        stageOfCaseText = stageOfCase.next_sibling.text
        dictionary['Stage of Case'] = stageOfCaseText
        courtNumber = soup.find('strong', text='Court Number and Judge')
        courtNumberText = courtNumber.next_sibling.next_sibling.text.strip()
        dictionary['Court Number and Judge'] = courtNumberText
    except:
        pass

    # section 6: FIR Details
    try:
        policeStationHeading = soup.find(
            'span', attrs={'class': 'FIR_details_table'}).next.next
        policeStation = policeStationHeading.next.next.next.next
        firnumberHeading = policeStation.next.next.next
        firNumber = policeStation.find_next('label').next
        firYearHeading = firNumber.next.next.next
        firYear = firNumber.find_next('span').find_next('label').next
        # same as previous sections.
        dictionary[policeStationHeading] = policeStation
        dictionary[firnumberHeading] = firNumber
        dictionary[firYearHeading] = firYear
    except:
        pass

    # section 3: Petioner and Advocate
    try:
        petitioner = soup.find('span', attrs={'class': 'Petitioner_Advocate_table'})
        petitionerName = petitioner.next
        dictionary['Name of the Petitioner'] = petitionerName
        petitionerAdvocate = petitionerName.next.next
        dictionary['Name of the Advocate'] = petitionerAdvocate
    # section 4: Respondent and Advocate
        respondent = petitionerAdvocate.find_next('span')
        respondentName = respondent.next
        dictionary['Name of the Respondent'] = respondentName
    except:
        pass
    # section 5: Acts

    acts = soup.select('#act_table td:nth-of-type(1)')
    sections = soup.select('#act_table td:nth-of-type(2)')
    dictionary['IPC'] = 'Not Applied'
    dictionary['PoA'] = 'Not Applied'
    dictionary['PCSO'] = 'Not Applied'
    dictionary['PCR'] = 'Not Applied'
    dictionary['Any Other Act'] = 'Not Applied'

    ipc = 'indian penal code'
    poa = 'prevention of atrocities'
    pcso = 'protection of children from sexual'
    pcr = 'protection of civil rights'


    try:
        act1 = tuple(acts[0].contents)
        sections1 = tuple(sections[0].contents)
        string = str(act1)
    except:
        pass
    try:
        act2 = tuple(acts[1].contents)
        sections2 = tuple(sections[1].contents)
    except:
        pass
    try:
        act3 = tuple(acts[2].contents)
        sections3 = tuple(sections[2].contents)
    except:
        pass
    try:
        act4 = tuple(acts[3].contents)
        sections4 = tuple(sections[3].contents)
    except:
        pass
    # using if and not for loop then actSession is not needed
    # for first act in list
    if len(acts) < 2:
        if ipc in string.lower():
            dictionary['IPC'] = sections1
        elif poa in string.lower():
            dictionary['PoA'] = sections1
        elif pcso in string.lower():
            dictionary['PCSO'] = sections1
        elif pcr in string.lower():
            dictionary['PCR'] = sections1
        else:
            pass
    # for 2nd act in list
    elif len(acts) == 2:
        if ipc in string.lower():
            dictionary['IPC'] = sections1
        elif poa in string.lower():
            dictionary['PoA'] = sections1
        elif pcso in string.lower():
            dictionary['PCSO'] = sections1
        else:
            pass
        if ipc in str(act2).lower():
            dictionary['IPC'] = sections2
        elif poa in str(act2).lower():
            dictionary['PoA'] = sections2
        elif pcso in str(act2).lower():
            dictionary['PCSO'] = sections2
        else:
            pass
    # for 3rd act in list
    elif len(acts) == 3:
        if ipc in string.lower():
            dictionary['IPC'] = sections1
        elif poa in string.lower():
            dictionary['PoA'] = sections1
        elif pcso in string.lower():
            dictionary['PCSO'] = sections1
        elif pcr in string.lower():
            dictionary['PCR'] = sections1
        else:
            pass
        if ipc in str(act2).lower():
            dictionary['IPC'] = sections2
        elif poa in str(act2).lower():
            dictionary['PoA'] = sections2
        elif pcso in str(act2).lower():
            dictionary['PCSO'] = sections2
        elif pcr in str(act2).lower():
            dictionary['PCR'] = sections2
        else:
            pass
    else:
        pass

    return dictionary


if __name__ == "__main__":
    convert_html_case_files_to_csv()
