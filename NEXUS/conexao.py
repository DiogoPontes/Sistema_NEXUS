from datetime import datetime
from flask import render_template, request, redirect, url_for, session, jsonify  # IMPORTANTE
from NEXUS import app
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="LOCALHOST",
        user="root",
        password="SENHA",
        database="plano_estrategico"
    )


