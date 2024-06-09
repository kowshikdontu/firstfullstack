from flask import ( Blueprint,flash,g,render_template,request,url_for)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
bp=Blueprint("home",__name__)

bp.route("/",methods=("GET","POST"))
@login_required
def create():
    if request.method=="POST":
        n=request.form["ticket_name"]
