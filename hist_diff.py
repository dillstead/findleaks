import sys
import argparse
import hist_utils

def calcDiffs(file1, file2):
    diffs = {}
    klasses1 = hist_utils.readIntoDict(file1)
    klasses2 = hist_utils.readIntoDict(file2)
    keys1 = set(klasses1.keys())
    keys2 = set(klasses2.keys())
    commonKeys = keys1 & keys2
    for commonKey in commonKeys:
        diffs[commonKey] = [klasses2[commonKey] - klasses1[commonKey]]
    keysIn1 = keys1 - keys2
    for keyIn1 in keysIn1:
        diffs[keyIn1] = [-klasses1[keyIn1]]
    keysIn2 = keys2 - keys1
    for keyIn2 in keysIn2:
        diffs[keyIn2] = [klasses2[keyIn2]]
    return diffs
                         
def main(argv = None):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description = "find differences between two jmap histogram files")
    parser.add_argument("histfile1", help = "histogram file")
    parser.add_argument("histfile2", help = "histogram file")
    try:
        args = parser.parse_args(argv)
        diffs = calcDiffs(args.histfile1, args.histfile2)
        # Sort by decreasing number of instances.
        diffs = sorted(zip(diffs.keys(), diffs.values()), key = lambda diff : diff[1], reverse = True)
        for diff in diffs:
            print("%s\t%d" % (diff[0], diff[1][0]))
    except SystemExit:
        return 2

# call script from command line
# call script from interpreter
# call function from other module
if __name__ == "__main__":
    sys.exit(main())
