import glob
import sys
import os
sys.path.append('../')

import ActionLogParser

sampleLogFiles = glob.glob("sampleLog\\*")
ActionLogParser.parseActionLogs(sampleLogFiles)

