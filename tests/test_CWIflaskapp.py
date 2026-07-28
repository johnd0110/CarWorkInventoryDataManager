import sqlite3
from flask import url_for

from CarWorkInventoryDataManager.web.db import get_CWI_db
from helperForTests import baseTestSuite
from CarWorkInventoryDataManager import create_and_initialize_app

class CWIFlaskAppTests(baseTestSuite):
    def setUp(self):
        from tempfile import mkstemp
        self.tmpFileTuple = mkstemp()


        self.CWI_app = create_and_initialize_app()
        self.CWI_app.config.update({'TESTING': True,
                                    'DATABASE_URI': self.tmpFileTuple[1]})

        with self.CWI_app.app_context():
            from pathlib import Path
            db = get_CWI_db()
            db.connection.set_authorizer(None)
            with self.CWI_app.open_resource(Path(__file__).parent.parent.resolve() / 'CarWorkInventoryDataManager/sql/schema/schema.sql', mode='rt', encoding='utf-8') as schemaFile:
                db.executeSQLStatement(schemaFile.read(), columnNamesClassWrapper=None, IsScript=True)

            with self.CWI_app.open_resource(Path(__file__).parent.parent.resolve() / 'CarWorkInventoryDataManager/sql/test_data/unittest_data.sql', mode='rt', encoding='utf-8') as unitTestDataFile:
                db.executeSQLStatement(unitTestDataFile.read(), columnNamesClassWrapper=None, IsScript=True)
            db.connection.set_authorizer(db.CWISqlAuthorizerCallback)


        self.testClient = self.CWI_app.test_client()

    def tearDown(self):
        import os
        os.close(self.tmpFileTuple[0])
        os.unlink(self.tmpFileTuple[1])


    def clearDatabase(self):
        with self.CWI_app.app_context():
            db = get_CWI_db()
            db.connection.set_authorizer(None)
            _ = db.executeSQLStatement("""DELETE FROM PurchasesHistory;
                                          DELETE FROM WorkEfforts;
                                          DELETE FROM Items;
                                          DELETE FROM ItemGroupTransactions;
                                          DELETE FROM Cars;
                                          DELETE FROM Employees;
                                          DELETE FROM ValueEstimates;
                                          DELETE FROM Purchases;
                                          """,
                                       columnNamesClassWrapper=None,
                                       IsScript=True)
            db.connection.set_authorizer(db.CWISqlAuthorizerCallback)

    def clientResponseHtmlTester(self, url, expectedHtml):
        response = self.testClient.get(url)
        self.assertEqual(response.status_code, 200)
        # Don't care about new line characters and white space, just the actual html text
        responseText = response.text
        cleanedUpResponseText = self.removeWhitespaceAndNewLineCharactersFromString(responseText.strip())
        # The expected table structure may have formatting when passed in
        # This is just so it is easy to read what the test case is
        # When doing the actual test, remove the formatting
        cleanedUpExpectedTableHtmlStructure = self.removeWhitespaceAndNewLineCharactersFromString(expectedHtml)
        self.assertIn(cleanedUpExpectedTableHtmlStructure, cleanedUpResponseText, msg=f'\nExpected:{expectedHtml.replace(' ', '')}\nActual:\n{responseText.replace(' ', '')}')

    def removeWhitespaceAndNewLineCharactersFromString(self, strToModify: str) -> str:
        return strToModify.replace('\n', '').replace(' ', '')

    def testCWIUniqueDbInstanceAndTeardown(self):
        # While app is active, there should only exist one unique database instance within an app context
        with self.CWI_app.app_context():
            CWI_db = get_CWI_db()
            self.assertIs(CWI_db, get_CWI_db())

        # Once app context finishes, the database connection should get torn down (closed) by the flask app
        # This database instance shouldn't allow execution of statements since it's closed
        self.exceptionMessageTester(sqlite3.ProgrammingError,
                                    'Cannot operate on a closed database.',
                                    'Unknown Error: ',
                                    CWI_db.CWI_executeSQLStatement,
                                    "SELECT 1")

    def testWebHomeNoResultsTextDisplaysWhenNoRelevantDataExists(self):
        HOME_URL = '/'
        self.clearDatabase()

        # No data in the database yet,
        # so the template should render display tables as No results found in a paragraph element
        tableids = ['cars_table', 'employees_table']
        for tableid in tableids:
            self.clientResponseHtmlTester(HOME_URL, f'<p id={tableid}> No results found. </p>')

    def testWebHomeCarsTableDisplaysWhenCarsExist(self):
        HOME_URL = '/'
        with self.CWI_app.test_request_context():
            self.clientResponseHtmlTester(HOME_URL, f"""
                <table id=cars_table>
                    <colgroup>
                        <col span="1" style=visibility:collapse>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:collapse>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                    </colgroup>
                    <thead>
                        <tr>
                            <th scope="col" id=carkey_tablecolumn></th>
                            <th scope="col" id=make_tablecolumn>Make</th>
                            <th scope="col" id=model_tablecolumn>Model</th>
                            <th scope="col" id=year_tablecolumn>Year</th>
                            <th scope="col" id=enginetype_tablecolumn>EngineType</th>
                            <th scope="col" id=mileage_tablecolumn>Mileage</th>
                            <th scope="col" id=purchasekey_tablecolumn></th>
                            <th scope="col" id=taxespaid_tablecolumn>TaxesPaid(USD)</th>
                            <th scope="col" id=shippingcost_tablecolumn>ShippingCost(USD)</th>
                            <th scope="col" id=cost_tablecolumn>Cost(USD)</th>
                            <th scope="col" id=refundamount_tablecolumn>AmountRefunded(USD)</th>
                            <th scope="col" id=purchasetotal_tablecolumn>PurchaseTotal(USD)</th>
                            <th scope="col" id=totalinvestedvalue_tablecolumn>TotalInvestedValue(USD)</th>
                            <th scope="col" id=estimatedvalue_tablecolumn>EstimatedActualValue(USD)</th>
                            <th scope="col" id=additionalnotes_tablecolumn>AdditionalNotes</th>
                            <th scope="col" id=viewlink_tablecolumn></th>
                            <th scope="col" id=editlink_tablecolumn></th>
                            <th scope="col" id=viewpurchasehistorylink_tablecolumn></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td headers=carkey_tablecolumn>1</td>
                            <td headers=make_tablecolumn>toyota</td>
                            <td headers=model_tablecolumn>corolla</td>
                            <td headers=year_tablecolumn>2012</td>
                            <td headers=enginetype_tablecolumn>test</td>
                            <td headers=mileage_tablecolumn>50000</td>
                            <td headers=purchasekey_tablecolumn>1</td>
                            <td headers=taxespaid_tablecolumn>1.00</td>
                            <td headers=shippingcost_tablecolumn>1.00</td>
                            <td headers=cost_tablecolumn>1.00</td>
                            <td headers=refundamount_tablecolumn>10.00</td>
                            <td headers=purchasetotal_tablecolumn>-7.00</td>
                            <td headers=totalinvestedvalue_tablecolumn>6501.00</td>
                            <td headers=estimatedvalue_tablecolumn>0.00</td>
                            <td headers=additionalnotes_tablecolumn>test</td>
                            <td headers=viewlink_tablecolumn><a href={url_for('web_car.car_items', keyorid=1)}>View</a></td>
                            <td headers=editlink_tablecolumn><a href={url_for('web_car.car_edit', keyorid=1)}>Edit</a></td>
                            <td headers=viewpurchasehistorylink_tablecolumn><a href={url_for('web_purchase_data.purchase_history_page', keyorid=1)}>View Purchase History</a></td>
                        </tr>                        
                        <tr>
                            <td headers=carkey_tablecolumn>2</td>
                            <td headers=make_tablecolumn>mitsubishi</td>
                            <td headers=model_tablecolumn>kodomo</td>
                            <td headers=year_tablecolumn>1999</td>
                            <td headers=enginetype_tablecolumn>testtest</td>
                            <td headers=mileage_tablecolumn>1000</td>
                            <td headers=purchasekey_tablecolumn>2</td>
                            <td headers=taxespaid_tablecolumn>0.00</td>
                            <td headers=shippingcost_tablecolumn>0.00</td>
                            <td headers=cost_tablecolumn>5000.00</td>
                            <td headers=refundamount_tablecolumn>0.00</td>
                            <td headers=purchasetotal_tablecolumn>5000.00</td>
                            <td headers=totalinvestedvalue_tablecolumn>7866.00</td>
                            <td headers=estimatedvalue_tablecolumn>0.00</td>
                            <td headers=additionalnotes_tablecolumn>test</td>
                            <td headers=viewlink_tablecolumn><a href={url_for('web_car.car_items', keyorid=2)}>View</a></td>
                            <td headers=editlink_tablecolumn><a href={url_for('web_car.car_edit', keyorid=2)}>Edit</a></td>
                            <td headers=viewpurchasehistorylink_tablecolumn><a href={url_for('web_purchase_data.purchase_history_page', keyorid=2)}>View Purchase History</a></td>
                        </tr>                        
                        <tr>
                            <td headers=carkey_tablecolumn>3</td>
                            <td headers=make_tablecolumn>chevy</td>
                            <td headers=model_tablecolumn>corvette</td>
                            <td headers=year_tablecolumn>1969</td>
                            <td headers=enginetype_tablecolumn>V8</td>
                            <td headers=mileage_tablecolumn>100000</td>
                            <td headers=purchasekey_tablecolumn>3</td>
                            <td headers=taxespaid_tablecolumn>0.00</td>
                            <td headers=shippingcost_tablecolumn>0.00</td>
                            <td headers=cost_tablecolumn>20000.00</td>
                            <td headers=refundamount_tablecolumn>0.00</td>
                            <td headers=purchasetotal_tablecolumn>20000.00</td>
                            <td headers=totalinvestedvalue_tablecolumn>20620.37</td>
                            <td headers=estimatedvalue_tablecolumn>50000.00</td>
                            <td headers=additionalnotes_tablecolumn>test</td>
                            <td headers=viewlink_tablecolumn><a href={url_for('web_car.car_items', keyorid=3)}>View</a></td>
                            <td headers=editlink_tablecolumn><a href={url_for('web_car.car_edit', keyorid=3)}>Edit</a></td>
                            <td headers=viewpurchasehistorylink_tablecolumn><a href={url_for('web_purchase_data.purchase_history_page', keyorid=3)}>View Purchase History</a></td>
                        </tr>                        
                        <tr>
                            <td headers=carkey_tablecolumn>4</td>
                            <td headers=make_tablecolumn>ford</td>
                            <td headers=model_tablecolumn>ranger</td>
                            <td headers=year_tablecolumn>2012</td>
                            <td headers=enginetype_tablecolumn>v9</td>
                            <td headers=mileage_tablecolumn>0</td>
                            <td headers=purchasekey_tablecolumn>4</td>
                            <td headers=taxespaid_tablecolumn>0.00</td>
                            <td headers=shippingcost_tablecolumn>0.00</td>
                            <td headers=cost_tablecolumn>0.00</td>
                            <td headers=refundamount_tablecolumn>0.00</td>
                            <td headers=purchasetotal_tablecolumn>0.00</td>
                            <td headers=totalinvestedvalue_tablecolumn>-1.00</td>
                            <td headers=estimatedvalue_tablecolumn>3000.00</td>
                            <td headers=additionalnotes_tablecolumn>test</td>
                            <td headers=viewlink_tablecolumn><a href={url_for('web_car.car_items', keyorid=4)}>View</a></td>
                            <td headers=editlink_tablecolumn><a href={url_for('web_car.car_edit', keyorid=4)}>Edit</a></td>
                            <td headers=viewpurchasehistorylink_tablecolumn><a href={url_for('web_purchase_data.purchase_history_page', keyorid=4)}>View Purchase History</a></td>
                        </tr>
                    </tbody>
                    <tfoot>
                        <tr>
                            <th colspan=11 scope=col></th>
                            <th colspan=1 scope=col id=footerTotalSpent_tablecolumn>Total Spent (USD)</th>
                            <th colspan=6 scope=col></th>
                        </tr>
                        <tr>
                            <td colspan=11></td>
                            <td colspan=1 headers=footerTotalSpent_tablecolumn>24993.00</td>
                            <td colspan=6></td>
                        </tr>
                    </tfoot>
                </table>
                """)

    def testWebHomeCarsFormExists(self):
        HOME_URL = '/'
        self.clientResponseHtmlTester(HOME_URL, f"""
        <form method="post" autocomplete="off" id=cars_form>
            <fieldset form=cars_form>
                <legend> Add New Entry </legend>
                
                <label for=make_input> Make </label>
                <input type=text form=cars_form spellcheck="true" autocomplete="on" id=make_input name=make required/>
                <br/>
                <label for=model_input> Model </label>
                <input type=text form=cars_form spellcheck="true" autocomplete="on" id=model_input name=model required/>
                <br/>
                <label for=year_input> Year </label>
                <input type=number form=cars_form spellcheck="true" autocomplete="on" min=1970 max=9999 step=1 id=year_input name=year required/>
                <br/>
                <label for=enginetype_input> Engine Type </label>
                <input type=text form=cars_form spellcheck="true" autocomplete="on" id=enginetype_input name=enginetype required/>       
                <br/>
                <label for=mileage_input> Mileage </label>
                <input type=number form=cars_form spellcheck="true" autocomplete="on" min=0 max=None step=None id=mileage_input name=mileage required/>
                <br/>
                <label for=taxespaid_input> Taxes Paid (USD) </label>
                <input type=number form=cars_form spellcheck="true" autocomplete="on" min=0 max=None step=0.01 id=taxespaid_input name=taxespaid required/>
                <br/>
                <label for=shippingcost_input> Shipping Cost (USD) </label>
                <input type=number form=cars_form spellcheck="true" autocomplete="on" min=0 max=None step=0.01 id=shippingcost_input name=shippingcost required/>
                <br/>
                <label for=cost_input> Cost (USD) </label>
                <input type=number form=cars_form spellcheck="true" autocomplete="on" min=None max=None step=0.01 id=cost_input name=cost required/>
                <br/>
                <label for=refundamount_input> Amount Refunded (USD) </label>
                <input type=number form=cars_form spellcheck="true" autocomplete="on" min=0 max=None step=0.01 id=refundamount_input name=refundamount required/>
                <br/>
                <label for=estimatedvalue_input> Estimated Actual Value (USD) </label>
                <input type=number form=cars_form spellcheck="true" autocomplete="on" min=0 max=None step=0.01 id=estimatedvalue_input name=estimatedvalue/>
                <br/>
                <label for=additionalnotes_input> Additional Notes </label>
                <textarea form=cars_form id=additionalnotes_input name=additionalnotes spellcheck="true" autocomplete="on" wrap=soft></textarea>
                <br/>
                <button type="submit" name="submit"> Submit </button>
                <input type="hidden" id=cars_form name="formid" value=cars_form>
            </fieldset>
        </form>
        """)

    def testWebHomeEmployeesTableDisplaysWhenEmployeesExist(self):
        HOME_URL = '/'
        self.clientResponseHtmlTester(HOME_URL, f"""
            <table id=employees_table>
                <colgroup>
                    <col span="1" style=visibility:collapse>
                    <col span="1" style=visibility:initial>
                </colgroup>
                <thead>
                    <tr>
                        <th scope="col" id=employeekey_tablecolumn></th>
                        <th scope="col" id=employeename_tablecolumn>EmployeeName</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td headers=employeekey_tablecolumn>1</td>
                        <td headers=employeename_tablecolumn>bob</td>
                    </tr>
                    <tr>
                        <td headers=employeekey_tablecolumn>2</td>
                        <td headers=employeename_tablecolumn>joe</td>
                    </tr>
                    <tr>
                        <td headers=employeekey_tablecolumn>3</td>
                        <td headers=employeename_tablecolumn>james</td>
                    </tr>
                    <tr>
                        <td headers=employeekey_tablecolumn>4</td>
                        <td headers=employeename_tablecolumn>Carrie</td>
                    </tr>
                    <tr>
                        <td headers=employeekey_tablecolumn>5</td>
                        <td headers=employeename_tablecolumn>jayden</td>
                    </tr>
                    <tr>
                        <td headers=employeekey_tablecolumn>6</td>
                        <td headers=employeename_tablecolumn>john</td>
                    </tr>                        
                </tbody>
            </table>
            """)

    def testWebHomeEmployeesFormExists(self):
        HOME_URL = '/'
        self.clientResponseHtmlTester(HOME_URL, f"""
        <form method="post" autocomplete="off" id=employees_form>
            <fieldset form=employees_form>
                <legend> Add New Entry </legend>

                <label for=employeename_input> Employee Name </label>
                <input type=text form=employees_form spellcheck="true" autocomplete="on" id=employeename_input name=employeename required/>
                <br/>
                <button type="submit" name="submit"> Submit </button>
                <input type="hidden" id=employees_form name="formid" value=employees_form>
            </fieldset>
        </form>
        """)

    def testWebCarCarsTableDisplaysWhenCarsExist(self):
        VIEW_CAR_KEY_1_URL = '/car/items/1'
        with self.CWI_app.test_request_context():
            self.clientResponseHtmlTester(VIEW_CAR_KEY_1_URL, f"""
                <table id=singlecar_table>
                    <colgroup>
                        <col span="1" style=visibility:collapse>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:collapse>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                    </colgroup>
                    <thead>
                        <tr>
                            <th scope="col" id=carkey_tablecolumn></th>
                            <th scope="col" id=make_tablecolumn>Make</th>
                            <th scope="col" id=model_tablecolumn>Model</th>
                            <th scope="col" id=year_tablecolumn>Year</th>
                            <th scope="col" id=enginetype_tablecolumn>EngineType</th>
                            <th scope="col" id=mileage_tablecolumn>Mileage</th>
                            <th scope="col" id=purchasekey_tablecolumn></th>
                            <th scope="col" id=taxespaid_tablecolumn>TaxesPaid(USD)</th>
                            <th scope="col" id=shippingcost_tablecolumn>ShippingCost(USD)</th>
                            <th scope="col" id=cost_tablecolumn>Cost(USD)</th>
                            <th scope="col" id=refundamount_tablecolumn>AmountRefunded(USD)</th>
                            <th scope="col" id=purchasetotal_tablecolumn>PurchaseTotal(USD)</th>
                            <th scope="col" id=totalinvestedvalue_tablecolumn>TotalInvestedValue(USD)</th>
                            <th scope="col" id=estimatedvalue_tablecolumn>EstimatedActualValue(USD)</th>
                            <th scope="col" id=additionalnotes_tablecolumn>AdditionalNotes</th>
                            <th scope="col" id=viewpurchasehistorylink_tablecolumn></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td headers=carkey_tablecolumn>1</td>
                            <td headers=make_tablecolumn>toyota</td>
                            <td headers=model_tablecolumn>corolla</td>
                            <td headers=year_tablecolumn>2012</td>
                            <td headers=enginetype_tablecolumn>test</td>
                            <td headers=mileage_tablecolumn>50000</td>
                            <td headers=purchasekey_tablecolumn>1</td>
                            <td headers=taxespaid_tablecolumn>1.00</td>
                            <td headers=shippingcost_tablecolumn>1.00</td>
                            <td headers=cost_tablecolumn>1.00</td>
                            <td headers=refundamount_tablecolumn>10.00</td>
                            <td headers=purchasetotal_tablecolumn>-7.00</td>
                            <td headers=totalinvestedvalue_tablecolumn>6501.00</td>
                            <td headers=estimatedvalue_tablecolumn>0.00</td>
                            <td headers=additionalnotes_tablecolumn>test</td>
                            <td headers=viewpurchasehistorylink_tablecolumn><a href={url_for('web_purchase_data.purchase_history_page', keyorid=1)}>View Purchase History</a></td>
                        </tr>                        
                    </tbody>
                </table>
                """)

    def testWebCarItemsTableDisplaysWhenItemsExist(self):
        VIEW_CAR_KEY_1_URL = '/car/items/1'
        with self.CWI_app.test_request_context():
            self.clientResponseHtmlTester(VIEW_CAR_KEY_1_URL, f"""
                <table id=items_table>
                    <colgroup>
                        <col span="1" style=visibility:collapse>
                        <col span="1" style=visibility:collapse>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:collapse>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                        <col span="1" style=visibility:initial>
                    </colgroup>
                    <thead>
                        <tr>
                            <th scope="col" id=itemkey_tablecolumn></th>
                            <th scope="col" id=incarkey_tablecolumn></th>
                            <th scope="col" id=source_tablecolumn>Item Source</th>
                            <th scope="col" id=itemname_tablecolumn>Item Name</th>
                            <th scope="col" id=purchasekey_tablecolumn></th>
                            <th scope="col" id=taxespaid_tablecolumn>TaxesPaid(USD)</th>
                            <th scope="col" id=shippingcost_tablecolumn>ShippingCost(USD)</th>
                            <th scope="col" id=cost_tablecolumn>Cost(USD)</th>
                            <th scope="col" id=refundamount_tablecolumn>AmountRefunded(USD)</th>
                            <th scope="col" id=purchasetotal_tablecolumn>PurchaseTotal(USD)</th>
                            <th scope="col" id=estimatedvalue_tablecolumn>EstimatedActualValue(USD)</th>
                            <th scope="col" id=additionalnotes_tablecolumn>AdditionalNotes</th>
                            <th scope="col" id=viewpurchasehistorylink_tablecolumn></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td headers=itemkey_tablecolumn>1</td>
                            <td headers=incarkey_tablecolumn>1</td>
                            <td headers=source_tablecolumn>store</td>
                            <td headers=itemname_tablecolumn>engine</td>
                            <td headers=purchasekey_tablecolumn>5</td>
                            <td headers=taxespaid_tablecolumn>100.00</td>
                            <td headers=shippingcost_tablecolumn>100.00</td>
                            <td headers=cost_tablecolumn>1000.00</td>
                            <td headers=refundamount_tablecolumn>0.00</td>
                            <td headers=purchasetotal_tablecolumn>1200.00</td>
                            <td headers=estimatedvalue_tablecolumn>1000.00</td>
                            <td headers=additionalnotes_tablecolumn></td>
                            <td headers=viewpurchasehistorylink_tablecolumn><a href={url_for('web_purchase_data.purchase_history_page', keyorid=5)}>View Purchase History</a></td>
                        </tr>              
                        <tr>
                            <td headers=itemkey_tablecolumn>2</td>
                            <td headers=incarkey_tablecolumn>1</td>
                            <td headers=source_tablecolumn>store</td>
                            <td headers=itemname_tablecolumn>alternator</td>
                            <td headers=purchasekey_tablecolumn>6</td>
                            <td headers=taxespaid_tablecolumn>10.00</td>
                            <td headers=shippingcost_tablecolumn>5.00</td>
                            <td headers=cost_tablecolumn>75.00</td>
                            <td headers=refundamount_tablecolumn>10.00</td>
                            <td headers=purchasetotal_tablecolumn>80.00</td>
                            <td headers=estimatedvalue_tablecolumn>N/A</td>
                            <td headers=additionalnotes_tablecolumn></td>
                            <td headers=viewpurchasehistorylink_tablecolumn><a href={url_for('web_purchase_data.purchase_history_page', keyorid=6)}>View Purchase History</a></td>
                        </tr>              
                        <tr>
                            <td headers=itemkey_tablecolumn>3</td>
                            <td headers=incarkey_tablecolumn>1</td>
                            <td headers=source_tablecolumn>store</td>
                            <td headers=itemname_tablecolumn>spark plug</td>
                            <td headers=purchasekey_tablecolumn>7</td>
                            <td headers=taxespaid_tablecolumn>23.00</td>
                            <td headers=shippingcost_tablecolumn>34.00</td>
                            <td headers=cost_tablecolumn>12.00</td>
                            <td headers=refundamount_tablecolumn>45.00</td>
                            <td headers=purchasetotal_tablecolumn>24.00</td>
                            <td headers=estimatedvalue_tablecolumn>N/A</td>
                            <td headers=additionalnotes_tablecolumn></td>
                            <td headers=viewpurchasehistorylink_tablecolumn><a href={url_for('web_purchase_data.purchase_history_page', keyorid=7)}>View Purchase History</a></td>
                        </tr>              
                        <tr>
                            <td headers=itemkey_tablecolumn>4</td>
                            <td headers=incarkey_tablecolumn>1</td>
                            <td headers=source_tablecolumn>store</td>
                            <td headers=itemname_tablecolumn>tire</td>
                            <td headers=purchasekey_tablecolumn>8</td>
                            <td headers=taxespaid_tablecolumn>23.00</td>
                            <td headers=shippingcost_tablecolumn>34.00</td>
                            <td headers=cost_tablecolumn>12.00</td>
                            <td headers=refundamount_tablecolumn>45.00</td>
                            <td headers=purchasetotal_tablecolumn>24.00</td>
                            <td headers=estimatedvalue_tablecolumn>123.00</td>
                            <td headers=additionalnotes_tablecolumn></td>
                            <td headers=viewpurchasehistorylink_tablecolumn><a href={url_for('web_purchase_data.purchase_history_page', keyorid=8)}>View Purchase History</a></td>
                        </tr>              
                        <tr>
                            <td headers=itemkey_tablecolumn>5</td>
                            <td headers=incarkey_tablecolumn>1</td>
                            <td headers=source_tablecolumn>store</td>
                            <td headers=itemname_tablecolumn>stereo</td>
                            <td headers=purchasekey_tablecolumn>9</td>
                            <td headers=taxespaid_tablecolumn>15.00</td>
                            <td headers=shippingcost_tablecolumn>15.00</td>
                            <td headers=cost_tablecolumn>150.00</td>
                            <td headers=refundamount_tablecolumn>0.00</td>
                            <td headers=purchasetotal_tablecolumn>180.00</td>
                            <td headers=estimatedvalue_tablecolumn>6.00</td>
                            <td headers=additionalnotes_tablecolumn></td>
                            <td headers=viewpurchasehistorylink_tablecolumn><a href={url_for('web_purchase_data.purchase_history_page', keyorid=9)}>View Purchase History</a></td>
                        </tr>              
                    </tbody>
                    <tfoot>
                        <tr>
                            <th colspan=9 scope=col></th>
                            <th colspan=1 scope=col id=footerTotalSpent_tablecolumn>Total Spent (USD)</th>                    
                            <th colspan=1 scope=col id=footerTotalEstimatedValue_tablecolumn>Total Estimated Value (USD)</th>
                            <th colspan=2 scope=col></th>
                        </tr>
                        <tr>
                            <td colspan=9></td>
                            <td colspan=1 headers=footerTotalSpent_tablecolumn>1508.00</td>
                            <td colspan=1 headers=footerTotalEstimatedValue_tablecolumn>1129.00</td>
                            <td colspan=2></td>
                        </tr>
                    </tfoot>
                </table>
                """)

    def testWebCarItemsFormExists(self):
        VIEW_CAR_KEY_1_URL = '/car/items/1'
        self.clientResponseHtmlTester(VIEW_CAR_KEY_1_URL, f"""
        <form method="post" autocomplete="off" id=items_form>
            <fieldset form=items_form>
                <legend> Add New Entry </legend>

                <label for=source_input> Item Source </label>
                <input type=text form=items_form spellcheck="true" autocomplete="on" id=source_input name=source required/>
                <br/>
                <label for=itemname_input> Item Name </label>
                <input type=text form=items_form spellcheck="true" autocomplete="on" id=itemname_input name=itemname required/>
                <br/>
                <label for=taxespaid_input> Taxes Paid (USD) </label>
                <input type=number form=items_form spellcheck="true" autocomplete="on" min=0 max=None step=0.01 id=taxespaid_input name=taxespaid required/>
                <br/>
                <label for=shippingcost_input> Shipping Cost (USD) </label>
                <input type=number form=items_form spellcheck="true" autocomplete="on" min=0 max=None step=0.01 id=shippingcost_input name=shippingcost required/>
                <br/>
                <label for=cost_input> Cost (USD) </label>
                <input type=number form=items_form spellcheck="true" autocomplete="on" min=None max=None step=0.01 id=cost_input name=cost required/>
                <br/>
                <label for=refundamount_input> Amount Refunded (USD) </label>
                <input type=number form=items_form spellcheck="true" autocomplete="on" min=0 max=None step=0.01 id=refundamount_input name=refundamount required/>
                <br/>
                <label for=estimatedvalue_input> Estimated Actual Value (USD) </label>
                <input type=number form=items_form spellcheck="true" autocomplete="on" min=0 max=None step=0.01 id=estimatedvalue_input name=estimatedvalue/>
                <br/>
                <label for=additionalnotes_input> Additional Notes </label>
                <textarea form=items_form id=additionalnotes_input name=additionalnotes spellcheck="true" autocomplete="on" wrap=soft ></textarea>
                <br/>
                <button type="submit" name="submit"> Submit </button>
                <input type="hidden" id=items_form name="formid" value=items_form>
            </fieldset>
        </form>
        """)

    def testWebCarWorkEffortsTableDisplaysWhenWorkEffortsExist(self):
        VIEW_CAR_KEY_1_URL = '/car/items/1'
        self.clientResponseHtmlTester(VIEW_CAR_KEY_1_URL, f"""
            <table id=workefforts_table>
                <colgroup>
                    <col span="1" style=visibility:collapse>
                    <col span="1" style=visibility:initial>
                    <col span="1" style=visibility:initial>
                </colgroup>
                <thead>
                    <tr>
                        <th scope="col" id=employeekey_tablecolumn></th>
                        <th scope="col" id=employeename_tablecolumn>Employee Name</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td headers=employeekey_tablecolumn>1</td>
                        <td headers=employeename_tablecolumn>bob</td>
                        <td>
                            <table>
                                <colgroup>
                                    <col span="1" style=visibility:collapse>
                                    <col span="1" style=visibility:collapse>
                                    <col span="1" style=visibility:initial>
                                    <col span="1" style=visibility:initial>
                                    <col span="1" style=visibility:initial>
                                    <col span="1" style=visibility:initial>
                                </colgroup>
                                <thead>
                                    <tr>
                                        <th scope="col" id=workeffortkey_tablecolumn></th>
                                        <th scope="col" id=carkeyworkedon_tablecolumn></th>
                                        <th scope="col" id=workeffortdate_tablecolumn>Work Effort Date</th>
                                        <th scope="col" id=laborhours_tablecolumn>Labor Hours</th>
                                        <th scope="col" id=estimatedpay_tablecolumn>Estimated Pay (USD)</th>
                                        <th scope="col" id=worktype_tablecolumn>Work Type</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td headers=workeffortkey_tablecolumn>1</td>
                                        <td headers=carkeyworkedon_tablecolumn>1</td>
                                        <td headers=workeffortdate_tablecolumn>2021-09-12</td>
                                        <td headers=laborhours_tablecolumn>10.00</td>
                                        <td headers=estimatedpay_tablecolumn>500.00</td>
                                        <td headers=worktype_tablecolumn>engine work</td>
                                    </tr>
                                    <tr>
                                        <td headers=workeffortkey_tablecolumn>2</td>
                                        <td headers=carkeyworkedon_tablecolumn>1</td>
                                        <td headers=workeffortdate_tablecolumn>2022-10-07</td>
                                        <td headers=laborhours_tablecolumn>10.00</td>
                                        <td headers=estimatedpay_tablecolumn>500.00</td>
                                        <td headers=worktype_tablecolumn>engine work</td>
                                    </tr>
                                    <tr>
                                        <td headers=workeffortkey_tablecolumn>3</td>
                                        <td headers=carkeyworkedon_tablecolumn>1</td>
                                        <td headers=workeffortdate_tablecolumn>2021-09-14</td>
                                        <td headers=laborhours_tablecolumn>10.00</td>
                                        <td headers=estimatedpay_tablecolumn>500.00</td>
                                        <td headers=worktype_tablecolumn>engine work</td>
                                    </tr>
                                    <tr>
                                        <td headers=workeffortkey_tablecolumn>4</td>
                                        <td headers=carkeyworkedon_tablecolumn>1</td>
                                        <td headers=workeffortdate_tablecolumn>2023-05-12</td>
                                        <td headers=laborhours_tablecolumn>10.00</td>
                                        <td headers=estimatedpay_tablecolumn>500.00</td>
                                        <td headers=worktype_tablecolumn>engine work</td>
                                    </tr>
                                    <tr>
                                        <td headers=workeffortkey_tablecolumn>5</td>
                                        <td headers=carkeyworkedon_tablecolumn>1</td>
                                        <td headers=workeffortdate_tablecolumn>2023-12-31</td>
                                        <td headers=laborhours_tablecolumn>10.00</td>
                                        <td headers=estimatedpay_tablecolumn>500.00</td>
                                        <td headers=worktype_tablecolumn>engine work</td>
                                    </tr>
                                    <tr>
                                        <td headers=workeffortkey_tablecolumn>6</td>
                                        <td headers=carkeyworkedon_tablecolumn>1</td>
                                        <td headers=workeffortdate_tablecolumn>2021-01-01</td>
                                        <td headers=laborhours_tablecolumn>10.00</td>
                                        <td headers=estimatedpay_tablecolumn>500.00</td>
                                        <td headers=worktype_tablecolumn>engine work</td>
                                    </tr>
                                    <tr>
                                        <td headers=workeffortkey_tablecolumn>7</td>
                                        <td headers=carkeyworkedon_tablecolumn>1</td>
                                        <td headers=workeffortdate_tablecolumn>2022-04-13</td>
                                        <td headers=laborhours_tablecolumn>10.00</td>
                                        <td headers=estimatedpay_tablecolumn>500.00</td>
                                        <td headers=worktype_tablecolumn>engine work</td>
                                    </tr>
                                    <tr>
                                        <td headers=workeffortkey_tablecolumn>8</td>
                                        <td headers=carkeyworkedon_tablecolumn>1</td>
                                        <td headers=workeffortdate_tablecolumn>2024-02-29</td>
                                        <td headers=laborhours_tablecolumn>10.00</td>
                                        <td headers=estimatedpay_tablecolumn>500.00</td>
                                        <td headers=worktype_tablecolumn>engine work</td>
                                    </tr>
                                    <tr>
                                        <td headers=workeffortkey_tablecolumn>9</td>
                                        <td headers=carkeyworkedon_tablecolumn>1</td>
                                        <td headers=workeffortdate_tablecolumn>2024-02-01</td>
                                        <td headers=laborhours_tablecolumn>10.00</td>
                                        <td headers=estimatedpay_tablecolumn>500.00</td>
                                        <td headers=worktype_tablecolumn>engine work</td>
                                    </tr>
                                    <tr>
                                        <td headers=workeffortkey_tablecolumn>10</td>
                                        <td headers=carkeyworkedon_tablecolumn>1</td>
                                        <td headers=workeffortdate_tablecolumn>2022-07-31</td>
                                        <td headers=laborhours_tablecolumn>10.00</td>
                                        <td headers=estimatedpay_tablecolumn>500.00</td>
                                        <td headers=worktype_tablecolumn>engine work</td>
                                    </tr>
                                </tbody>
                                <tfoot>
                                    <tr>
                                        <th colspan=4 scope=col></th>
                                        <th colspan=1 scope=col id=footerTotalPay_tablecolumn>Total Pay (USD)</th>
                                        <th colspan=1 scope=col></th>
                                    </tr>
                                    <tr>
                                        <td colspan=4></td>
                                        <td colspan=1 headers=footerTotalPay_tablecolumn>5000.00</td>
                                        <td colspan=1></td>
                                    </tr>
                                </tfoot>
                            </table>
                        </td>
                    </tr>
                </tbody>
            </table>
            """)

    def testWebCarWorkEffortsFormExists(self):
        VIEW_CAR_KEY_1_URL = '/car/items/1'
        self.clientResponseHtmlTester(VIEW_CAR_KEY_1_URL, f"""
        <form method="post" autocomplete="off" id=workefforts_form>
            <fieldset form=workefforts_form>
                <legend> Add New Entry </legend>

                <label for=employeename_input> Employee Name </label>
                <select form=workefforts_form id=employeename_input name=employeeKey required>
                    <option value=1> bob </option>
                    <option value=2> joe </option>
                    <option value=3> james </option>
                    <option value=4> Carrie </option>
                    <option value=5> jayden </option>
                    <option value=6> john </option>
                </select>
                <br/>
                <label for=workeffortdate_input> Work Effort Date </label>
                <input type=date form=workefforts_form spellcheck="true" autocomplete="on" min=1970-01-01 max=9999-12-31 step=1 id=workeffortdate_input name=workeffortdate required/>
                <br/>
                <label for=laborhours_input> Labor Hours </label>
                <input type=number form=workefforts_form spellcheck="true" autocomplete="on" min=0 max=24 step=0.01 id=laborhours_input name=laborhours required/>
                <br/>
                <label for=estimatedpay_input> Estimated Pay (USD) </label>
                <input type=number form=workefforts_form spellcheck="true" autocomplete="on" min=0 max=None step=0.01 id=estimatedpay_input name=estimatedpay required/>
                <br/>
                <label for=worktype_input> Work Type </label>
                <input type=text form=workefforts_form spellcheck="true" autocomplete="on" id=worktype_input name=worktype required/>
                <br/>
                <button type="submit" name="submit"> Submit </button>
                <input type="hidden" id=workefforts_form name="formid" value=workefforts_form>
            </fieldset>
        </form>
        """)

if __name__ == '__main__':
    from unittest import main
    main()