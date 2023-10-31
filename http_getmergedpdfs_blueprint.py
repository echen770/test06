from PyPDF2 import PdfMerger
import azure.functions as func
import logging
import json
import base64
import traceback
import io

bp = func.Blueprint()


def merge_pdfs(files):
    merged_pdf = PdfMerger()

    for file_data in files:
        file_base64 = file_data.get("file_content_base64")
        binary_data = base64.b64decode(file_base64.get("$content"))
        pdf_buffer = io.BytesIO(binary_data)
        merged_pdf.append(pdf_buffer)

    return merged_pdf


@bp.route(route="getmergedpdfs")
def get_merged_pdfs(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    try:
        req_body = req.get_json()

        # Extract the JSON content from the request
        pdf_files = req_body

        merged_pdf = merge_pdfs(pdf_files)

        # Create a BytesIO object to store the merged PDF file
        merged_pdf_buffer = io.BytesIO()
        merged_pdf.write(merged_pdf_buffer)
        merged_pdf_binary = merged_pdf_buffer.getvalue()
        merged_pdf_buffer.close()

        # Encode the merged PDF file as base64
        merged_pdf_base64 = base64.b64encode(merged_pdf_binary).decode()

        # Create a JSON response
        response_data = {
            "file_name": "merged_pdf.pdf",
            "file_content_base64": merged_pdf_base64,
        }

        # Return the JSON response
        return func.HttpResponse(
            json.dumps(response_data), status_code=200, mimetype="application/json"
        )
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
