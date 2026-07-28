from flask import Blueprint, render_template

from db import get_CWI_db
from tableConfig import setPurchaseHistoryTableConfig

web_purchase_data = Blueprint('web_purchase_data', __name__, url_prefix="/purchase")

@web_purchase_data.route('history/<int:keyorid>')
def purchase_history_page(keyorid):
    sqlapp = get_CWI_db()

    purchasehistorysqlres = sqlapp.getPurchaseHistoryByKey(keyorid)
    setPurchaseHistoryTableConfig(purchasehistorysqlres[1])

    return render_template("generic_table_view.html",
                           tablesqlres=purchasehistorysqlres)