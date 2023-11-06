import azure.functions as func
import logging
from http_getmergedpdfs_blueprint import bp_pdf
from http_getschema_blueprint import bp_schema
from bp_http_parsecsv import bp_parse_csv

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

app.register_functions(bp_pdf)
app.register_functions(bp_schema)
app.register_functions(bp_parse_csv)
