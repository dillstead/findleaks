import fileinput

def readIntoDict(file):
    klassInstances = {}
    for line in fileinput.input(file):
        tokens = line.split()
        if len(tokens) != 4 or not tokens[1].isdigit() or not tokens[2].isdigit():
            continue
        klassInstances[tokens[3]] = int(tokens[1])
    fileinput.close()
    return klassInstances

