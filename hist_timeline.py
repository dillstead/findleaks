import sys
import argparse
import os
import hist_utils
import glob
from numpy import array,ones,linalg

class KlassTimeLine:
    def __init__(self, name, initialCount, timePoint):
        self.name = name
        #self.counts = [0 for i in range(timePoint)]
        self.counts = []
        self.counts.append(initialCount)
        self.alwaysIncreasing = True
        self.alwaysDecreasing = True
        self.slope = 0.0;

    def calculateSlope(self):
        A = array([range(len(self.counts)), ones(len(self.counts))])
        self.slope = linalg.lstsq(A.T, self.counts)[0][0]
        
    def updateCount(self, count):
        try:
            diff = count - self.counts[-1]
            if diff > 0:
                self.alwaysDecreasing = False
            elif diff < 0:
                self.alwaysIncreasing = False
        except IndexError:
            pass 
        self.counts.append(count)

    def __str__(self):
        return self.name + "," + self.slope + ",".join(str(count) for count in self.counts)

    def __repr__(self):
        return "KlassTimeLine(name=%r,initialCount=%r,timePoint=0)" % (self.name, self.counts[0])

def filterTimeLines(klassTimeLines):
    # filter out the entries in the timeline whose number of instances is
    # always increasing
    increasing = {klassName : klassTimeLine for klassName, klassTimeLine in klassTimeLines.items() if klassTimeLine.alwaysIncreasing == True and klassTimeLine.alwaysDecreasing == False}
    alternating = {klassName : klassTimeLine for klassName, klassTimeLine in klassTimeLines.items() if klassTimeLine.alwaysIncreasing == False and klassTimeLine.alwaysDecreasing == False}
    return increasing, alternating

def applyInstancesToTimeLines(klassInstances, klassTimeLines, timePoint):
    kiKeys = set(klassInstances.keys())
    ktlKeys = set(klassTimeLines.keys())
    commonKeys = ktlKeys & kiKeys
    for commonKey in commonKeys:
        # add next time point
        klassTimeLines[commonKey].updateCount(klassInstances[commonKey])
    keysInKi = kiKeys - ktlKeys
    for keyInKi in keysInKi:
        # initialize a new timeline with an initial instance count
        klassTimeLines[keyInKi] = KlassTimeLine(keyInKi, klassInstances[keyInKi], timePoint)
    keysInKtl = ktlKeys - kiKeys
    for keyInKtl in keysInKtl:
        # no entry for this instance at this time, mark it as 0.
        klassTimeLines[keyInKtl].updateCount(0)
    
def calcTimeLines(files):
    klassTimeLines = {}
    # list of files sorted by timestamp
    files.sort(key = lambda x: os.stat(x).st_ctime)
    timePoint = 0
    for file in files:
        klassInstances = hist_utils.readIntoDict(file)
        applyInstancesToTimeLines(klassInstances, klassTimeLines, timePoint)
        timePoint += 1
    return klassTimeLines

def printDiffTimeLine(timeLine):
    # extract list of values from dictionary
    klassTimeLines = timeLine.values()
    klassTimeLines.sort(key = lambda ktl : ktl.counts[-1] - ktl.counts[0], reverse = True)
    for klassTimeLine in klassTimeLines:
        print("%s,%d" % (klassTimeLine.name, klassTimeLine.counts[-1] - klassTimeLine.counts[0]))
        
def printSlopeTimeLine(timeLine):
    # name, list
        klassTimeLines = timeLine.values()
        map(lambda tl : tl.calculateSlope(), klassTimeLines)
        klassTimeLines.sort(key = lambda ktl : ktl.slope, reverse = True)
        for klassTimeLine in klassTimeLines:
        #print("%s,%f,%s" % (klassTimeLine.name, klassTimeLine.slope, 
            print("%s,%f,%d" % (klassTimeLine.name, klassTimeLine.slope, klassTimeLine.counts[-1]))
        
def printTimeLine(timeLine):
    for klassName, klassTimeLine in timeLine.items():
        print(klassTimeLine)
    
def main(argv = None):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description = "create timeline spanning multiple jmap histogram files")
    parser.add_argument("histfiles", nargs="+", help = "one or more histogram files ")
    try:
        args = parser.parse_args(argv)
        klassTimeLines = calcTimeLines(glob.glob(args.histfiles[0]))
        #printTimeLine(klassTimeLines)
        increasing, alternating = filterTimeLines(klassTimeLines)
        print("always increasing:")
        printDiffTimeLine(increasing)
        print("alternating slopes:")
        # slope of least squares
        printSlopeTimeLine(alternating)        
    except SystemExit:
        return 2

# call script from command line
# call script from interpreter
# call function from other module
if __name__ == "__main__":
    sys.exit(main())
    
