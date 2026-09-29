from flask import Blueprint, request, redirect, url_for, Response

from ..tableConfig import setPurchaseHistoryTableConfig, setPurchasesInputConfig
from CarWorkInventoryDataManager.common_helper import lowerCaseKeyDict
from ..viewclasses import getPostKeyViewBase

web_purchase_data = Blueprint('web_purchase_data', __name__, url_prefix="/purchase")

class purchaseDataView(getPostKeyViewBase):
    def GET_Handler(self, key) -> dict:
        purchasehistorysqlres = self.sqlapp.getPurchaseHistoryAndCurrentPurchaseDataByKey(key)
        setPurchaseHistoryTableConfig(purchasehistorysqlres[1])
        setPurchasesInputConfig(purchasehistorysqlres[1])

        return {"tablesqlres": purchasehistorysqlres,
                "formId": "editPurchaseData",
                "legendText": "Edit Purchase Data",
                "prefillData": purchasehistorysqlres[0][-1]}

    def POST_Handler(self, key) -> Response:
        form = lowerCaseKeyDict(request.form.to_dict())
        match form["formid"][0].lower():
            case "editpurchasedata_form":
                form['purchasekey'] = key
                _ = self.sqlapp.updatePurchaseData(form)
            case _:
                raise NotImplementedError
        return redirect(url_for('web_home.main_page'))

web_purchase_data.add_url_rule('data/<int:key>', view_func=purchaseDataView.as_view('purchase_data_page', "generic_table_form_view.html", "purchase_data"))