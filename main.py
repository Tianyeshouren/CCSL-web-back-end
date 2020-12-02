import datetime
import os
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from tools import HtmlHeader
import json
from SMT import SMT
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import Column, SmallInteger

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

host = 'localhost'
port = 3306
username = 'root'
password = '123456'
db = 'ccsl'
connect_str = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(username, password, host, port, db)
# 设置连接数据库的URL
app.config['SQLALCHEMY_DATABASE_URI'] = connect_str
# 设置每次请求结束后会自动提交数据库中的改动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
#
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# 查询时会显示原始SQL语句
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class CCSL(db.Model):
    # 定义表名
    __tablename__ = 'CCSL'
    # 定义列对象
    name = db.Column(db.String(64), primary_key=True)
    bound = db.Column(db.Integer)
    res = db.Column(db.String(64))
    time = db.Column(db.String(64))
    date = db.Column(db.DateTime, default=datetime.datetime.now)

    # repr()方法显示一个可读字符串
    def __repr__(self):
        return 'CCSL:%s' % self.name


# print("+++++++++++++++++++++++++++++++++++++++")
# print(User.query.filter_by(name='zhou').all())


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/getMsg', methods=['GET', 'POST'])
def home():
    data = json.loads(request.get_data().decode("utf-8"))
    # print(type(data))
    # print(data.get('ccsl'))
    ccslsrc = data.get('ccsl')
    bound = int(data.get('bound'))
    print(bound)
    with open("ccsl.txt", "w", encoding='utf-8') as f:
        f.write(str(ccslsrc))
        f.close()

    HtmlHeader()
    smt = SMT("ccsl.txt", bound=bound, period=0, realPeroid=0)
    smt.getAllSchedule()
    time = smt.getTime()
    result = smt.getResult()
    # HTMLFooter()
    html = ''
    with open("static/output.html", "r", encoding='utf-8') as f:
        html = f.read()
        f.close()
    response = {
        'ccsl': ccslsrc,
         'result': result,
        'time': time,
        'output': html
    }

    return jsonify(response)


@app.route('/store', methods=['GET', 'POST'])
def store():
    data = json.loads(request.get_data().decode("utf-8"))
    fname = data.get('name')



    bound = (data.get('bound'))
    res = data.get('result')
    time = data.get('time')

    with open("static/output.html", "r", encoding='utf-8') as f:
        output = f.read()
        f.close()
    with open("storedata/" + fname + ".output", "w", encoding='utf-8') as f:
        f.write(output)
        f.close()
    with open("ccsl.txt", "r", encoding='utf-8') as f:
        ccsl = f.read()
        f.close()

    with open("storedata/" + fname + ".ccsl", "w", encoding='utf-8') as f:
        f.write(ccsl)
        f.close()

    c1 = CCSL(name=fname, res=res, time=time, bound=int(bound))
    db.session.add(c1)
    db.session.commit()

    response = {
        'res': "store success"
    }

    return jsonify(response)

@app.route('/Query', methods=['GET', 'POST'])
def query():
    ares = list()
    qres = CCSL.query.all()
    for item in qres:
        name = item.name
        bound = item.bound
        res = item.res
        time = item.time
        date = item.date
        with open("storedata/"+name+".ccsl", "r", encoding='utf-8') as f:
            ccsl = f.read()
            f.close()
        with open("storedata/" + name + ".output", "r", encoding='utf-8') as f:
            output = f.read()
            f.close()
        response = {
        'name': name,
        'bound': bound,
        'time': time,
        'date': date,
        'ccsl': ccsl,
        'result': res,
        'output': output
        }
        ares.append(response)

    print(ares)
    return jsonify(ares)
@app.route('/queryOutput', methods=['GET', 'POST'])
def queryoutput():
    data = json.loads(request.get_data().decode("utf-8"))
    name = data.get('name')


    with open("storedata/"+name+".ccsl", "r", encoding='utf-8') as f:
        ccsl = f.read()
        f.close()
    with open("storedata/" + name + ".output", "r", encoding='utf-8') as f:
        output = f.read()
        f.close()
    response = {
        'ccsl': ccsl,
        'output': output
    }

    return jsonify(response)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    data = json.loads(request.get_data().decode("utf-8"))
    name = data.get('name')
    que = CCSL.query.get(name)
    db.session.delete(que)
    db.session.commit()
    os.remove("storedata/"+name+".ccsl")
    os.remove("storedata/" + name + ".output")

    response = {
        'delete': 'delete succesee'
    }

    return jsonify(response)


# 启动运行
if __name__ == '__main__':
    app.run()  # 这样子会直接运行在本地服务器，也即是 localhost:5000
# app.run(host='your_ip_address') # 这里可通过 host 指定在公网IP上运行
