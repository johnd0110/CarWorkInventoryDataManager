DROP TABLE IF EXISTS WorkEfforts;
DROP TABLE IF EXISTS Parts;
DROP TABLE IF EXISTS Employees;
DROP TABLE IF EXISTS Cars;

CREATE TABLE Cars(carID INTEGER PRIMARY KEY,
                  make TEXT NOT NULL,
                  model TEXT NOT NULL,
                  "year" NUMERIC NOT NULL,
                  engineType TEXT NOT NULL,
                  mileage INTEGER NOT NULL DEFAULT 0,
                  initialCost NUMERIC NOT NULL);

CREATE TABLE Parts(partID INTEGER PRIMARY KEY,
                   InCarID INTEGER NOT NULL,
                   partName TEXT NOT NULL,
                   taxesPaid NUMERIC NOT NULL,
                   shippingCost NUMERIC NOT NULL,
                   price NUMERIC NOT NULL,
                   FOREIGN KEY (InCarID) REFERENCES Cars(carID) ON UPDATE RESTRICT ON DELETE RESTRICT);

CREATE TABLE Employees(employeeKey INTEGER PRIMARY KEY,
                       --employeeID INTEGER,
                       employeeName TEXT NOT NULL);

CREATE TABLE WorkEfforts(workEffortID INTEGER PRIMARY KEY,
                         carIDWorkedOn INTEGER NOT NULL,
                         employeeWorkerKey INTEGER NOT NULL,
                         -- Check constraint for dates like 2023-02-30 and malformed dates
                         -- Since sqlite quietly handles near leap year cases like 2023-02-30 to be 2023-03-02
                         -- Malformed dates become null so IS is needed to block null values from passing
                         -- since NULL values are not constraint violations by default in Sqlite
                         workEffortDate DATE NOT NULL CHECK (date(workEffortDate) IS workEffortDate),
                         laborHours NUMERIC NOT NULL,
                         estimatedPay NUMERIC NOT NULL,
                         workType TEXT NOT NULL,
                         FOREIGN KEY (carIDWorkedOn) REFERENCES Cars(CarID) ON UPDATE RESTRICT ON DELETE RESTRICT,
                         FOREIGN KEY (employeeWorkerKey) REFERENCES Employees(employeeKey) ON UPDATE RESTRICT ON DELETE RESTRICT);
