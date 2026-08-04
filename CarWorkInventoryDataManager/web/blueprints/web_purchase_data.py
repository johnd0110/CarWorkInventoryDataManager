from flask import Blueprint, render_template, request, redirect, url_for

from db import get_CWI_db
from tableConfig import setPurchaseHistoryTableConfig, setPurchasesInputConfig
from CarWorkInventoryDataManager.common_helper import lowerCaseKeyDict

web_purchase_data = Blueprint('web_purchase_data', __name__, url_prefix="/purchase")

@web_purchase_data.route('history/<int:keyorid>', methods=["GET", "POST"])
def purchase_data_page(keyorid):
    sqlapp = get_CWI_db()

    if request.method == "POST":
        req_form_dict = lowerCaseKeyDict(request.form)
        match request.form["formid"].lower():
            case "editpurchasedata_form":
                req_form_dict['purchasekey'] = keyorid
                _ = sqlapp.updatePurchaseData(req_form_dict)
                return redirect(url_for('web_home.main_page'))
            case _:
                raise NotImplementedError

    purchasehistorysqlres = sqlapp.getPurchaseHistoryAndCurrentPurchaseDataByKey(keyorid)
    setPurchaseHistoryTableConfig(purchasehistorysqlres[1])
    setPurchasesInputConfig(purchasehistorysqlres[1])

    return render_template("generic_table_form_view.html",
                           tablesqlres=purchasehistorysqlres,
                           formId="editPurchaseData",
                           legendText="Edit Purchase Data",
                           prefillData=purchasehistorysqlres[0][-1])