from flask import Flask,render_template,redirect,request,flash,url_for
from stoken import token
from key import secret_key,salt,salt2
from cmail import sendmail
from flask_mysqldb import MySQL
import mysql.connector
from flask import session
import datetime
from itsdangerous import URLSafeTimedSerializer
app = Flask(__name__)
app.secret_key = secret_key
app.config['SESSION_TYPE'] ='filesystem'
app.config['SECRET_KEY'] ='ists-flask_short@terminternship12345'
mydb = mysql.connector.connect(host ='localhost',user='root',password='admin',db='ists')
@app.route("/")
def home():
    return render_template("index.html")
 
@app.route("/registration",methods=['GET','POST'])
def register():
    if request.method=='POST':
        name = request.form['name']
        ph_number = request.form['phone_number']
        email = request.form['email']
        password = request.form['password']
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select count(*) from registration where email = %s', [email])
        count = cursor.fetchone()[0]
        if count == 1:
            flash('email already used')
            return render_template('registration.html')
            # return redirect(URL_for('registration'))
        else:
            data = {'name': name,'ph_number': ph_number,'email': email,'password': password}
            subject = 'Email Confirmation'
            body = f"Thanks for signing up\n\n follow this link for further steps - {url_for('confirm',token = token(data,salt),_external = True)}"
            sendmail(to = email,subject = subject, body = body)
            flash('confirmation link sent to your mail')
            return redirect(url_for('registration'))
        cursor.execute("INSERT INTO registration (name, phone_number, email, password) VALUES (%s, %s, %s, %s)", (name, ph_number, email, password))
        # mydb.commit()
        # cursor.close()
        # flash("your account is creted")
        # return redirect(url_for('home'))
    else:
        return render_template("registration.html")
@app.route('/confirm/<token>')
def confirm(token):
    try:
        serializer = URLSaafeTimedSerializer(secret_key)
        dat = serializer.loads(token = token, salt = salt, max_age = 180)
    except Exception as e:
        return 'Link Expired try again'
    else:
        cursor = mysql.connect(buffered=True)
        email = data['email']
        cursor.execute('insert into registration values(%s,%s,%s,%s)',[data['name'],data['ph_number'],data['email'],data['password']])
        mydb.commit()
        cursor.close()
        flash('Details registered sucessfully')
        return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="POST":
        email = request.form['email']
        password = request.form['password']
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select count(*) from registration where email=%s and password=%s',[email,password])
        count = cursor.fetchone()[0]
        cursor.close()
        if count==1:
            session['email'] =email
            flash("sucessfully login")
            return redirect(url_for('home'))
        else:
            flash('invalid crenditials')
            return redirect(url_for('home'))

    return render_template("login.html")

@app.route('/logout')
def logout():
    if session.get('email'):
        session.pop('email')
        flash("sucessfully loged out")
        return redirect(url_for('login'))
#----------------------------notes management - crud operations
#-------To create notes
@app.route('/createnotes',methods=['GET','POST'])
def createnotes():
    if session.get('email'):
        if request.method=="POST":
            email = session['email']
            title = request.form['title']
            notes = request.form['notes']
            cursor = mydb.cursor(buffered=True)
            cursor.execute('insert into notes(email,title,notes) values (%s,%s,%s)',[email,title,notes])
            mydb.commit()
            cursor.close()
            flash('notes creted sucessfully')
            return redirect(url_for('readnotes'))
        return render_template('cretenotes.html')
    else:
        return render_template('login.html')

#------------to read notes by the titles
@app.route('/readnotes')
def readnotes():
    if session.get('email'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select title,creted_date,id from notes where email = %s',[session.get('email')])
        data = cursor.fetchall()
        return render_template('notestitles.html',data=data)
    else:
        return redirect(url_for('login'))
#----------------to read particulr notes
@app.route('/toreadnotes,<id1>')
def particulrnotes(id1):
    if session.get('email'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select * from notes where id = %s',[id1])
        notes = cursor.fetchall()
        cursor.close()
        return render_template('readnotes.html',notes = notes)

    return redirect(url_for('login'))
#---------------UPDATE notes
@app.route('/updatenotes,<id1>',methods=['GET','POST'])
def updatenotes(id1):
    if session.get('email'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select * from notes where id=%s',[id1])
        notes = cursor.fetchone()
        if request.method=="POST":
            title = request.form['title']
            notes = request.form['notes']
            date = datetime.datetime.now()
            cursor.execute('update notes set title=%s,notes=%s,updated_at=%s where id=%s',[title,notes,date,id1])
            mydb.commit()
            cursor.close()
            flash('notes update sucessfully')
            return redirect(url_for('readnotes'))
       
        return render_template('updatenotes.html',notes = notes)
    return redirect(url_for('login'))
#------------delete notes
@app.route('/deletenotes,<id1>')
def deletenotes(id1):
    if session.get('email'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('delete from notes where id=%s',[id1])
        mydb.commit()
        cursor.close()
        flash('notes deleted sucessfully')
        return redirect(url_for('readnotes'))
    return redirect(url_for('login'))

#----------------forgot password -html->python->database
@app.route('/forgot_password',methods=['GET','POST'])
def forgotpassword():
    if request.method=='POST':
        email = request.form['email']
        npassword = request.form['new_password']
        cpassword = request.form['c_password']
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select count(*) from registration where email=%s',[email])
        count = cursor.fetchone()[0]
        if count == 1:
            if npassword == cpassword:
                cursor = mydb.cursor(buffered=True)
                cursor.execute('update registration set password = %s where email=%s',[cpassword,email])
                mydb.commit()
                flash('password updated sucessfully')
                return redirect(url_for('login'))
            else:
                flash('new password and confirm passwird mismatched')
                return redirect(url_for('forgotpassword'))
        else:
            flash('email is wrong')
            return redirect(url_for('forgotpassword'))
    else:
        return render_template('forgotpassword.html')
    
#--------------profile feature - database->python code->html
@app.route('/profile')
def profile():
    cursor = mydb.cursor(buffered=True)
    cursor.execute('select * from registration where email=%s',[session.get('email')])
    data = cursor.fetchall()
    return render_template('profile.html',profile = data)















app.run(use_reloader=True,debug=True)

