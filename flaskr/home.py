from flask import Blueprint,jsonify, flash, g, render_template, request, url_for, redirect,session
from werkzeug.exceptions import abort
from flaskr.db import get_db
import json

import functools
bp = Blueprint("home", __name__)
from collections import defaultdict
from werkzeug.security import check_password_hash, generate_password_hash
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.member is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route("/",methods=["GET","POST"])
def indexPage():
    loginUrl= url_for("auth.login")
    registerUrl= url_for("auth.register")

    return render_template("index.html",ru=registerUrl,lu=loginUrl)



@bp.route("/<cname>", methods=["GET"])
@login_required
def index(cname):
    cname = session["cname"]
    t = get_tickets(cname)
    print(session["position"])
    print(t)
    tickets=defaultdict(lambda:[])
    s = ["review", "requested", "in-progress", "available", "completed"]
    for i in t:
        tickets[i["status"]].append(i)
    else:
        print("for ended",dict(tickets))
    db = get_db()

    m = db.execute(
        "SELECT DISTINCT mem_name FROM belongsTo WHERE club_name=?",
        (cname,)
    )
    home_url = url_for("home.index",cname=cname)
    analysis_url = url_for("analysis.progress")
    logout_url = url_for("auth.logout")
    print(dict(tickets))
    return render_template("home.html", tickets=tickets,sections=s,user=session["position"],members=m,hurl=home_url,aurl=analysis_url,lurl=logout_url)


@bp.route("/crud", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        ticket = {
            "tname": request.form["tname"],
            "description": request.form["description"],
            "team": request.form["team"],
            "deadline": request.form["deadline"],
            "status": request.form["status"],
            "priority": request.form["priority"],
            "assigned_for": request.form["assigned_for"],
            "points": request.form["points"],
            "submitted_time": request.form["submitted_time"]
        }
        error=None
        print("received",ticket)
        for i in ticket:
            if ticket[i] == None and (i not in ["assigned_for", "submitted_time"]):
                error=f"server received None for {i}"
        db = get_db()
        if ticket["assigned_for"]:
            a=db.execute(
                "select mem_name from belongsTo where club_name=? and mem_name=?",
                (session["cname"],ticket["assigned_for"])
            ).fetchone()
            if a==None:
                error="such member doesnot exist"
        if error==None:
            try:
                t = session["cname"] + "Tickets"
                existing_ticket = db.execute(
                    f'SELECT * FROM {t} WHERE tname = ?', (ticket["tname"],)
                ).fetchone()

                ticket_keys = ["tname", "description", "team", "deadline", "status", "priority", "assigned_for", "points",
                               "submitted_time"]
                ticket_values = tuple([ticket[key] for key in ticket_keys]+[session["mname"]])
                print(existing_ticket,ticket_values)
                if existing_ticket is None:
                    print("inserting")
                    db.execute(
                        f"INSERT INTO {t}(tname, description, team, deadline, status, priority, assigned_for, points, submitted_time,assigned_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?)",
                        ticket_values
                    )
                    print("inserted")
                else:
                    k = [ticket[key] for key in ticket_keys[1:]]  # Get the values excluding 'tname'
                    db.execute(
                        f'UPDATE {t} SET description = ?, team = ?, deadline = ?, status = ?, priority = ?, assigned_for = ?, points = ?, submitted_time = ? '
                        f'WHERE tname = ? ',
                        tuple(k) + (ticket["tname"],)  # Add tname and cname to the tuple
                    )

                print("committing")
                db.commit()
                print("comitted")
            except db.IntegrityError as e:
                error = "Database error. Please contact the admin."
                flash(error)
                print(error,e)
            else:
                return jsonify(success=True)
        else:
            print(error)
            flash(error)
    return redirect(url_for('home.index',cname=session["cname"]))


def get_tickets(cname):
    db = get_db()
    t = cname + "Tickets"
    tickets = db.execute(f'SELECT * FROM {t}').fetchall()
    return tickets


def get_ticket(cname, tname):
    db = get_db()
    t = cname + "Tickets"
    ticket = db.execute(f'SELECT * FROM {t} WHERE tname = ?', (tname,)).fetchone()
    if ticket is None:
        abort(404, f"Ticket {tname} doesn't exist.")
    return ticket


@bp.route("/<tname>/delete", methods=["POST"])
@login_required
def delete(tname):
    cname = session["cname"]
    get_ticket(cname, tname)
    db = get_db()
    db.execute(f'DELETE FROM {cname + "Tickets"} WHERE tname = ?', (tname,))
    db.commit()
    return jsonify(success=True)


@bp.route("/<tname>/request", methods=["POST"])
@login_required
def requested( tname):
    cname = session["cname"]
    db = get_db()
    p = get_ticket(cname, tname)
    if p["status"] in [ "available","requested"]:
        # Ensure assigned_for is properly initialized
        if p["assigned_for"]:
            try:
                assigned_for = json.loads(p["assigned_for"])
            except json.JSONDecodeError:
                assigned_for = []
        else:
            assigned_for = []

        assigned_for.append(session["mname"])

        db.execute(
            f'UPDATE {cname + "Tickets"} SET status = ?, assigned_for = ? WHERE tname = ?',
            ("requested", json.dumps(assigned_for), tname)
        )
    else:
        flash("This ticket is already assigned.")
    db.commit()
    return jsonify(success=True)


@bp.route("/<tname>/withdraw", methods=["POST"])
@login_required
def withdraw(tname):
    cname = session["cname"]
    db = get_db()
    p = get_ticket(cname, tname)
    if p["status"] == "requested":
        assigned_for = json.loads(p["assigned_for"])
        assigned_for.remove(session["mname"])
        new_status = "available" if not assigned_for else "requested"
        db.execute(
            f'UPDATE {cname + "Tickets"} SET status = ?, assigned_for = ? WHERE tname = ?',
            (new_status, json.dumps(assigned_for) if assigned_for else None, tname)
        )
    else:
        flash("Cannot withdraw as the ticket is already approved.")
    db.commit()
    return jsonify(success=True)


@bp.route("/<tname>/approve", methods=["POST"])
@login_required
def approve(tname):
    cname = session["cname"]
    assigned_for = request.form["assigned_for"]
    points = request.form["points"]
    db = get_db()
    p = get_ticket(cname, tname)
    if p["status"] == "requested":
        db.execute(
            f'UPDATE {cname + "Tickets"} SET status = ?, assigned_for = ? WHERE tname = ?',
            ("in-progress", assigned_for, tname)
        )
    elif p["status"] == "review":
        db.execute(
            f'UPDATE {cname + "Tickets"} SET status = ?, assigned_for = ?, points = ? WHERE tname = ?',
            ("completed", assigned_for, points, tname)
        )
    else:
        flash("Cannot approve as the ticket is already in progress.")
    db.commit()
    return jsonify(success=True)


@bp.route("/<tname>/review", methods=["POST"])
@login_required
def review(tname):
    cname = session["cname"]
    db = get_db()
    p = get_ticket(cname, tname)
    if p["status"] == "in-progress":
        db.execute(
            f'UPDATE {cname + "Tickets"} SET status = ? WHERE tname = ?',
            ("review", tname)
        )
    else:
        flash("Cannot move to review status.")
    db.commit()
    return jsonify(success=True)
@bp.route('/<tname>/ticket',methods=["GET","POST"])
def render(tname):
    if request.method == "POST":
        return jsonify(success=True)
    db = get_db()
    t = session["cname"] + "Tickets"

    existing_ticket = db.execute(
        f'SELECT * FROM {t} WHERE tname = ?' , (tname,)
    ).fetchone()
    try:
        if existing_ticket:
            assigned_for = json.loads(existing_ticket['assigned_for']) if existing_ticket['assigned_for'] else []
        else:
            assigned_for=''
    except json.JSONDecodeError:
        assigned_for = []

    print(existing_ticket)
    return render_template('ticket.html',ticket=existing_ticket,position=session["position"],assignedfor=assigned_for,memname=session["mname"])


@bp.route("/addmem",methods=["GET","POST"])
@login_required
def add_mem():
    n = request.form["name"]
    a = request.form["member"]
    db = get_db()
    b = db.execute(
        f"SELECT * FROM belongsTo WHERE club_name=? and mem_name=? ",
        (session["cname"],n)
    ).fetchone()
    if b:
        db.execute(
            "UPDATE belongsTo SET positioned_in=? where club_name=? and mem_name=? ",
            (a,session["cname"],n)
        )
    else:

        db.execute(
            "INSERT INTO belongsTo(mem_name,club_name,password,positioned_in) VALUES(?,?,?,?)",
            (n,session["cname"],generate_password_hash(session["clubcode"]),a)
        )
    db.commit()
    return "",204
@bp.route("/delmem",methods=["GET","POST"])
@login_required
def del_mem():
    n = request.form["name"]
    t = session["cname"] + "Tickets"
    db = get_db()
    b = db.execute(
        f"SELECT * FROM belongsTo WHERE club_name=? and mem_name=? ",
        (session["cname"], n)
    ).fetchone()
    print(b)
    if b :
        if b["positioned_in"] not in ["creator" , "president"]:

            db.execute(
                "DELETE FROM belongsTo WHERE mem_name = ? and club_name=?",
                (n,session["cname"])
            )
            db.execute(
                f"DELETE from {t} WHERE assigned_for=?",
                (n,)
            )
        else:
            if b["positioned_in"] == "president":
                if session["position"] == "creator":
                    db.execute(
                        "DELETE FROM belongsTo WHERE mem_name = ? and club_name=?",
                        (n, session["cname"])
                    )
                    db.execute(
                        f"DELETE from {t} WHERE assigned_by=?",
                        (n,)
                    )
                else:
                    flash("only creator can delete president")
        db.commit()
    else:
        flash("no such member exist, use dropdown list")
    return "",204




