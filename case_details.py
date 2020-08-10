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

    def fir_details(self):
        fir = self.soup.find_all(class_='FIR_details_table')
        if fir is not None:
            list_text = []
            for detail in fir:
                for string in detail.stripped_strings:
                    whole_text = unicodedata.normalize("NFKD", string)
                    if ":" in str(whole_text):
                        text = str(whole_text).replace(":", "")
                        list_text.append(text)
                    else:
                        list_text.append(whole_text)
            list_fir = [i for i in list_text if i != ":"]
            headers_fir = list_fir[0:5:2]
            fir_dictioanry_values = list_fir[1:6:2]
            fir_dictioanry = {headers_fir[i]: fir_dictioanry_values[i]
                              for i in range(len(headers_fir))}
            return fir_dictioanry
        else:
            return False


    def petitioner_details(self):
        petitioner = self.soup.find_all(class_='Petitioner_Advocate_table')
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
            petitioner_dictionary = {'Petitioner & Adv.': list_text}
            return petitioner_dictionary
        else:
            return False

    def respondent_details(self):
        respondent = self.soup.find_all(class_='Respondent_Advocate_table')
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
            respondent_dictionary = {'Respondent & Adv.': list_text}
            return respondent_dictionary
        else:
            return False


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
        if self.fir_details():
            fir_dictioanry = self.fir_details()
            for key in self.dictionary:
                if key in fir_dictioanry:
                    self.dictionary[key] = fir_dictioanry[key]
        if self.petitioner_details():
            petitioner_dictionary = self.petitioner_details()
            for key in self.dictionary:
                if key in petitioner_dictionary:
                    self.dictionary[key] = str(petitioner_dictionary[key]).replace("[", "").replace("]", "")
        if self.respondent_details():
            respondent_dictionary = self.petitioner_details()
            for key in self.dictionary:
                if key in respondent_dictionary:
                    self.dictionary[key] = str(respondent_dictionary[key]).replace("[", "").replace("]", "")
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

"""source = open('/home/sangharshmanuski/EcourtsData/disposed_off/pune3/Khed, Civil Court/case_info50.html')
base_soup = BS(source, 'lxml')

file = '/home/sangharshmanuski/EcourtsData/disposed_off/pune3/idarich.csv'
case_details = ParseCase(base_soup, dictionary)
history_table = History(base_soup, dictionary, file)

print(case_details.set_dictionary(), history_table.case_history(), sep='\n\n')
"""
