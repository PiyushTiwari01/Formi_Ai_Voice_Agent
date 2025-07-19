# app/routes.py

from fastapi import APIRouter, Request
from app.utils.loader import load_room_info, load_pricing, load_rules, load_queries
from app.utils.sheet_logger import log_to_sheet
from datetime import datetime
from app.utils.tokenizer import chunk_content


router = APIRouter()

# ➤ Sample endpoint for rooms
@router.get("/rooms")
def get_rooms():
    data = load_room_info()
    return {"data": data[:5]}

@router.get("/pricing")
def get_pricing():
    data = load_pricing()
    return {"data": data[:5]}

@router.get("/rules")
def get_rules():
    data = load_rules()
    return {"data": data[:5]}

@router.get("/faqs")
def get_queries():
    data = load_queries()
    return {"data": data[:5]}


@router.get("/rules/chunks")
def get_rules_chunks():
    data = load_rules()
    chunks = chunk_content(data, max_tokens=800)
    return {"chunks": chunks}

# ➤ Ye hai Google Sheet logging ke liye endpoint
@router.post("/log-call-summary")
async def log_call(request: Request):
    body = await request.json()
    row = [
        body.get("call_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        body.get("phone", "NA"),
        body.get("outcome", "NA"),
        body.get("name", "NA"),
        body.get("room_name", "NA"),
        body.get("check_in", "NA"),
        body.get("check_out", "NA"),
        body.get("guest_count", "NA"),
        body.get("summary", "NA"),
    ]
    try:
        log_to_sheet(row)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "details": str(e)}
