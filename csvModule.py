import csv
import glob
pathDir = r'/home/sangharshmanuski/Documents/e_courts/maharashtra'
inputs = glob.glob(pathDir + '/**/*.csv', recursive=True)

# First determine the field names from the top line of each input file
# Comment 1 below
fieldnames = []

with open(inputs[1], 'r', newline='') as f:
  read = csv.reader(f)
  headers = next(read)
fieldnames.append(headers)

# Then copy the data
with open("/home/sangharshmanuski/Documents/e_courts/mCases/out.csv", "w", newline="") as f_out:
  writer = csv.DictWriter(f_out, fieldnames=fieldnames)
  for filename in inputs:
    with open(filename, "r", newline="") as f_in:
      reader = csv.DictReader(f_in)  # Uses the field names in this file
      for line in next(reader):
        # Comment 3 below
        writer.writerow(line)
