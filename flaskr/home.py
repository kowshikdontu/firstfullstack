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
@bp.route("/", methods=["GET"])
@login_required
def index():
    cname = session["cname"]
    t = get_tickets(cname)
    print(session["position"])
    tickets=defaultdict(lambda:[])
    s = ["review", "requested", "in-progress", "available", "completed"]
    for i in t:
        tickets[i.status].append(i)
    db = get_db()
    m = db.execute(
        "SELECT DISTINCT mem_name FROM belongsTo WHERE club_name=?",
        (cname,)
    )
    return render_template("home.html", tickets=tickets,sections=s,user=session["position"],members=m)


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
            )
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
                ticket_values = tuple(ticket[key] for key in ticket_keys)

                if existing_ticket is None:
                    db.execute(
                        f"INSERT INTO {t} (tname, description, team, deadline, status, priority, assigned_for, points, submitted_time) "
                        f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        ticket_values
                    )
                else:
                    k=[ticket[key] for key in ticket_keys[1:]]
                    k.append(ticket["tname"])
                    db.execute(
                        f'UPDATE {t} SET description = ?, team = ?, deadline = ?, status = ?, priority = ?, assigned_for = ?, points = ?, submitted_time = ? '
                        f'WHERE tname = ?',
                        tuple(k)
                    )
                db.commit()
            except db.IntegrityError:
                error = "Database error. Please contact the admin."
                flash(error)
                print(error)
            else:
                return jsonify(success=True)
        else:
            print(error)
            flash(error)
    return redirect(url_for('home.index'))


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
    return redirect(url_for('home.index'))


@bp.route("/<tname>/request", methods=["POST"])
@login_required
def requested( tname):
    cname = session["cname"]
    db = get_db()
    p = get_ticket(cname, tname)
    if p["status"] == "available":
        assigned_for = json.loads(p["assigned_for"]) if p["assigned_for"] else []
        assigned_for.append(session["mname"])
        db.execute(
            f'UPDATE {cname + "Tickets"} SET status = ?, assigned_for = ? WHERE tname = ?',
            ("requested", json.dumps(assigned_for), tname)
        )
    else:
        flash("This ticket is already assigned.")
    db.commit()
    return redirect(url_for('home.index'))


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
    return redirect(url_for('home.index'))


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
    return redirect(url_for('home.index'))


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
    return redirect(url_for('home.index'))
@bp.route('/<tname>/ticket',methods=["GET","POST"])
def render(tname):
    if request.method == "POST":
        return jsonify(success=True)
    db = get_db()

    t = session["cname"] + "Tickets"

    existing_ticket = db.execute(
        f'SELECT * FROM {t} WHERE tname = ?', (tname,)
    ).fetchone()
    print(existing_ticket)
    return render_template('ticket.html',ticket=existing_ticket,position=session["position"])


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
    a = request.form["member"]
    db = get_db()
    b = db.execute(
        f"SELECT * FROM belongsTo WHERE club_name=? and mem_name=? ",
        (session["cname"], n)
    ).fetchone()
    if b :
        if b.positioned_in !=("creator" or "president"):
            db.execute(
                "DELETE FROM belongsTo WHERE mem_name = ? and club_name=?",
                (n,session["cname"])
            )
        else:
            if b.positioned_in == "president":
                if session["position"] == "creator":
                    db.execute(
                        "DELETE FROM belongsTo WHERE mem_name = ? and club_name=?",
                        (n, session["cname"])
                    )
                else:
                    flash("only creator can delete president")
    else:
        flash("no such member exist, use dropdown list")
    return "",204




