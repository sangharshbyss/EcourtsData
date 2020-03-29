#taking final output with this. will combine all csv files then. will write another code for that.
#with orientation as index shifting to htmltoCsv_2_perfection as couldn't orient to columns
#note: acts copied from offlineWork_actTable.py
#note: everything is working fine in this file if in creating the data frame the orientation is set to index. delet this comment if this problem is fixed.
# ref https://markhneedham.com/blog/2016/07/11/python-scraping-elements-relative-to-each-other-with-beautifulsoup/
# for opening file and processing soup ref https://www.experts-exchange.com/questions/26439956/Parse-local-html-file-with-python-and-beautifulsoup.html
import os
from bs4 import BeautifulSoup as bs
import pandas as pd
import csv

dictionary = {}
df = pd.DataFrame.from_dict(dictionary, orient="index")
pathToDir = r'/home/sangharshmanuski/Documents/e_courts/aurangabad/rawDownloadedFiles'
arr = os.listdir(pathToDir)
# itirate all files for new file ref - https://stackoverflow.com/questions/51372363/repeat-beautifulsoup-scrape-for-all-files-in-a-local-folder
for newFile in os.listdir(pathToDir):

    fileName = os.path.join(pathToDir, newFile)
    # create soup.
    fileNameOpen = open(fileName)
    soup = bs(fileNameOpen, 'html.parser')
    # section 1: Case Details
    try:
        caseType = soup.find('span', {'class': 'case_details_table'})
        caseTypeChild = caseType.findChild()
        # ref for .next - https://stackoverflow.com/questions/5999407/extract-content-within-a-tag-with-beautifulsoup
        sessionsCase = caseTypeChild.next.next.next
        filing = sessionsCase.next.next
        filingNumberHeading = filing.find('label')
        filingNumber = filingNumberHeading.next.next
        dictionary['Filing Number'] = filingNumber
        filingDate = filingNumber.next.next.next.next
        dictionary['Filing Date'] = filingDate
        registration = filingDate.next.next
        registrationNumberHeading = registration.find('label')
        registrationNumber = registrationNumberHeading.next.next.next
        dictionary['Registration Number'] = registrationNumber
        cnrHeading = soup.find('b').find('label')
        cnrNumber = cnrHeading.next.next
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
        policeStationHeading = soup.find('span', attrs={'class': 'FIR_details_table'}).next.next
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
    except:
        pass

    # section 4: Respondent
    try:
        respondentName = petitionerAdvocate.find_next('span').text + ' and others'
        dictionary['Name of the Respondent'] = respondentName
    except:
        pass
    # section 5: Acts
    '''In this section 1. soup is prepared from act_table tab of web page
    2. Keys for main dictionary are created defining headings of acts. with 'not applied' values. 
    3. short form variables are created for names of the act. 
    4. list of acts is compared with list of variables and sections are replaced as values in the dictionary. '''

    acts = soup.select('#act_table td:nth-of-type(1)')
    sections = soup.select('#act_table td:nth-of-type(2)')
    dictionary['IPC'] = 'Not Applied'
    dictionary['PoA'] = 'Not Applied'
    dictionary['PCSO'] = 'Not Applied'
    dictionary['PCR'] = 'Not Applied'
    dictionary['Any Other Act'] = 'Not Applied'

    ipc = 'indian penal code'.lower()
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
        if ipc in str(act3).lower():
            dictionary['IPC'] = sections1
        elif poa in str(act3).lower():
            dictionary['PoA'] = sections2
        elif pcso in str(act3).lower():
            dictionary['PCSO'] = sections3
        elif pcr in str(act3).lower():
            dictionary['PCR'] = sections3
        else:
            pass
    # for 4th act in list
    elif len(acts) == 4:
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
        if ipc in str(act3).lower():
            dictionary['IPC'] = sections3
        elif poa in str(act3).lower():
            dictionary['PoA'] = sections3
        elif pcso in str(act3).lower():
            dictionary['PCSO'] = sections3
        elif pcr in str(act3).lower():
            dictionary['PCR'] = sections3
        else:
            pass
        if ipc in str(act4).lower():
            dictionary['IPC'] = sections4
        elif poa in str(act4).lower():
            dictionary['PoA'] = sections4
        elif pcso in str(act4).lower():
            dictionary['PCSO'] = sections4
        elif pcr in str(act4).lower():
            dictionary['PCR'] = sections4
        else:
            pass
    else:
        pass

    df = pd.DataFrame.from_dict(dictionary, orient="index")
    outputFile = open('/home/sangharshmanuski/Documents/e_courts/aurangabad/csvFiles/Files_' + str(arr.index(newFile)) + ".csv", "w")
    df.to_csv(outputFile)
    outputFile.close()