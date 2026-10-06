from flask import Flask, jsonify, request, Response
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

class ProblemError(Exception): 
    def __init__(self, status: int, title: str, detail:str, type_uri: str = "about:blank"):
        super().__init__()
        self.status = status
        self.title = title 
        self.detail = detail 
        self.type_uri = type_uri

@app.errorhandler(ProblemError) 
def handle_problem_error(e):
    response_body = {
        "type": e.type_uri, 
        "title": e.title,
        "detail": e.detail,
        "status": e.status,
        "instance": request.path
    }
    return jsonify(response_body), e.status, {"Content-Type": "application/problem+json"}

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    response_body = {
        "type": "about:blank", 
        "title": e.name,
        "detail": e.description,
        "status": e.code,
        "instance": request.path
    }
    return jsonify(response_body), e.code, {"Content-Type": "application/problem+json"} 

@app.get("/resources/<int:res_id>") 
def get_resource(res_id):
    if res_id != 1:
        raise ProblemError(
            status=404,
            title="Resource Not Found",
            detail=f"Resource with id {res_id} does not exist.",
            type_uri="https://api.example.com/probs/not-found"
        )
    return jsonify({"id": 1, "name": "Valid Resource"}) 

@app.errorhandler(Exception)
def handle_unexpected_error(e):
    # Trả 500 với message trung tính, không để lộ stack trace[cite: 14, 16]
    response_body = {
        "type": "about:blank",
        "title": "Internal Server Error",
        "detail": "An unexpected error occurred. Please try again later.",
        "status": 500,
        "instance": request.path
    }
    return jsonify(response_body), 500, {"Content-Type": "application/problem+json"}

@app.get("/test-crash")
def trigger_crash():
    x = 1 / 0  # ZeroDivisionError (Lỗi crash chưa được bắt trước)
    return {"message": "will never reach here"}

if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True, port=5000)