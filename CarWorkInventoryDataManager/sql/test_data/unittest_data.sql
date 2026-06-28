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
INSERT INTO Cars(carKey, purchaseKey, valueEstimateKey, make, model, "year", engineType, mileage, additionalNotes)
VALUES
(1, 1, NULL, "toyota", "corolla", 2012, "test", 50000, "test"),
(2, 2, NULL, "mitsubishi", "kodomo", 1999, "testtest", 1000, "test"),
(3, 3, 1, "chevy", "corvette", 1969, "V8", 100000, "test"),
(4, 4, 2, "ford", "ranger", 2012, "v9", 0, "test");

-- Items Purchases Table Test Data
INSERT INTO Purchases(purchaseKey, taxesPaid, shippingCost, cost, refundAmount)
VALUES (5, 100, 100, 1000, 0),
       (6, 10, 5, 75, 10),
       (7, 5, 10, 50, 0),
       (8, 25, 50, 200, 0),
       (9, 15, 15, 150, 0),
       (10, 200, 123, 2543, 0),
       (11, 110, 89, 198, 0),
       (12, 28.37, 13.99, 86.55, 0),
       (13, 8.88, 1.23, 46.41, 0),
       (14, 2.74, 3.09, 32.11, 0),
       (15, 1, 1, 1, 0),
       (16, 1, 2, 3, 10),
       (17, 123, 12, 1, 136);

INSERT INTO ValueEstimates(valueEstimateKey, estimatedValue)
VALUES (3, 1000),
       (4, 123),
       (5, 6),
       (6, 500),
       (7, 100);

-- Item Group Transactions Table Test Data
INSERT INTO ItemGroupTransactions(itemGroupTransactionKey, description)
VALUES (1, ''),
       (2, ''),
       (3, ''),
       (4, ''),
       (5, ''),
       (6, ''),
       (7, ''),
       (8, ''),
       (9, ''),
       (10, '');

-- Items Table Test Data
INSERT INTO Items(itemKey, inCarKey, itemGroupTransactionKey, valueEstimateKey, purchaseKey, source, itemName, additionalNotes)
VALUES (1, 1, 1, 3, 5, 'store', "engine", ''),
(2, 1, 1, NULL, 6, 'store', "alternator", ''),
(3, 1, 1, NULL, 7, 'store', "spark plug", ''),
(4, 1, 2, 4, 8, 'store', "tire", ''),
(5, 1, 3, 5, 9, 'store', "stereo", ''),
(6, 2, 4, 6, 10, 'store', "engine", ''),
(7, 3, 5, 7, 11, 'store', "hub cap", ''),
(8, 3, 5, NULL, 12, 'store', "front lights", ''),
(9, 3, 6, NULL, 13, 'store', "brake pad", ''),
(10, 3, 7, NULL, 14, 'store', "axle", ''),
(11, 4, 8, NULL, 15, 'store', 'front bumper', ''),
(12, 4, 9, NULL, 16, 'store', 'back bumper', ''),
(13, 4, 10, NULL, 17, 'store', 'key replacement', '');

-- Employees Table Test Data
INSERT INTO Employees(employeeKey, employeeName) VALUES
(1, "bob"),
(2, "joe"),
(3, "james"),
(4, "Carrie"),
(5, "jayden"),
(6, "john");

-- WorkEfforts Table Test Data
INSERT INTO WorkEfforts(WorkEffortKey, carKeyWorkedOn, employeeKey, workEffortDate, laborHours, estimatedPay, workType)
VALUES (1, 1, 1, date('2021-09-12'), 10, 500, 'engine work'),
(2, 1, 1, date('2022-10-07'), 10, 500, 'engine work'),
(3, 1, 1, date('2021-09-14'), 10, 500, 'engine work'),
(4, 1, 1, date('2023-05-12'), 10, 500, 'engine work'),
(5, 1, 1, date('2023-12-31'), 10, 500, 'engine work'),
(6, 1, 1, date('2021-01-01'), 10, 500, 'engine work'),
(7, 1, 1, date('2022-04-13'), 10, 500, 'engine work');

-- Leap Year test
INSERT INTO WorkEfforts(WorkEffortKey, carKeyWorkedOn, employeeKey, workEffortDate, laborHours, estimatedPay, workType)
VALUES (8, 1, 1, date('2024-02-29'), 10, 500, 'engine work'),
(9, 1, 1, date('2024-02-01'), 10, 500, 'engine work'),
(10, 1, 1, date('2022-07-31'), 10, 500, 'engine work');

-- Purchase History Test Data
UPDATE Purchases
SET cost = 12,
taxesPaid = 23,
shippingCost = 34,
refundAmount = 45
WHERE purchaseKey IN (1, 7, 8);

UPDATE Purchases
SET cost = 0,
taxesPaid = 0,
shippingCost = 0,
refundAmount = 0
WHERE purchaseKey IN (1);

UPDATE Purchases
SET cost = -100,
taxesPaid = 0,
shippingCost = 0,
refundAmount = 0
WHERE purchaseKey IN (1);

UPDATE Purchases
SET cost = 1,
taxesPaid = 1,
shippingCost = 1,
refundAmount = 10
WHERE purchaseKey IN (1);