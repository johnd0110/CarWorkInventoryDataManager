DROP TABLE IF EXISTS PurchasesHistory;
DROP TABLE IF EXISTS WorkEfforts;
DROP TABLE IF EXISTS Items;
DROP TABLE IF EXISTS ItemGroupTransactions;
DROP TABLE IF EXISTS Cars;
DROP TABLE IF EXISTS Employees;
DROP TABLE IF EXISTS ValueEstimates;
DROP TABLE IF EXISTS Purchases;
DROP TABLE IF EXISTS Sales;

-- Triggers are dropped automatically when the associated table is dropped

CREATE TABLE Cars(carKey INTEGER PRIMARY KEY,
                  purchaseKey INTEGER NOT NULL,
                  valueEstimateKey INTEGER DEFAULT NULL, -- A car may or may not have a value estimate,
                  make TEXT NOT NULL,
                  model TEXT NOT NULL,
                  "year" NUMERIC NOT NULL,
                  engineType TEXT NOT NULL,
                  mileage INTEGER NOT NULL DEFAULT 0,
                  additionalNotes TEXT NOT NULL DEFAULT '',
                  FOREIGN KEY (purchaseKey) REFERENCES Purchases(purchaseKey) ON UPDATE RESTRICT ON DELETE RESTRICT,
                  FOREIGN KEY (valueEstimateKey) REFERENCES ValueEstimates(valueEstimateKey) ON UPDATE RESTRICT ON DELETE SET NULL);

CREATE TRIGGER verifyCarsForeignKeyUpdate
BEFORE UPDATE OF purchaseKey, valueEstimateKey ON Cars
FOR EACH ROW
WHEN (OLD.purchaseKey != NEW.purchaseKey) OR (OLD.valueEstimateKey NOT NULL AND NEW.valueEstimateKey NOT NULL AND OLD.valueEstimateKey != NEW.valueEstimateKey)
BEGIN
    -- In general, updating a foreign key should not happen
    -- as in most cases in this schema: foreign keys are a 1:1 relationship
    --    There can only ever be at most 1 foreign key for a given row of data and that foreign key is strictly assigned
    --    To that row of data.
    --    So a foreign key entry can only realistically be in two scenarios in this application
    --          Scenario 1: No foreign key exists yet and there is no data in the relevant parent table yet for the respective child entry
    --          Scenario 2: A foreign key exists and there is data in the relevant parent table for the respective child entry
    --          Other scenarios are undefined and it is unclear how that data should be interpreted
    -- if the assigned foreign key changes, this will cause various problems
    --    1) The original foreign key becomes childless thus the relevant data loses meaning and breaks the strict 1:1 relationship
    --    2) If changed to a pre-existing foreign key, then the strict 1:1 relationship is broken and the data clarity is ruined
    --    3) If changed to a brand new foreign key, this new key would have no meaning and leads to no data
    --       and could lead to confusion down the line if not remedied and the parent table creates a row with that key.
    -- As such, there really isn't a good reason to run updates on the purchase key outside of severe measures like data corruption

    SELECT RAISE(ABORT, CONCAT('Updates to the cars foreign keys are not allowed. They should only be done by people who know what they are doing.'));
END;

-- Table for holding entries of grouped items that have been obtained together via some method
-- Must always be a child of another item row
-- Otherwise they have no inherent meaning or there is an unaccounted for item group
CREATE TABLE ItemGroupTransactions(itemGroupTransactionKey INTEGER PRIMARY KEY,
                                   description TEXT NOT NULL);

CREATE TABLE Items(itemKey INTEGER PRIMARY KEY,
                   itemGroupTransactionKey INTEGER NOT NULL,
                   purchaseKey INTEGER NOT NULL,
                   inCarKey INTEGER, -- An item could be orphaned as it may be used across multiple projects or was unused
                   valueEstimateKey INTEGER DEFAULT NULL, --An item may or may not have a value estimate
                   source TEXT NOT NULL DEFAULT '',
                   itemName TEXT NOT NULL,
                   additionalNotes TEXT NOT NULL DEFAULT '',
                   FOREIGN KEY (inCarKey) REFERENCES Cars(carKey) ON UPDATE RESTRICT ON DELETE RESTRICT,
                   FOREIGN KEY (itemGroupTransactionKey) REFERENCES ItemGroupTransactions(itemGroupTransactionKey) ON UPDATE RESTRICT ON DELETE SET NULL,
                   FOREIGN KEY (valueEstimateKey) REFERENCES ValueEstimates(valueEstimateKey) ON UPDATE RESTRICT ON DELETE SET NULL,
                   FOREIGN KEY (purchaseKey) REFERENCES Purchases(purchaseKey) ON UPDATE RESTRICT ON DELETE RESTRICT);

CREATE TRIGGER verifyItemsForeignKeyUpdate
BEFORE UPDATE OF itemGroupTransactionKey, valueEstimateKey, purchaseKey ON Items
FOR EACH ROW
WHEN (OLD.itemGroupTransactionKey != NEW.itemGroupTransactionKey) OR (OLD.valueEstimateKey NOT NULL AND NEW.valueEstimateKey NOT NULL AND OLD.valueEstimateKey != NEW.valueEstimateKey) OR OLD.purchaseKey != NEW.purchaseKey
BEGIN
    -- Refer to trigger verifyCarsForeignKeyUpdate for reasoning
    SELECT RAISE(ABORT, CONCAT('Updates to the items foreign keys are not allowed. They should only be done by people who know what they are doing.'));
END;


-- Table for holding purchase data of an item
-- An item may be something like a car row or a item row
-- Any row in this table should always be a child of another row in the database
-- Otherwise the row has no inherent meaning if not attached to an item
-- Or would mean there are unaccounted for purchases
CREATE TABLE Purchases(purchaseKey INTEGER PRIMARY KEY,
                       cost NUMERIC NOT NULL DEFAULT 0,
                       taxesPaid NUMERIC NOT NULL DEFAULT 0,
                       shippingCost NUMERIC NOT NULL DEFAULT 0,
                       refundAmount NUMERIC NOT NULL DEFAULT 0 CHECK (refundAmount >= 0),
                       totalSpent NUMERIC AS (cost + taxesPaid + shippingCost - refundAmount));

-- Version history table for the Purchases table
CREATE TABLE PurchasesHistory(purchaseKey INTEGER NOT NULL,
                              version INTEGER NOT NULL,
                              effectiveDate DATE NOT NULL CHECK (datetime(effectiveDate) IS effectiveDate) DEFAULT CURRENT_TIMESTAMP,
                              cost NUMERIC NOT NULL DEFAULT 0,
                              taxesPaid NUMERIC NOT NULL DEFAULT 0,
                              shippingCost NUMERIC NOT NULL DEFAULT 0,
                              refundAmount NUMERIC NOT NULL DEFAULT 0 CHECK (refundAmount >= 0),
                              FOREIGN KEY (purchaseKey) REFERENCES Purchases(purchaseKey) ON UPDATE RESTRICT ON DELETE RESTRICT,
                              PRIMARY KEY (purchaseKey, version));

-- ========================================= Purchase History Triggers ====================================

CREATE TRIGGER preventPurchasesHistoryUpdate
BEFORE UPDATE ON PurchasesHistory
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, CONCAT('Updates on PurchasesHistory are not allowed in order to maintain history integrity. Updates should only be done by people who know what they are doing.'));
END;

-- Verifies that the purchaseKey of the inserted row has valid history version data
CREATE TRIGGER verifyInsertOnPurchaseHistory
AFTER INSERT ON PurchasesHistory
FOR EACH ROW
BEGIN
    -- A history version of 0 is not the initial row, meaning we're missing the original row or the version got corrupted somehow
    SELECT RAISE(ROLLBACK, CONCAT('Purchase history versions do not start with 0 for purchase key: ', NEW.purchaseKey))
    WHERE EXISTS(SELECT ph.purchaseKey
                 FROM PurchasesHistory ph
                 WHERE ph.purchaseKey = NEW.purchaseKey
                 GROUP BY ph.purchaseKey
                 HAVING MIN(ph.version) != 0);

    -- History versions are not strictly increasing i.e. 1 -> 2 -> 3 -> 4 but not 1 -> 3 -> 5 or 1 -> 0
    SELECT RAISE(ROLLBACK, CONCAT('Purchase history versions are incorrect for purchase key: ', NEW.purchaseKey))
    WHERE EXISTS(SELECT strictly_increasing_history_versions.strictly_increasing_flag
                 FROM (SELECT CASE
                                WHEN ph.version - 1 == LAG(ph.version, 1, ph.version - 1) OVER (PARTITION BY ph.purchaseKey ORDER BY ph.version ASC)
                                THEN TRUE ELSE FALSE END as strictly_increasing_flag
                       FROM PurchasesHistory ph
                       WHERE ph.purchaseKey = NEW.purchaseKey
                      ) as strictly_increasing_history_versions
                 WHERE strictly_increasing_history_versions.strictly_increasing_flag == FALSE);
    -- By this point we have verified that the history versions are strictly increasing starting at 0 for the given new row's purchase key
END;

-- ==================================== Purchase Table Triggers ===========================================

CREATE TRIGGER generateHistoryRowAndVerifyPurchaseUpdate
AFTER UPDATE ON Purchases
FOR EACH ROW
BEGIN
    -- Prevent purchase key from changing from its original value
    -- In general, this shouldn't need to happen since this is just a surrogate with no other innate meaning
    SELECT RAISE(ABORT, CONCAT('Updates to the purchase key are not allowed. They should only be done by people who know what they are doing.'))
    WHERE OLD.purchaseKey != NEW.purchaseKey;

    -- Create a new purchase history row using the updated purchase data with the latest version incremented
    -- If no history rows found then set the version = 0 for the first row inserted
    INSERT INTO PurchasesHistory(purchaseKey, version, cost, taxesPaid, shippingCost, refundAmount)
    VALUES(NEW.purchaseKey,
           COALESCE((SELECT latestVersion FROM (SELECT ph2.purchaseKey, MAX(ph2.version) as latestVersion FROM purchasesHistory ph2 GROUP BY ph2.purchaseKey) ph_max_ver WHERE ph_max_ver.purchaseKey = NEW.purchaseKey) + 1, 0),
           NEW.cost,
           NEW.taxesPaid,
           NEW.shippingCost,
           NEW.refundAmount);
END;

-- ========================================================================================================

-- Table for holding estimated values of an item
-- An item may be something like a car row or a part row
-- Any row in this table should always be a child of another row in the database
-- Otherwise the row has no inherent meaning if not attached to an item
CREATE TABLE ValueEstimates(valueEstimateKey INTEGER PRIMARY KEY,
                            estimatedValue NUMERIC NOT NULL -- In general taxesPaid + shippingCost + cost = estimatedValue, but on older data this may differ
                            );

-- Table for holding sales of items or cars
-- TODO: Create links from cars/items to sales
-- TODO: Handle returned/refunded sales
--CREATE TABLE Sales(salesKey INTEGER PRIMARY KEY,
--                   amount NUMERIC NOT NULL);

CREATE TABLE Employees(employeeKey INTEGER PRIMARY KEY,
                       --employeeID INTEGER,
                       employeeName TEXT NOT NULL);

CREATE TABLE WorkEfforts(workEffortKey INTEGER PRIMARY KEY,
                         carKeyWorkedOn INTEGER NOT NULL,
                         employeeKey INTEGER NOT NULL,
                         -- Check constraint for dates like 2023-02-30 and malformed dates
                         -- Since sqlite quietly handles near leap year cases like 2023-02-30 to be 2023-03-02
                         -- Malformed dates become null so IS is needed to block null values from passing
                         -- since NULL values are not constraint violations by default in Sqlite
                         workEffortDate DATE NOT NULL CHECK (date(workEffortDate) IS workEffortDate),
                         laborHours NUMERIC NOT NULL,
                         estimatedPay NUMERIC NOT NULL,
                         workType TEXT NOT NULL,
                         FOREIGN KEY (carKeyWorkedOn) REFERENCES Cars(carKey) ON UPDATE RESTRICT ON DELETE RESTRICT,
                         FOREIGN KEY (employeeKey) REFERENCES Employees(employeeKey) ON UPDATE RESTRICT ON DELETE RESTRICT);

CREATE TRIGGER verifyWorkEffortsForeignKeyUpdate
BEFORE UPDATE OF carKeyWorkedOn, employeeKey ON WorkEfforts
FOR EACH ROW
WHEN (OLD.carKeyWorkedOn != NEW.carKeyWorkedOn) OR (OLD.employeeKey != NEW.employeeKey)
BEGIN
    -- For reasoning refer to trigger verifyCarsForeignKeyUpdate
    SELECT RAISE(ABORT, CONCAT('Updates to the work efforts foreign keys are not allowed. They should only be done by people who know what they are doing.'));
END;
