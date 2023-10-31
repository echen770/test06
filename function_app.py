import io
import traceback
import azure.functions as func
import logging
import json
import base64
import zipfile
from xml.etree import ElementTree as ET
from http_getmergedpdfs_blueprint import bp


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

app.register_functions(bp)


def find_xml_elements_in_zip(zip_data):
    # Decode the base64-encoded zip data
    zip_bytes = base64.b64decode(zip_data)

    # Create a list to store the values
    result = []

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        with archive.open("word/document.xml") as xml_file:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Define the namespaces
            namespaces = {
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            }

            # # Find all occurrences of the specified XML elements
            elements = root.findall(".//w:sdtPr[w:tag]", namespaces)

            # # Iterate through all found tag elements
            for e in elements:
                result.append(
                    {
                        "fieldName": e.find("./w:tag", namespaces).attrib[
                            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
                        ],
                        "id": e.find("./w:id", namespaces).attrib[
                            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
                        ],
                    }
                )

    return result


def get_dynamic_file_schema(
    item_list: [], schema_ids: [], field_list: [], event_date: str
) -> []:
    # initialize an empty list to store the values
    result = []
    dynamic_schema = {}

    sorted_item_list = sorted(item_list, key=lambda x: x["bos_rowcounter"])

    for item in sorted_item_list:
        for id in schema_ids:
            logical_name = id.get("fieldName")
            if logical_name != "EventDate":
                dynamic_schema[id.get("id")] = item[field_list[logical_name]]
            else:
                dynamic_schema[id.get("id")] = event_date
        result.append(dynamic_schema)
        dynamic_schema = {}

    return result


def get_req_data(req_body: json, name: str) -> []:
    if name in req_body:
        return req_body[name]
    else:
        raise ValueError(f"The '{name}' key is missing in the request JSON.")


@app.route(route="getdynamicschema")
def get_dynamic_schema(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    try:
        req_body = req.get_json()

        zip_data = get_req_data(req_body, "zip_data")
        item_list = get_req_data(req_body, "item_list")
        field_list = get_req_data(req_body, "field_list")

        schema_ids = find_xml_elements_in_zip(zip_data.get("$content"))

        result = get_dynamic_file_schema(
            item_list, schema_ids, field_list, req_body["event_date"]
        )

        # Convert the result list to JSON format
        result_json = json.dumps(result)

        return func.HttpResponse(result_json, mimetype="application/json")

    except Exception as e:
        # Capture the line number where the exception occurred
        tb = traceback.extract_tb(e.__traceback__)
        line_number = tb[-1][1]
        error_message = {
            "error": str(e),
            "line_number": line_number,
            "stack_trace": traceback.format_exc(),
        }
        return func.HttpResponse(
            json.dumps(error_message), status_code=400, mimetype="application/json"
        )
