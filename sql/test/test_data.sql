-- Cars Table Test Data
INSERT INTO Cars(make, model, "year", engineType, mileage, initialCost)
VALUES
("toyota", "corolla", 2012, "test", 50000, 1234.99),
("mitsubishi", "kodomo", 1999, "testtest", 1000, 5000),
("chevy", "corvette", 1969, "V8", 100000, 20000),
("ford", "ranger", 2012, "v9", 0, 0);

-- Parts Table Test Data

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
SELECT carID, abs(RANDOM() % 100), abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
SELECT carID, abs(RANDOM() % 100), abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
SELECT carID, abs(RANDOM() % 100), abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
SELECT carID, abs(RANDOM() % 100), abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
SELECT carID, abs(RANDOM() % 100), abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
SELECT carID, abs(RANDOM() % 100), abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
SELECT carID, abs(RANDOM() % 100), abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
SELECT carID, abs(RANDOM() % 100), abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
SELECT carID, abs(RANDOM() % 100), abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
SELECT carID, abs(RANDOM() % 100), abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)
FROM Cars
ORDER BY RANDOM() LIMIT 1;


-- Employees Table Test Data
INSERT INTO Employees(employeeName) VALUES
("bob"),
("joe"),
("james"),
("Carrie"),
("jayden"),
("john");

-- WorkEfforts Table Test Data
INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carID, employeeKey, datetime(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carID, employeeKey, datetime(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carID, employeeKey, datetime(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carID, employeeKey, datetime(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carID, employeeKey, datetime(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carID, employeeKey, datetime(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carID, employeeKey, datetime(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carID, employeeKey, datetime(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carID, employeeKey, datetime(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carID, employeeKey, datetime(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

