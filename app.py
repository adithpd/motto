from flask import Flask, request, render_template, redirect, url_for, session
from datetime import timedelta, datetime, date
import sqlite3

con = sqlite3.connect('tracker.db', check_same_thread=False)
c = con.cursor()

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5)
app.secret_key = b'_5#y3L"F4Q8z\n\xec]/'

if __name__ == '__main__':
    app.run()
    app.debug = True
    session.permanent = False

@app.route('/')
def starting1():
    session.pop('username', None)
    return render_template("base.html")

@app.route('/signup', methods=['GET', 'POST'])
def starting2():
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        uname = request.form.get('username')
        passw = request.form.get('pass')
        statement = f"SELECT * from LOGIN WHERE username = '{uname}';"
        c.execute(statement)
        data = c.fetchone()
        if data:
            error = 'Username already Taken'
            return render_template("indexsp.html", error = error)
        else:
            c.execute("INSERT OR IGNORE INTO LOGIN (NAME,USERNAME,PASSWORD) VALUES (?,?,?)", (name,uname,passw))
            con.commit()
            error = ' Please Sign In Now'
            return render_template("index.html",error = error)
    return render_template("indexsp.html")


@app.route('/signin', methods=['GET', 'POST'])
def starting3():
    error = None
    session.pop('username', None)
    if request.method == 'POST':
        uname = request.form.get('username')
        passw = request.form.get('pass')
        statement = f"SELECT * from LOGIN WHERE username = '{uname}';"
        c.execute(statement)
        data = c.fetchone()
        if data and passw == data[1]:
            session['username'] = uname
            return redirect(url_for('starting4', uuname = uname))
        elif not data:
            error = 'Username not found, SignUp Now'
            return render_template("index.html", error = error)
        else:
            error = 'Incorrect Password'
            return render_template("index.html", error = error)
    return render_template("index.html")

@app.route('/user/<uuname>',methods=['GET', 'POST'])
def starting4(uuname):
    statement = f"SELECT * from LOGIN WHERE username = '{uuname}';"
    c.execute(statement)
    data = c.fetchone()
    if data:
        if request.method == 'POST':
            tname = request.form.get('tname')
            tid = request.form.get('tid')
            tvtype = request.form.get('tvtype')
            tdesc = request.form.get('tdesc')
            c.execute("INSERT INTO {} (tid,tvtype,tname,tdesc) VALUES (?,?,?,?)".format(uuname), (int(tid),tvtype,tname,tdesc))
            con.commit()
            sql_command3 = f"SELECT * FROM {uuname};"
            c.execute(sql_command3)
            rows = c.fetchall()
            return render_template("user.html",uuname = uuname, rows = rows)
        sql_command1 = """CREATE TABLE IF NOT EXISTS {} ( 
                tid TEXT PRIMARY KEY NOT NULL,
                tvtype TEXT NOT NULL, 
                tname TEXT NOT NULL, 
                tdesc TEXT,  
                tlog TEXT);""".format(uuname)
        c.execute(sql_command1)
        sql_command2 = f"SELECT * FROM {uuname};"
        c.execute(sql_command2)
        rows = c.fetchall()

        if 'username' in session:
            session.permanent = True
            return render_template("user.html",uuname = uuname, rows = rows)
        else:
            return render_template("index.html",error = "Session Timed Out, Login Again")
    return render_template("index.html", error = "Invalid Access Not Allowed")

@app.route('/settings/<uuname>', methods=['GET', 'POST'])
def starting5(uuname):
    if request.method == 'POST':
        tname = request.form.get('tname1')
        tid = request.form.get('tid')
        tid1 = request.form.get('tid1')
        tvtype = request.form.get('tvtype1')
        tdesc = request.form.get('tdesc1')
        if tname == None:
            sql_command4 = f"DELETE FROM '{uuname}' WHERE tid = '{tid}'"
            c.execute(sql_command4)
            con.commit()
        else:
            sql_command5 = f"UPDATE {uuname} SET tvtype = '{tvtype}' ,tname = '{tname}' ,tdesc = '{tdesc}' WHERE tid = '{tid1}';"
            c.execute(sql_command5)
            con.commit()
    statement = f"SELECT * from LOGIN WHERE username = '{uuname}';"
    c.execute(statement)
    data = c.fetchone()
    if data:    
        if 'username' in session:
            return render_template('settings.html',uuname = uuname)
        else:
            return render_template('index.html', error = "Session Timed Out, Login Again")
    return render_template("index.html", error = "Invalid Access Not Allowed")


@app.route('/logging/<uuname>', methods=['GET', 'POST'])
def starting6(uuname):
    statement = f"SELECT * from LOGIN WHERE username = '{uuname}';"
    c.execute(statement)
    data = c.fetchone()
    if data:    
        if 'username' in session:
            sql_command7 = """CREATE TABLE IF NOT EXISTS {} (
                id INTEGER PRIMARY KEY,
                tid TEXT NOT NULL,
                tname TEXT NOT NULL,
                tvalue TEXT NOT NULL, 
                date TEXT NOT NULL,   
                time TEXT NOT NULL);""".format(uuname + 'log')
            c.execute(sql_command7)

            if request.form.get("deletelog"):
                c.execute("DELETE FROM {} WHERE id = (SELECT MAX(id) FROM {})".format(uuname + 'log',uuname + 'log'))
                con.commit()
                sql_command_columns = f"SELECT * from {uuname + 'log'};"
                c.execute(sql_command_columns)
                columns = c.fetchall()
                return render_template('logging.html',uuname = uuname, rows = columns)

            if request.method == 'POST':
                tid = request.form.get('tid')
                tvalue = request.form.get('tvalue')
                sql_command7 = """CREATE TABLE IF NOT EXISTS {} (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                tid TEXT NOT NULL,
                tname TEXT NOT NULL,
                tvalue TEXT NOT NULL, 
                date TEXT NOT NULL,   
                time TEXT NOT NULL);""".format(uuname + 'log')
                c.execute(sql_command7)
                sql_command8 = f"SELECT tname from {uuname} WHERE tid = '{tid}';"
                c.execute(sql_command8)
                tname = c.fetchone()[0]
                today = date.today()
                d1 = today.strftime("%d/%m/%Y")
                now = datetime.now()
                time = now.strftime("%H:%M:%S")
                c.execute("INSERT INTO {} (tid,tname,tvalue,date,time) VALUES (?,?,?,?,?)".format(uuname + 'log'), (tid,tname,tvalue,d1,time))
                con.commit()
                sql_command9 = f"SELECT * from {uuname + 'log'};"
                c.execute(sql_command9)
                columns = c.fetchall()
                return render_template('logging.html',uuname = uuname, rows = columns)
            sql_command9 = f"SELECT * from {uuname + 'log'};"
            c.execute(sql_command9)
            columns = c.fetchall()
            return render_template('logging.html',uuname = uuname, rows = columns)
        else:
            return render_template('index.html', error = "Session Timed Out, Login Again")
    return render_template("index.html", error = "Invalid Access Not Allowed")

@app.route('/dashboard/<uuname>', methods=['GET', 'POST'])
def starting7(uuname):
    statement = f"SELECT * from LOGIN WHERE username = '{uuname}';"
    c.execute(statement)
    data = c.fetchone()
    if data:
        if 'username' in session:
            sql_command10 = f"SELECT DISTINCT tid from {uuname} ;"
            c.execute(sql_command10)
            rows = c.fetchall()
            if request.method == 'POST':
                tid = request.form.get('dash')
                logtablename = uuname + 'log'

                sql_command11 = f"SELECT tvalue from {logtablename} where tid = '{tid}';"
                c.execute(sql_command11)
                tuples = c.fetchall()
                data = []
                for i in tuples:
                    data.append(i[0])
                count = [data.count(x) for x in set(data)]

                sql_command12 = f"SELECT date from {logtablename} where tid = '{tid}';"
                c.execute(sql_command12)
                tuples = c.fetchall()
                date = []
                for i in tuples:
                    date.append(i[0])

                sql_command13 = f"SELECT tname from {uuname} where tid = '{tid}';"
                c.execute(sql_command13)
                tuples = c.fetchone()
                labels = tuples[0]

                sql_command14 = f"SELECT time from {logtablename} where tid = '{tid}';"
                c.execute(sql_command14)
                tuples = c.fetchall()
                time = []
                for i in tuples:
                    time.append(i[0])
                
                datetime = [i + ' ' + j for i, j in zip(time, date)]
                return render_template('dashboard.html',uuname = uuname, rows=rows, tid = tid, data=data, date=datetime, count=count, labels=labels)
            return render_template('dashboard.html',uuname = uuname, tid=None, rows=rows)
    else:
            return render_template('index.html', error = "Session Timed Out, Login Again")
    return render_template("index.html", error = "Invalid Access Not Allowed")

@app.errorhandler(404) 
def invalid_route(e): 
    return render_template("error404.html")

@app.errorhandler(500) 
def invalid_route(e): 
    uuname = session['username']
    return render_template("error500.html",uuname = uuname)


