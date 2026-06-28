from flask import current_app

from CarWorkInventoryDataManager.common_helper import lowerCaseKeyDict

TEXT_MAP_FILE_NAME = "mappings/textMapping.txt"

def getTextMapping():
    mapDict = lowerCaseKeyDict()
    with current_app.app_context():
        from pathlib import Path
        with current_app.open_resource(Path(__file__).parent.parent.resolve() / TEXT_MAP_FILE_NAME, mode='rt', encoding='utf-8') as f:
            for line in f.read().split(';'):
                if line:
                    strippedLine = line.strip('\r').strip('\n')
                    lineMap = strippedLine.split(',')
                    mapDict[lineMap[0]] = lineMap[1]
    return mapDict