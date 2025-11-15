This is a web app built in Flask designed for car enthusiasts and mechanics who work on cars and wish to record data about the cars they work on.

Information is recorded with the idea in mind that the car enthusiast/mechanic is performing work on a car in an effort to resell it. 
As such, there will be features to assist in making that effort easier like determining the estimated value of a car after the work is completed or while in progress.

It allows for recording of cars, the parts purchased and used for a particular car, as well as any labor related data such as employees and employee wages/hours performed for a particular car.

Features:
- Data Persistence via SQLite
  - Project context: 
    - Car Information (make, model, year, engine type, etc.)
    - Part Information (Part Name, Taxes paid, shipping cost, actual cost, and a link to a car it was used in)
    - Employee Basic Info (Name)
    - Labor Information (What car the labor was performed on, which employee, labor time, estimated labor value, etc.)
- Enforced Data Relations 
  - Project Context:
    - Link between Parts and Cars
    - Link between Cars and Labor
    - Link between Labor and Employee
- Upcoming: Data Processing (i.e. Cost Aggregation)
- For Developers: 
  - Easy setup for new tables: 
    - Create a SQL table and query it
    - Configure the Column Web Attributes as desired in the flask app code 
    - Pass the data to the necessary macros from helper.html which can be used to quickly create a new web page if desired or add/modify an existing one
    - See web/web_display.py and index.html/helper.html/car_view.html for examples.
    - Since Sqlite uses unix timestamps, the earliest date that can be stored is 1/1/1970 00:00:00 and the latest is 12/31/9999 23:59:59, as such there is a SQL_Constants.py script containing these values as constants for ease of access. 

Run by changing to this project's directory then running web/web_display.py as a flask application: python -m flask --app web/web_display run 
(Note: this is not for deployment, just for running in development mode)