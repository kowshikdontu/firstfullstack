from flask import redirect, render_template, session, url_for, Blueprint
from flaskr.auth import login, login_required
from flaskr.db import get_db

bp = Blueprint("analysis", __name__, url_prefix="/analysis")


def get_club_progress(club_name):
    db = get_db()
    tTable_id = club_name + "Tickets"

    club_progress = db.execute(
        f"""
        SELECT SUM(points) AS total_points,
        SUM(CASE WHEN priority = 'high priority' THEN 1 ELSE 0 END) AS high_priority,
        SUM(CASE WHEN priority = 'low priority' THEN 1 ELSE 0 END) AS low_priority
        FROM {tTable_id}
        WHERE status = "completed"
        """
    ).fetchone()

    top_performers = db.execute(
        f"""
        SELECT assigned_for, SUM(points) AS total_points, 
        SUM(CASE WHEN priority = 'high priority' THEN 1 ELSE 0 END) AS high_priority, 
        SUM(CASE WHEN priority = 'low priority' THEN 1 ELSE 0 END) AS low_priority 
        FROM {tTable_id}
        WHERE status = "completed"
        GROUP BY assigned_for
        ORDER BY total_points DESC
        """
    ).fetchall()

    return club_progress, top_performers


@bp.route('/progress', methods=['GET', 'POST'])
@login_required
def progress():
    club_name = session.get('cname')
    club_progress, top_performers = get_club_progress(club_name)
    home_url = url_for("home.index", cname=session["cname"])
    analysis_url = url_for("analysis.progress")
    logout_url = url_for("auth.logout")
    return render_template('analysis.html', club_progress=club_progress, top_performers=top_performers,hurl=home_url,aurl=analysis_url,lurl=logout_url,cname=club_name)
