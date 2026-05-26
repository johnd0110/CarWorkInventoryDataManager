-- Cars Table Test Data
INSERT INTO Cars(make, model, "year", engineType, mileage, initialCost)
VALUES
("toyota", "corolla", 2012, "test", 50000, 1234.99),
("mitsubishi", "kodomo", 1999, "testtest", 1000, 5000),
("chevy", "corvette", 1969, "V8", 100000, 20000),
("ford", "ranger", 2012, "v9", 0, 0);

-- Parts Table Test Data

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
VALUES (1, "engine", 100, 100, 1000);

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
VALUES (1, "alternator", 10, 5, 75);

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
VALUES (1, "spark plug", 5, 10, 50);

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
VALUES (1, "tire", 25, 50, 200);

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
VALUES (1, "stereo", 15, 15, 150);

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
VALUES (2, "engine", 200, 123, 2543);

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
VALUES (3, "hub cap", 110, 89, 198);

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
VALUES (3, "front lights", 28.37, 13.99, 86.55);

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
VALUES (3, "brake pad", 8.88, 1.23, 46.41);

INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price)
VALUES (3, "axle", 2.74, 3.09, 32.11);

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
VALUES (1, 1, date('2021-09-12'), 10, 500, 'engine work');

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
VALUES (1, 1, date('2022-10-07'), 10, 500, 'engine work');

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
VALUES (1, 1, date('2021-09-14'), 10, 500, 'engine work');

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
VALUES (1, 1, date('2023-05-12'), 10, 500, 'engine work');

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
VALUES (1, 1, date('2023-12-31'), 10, 500, 'engine work');

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
VALUES (1, 1, date('2021-01-01'), 10, 500, 'engine work');

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
VALUES (1, 1, date('2022-04-13'), 10, 500, 'engine work');

-- Leap Year test
INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
VALUES (1, 1, date('2024-02-29'), 10, 500, 'engine work');

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
VALUES (1, 1, date('2024-02-01'), 10, 500, 'engine work');

INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType)
VALUES (1, 1, date('2022-07-31'), 10, 500, 'engine work');