import azure.functions as func
import logging
from http_getmergedpdfs_blueprint import bp_pdf
from http_getschema_blueprint import bp_schema


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

app.register_functions(bp_pdf)
app.register_functions(bp_schema)
