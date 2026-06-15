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
- Configure the Column Web Attributes as desired in the flask app code 
- Pass the data to the necessary macros from `helper.html` which can be used to quickly create a new web page if desired or add/modify an existing one
- See `web/web_display.py` and `index.html`/`helper.html`/`car_view.html` for examples.
- Since Sqlite uses unix timestamps, the earliest date that can be stored is `1/1/1970 00:00:00` and the latest is `12/31/9999 23:59:59` 
  - There is a `sql/SQL_Constants.py` file containing these values as constants for ease of access. 
##### Data Conversion
- `sql/conversion/conversion_helper.py` is provided
  - This module provides a variety of dataclasses for storing data to be converted in a structured format
    - Serialization methods available to easily translate the data into a format that can be read by the carworkinvsql database object and insert the data into the database
  - Also, may have functions to assist with normalizing data such as converting dollar strings (e.g. $100 -> 100.0) into its appropriate value and data type

## Setup Instructions:
> ### Dependencies:
> Python >= 3.13\
> Flask >= 3.1.2 + Dependencies

1) Run `sql/CWI_schemaBuilder.py` as a script 
   - If the `CWI_database.db` database file has not been created yet:
     - It will generate a brand new `CWI_database.db` file under `sql/databases`
     - Otherwise, the existing `CWI_database.db` file is modified
   - Then `CWI_database.db` has its schema initialized using `sql/schema/schema.sql`
   - The script will print out to the terminal the whole schema of the database from the sqlite_schema table
   > [!CAUTION]
   > If this script is run again, and 'y' is provided in the terminal prompt:\
   > **EXISTING DATA IS DELETED DUE TO THE DROPPED TABLES**
2) Run `python -m flask --app web/web_display` run with the working directory as the project root directory
   - This by default runs Flask in testing mode due to `config/default_config.py`
   > [!CAUTION] 
   > This only runs the application in development mode\
   > **Actual Deployment setup TBD**
   