import unicodedata
import pandas


class ParseCase:
    def __init__(self, soup, main_dictionary):
        self.soup = soup
        self.dictionary = main_dictionary

    def case_details_table(self):
        case_details = self.soup.find_all(class_="case_details_table")
        list_case_details = []
        for details in case_details:
            for detail in details.stripped_strings:
                whole_text = unicodedata.normalize("NFKD", detail)
                if ":" in str(whole_text):
                    text = str(whole_text).replace(":", "")
                    list_case_details.append(text)
                else:
                    list_case_details.append(whole_text)
        headers = list_case_details[0::2]
        dictioanry_values = list_case_details[1::2]
        case_details_dictioanry = {headers[i]: dictioanry_values[i]
                                   for i in range(len(headers))}

        return case_details_dictioanry

    def case_status(self):
        case_status_table = self.soup.find_all('strong')
        list_status_details = []
        for detail in case_status_table:
            for string in detail.stripped_strings:
                whole_text = unicodedata.normalize("NFKD", string)
                if ":" in str(whole_text):
                    text = str(whole_text).replace(":", "")
                    list_status_details.append(text)
                else:
                    list_status_details.append(whole_text)
        headers = list_status_details[0:9:2]
        dictioanry_values = list_status_details[1:10:2]
        case_status_dictioanry = {headers[i]: dictioanry_values[i]
                                  for i in range(len(headers))}
        return case_status_dictioanry

    def act_table(self):
        act = self.soup.find_all(id="act_table")
        if act is not None:
            df = pandas.read_html(str(act))
            ipc = 'indian penal code'
            poa = 'prevention of atrocities'
            pcso = 'protection of children from sexual'
            pcr = 'protection of civil rights'
            cpr = 'code of criminal procedure'

            headers = [ipc, poa, pcso, pcr, cpr]
            act_dictionary = {'indian penal code': "BLANK",
                              'prevention of atrocities': "BLANK",
                              'protection of children from sexual': "BLANK",
                              'protection of civil rights': "BLANK",
                              'code of criminal procedure': "BLANK", 'Other': "BLANK"}

            for row in df[0].itertuples(index=False):
                for key in headers:
                    if key in str(row[0]).lower():
                        if ":" in str((row[1])):
                            text = str(row[1]).replace(":", "")
                            act_dictionary[key] = text
                        else:
                            text = str(row[1])
                            act_dictionary[key] = text
                if not any(item in str(row[0]).lower() for item in headers):
                    if ":" in str(row[0]):
                        other = str(row[0]).replace(":", "")
                        act_dictionary['Other'] = other
                    else:
                        act_dictionary['Other'] = (str(row[0]).lower())
            return act_dictionary
        else:
            return False

    def set_dictionary(self):
        case_details_dictioanry = self.case_details_table()
        case_status_dictioanry = self.case_status()

        acts_dictionary = self.act_table()

        for key in self.dictionary:
            if key in case_details_dictioanry:
                self.dictionary[key] = case_details_dictioanry[key]
        for key in self.dictionary:
            if key in case_status_dictioanry:
                self.dictionary[key] = case_status_dictioanry[key]

        fir = self.soup.find_all(class_='FIR_details_table')
        if not fir:
            print("no fir details given")
        else:
            fir_dictionary = fir_details(fir)
            for key in fir_dictionary:
                if key in self.dictionary:
                    self.dictionary[key] = fir_dictionary[key]
                else:
                    print("some issue")

        petitioner = self.soup.find_all(class_='Petitioner_Advocate_table')
        if not petitioner:
            print("no Petitioner and advocate details given")
        else:
            petitioner_dictionary = petitioner_details(petitioner)
            self.dictionary['Petitioner & Adv.'] = str(
                petitioner_dictionary['Petitioner & Adv.']).replace("[", "").replace("]", "")

        respondent = self.soup.find_all(class_='Respondent_Advocate_table')
        if not respondent:
            print("no Respondent and advocate details given")
        else:
            respondent_dictionary = respondent_details(respondent)
            self.dictionary['Respondent & Adv.'] = str(
                respondent_dictionary['Respondent & Adv.']).replace("[", "").replace("]", "")

        if self.act_table():
            for key in self.dictionary:
                if key in acts_dictionary:
                    self.dictionary[key] = acts_dictionary[key]
        return self.dictionary


class History(ParseCase):
    def __init__(self, soup, main_dictionary, file):
        super().__init__(soup, main_dictionary)
        self.file = file

    def case_history(self):
        history_table = self.soup.find_all(class_="history_table")
        df = pandas.read_html(
            str(history_table), na_values="Not Available", keep_default_na=False)
        history = df[0]
        history.to_csv(self.file, index=False)
        return history


def fir_details(fir):
    list_text = []
    for detail in fir:
        for string in detail.stripped_strings:
            list_text.append(string)
    if not list_text:
        print("no FIR details")
        return False
    else:
        headers_fir = ['Police Station', 'FIR Number', 'Year']
        fir_dictioanry_values = list_text[2::2]
        # remove ":" from text
        details = []
        for one in fir_dictioanry_values:
            if ":" in str(one):
                values = str(one).replace(":", "")
                details.append(values)
            else:
                details.append(one)
        fir_dictioanry = {headers_fir[i]: details[i]
                          for i in range(len(headers_fir))}
        return fir_dictioanry


def petitioner_details(petitioner):
    if petitioner is not None:
        list_text = []
        for detail in petitioner:
            for string in detail.stripped_strings:
                whole_text = unicodedata.normalize("NFKD", string)
                if ":" in str(whole_text):
                    text = str(whole_text).replace(":", "")
                    list_text.append(text)
                else:
                    list_text.append(whole_text)
        if list_text is None:
            print("No petitioner_detials")
            return False
        else:
            petitioner_dictionary = {'Petitioner & Adv.': list_text}
        return petitioner_dictionary
    else:
        return False


def respondent_details(respondent):
    if respondent is not None:
        list_text = []
        for detail in respondent:
            for string in detail.stripped_strings:
                whole_text = unicodedata.normalize("NFKD", string)
                if ":" in str(whole_text):
                    text = str(whole_text).replace(":", "")
                    list_text.append(text)
                else:
                    list_text.append(whole_text)
        if not list_text:
            print("no respondent table")
        else:
            respondent_dictionary = {'Respondent & Adv.': list_text}
            return respondent_dictionary
    else:
        return False


"""source = open('/home/sangharshmanuski/EcourtsData/disposed_off/pune3/Khed, Civil Court/case_info50.html')
base_soup = BS(source, 'lxml')

file = '/home/sangharshmanuski/EcourtsData/disposed_off/pune3/idarich.csv'
case_details = ParseCase(base_soup, dictionary)
history_table = History(base_soup, dictionary, file)

print(case_details.set_dictionary(), history_table.case_history(), sep='\n\n')
"""
