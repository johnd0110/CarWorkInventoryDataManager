

# What this is:
This is a web app built in Flask designed for car enthusiasts and mechanics who work on cars and wish to record data about the cars they work on.

Information is recorded with the idea in mind that the car enthusiast/mechanic is performing work on a car in an effort to resell it. 
As such, there are features to assist in making that effort easier like determining the estimated value of a car after the work is completed or while in progress.

It allows for recording of cars, the items purchased and used for a particular car, as well as any labor related data such as employees and employee wages/hours performed for a particular car.

### Features:
#### Data Persistence via SQLite
- Car Information (make, model, year, engine type, etc.)
- Item Information (Item Name, Where it was sourced from, additional notes that can't be categorized)
- Purchase data (Taxes paid amount, shipping cost, actual cost of the item, and refunded amount)
  - Change history is also recorded
- Value Estimate data
  - So that one may be able to compare their total investment against potential market value to identify potential profits and negotiation ranges.
- Employee Basic Info (Name)
- Labor Information (What car the labor was performed on, which employee, labor time, estimated labor value, etc.)

#### Enforced Data Relations
- Purchases can be linked to either Cars or Items
  - Purchases track change history
- Value estimates can be linked to either Cars or Items
- Items can be grouped together to represent something akin to shopping carted orders
- Labor can be tracked per project/car per employee
- Data Relationships (Child → Parent):
  - Cars
    - → Purchases
    - → Value Estimates
  - Items
    - → Cars
    - → Purchases
    - → Value Estimates
    - → Item Group Transactions
  - Labor 
    - → Cars
    - → Employees
  - Purchase History 
    - → Purchases

#### Data Processing
  - Calculates total invested value of a car by totaling together the value of all labor and parts used for the car including the initial cost of the car

#### For Developers: 
##### Easy setup for new tables: 
- Create a SQL table and query it
- Configure the Column Web Attributes as desired in the Flask app Python code 
- Pass the data to the relevant macros from [tables.html](CarWorkInventoryDataManager/web/templates/modules/tables.html) and [forms.html](CarWorkInventoryDataManager/web/templates/modules/forms.html) which can be used to quickly create a new web page if desired or add/modify an existing one
  - See [tableConfig.py](CarWorkInventoryDataManager/web/tableConfig.py) and [templates](CarWorkInventoryDataManager/web/templates/) for examples.
- Since Sqlite uses unix timestamps, the earliest date that can be stored is `1/1/1970 00:00:00` and the latest is `12/31/9999 23:59:59` 
  - There is a [SQL_Constants.py](CarWorkInventoryDataManager/sql/SQL_Constants.py) file containing these values as constants for ease of access. 
##### Data Conversion
- [conversion_helper.py](CarWorkInventoryDataManager/conversion/conversion_helper.py) is provided
  - This module provides a variety of dataclasses for storing data to be converted in a structured format
    - Serialization methods available to easily translate the data into a format that can be read by the carworkinvsql database object and insert the data into the database
  - Also, may have functions to assist with normalizing data such as converting dollar strings (e.g. $100 -> 100.0) into its appropriate value and data type
#### Custom CLI Commands
- How to call custom CLI command: `flask --app CarWorkInventoryDataManager:create_and_initialize_app CUSTOM_COMMAND_HERE`
  - `initTestData`
    - Clears out existing database data and prepopulates it with fake test data 
      - **<ins>DELETES ALL EXISTING DATA THUS: TESTING config option must be true for this to run</ins>**
  - `initDb`
    - Rebuilds database schema using `sql/schema/schema.sql` and prints out the entire schema after it is done.
      - **<ins>WARNING: DELETES ALL EXISTING DATA</ins>**
## Setup Instructions:
### Dependencies:
- Python >= 3.14
- Flask >= 3.1.3 + Dependencies

1) Run `initDb` custom flask command. See: [Custom CLI Commands](#custom-cli-commands)
   
2) Run `python -m flask --app CarWorkInventoryDataManager:create_and_initialize_app run` with the working directory as the project root directory
   - This by default runs Flask in testing mode due to [default_config.py](CarWorkInventoryDataManager/config/default_config.py)
   - _This only runs the application in development mode_
   - **Actual Deployment setup TBD**


   