import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        p_name = request.form['presidentName']
        c_name = request.form['clubName']
        c_code = request.form['clubCode']
        db = get_db()
        error = None

        if not c_name:
            error = 'Club name is required.'
        elif not c_code:
            error = 'Code is required.'

        if error is None:
            try:
                tTable_id = c_name + "Tickets"
                db.execute(
                    "INSERT INTO Clubs (president_name, club_name, club_code, ticketTable_id) VALUES (?, ?, ?, ?)",
                    (p_name, c_name, generate_password_hash(c_code), tTable_id)
                )
                db.execute(
                    "INSERT INTO belongsTo (club_name, mem_name, positioned_in, password) VALUES (?, ?, ?, ?)",
                    (c_name, p_name, "creater", generate_password_hash(c_code))
                )

                db.execute(f"CREATE TABLE {tTable_id} ( \
                                tname TEXT, \
                                description TEXT, \
                                team TEXT, \
                                deadline TEXT, \
                                status TEXT, \
                                priority TEXT, \
                                assigned_for TEXT, \
                                points TEXT,\
                                submitted_time TEXT, \
                                assigned_by TEXT \
                            );")
                db.commit()
            except db.IntegrityError:
                error = f"Club {c_name} is already registered."
            else:
                return redirect(url_for('auth.login'))

        flash(error)

    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cname = request.form['clubName']
        mname = request.form['memName']
        pwd = request.form['clubCode']
        print(cname,mname)
        db = get_db()
        error = None
        member = db.execute(
            'SELECT * FROM belongsTo WHERE club_name = ? AND mem_name = ?', (cname, mname)
        ).fetchone()
        print(member)
        if member is None:
            error = 'Incorrect club name.'
        elif not check_password_hash(member['password'], pwd):
            error = 'Incorrect password.'
        print(error)
        if error is None:
            session.clear()
            session['mname'] = member['mem_name']
            session['cname'] = member['club_name']
            session["position"]=member["positioned_in"]
            session["clubcode"]=pwd
            return redirect(url_for('home.index'))

        flash(error)

    return render_template('login.html')

@bp.before_app_request
def load_logged_in_user():
    mem = session.get('mname')
    club = session.get('cname')

    if mem is None or club is None:
        g.member = None
    else:
        g.member = get_db().execute(
            'SELECT * FROM belongsTo WHERE club_name = ? AND mem_name = ?', (club, mem)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.member is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


