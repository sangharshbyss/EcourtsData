#from htmltoCsv_2 after skipping version 2_1 and 2_perfection
import os
import glob
import pandas as pd
import os
import glob
pathToDir = r'/home/sangharshmanuski/Documents/e_courts/aurangabad/csvFiles'
arr = os.listdir(pathToDir)
list_of_dataframes = []
for fileNames in arr:
    if fileNames.endswith(".csv"):
        df = pd.read_csv(os.path.join(pathToDir, fileNames), header=1, skip_blank_lines=True, engine='python')
        df_1 = df.transpose()
        newfile = open('/home/sangharshmanuski/Documents/e_courts/aurangabad/csvFiles/tFiles/file_' + str(arr.index(fileNames)) + '.csv', 'w')
        df_1.to_csv(newfile)
        newfile.close()
newPathDir = r'/home/sangharshmanuski/Documents/e_courts/aurangabad/csvFiles/tFiles'
allFile = glob.glob(newPathDir + "/*.csv")
for files in allFile:
    f = pd.read_csv(files, index_col=None, header=1)
    list_of_dataframes.append(f)
frame1 = pd.concat(list_of_dataframes, axis=0, ignore_index=True)
allInOne = open('/home/sangharshmanuski/Documents/e_courts/aurangabad/csvFiles/aurangabadCasesMarch2020.csv', 'w')
frame1.to_csv(allInOne)
