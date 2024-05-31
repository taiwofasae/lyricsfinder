import os
import csv




def csv_reader(filepath, take, skip=0):
  output = []
  row_index = -1
  count = 0
  with open(filepath,"r") as file:
    reader = csv.reader(file)
    for line in reader:
      # skip the first skip rows
      row_index += 1
      if row_index < skip:
        continue
      # terminate once enough
      if count > take:
        break
      output.append(line)
      count += 1
      

  return output

def read_csv_max_split(filepath, take, skip=0):
  output = []
  count = 0
  with open(filepath,"r") as file:
    # skip the first skip rows
    for i in range(skip):
      next(file)
    for line in file:
      # terminate once enough
      if count > take:
        break
      output.append([x.lstrip('\"').rstrip('\"') for x in line.rstrip().split('","',4)])
      count += 1

  return output

def read_csv_max_split_folder(folder, func):
  for f in os.listdir(folder):
    if os.path.isfile(os.path.join(folder, f)):
      output = read_csv_max_split(os.path.join(folder, f))
      func(output)


def read_first_N_lines(filepath, cols=4, N=5):
  output = []
  with open(filepath,"r") as file:
    for i in range(N):
      line = next(file)
      output.append(line.rstrip())

  return output
