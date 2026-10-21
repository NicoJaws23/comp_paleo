import csv
import sys
from datetime import datetime
import psycopg2
import psycopg2.extras
from config import DSN

TSV_FILE = "ppgbd.tsv"

TRUE_VALUES = {"1", "true", "t", "yes", "y", "-1"}
PLACEHOLDERS = {"distance", "how ended", "beh when enc"}   # dropdown labels, not data
HOW_ENDED_MAP = {"animals leave": "left animals"}


def val(row, key):
    """Stripped string or None if blank/missing."""
    return (row.get(key) or "").strip() or None

def choice(row, key, lowercase=True):
    """Value, or None if blank or a dropdown placeholder."""
    v = val(row, key)
    if v is None or v.lower() in PLACEHOLDERS:
        return None
    return v.lower() if lowercase else v

def to_bool(row, key):
    v = val(row, key)
    return v is not None and v.lower() in TRUE_VALUES

def to_date(s):                       # 07-Jun-26
    return datetime.strptime(s, "%d-%b-%y").date() if s else None

def to_time(s):                       # 8:07:38 AM
    return datetime.strptime(s, "%I:%M:%S %p").time() if s else None


def load(path):
    conn = psycopg2.connect(DSN,
        cursor_factory=psycopg2.extras.RealDictCursor)
    cur = conn.cursor()

    obs_cache = set()    # Obs_Sample_ID already inserted
    avi_cache = set()    # Avistaje_ID already inserted
    bad_avi = set()      # Avistaje_ID whose insert failed
    n_focal = n_err = n_skipped = 0

    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh, delimiter='\t')
        for lineno, row in enumerate(reader, start=2):
            avi_id = val(row, 'Avistaje ID')

            # Don't retry an avistaje that already failed
            if avi_id in bad_avi:
                n_skipped += 1
                continue

            cur.execute("SAVEPOINT sp")
            new_obs = new_avi = None
            try:
                # ── Observer samples ──────────────────────────────
                obs_id = val(row, 'Obs Sample ID')
                if obs_id not in obs_cache:
                    obs_date = to_date(val(row, 'Date'))
                    created_time = to_time(val(row, 'Time Record Created'))
                    created = (datetime.combine(obs_date, created_time)
                               if obs_date and created_time else None)
                    cur.execute(
                        """INSERT INTO observer_samples
                               (Obs_Sample_ID, Observer, Obs_Date,
                                Time_Record_Created, Comments, GPS_Used)
                           VALUES (%s, %s, %s, %s, %s, %s)
                           ON CONFLICT DO NOTHING""",
                        (obs_id, val(row, 'Observer'), obs_date, created,
                         val(row, 'observer samples.Comments'),
                         val(row, 'GPS Used'))
                    )
                    new_obs = obs_id

                # ── Avistajes ─────────────────────────────────────
                if avi_id and avi_id not in avi_cache:
                    how_ended = choice(row, 'How Ended')
                    how_ended = HOW_ENDED_MAP.get(how_ended, how_ended)
                    cur.execute(
                        """INSERT INTO avistajes
                               (Avistaje_ID, Obs_Sample_ID, Taxon, Group_Name,
                                Time_Enc, Beh_When_Enc, Follow_Data_Included,
                                Time_Left_Lost, How_Ended, Avistaje_Notes,
                                Voc_Contact, Voc_Distance,
                                Other_Observers_Present)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                   %s, %s, %s)
                           ON CONFLICT DO NOTHING""",
                        (avi_id, obs_id, val(row, 'Taxon'), val(row, 'Group'),
                         to_time(val(row, 'Time Enc')),
                         choice(row, 'Beh When Enc'),
                         to_bool(row, 'Follow Data Included'),
                         to_time(val(row, 'Time Left/Lost')),
                         how_ended,
                         val(row, 'Avistaje Notes'),
                         to_bool(row, 'Voc Contact'),
                         choice(row, 'Voc Distance', lowercase=False),
                         val(row, 'Other Observer Present'))
                    )
                    new_avi = avi_id

                # ── Focal samples ─────────────────────────────────
                focal_id = val(row, 'Focal Sample ID')
                if focal_id:
                    age_sex = val(row, 'Focal Age-Sex Class')
                    if age_sex:
                        age_sex = age_sex.rstrip('/').strip() or None
                    cur.execute(
                        """INSERT INTO focal_samples
                               (Focal_Sample_ID, Avistaje_ID, Focal_Animal,
                                Focal_Age_Sex_Class, Time_Start, Time_End,
                                Comments)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)
                           ON CONFLICT DO NOTHING""",
                        (focal_id, avi_id, val(row, 'Focal Animal'), age_sex,
                         to_time(val(row, 'Time Start')),
                         to_time(val(row, 'Time End')),
                         val(row, 'focal samples.Comments'))
                    )
                    n_focal += cur.rowcount

                cur.execute("RELEASE SAVEPOINT sp")
                if new_obs: obs_cache.add(new_obs)
                if new_avi: avi_cache.add(new_avi)

            except Exception as e:
                cur.execute("ROLLBACK TO SAVEPOINT sp")
                n_err += 1
                if avi_id and avi_id not in avi_cache:
                    bad_avi.add(avi_id)
                msg = str(e).strip().splitlines()[0] if str(e).strip() else repr(e)
                print(f"Line {lineno} ({row.get('Focal Sample ID') or avi_id or '?'}): {msg}",
                      file=sys.stderr)

    conn.commit()
    conn.close()
    print(f"Done. {len(obs_cache)} observer samples, {len(avi_cache)} avistajes, "
          f"{n_focal} focal samples, {n_err} errors, "
          f"{n_skipped} rows skipped (parent avistaje failed).")

if __name__ == '__main__':
    load(TSV_FILE)