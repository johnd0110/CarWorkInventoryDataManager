from datetime import datetime

# sqlite unix timestamps epoch is 1/1/1970 and the maximum storable datetime is 12/31/9999 23:59:59
# These constants are created in order to validate any dates before we insert them into the sqlite database
MIN_SQL_YEAR = 1970
MAX_SQL_YEAR = 9999
MINIMUM_SQL_DATE = datetime(MIN_SQL_YEAR, 1, 1, 0, 0, 0)
MAXIMUM_SQL_DATE = datetime(MAX_SQL_YEAR, 12, 31, 23, 59, 59)