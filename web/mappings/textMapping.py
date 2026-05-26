from flask import current_app
from common_helper import lowerCaseKeyDict

TEXT_MAP_FILE_NAME = "mappings/textMapping.txt"

def getTextMapping():
    mapDict = lowerCaseKeyDict()
    with current_app.app_context():
        with current_app.open_resource(TEXT_MAP_FILE_NAME) as f:
            for line in f.read().decode('utf-8').split(';'):
                if line:
                    strippedLine = line.strip('\r').strip('\n')
                    lineMap = strippedLine.split(',')
                    mapDict[lineMap[0]] = lineMap[1]
    return mapDict