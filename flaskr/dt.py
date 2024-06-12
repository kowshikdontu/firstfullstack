#
#
# from flaskr.db import get_db
#
# def drop_all_tables():
#     db = get_db()
#     cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     tables = cursor.fetchall()
#     cursor.close()
#
#     for table in tables:
#         table_name = table[0]
#         db.execute(f"DROP TABLE IF EXISTS {table_name};")
#
#     db.commit()
#
# # Call drop_all_tables() before executing schema.sql
# drop_all_tables()
from flask import ( Blueprint,flash,g,render_template,request,url_for,redirect,abort)
import json
from werkzeug.exceptions import abort
from flaskr.auth import login_required,session,g
from flaskr.db import get_db
bp=Blueprint("home",__name__)

'''proper naming you give...
clubs(club_name(primary key), president_name,club_code ,ttable_id)

belongs( club_name,mem_name, position, password)

 {club_name,mem_name} is primary key

ttable_id(ticket_id, description,team_type, deadline, status, priority,assigned_for(foreign key referencing members table I guess),points, submitted_time)'''

@bp.route("/<cname>",methods=["GET"])
@login_required
def index(cname):
    return render_template("home.html",get_ticket((str(cname+"Tickets"))))


@bp.route("/crud",methods=("GET","POST"))
@login_required
def create():
    designation=g.member["positioned_in"]
    o=["tname","description","team", "deadline", "status", "priority","assigned_for","points", "submitted_time"]
    if request.method=="POST":
        ticket={}
        ticket["tname"]=request.form["tname"]
        ticket["description"]=request.form["description"]
        ticket["team"]=request.form["team"]
        pwd=request.form["password"]
        ticket["deadline"]=request.form["deadline"]
        ticket["status"]=request.form["status"]
        ticket["priority"]=request.form["priority"]
        ticket["assigned_for"]=request.form["assigned_for"]
        ticket["points"]=request.form["points"]
        ticket["submitted_time"]=request.form["submitted_time"]
        error=None
        db=get_db()
        for i in ticket:
            if ticket[i]==None:
                error=f"server received None for {i}"
        if error is None:
            try:
                t = session["cname"] + "Tickets"
                p= db.execute(
                    f'SELECT * FROM {t} WHERE tname = ? ', (ticket["tname"])
                ).fetchone()
                if p==None:
                    db.execute(
                        f"INSERT INTO {t}(tname,description,team, deadline, status, priority,assigned_for,points, submitted_time) VALUES({','.join([ticket[i] for i in o])})"
                    )
                else:
                    db.execute(
                        f'UPDATE {t} SET tname=?,description=?, team=?, deadline=?, status=?, priority=?,assigned_for=?,points=?, submitted_time=?'
                        f' WHERE  tname= {ticket["tname"]}',
                        (i for i in ticket.values())
                    )
                db.commit()
            except db.IntegrityError:
                error = f"Club name has issue contact api team"
            else:
                return redirect(url_for('home.index'))
    return render_template("home_ticket.html")

def get_ticket(tn):
    t = session["cname"] + "Tickets"
    p = get_db.execute(
        f'SELECT * FROM {t} WHERE tname = ? ', (tn)
    ).fetchone()
    if p is None:
        abort(404, f"ticket name {tn} doesn't exist.")

    return p
@bp.route("/<tname>/delete")
@login_required
def delete(id):
    get_ticket(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('home.index'))

@bp.route("/<cname>/<tname>/request",methods=["POST"])
@login_required
def request(cname,tname):
    db = get_db()
    p = get_db.execute(
        f'SELECT * FROM {cname+"Tickets"} WHERE tname = ? ', (tname)
    ).fetchone()
    t=None
    if p["status"]=="available":
        if p["assigned_for"]==None:
            t=json.dumps([f"{session['mname']}"])
        else:
            t=json.loads(p["assinged_for"])
            t.append(session["mname"])
            t=json.dumps(t)
        db.execute(
            f'UPDATE {str(cname+"Tickets")} SET  status=?,assigned_for=?'
            f' WHERE  tname= {tname}',("requested",t)
        )
    else:
        flash("some got assigned already")
    db.commit()
    return render_template("home_ticket.html")
@bp.route("/<cname>/<tname>/withdraw")
@login_required
def withdraw(cname,tname):
    db = get_db()
    p = get_db.execute(
        f'SELECT * FROM {cname+"Tickets"} WHERE tname = ? ', (tname)
    ).fetchone()
    if p["status"]=="requested":
        t=json.loads(p["assigned_for"])
        t.remove(session["memname"])
        db.execute(
            f'UPDATE {str(cname + "Tickets")} SET  status=?,assigned_for=?'
            f' WHERE  tname= {tname}', ("available",None)
        )
    else:
        flash("can't withdraw as president approved your request")
    db.commit()
    return render_template("home_ticket.html")
@bp.route("/<cname>/<tname>/approve",methods=["GET","POST"])
@login_required
def approve(tname,cname):
    if request.method=="POST":
        af=request.form["assigned_for"]
        poi=request.form["points"]
        db=get_db()
        p = db.execute(
            f'SELECT * FROM {cname + "Tickets"} WHERE tname = ? ', (tname)
        ).fetchone()
        if p["status"] == "requested":
            db.execute(
                f'UPDATE {str(cname + "Tickets")} SET  status=?,assigned_for=?'
                f' WHERE  tname= {tname}', ("in-progress", af)
            )
        elif p["status"]=="review":
            db.execute(
                f'UPDATE {str(cname + "Tickets")} SET  status=?,assigned_for=?,points=?'
                f' WHERE  tname= {tname}', ("completed", af,poi)
            )
        else:
            flash("can't approve as your requested ticket is in-progress")
        db.commit()
    return render_template("home.html")
@bp.route("/<cname>/<tname>/review",methods=["GET","POST"])
@login_required
def review(tname,cname):
    db = get_db()
    p = get_db.execute(
        f'SELECT * FROM {cname+"Tickets"} WHERE tname = ? ', (tname)
    ).fetchone()
    t=None
    if p["status"]=="in-progress":
        db.execute(
            f'UPDATE {str(cname+"Tickets")} SET  status=?'
            f' WHERE  tname= {tname}',("review")
        )
    else:
        flash("issue with ticket db")
    db.commit()
    return render_template("home.html")















