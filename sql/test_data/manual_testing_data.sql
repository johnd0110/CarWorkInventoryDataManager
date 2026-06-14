DELETE FROM PurchasesHistory;
DELETE FROM WorkEfforts;
DELETE FROM Items;
DELETE FROM ItemGroupTransactions;
DELETE FROM Cars;
DELETE FROM Employees;
DELETE FROM ValueEstimates;
DELETE FROM Purchases;

-- Car Purchase Table Data
INSERT INTO Purchases(purchaseKey, cost)
VALUES (1, 1234.99), (2, 5000), (3, 20000), (4, 0);

-- Car Value Estimate Table Data
INSERT INTO ValueEstimates(valueEstimateKey, estimatedValue)
VALUES (1, 50000), (2, 3000);

-- Cars Table Test Data
INSERT INTO Cars(purchaseKey, valueEstimateKey, make, model, "year", engineType, mileage, additionalNotes)
VALUES
(1, NULL, "toyota", "corolla", 2012, "test", 50000, "test"),
(2, NULL, "mitsubishi", "kodomo", 1999, "testtest", 1000, "test"),
(3, 1, "chevy", "corvette", 1969, "V8", 100000, "test"),
(4, 2, "ford", "ranger", 2012, "v9", 0, "test");

-- Items Purchases Table Test Data
INSERT INTO Purchases(purchaseKey, taxesPaid, shippingCost, cost)
VALUES (5, abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)),
       (6, abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)),
       (7, abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)),
       (8, abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)),
       (9, abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)),
       (10, abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)),
       (11, abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)),
       (12, abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)),
       (13, abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)),
       (14, abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)),
       (15, abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)),
       (16, abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000)),
       (17, abs(RANDOM() % 1000), abs(RANDOM() % 1000), abs(RANDOM() % 1000));

INSERT INTO ValueEstimates(valueEstimateKey, estimatedValue)
VALUES (3, abs(RANDOM() % 100000)),
       (4, abs(RANDOM() % 100000)),
       (5, abs(RANDOM() % 100000)),
       (6, abs(RANDOM() % 100000)),
       (7, abs(RANDOM() % 100000));

-- Item Group Transactions Table Test Data
INSERT INTO ItemGroupTransactions(itemGroupTransactionKey, description)
VALUES (1, abs(RANDOM() % 1000)),
       (2, abs(RANDOM() % 1000)),
       (3, abs(RANDOM() % 1000)),
       (4, abs(RANDOM() % 1000)),
       (5, abs(RANDOM() % 1000)),
       (6, abs(RANDOM() % 1000)),
       (7, abs(RANDOM() % 1000)),
       (8, abs(RANDOM() % 1000)),
       (9, abs(RANDOM() % 1000)),
       (10, abs(RANDOM() % 1000));

-- Items Table Test Data

INSERT INTO Items(inCarKey, itemGroupTransactionKey, valueEstimateKey, purchaseKey, source, itemName, additionalNotes)
SELECT carKey, 1, 3, 5, abs(RANDOM() % 100), abs(RANDOM() % 100), abs(RANDOM() % 100)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Items(inCarKey, itemGroupTransactionKey, valueEstimateKey, purchaseKey, source, itemName, additionalNotes)
SELECT carKey, 1, NULL, 6, abs(RANDOM() % 100), abs(RANDOM() % 100), abs(RANDOM() % 100)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Items(inCarKey, itemGroupTransactionKey, valueEstimateKey, purchaseKey, source, itemName, additionalNotes)
SELECT carKey, 1, NULL, 7, abs(RANDOM() % 100), abs(RANDOM() % 100), abs(RANDOM() % 100)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Items(inCarKey, itemGroupTransactionKey, valueEstimateKey, purchaseKey, source, itemName, additionalNotes)
SELECT carKey, 2, 4, 8, abs(RANDOM() % 100), abs(RANDOM() % 100), abs(RANDOM() % 100)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Items(inCarKey, itemGroupTransactionKey, valueEstimateKey, purchaseKey, source, itemName, additionalNotes)
SELECT carKey, 3, 5, 9, abs(RANDOM() % 100), abs(RANDOM() % 100), abs(RANDOM() % 100)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Items(inCarKey, itemGroupTransactionKey, valueEstimateKey, purchaseKey, source, itemName, additionalNotes)
SELECT carKey, 4, 6, 10, abs(RANDOM() % 100), abs(RANDOM() % 100), abs(RANDOM() % 100)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Items(inCarKey, itemGroupTransactionKey, valueEstimateKey, purchaseKey, source, itemName, additionalNotes)
SELECT carKey, 5, 7, 11, abs(RANDOM() % 100), abs(RANDOM() % 100), abs(RANDOM() % 100)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Items(inCarKey, itemGroupTransactionKey, valueEstimateKey, purchaseKey, source, itemName, additionalNotes)
SELECT carKey, 5, NULL, 12, abs(RANDOM() % 100), abs(RANDOM() % 100), abs(RANDOM() % 100)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Items(inCarKey, itemGroupTransactionKey, valueEstimateKey, purchaseKey, source, itemName, additionalNotes)
SELECT carKey, 6, NULL, 13, abs(RANDOM() % 100), abs(RANDOM() % 100), abs(RANDOM() % 100)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Items(inCarKey, itemGroupTransactionKey, valueEstimateKey, purchaseKey, source, itemName, additionalNotes)
SELECT carKey, 7, NULL, 14, abs(RANDOM() % 100), abs(RANDOM() % 100), abs(RANDOM() % 100)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Items(inCarKey, itemGroupTransactionKey, valueEstimateKey, purchaseKey, source, itemName, additionalNotes)
SELECT carKey, 8, NULL, 15, abs(RANDOM() % 100), abs(RANDOM() % 100), abs(RANDOM() % 100)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Items(inCarKey, itemGroupTransactionKey, valueEstimateKey, purchaseKey, source, itemName, additionalNotes)
SELECT carKey, 9, NULL, 16, abs(RANDOM() % 100), abs(RANDOM() % 100), abs(RANDOM() % 100)
FROM Cars
ORDER BY RANDOM() LIMIT 1;

INSERT INTO Items(inCarKey, itemGroupTransactionKey, valueEstimateKey, purchaseKey, source, itemName, additionalNotes)
SELECT carKey, 10, NULL, 17, abs(RANDOM() % 100), abs(RANDOM() % 100), abs(RANDOM() % 100)
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
INSERT INTO WorkEfforts(carKeyWorkedOn, employeeKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carKey, employeeKey, date(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carKeyWorkedOn, employeeKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carKey, employeeKey, date(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carKeyWorkedOn, employeeKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carKey, employeeKey, date(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carKeyWorkedOn, employeeKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carKey, employeeKey, date(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carKeyWorkedOn, employeeKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carKey, employeeKey, date(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carKeyWorkedOn, employeeKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carKey, employeeKey, date(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carKeyWorkedOn, employeeKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carKey, employeeKey, date(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carKeyWorkedOn, employeeKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carKey, employeeKey, date(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carKeyWorkedOn, employeeKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carKey, employeeKey, date(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;

INSERT INTO WorkEfforts(carKeyWorkedOn, employeeKey, workEffortDate, laborHours, estimatedPay, workType)
SELECT carKey, employeeKey, date(strftime('%s', '1990-01-01 00:00:00') + abs(random() % (strftime('%s', '2025-01-01 00:00:00') - strftime('%s', '1990-01-01 00:00:00'))), 'unixepoch'), abs(RANDOM() % 24), abs(RANDOM() % 1000), abs(RANDOM() % 100)
FROM Cars, Employees
ORDER BY RANDOM() LIMIT 1;


-- Purchase History Test Data
UPDATE Purchases
SET cost = abs(RANDOM() % 1000),
taxesPaid = abs(RANDOM() % 1000),
shippingCost = abs(RANDOM() % 1000),
refundAmount = abs(RANDOM() % 1000)
WHERE purchaseKey IN (1, 7, 8);

UPDATE Purchases
SET cost = abs(RANDOM() % 1000),
taxesPaid = abs(RANDOM() % 1000),
shippingCost = abs(RANDOM() % 1000),
refundAmount = abs(RANDOM() % 1000)
WHERE purchaseKey IN (1);

UPDATE Purchases
SET cost = abs(RANDOM() % 1000),
taxesPaid = abs(RANDOM() % 1000),
shippingCost = abs(RANDOM() % 1000),
refundAmount = abs(RANDOM() % 1000)
WHERE purchaseKey IN (1);

UPDATE Purchases
SET cost = abs(RANDOM() % 1000),
taxesPaid = abs(RANDOM() % 1000),
shippingCost = abs(RANDOM() % 1000),
refundAmount = abs(RANDOM() % 1000)
WHERE purchaseKey IN (1);


