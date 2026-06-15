This is a web app built in Flask designed for car enthusiasts and mechanics who work on cars and wish to record data about the cars they work on.

Information is recorded with the idea in mind that the car enthusiast/mechanic is performing work on a car in an effort to resell it. 
As such, there are features to assist in making that effort easier like determining the estimated value of a car after the work is completed or while in progress.

It allows for recording of cars, the items purchased and used for a particular car, as well as any labor related data such as employees and employee wages/hours performed for a particular car.

Features:
- Data Persistence via SQLite
  - Project context: 
    - Car Information (make, model, year, engine type, etc.)
    - Item Information (Item Name, Where it was sourced from, additional notes that can't be categorized)
    - Purchase data (Taxes paid amount, shipping cost, actual cost of the item, and refunded amount)
      - Change history is also recorded
    - Value Estimate data
      - So that one may be able to compare their total investment against potential market value to identify potential profits and negotiation ranges.
    - Employee Basic Info (Name)
    - Labor Information (What car the labor was performed on, which employee, labor time, estimated labor value, etc.)
- Enforced Data Relations 
  - Project Context:
    - Purchases can be linked to either Cars or Items
      - Purchases track change history
    - Value estimates can be linked to either Cars or Items
    - Items can be grouped together to represent something akin to shopping carted orders
    - Link between Items and Cars
    - Link between Cars and Labor
    - Link between Labor and Employee
- Data Processing
  - Project Context:
    - Calculates total invested value of a car by totaling together the value of all labor and parts used for the car including the initial cost of the car
- For Developers: 
  - Easy setup for new tables: 
    - Create a SQL table and query it
    - Configure the Column Web Attributes as desired in the flask app code 
    - Pass the data to the necessary macros from helper.html which can be used to quickly create a new web page if desired or add/modify an existing one
    - See web/web_display.py and index.html/helper.html/car_view.html for examples.
    - Since Sqlite uses unix timestamps, the earliest date that can be stored is 1/1/1970 00:00:00 and the latest is 12/31/9999 23:59:59, as such there is a SQL_Constants.py script containing these values as constants for ease of access. 
  - Data Conversion
    - sql/conversion/conversion_helper.py is provided
      - This module provides a variety of dataclasses for storing data to be converted in a structured way
        - Serialization methods available to easily translate the data into a format that can be read by the carworkinvsql database object and insert the data into the database
      - Also, may have functions to assist with normalizing data such as converting dollar strings (e.g. $100 -> 100.0) into its appropriate value and data type

Run by changing to this project's directory then running web/web_display.py as a flask application: python -m flask --app web/web_display run 
(Note: this is not for deployment, just for running in development mode)