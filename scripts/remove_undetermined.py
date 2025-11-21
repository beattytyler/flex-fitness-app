import sqlite3

DB = 'db.sqlite3'

def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    try:
        cur.execute("SELECT count(*) FROM food_measure WHERE lower(coalesce(measure_name,'')) = 'undetermined'")
        before = cur.fetchone()[0]
        print('UND_DET_BEFORE:', before)

        cur.execute("DELETE FROM food_measure WHERE lower(coalesce(measure_name,'')) = 'undetermined'")
        deleted = cur.rowcount
        con.commit()

        cur.execute('SELECT count(*) FROM food_measure')
        remaining = cur.fetchone()[0]
        print('DELETED:', deleted)
        print('REMAINING_TOTAL:', remaining)
    except Exception as e:
        print('ERROR:', e)
    finally:
        con.close()

if __name__ == '__main__':
    main()
