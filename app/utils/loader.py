# app/utils/loader.py
import pandas as pd

def load_room_info():
    return pd.read_csv("data/Information.csv").to_dict(orient="records")

def load_pricing():
    return pd.read_csv("data/Pricing.csv").to_dict(orient="records")

def load_rules():
    return pd.read_csv("data/Rules.csv").to_dict(orient="records")

def load_queries():
    return pd.read_csv("data/Queries.csv").to_dict(orient="records")
