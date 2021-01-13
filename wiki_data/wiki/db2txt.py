import sqlite3
def komut(fname):

    db = sqlite3.connect(fname, isolation_level=None)
    c = db.cursor()

    q = ("select * from mapping")
    result = c.execute(q)
    result = result.fetchall()
    print(result[1][0])
    path = "wiki_name_id_map.txt"
    with open(path, "w") as f:
        for x in result:
            f.write('{} {} {}\n'.format(x[0], x[1], x[2]))

if __name__ == "__main__":
    komut('index_trwiki-latest.db')