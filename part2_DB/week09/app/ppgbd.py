from datetime import datetime, date, time
import psycopg2
import psycopg2.extras
from psycopg2 import errors as pg_errors
from flask import Flask, render_template, request, redirect, url_for

from config import DSN

app = Flask(__name__)

# ── Database helper ──────────────────────────────────────────────────────────

def get_db():
    return psycopg2.connect(DSN,
        cursor_factory=psycopg2.extras.RealDictCursor)

def val(name):
    """Form value stripped, or None if blank."""
    return request.form.get(name, '').strip() or None

@app.template_filter('cell')
def cell(v):
    """Format times, dates, booleans, and blanks for display."""
    if v is None:
        return ''
    if isinstance(v, bool):
        return 'TRUE' if v else 'FALSE'
    if isinstance(v, datetime):
        return v.strftime('%d-%b-%y %I:%M:%S %p')
    if isinstance(v, date):
        return v.strftime('%d-%b-%y')
    if isinstance(v, time):
        return v.strftime('%I:%M:%S %p').lstrip('0')
    return v

# ── Index ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT COUNT(*) AS n FROM observer_samples")
    n_observer_samples = cur.fetchone()['n']
    cur.execute("SELECT COUNT(*) AS n FROM avistajes")
    n_avistajes = cur.fetchone()['n']
    cur.execute("SELECT COUNT(*) AS n FROM focal_samples")
    n_focal_samples = cur.fetchone()['n']
    conn.close()
    return render_template('index.html',
        n_observer_samples=n_observer_samples,
        n_avistajes=n_avistajes,
        n_focal_samples=n_focal_samples)

# ── Observer samples ─────────────────────────────────────────────────────────

@app.route('/observer-samples')
def list_observer_samples():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM observer_samples"
                " ORDER BY obs_date DESC NULLS LAST, obs_sample_id DESC")
    rows = cur.fetchall()
    conn.close()
    return render_template('observer_samples_list.html', rows=rows)

@app.route('/observer-samples/new', methods=['GET', 'POST'])
def new_observer_sample():
    error = None
    if request.method == 'POST':
        conn = get_db()
        cur  = conn.cursor()
        try:
            cur.execute(
                """INSERT INTO observer_samples
                       (obs_sample_id, observer, obs_date,
                        time_record_created, comments, gps_used)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (val('obs_sample_id'), val('observer'), val('obs_date'),
                 datetime.now(), val('comments'), val('gps_used'))
            )
            conn.commit()
            return redirect(url_for('list_observer_samples'))
        except pg_errors.UniqueViolation:
            conn.rollback()
            error = "That observer sample ID already exists."
        except pg_errors.NotNullViolation:
            conn.rollback()
            error = "Obs sample ID is required."
        except pg_errors.CheckViolation:
            conn.rollback()
            error = "Obs sample ID must be exactly 7 characters (OS + 5 digits)."
        except psycopg2.DataError:
            conn.rollback()
            error = "A date or time isn't in a valid format."
        finally:
            conn.close()
    return render_template('observer_samples_form.html', error=error)

# ── Avistajes ────────────────────────────────────────────────────────────────

@app.route('/avistajes')
def list_avistajes():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM avistajes ORDER BY avistaje_id DESC")
    rows = cur.fetchall()
    conn.close()
    return render_template('avistajes_list.html', rows=rows)

@app.route('/avistajes/new', methods=['GET', 'POST'])
def new_avistaje():
    error = None
    if request.method == 'POST':
        conn = get_db()
        cur  = conn.cursor()
        try:
            cur.execute(
                """INSERT INTO avistajes
                       (avistaje_id, obs_sample_id, taxon, group_name, time_enc,
                        beh_when_enc, follow_data_included, time_left_lost,
                        how_ended, avistaje_notes, voc_contact, voc_distance,
                        other_observers_present)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (val('avistaje_id'), val('obs_sample_id'), val('taxon'),
                 val('group_name'), val('time_enc'), val('beh_when_enc'),
                 'follow_data_included' in request.form, val('time_left_lost'),
                 val('how_ended'), val('avistaje_notes'),
                 'voc_contact' in request.form, val('voc_distance'),
                 val('other_observers'))
            )
            conn.commit()
            return redirect(url_for('list_avistajes'))
        except pg_errors.UniqueViolation:
            conn.rollback()
            error = "That avistaje ID already exists."
        except pg_errors.NotNullViolation:
            conn.rollback()
            error = "Avistaje ID and obs sample are required."
        except pg_errors.ForeignKeyViolation:
            conn.rollback()
            error = "Selected observer sample no longer exists."
        except pg_errors.CheckViolation:
            conn.rollback()
            error = "Avistaje ID must be exactly 7 characters (AV + 5 digits)."
        except psycopg2.DataError:
            conn.rollback()
            error = "A date or time isn't in a valid format."
        finally:
            conn.close()

    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT obs_sample_id, observer, obs_date FROM observer_samples"
                " ORDER BY obs_date DESC NULLS LAST, obs_sample_id DESC")
    observer_samples = cur.fetchall()
    conn.close()
    return render_template('avistajes_form.html',
                           observer_samples=observer_samples, error=error)

# ── Focal samples ────────────────────────────────────────────────────────────

@app.route('/focal-samples')
def list_focal_samples():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM focal_samples ORDER BY focal_sample_id DESC")
    rows = cur.fetchall()
    conn.close()
    return render_template('focal_samples_list.html', rows=rows)

@app.route('/focal-samples/new', methods=['GET', 'POST'])
def new_focal_sample():
    error = None
    if request.method == 'POST':
        conn = get_db()
        cur  = conn.cursor()
        try:
            cur.execute(
                """INSERT INTO focal_samples
                       (focal_sample_id, avistaje_id, focal_animal,
                        focal_age_sex_class, time_start, time_end, comments)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (val('focal_sample_id'), val('avistaje_id'), val('focal_animal'),
                 val('age_sex_class'), val('time_start'), val('time_end'),
                 val('comments'))
            )
            conn.commit()
            return redirect(url_for('list_focal_samples'))
        except pg_errors.UniqueViolation:
            conn.rollback()
            error = "That focal sample ID already exists."
        except pg_errors.NotNullViolation:
            conn.rollback()
            error = "Focal sample ID and avistaje are required."
        except pg_errors.ForeignKeyViolation:
            conn.rollback()
            error = "Selected avistaje no longer exists."
        except pg_errors.CheckViolation:
            conn.rollback()
            error = "Focal sample ID must be exactly 7 characters (FS + 5 digits)."
        except psycopg2.DataError:
            conn.rollback()
            error = "A time isn't in a valid format."
        finally:
            conn.close()

    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT avistaje_id, taxon, group_name FROM avistajes"
                " ORDER BY avistaje_id DESC")
    avistajes = cur.fetchall()
    conn.close()
    return render_template('focal_samples_form.html',
                           avistajes=avistajes, error=error)

# ── Full dataset ─────────────────────────────────────────────────────────────

@app.route('/dataset')
def list_full():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        SELECT o.obs_sample_id, o.observer, o.obs_date, o.time_record_created,
               o.comments AS os_comments, o.gps_used,
               a.avistaje_id, a.taxon, a.group_name, a.time_enc, a.beh_when_enc,
               a.follow_data_included, a.time_left_lost, a.how_ended,
               a.avistaje_notes, a.voc_contact, a.voc_distance,
               a.other_observers_present,
               f.focal_sample_id, f.focal_animal, f.focal_age_sex_class,
               f.time_start, f.time_end, f.comments AS fs_comments
        FROM   observer_samples o
        LEFT JOIN avistajes     a ON a.obs_sample_id = o.obs_sample_id
        LEFT JOIN focal_samples f ON f.avistaje_id   = a.avistaje_id
        ORDER BY o.obs_date DESC NULLS LAST, o.obs_sample_id DESC,
                 a.avistaje_id, f.focal_sample_id
        LIMIT 500
    """)
    rows = cur.fetchall()
    conn.close()
    return render_template('full_list.html', rows=rows)

if __name__ == '__main__':
    app.run(debug=True)