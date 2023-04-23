from flask import Flask, render_template, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
import hashlib, datetime, csv, os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db = SQLAlchemy(app)
HOST = '0.0.0.0'
PORT = 5000
# Write Metodists logins to file through a space
admins = open('admins.txt', encoding='utf-8').read().split()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    dateR = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __repr__(self):
        return '<Users %r>' % self.id


class Rasp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(150), nullable=False)
    date = db.Column(db.String(150), nullable=False)
    group = db.Column(db.String(150), nullable=False)
    cabinet = db.Column(db.String(500), nullable=False)
    time = db.Column(db.String(500), nullable=False)
    data = db.Column(db.String(500), nullable=False)
    path = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return '<Rasps %r>' % self.id


def py2csv(filename, time, cab, data):
    l = len(time)
    with open(filename, mode="w", encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=',', lineterminator="\r")
        writer.writerow(['Время', 'Кабинет', 'Предмет'])
        for i in range(l):
            writer.writerow([time[i], cab[i], data[i]])


def csv2py(filename):
    time = ''
    cab = ''
    data = ''
    with open(filename, encoding='utf-8') as r_file:
        file_reader = csv.reader(r_file, delimiter=",")
        count = 0
        for row in file_reader:
            if count == 0:
                pass
            else:
                time += row[0] + '.'
                cab += row[1] + '.'
                data += row[2] + '.'
            count += 1
    time = time[:-1]
    cab = cab[:-1]
    data = data[:-1]
    return time, cab, data


@app.route('/')
def main():
    global admins
    name = request.cookies.get('user')
    if name is None:
        return redirect("/login")
    admins = open('admins.txt', encoding='utf-8').read().split()
    year = str(datetime.datetime.now().year)
    month = str(datetime.datetime.now().month)
    day = str(datetime.datetime.now().day)
    if len(month) == 1:
        month = '0' + month
    if len(day) == 1:
        day = '0' + day
    date = year + '-' + month + '-' + day
    try:
        rasps = list(Rasp.query.filter_by(date=date).all())
        if len(rasps) >= 3:
            rasps.reverse()
        elif len(rasps) == 2:
            rasps[0], rasps[1] = rasps[1], rasps[0]
    except:
        rasps = ''
    return render_template("index.html", name=name, rasps=rasps, isAdmin=name in admins, date=date)


@app.route('/register', methods=['POST', 'GET'])
def register():
    name = request.cookies.get('user')
    if request.method == "POST":
        login = request.form['login']
        passw1 = request.form['passw1']
        password = hashlib.md5(passw1.encode("utf-8")).hexdigest()
        exists = db.session.query(Users.id).filter_by(login=login).first() is not None
        if not exists:
            user = Users(login=login, password=password)
            try:
                db.session.add(user)
                db.session.commit()
                resp = make_response(redirect("/"))
                resp.set_cookie('user', user.login)
                return resp
            except Exception as ex:
                print(ex)
                return redirect("/register")
        else:
            return redirect("/register")
    else:
        return render_template("register.html", isAdmin=name in admins)


@app.route('/login', methods=['POST', "GET"])
def login():
    name = request.cookies.get('user')
    if request.method == "POST":
        login = request.form['login']
        passw1 = request.form['passw1']
        password = hashlib.md5(passw1.encode("utf-8")).hexdigest()
        exists = db.session.query(Users.id).filter_by(login=login, password=password).first() is not None
        user = db.session.query(Users.login).filter_by(login=login, password=password).first()
        if exists:
            resp = make_response(redirect("/"))
            resp.set_cookie('user', user[0])
            return resp
        else:
            return redirect("/login")
    else:
        return render_template("login.html", isAdmin=name in admins)


@app.route('/logout')
def logout():
    resp = make_response(redirect("/login"))
    resp.set_cookie('user', '', expires=0)
    return resp


@app.route('/addrasp', methods=['POST', 'GET'])
def add():
    name = request.cookies.get('user')
    if name is None or name not in admins:
        return redirect('/login')
    if request.method == 'POST':
        time = request.form['time']
        text = request.form['text']
        date = request.form['date']
        group = request.form['group']
        cab = request.form['cab']
        if len(time.split('.')) == len(text.split('.')) == len(cab.split()):
            filename = f'static/rasps/Расписание-{group}-{date}.csv'
            if os.path.exists(filename):
                return redirect('/addrasp')
            py2csv(filename, time.split('.'), cab.split('.'), text.split('.'))
            try:
                rasp = Rasp(time=time, data=text, author=name, date=date, group=group, cabinet=cab, path=filename)
                db.session.add(rasp)
                db.session.commit()
            except:
                return redirect('/addrasp')
            return redirect('/')
        return redirect('/addrasp')
    else:
        return render_template('addrasp.html', isAdmin=name in admins)


@app.route('/addraspcsv', methods=['POST', 'GET'])
def add_csv():
    name = request.cookies.get('user')
    if name is None or name not in admins:
        return redirect('/login')
    if request.method == 'POST':
        file = request.files['file[]']
        group = request.form['group']
        date = request.form['date']
        filename = f'static/cache/{file.filename}'
        file.save(filename)
        time, cab, text = csv2py(filename)
        os.remove(filename)
        filename = f'static/rasps/Расписание-{group}-{date}.csv'
        if os.path.exists(filename):
            return redirect('/addraspcsv')
        py2csv(filename, time.split('.'), cab.split('.'), text.split('.'))
        try:
            rasp = Rasp(time=time, data=text, author=name, date=date, group=group, cabinet=cab, path=filename)
            db.session.add(rasp)
            db.session.commit()
        except:
            return redirect('/addraspcsv')
        return redirect('/')
    else:
        return render_template('addraspcsv.html', isAdmin=name in admins)


@app.route('/delrasp')
def delete():
    name = request.cookies.get('user')
    if name is None or name not in admins:
        return redirect('/login')
    try:
        _id = int(request.args.get('id'))
        rasp = Rasp.query.filter_by(id=_id).first()
        os.remove(rasp.path)
        db.session.delete(rasp)
        db.session.commit()
        return redirect('/')
    except Exception as ex:
        print(ex)
        return redirect('/')


@app.route('/editrasp', methods=['POST', 'GET'])
def edit():
    name = request.cookies.get('user')
    if name is None:
        return redirect('/login')
    try:
        _id = int(request.args.get('id'))
        post = Rasp.query.filter_by(id=_id).first()
    except:
        return redirect('/addrasp')
    if request.method == 'POST':
        time = request.form['time']
        text = request.form['text']
        date = request.form['date']
        group = request.form['group']
        cab = request.form['cab']
        try:
            filename = f'static/rasps/Расписание-{group}-{date}.csv'
            py2csv(filename, time.split('.'), cab.split('.'), text.split('.'))
            post.time = time
            post.data = text
            post.date = date
            post.group = group
            post.cabinet = cab
            post.path = filename
            db.session.commit()
            return redirect('/')
        except:
            return redirect('/addrasp')
    else:
        if post is None:
            return redirect('/addrasp')
        return render_template('editrasp.html', post=post, isAdmin=name in admins)


@app.route('/editraspcsv', methods=['POST', 'GET'])
def edit_csv():
    name = request.cookies.get('user')
    if name is None:
        return redirect('/login')
    try:
        _id = int(request.args.get('id'))
        post = Rasp.query.filter_by(id=_id).first()
    except:
        return redirect('/addraspcsv')
    if request.method == 'POST':
        file = request.files['file[]']
        group = request.form['group']
        date = request.form['date']
        if file:
            filename = f'static/cache/{file.filename}'
            file.save(filename)
            time, cab, text = csv2py(filename)
            os.remove(filename)
            filename = f'static/rasps/Расписание-{group}-{date}.csv'
            py2csv(filename, time.split('.'), cab.split('.'), text.split('.'))
            filename = f'static/rasps/Расписание-{group}-{date}.csv'
            py2csv(filename, time.split('.'), cab.split('.'), text.split('.'))
        try:
            if file:
                post.time = time
                post.data = text
                post.cabinet = cab
                post.path = filename
            post.date = date
            post.group = group
            db.session.commit()
            return redirect('/')
        except:
            return redirect('/addraspcsv')
    else:
        if post is None:
            return redirect('/addraspcsv')
        return render_template('editraspcsv.html', post=post, isAdmin=name in admins)


@app.route('/help')
def help():
    name = request.cookies.get('user')
    if name is None:
        return redirect('/login')
    return render_template('help.html', isAdmin=name in admins)


@app.route('/allrasps')
def allrasps():
    name = request.cookies.get('user')
    if name is None and name not in admins:
        return redirect('/login')
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day
    overdue = []
    today = []
    planned = []
    rasps = list(Rasp.query.all())
    try:
        for i in rasps:
            i_s = list(i.date.split('-'))
            if (int(i_s[0]) < year) or (int(i_s[0]) <= year and int(i_s[1]) < month) or (
                    int(i_s[0]) <= year and int(i_s[1]) <= month and int(i_s[2]) < day):
                overdue.append(i)
            elif (int(i_s[0]) > year) or (int(i_s[0]) >= year and int(i_s[1]) > month) or (
                        int(i_s[0]) >= year and int(i_s[1]) >= month and int(i_s[2]) > day):
                planned.append(i)
            elif int(i_s[0]) == year and int(i_s[1]) == month and int(i_s[2]) == day:
                today.append(i)
    except:
        pass
    return render_template('allrasps.html', name=name, isAdmin=name in admins, overdue=overdue, planned=planned, today=today)


@app.route('/api')
def api():
    group = request.args.get('group')
    date = request.args.get('date')
    try:
        if date == 'today':
            year = str(datetime.datetime.now().year)
            month = str(datetime.datetime.now().month)
            day = str(datetime.datetime.now().day)
            if len(month) == 1:
                month = '0' + month
            if len(day) == 1:
                day = '0' + day
            date = year + '-' + month + '-' + day
        rasp = Rasp.query.filter_by(group=group, date=date).first()
        return str(rasp.time + '<br>' + rasp.cabinet + '<br>' + rasp.data)
    except:
        return 'Error'


@app.route('/getapi')
def getapi():
    name = request.cookies.get('user')
    return render_template('api.html', isAdmin=name in admins)


if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)
