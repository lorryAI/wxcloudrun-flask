from datetime import datetime
from flask import render_template, request
from run import app
import json
import sqlite3
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')

@app.route('/survey')
def survey():
    """
    :return: 返回index页面
    """
    questions = get_questions()
    return render_template('survey.html',questions=questions)


def get_questions():
    with open('questions.json', 'r', encoding='utf-8') as f:
        questions = json.loads(f.read())
    return questions

@app.route('/submit', methods=['POST'])
def submit():
    answers = {}
    for key, value in request.form.items():
        answers[key] = value
    conn = sqlite3.connect('answers.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS answers
                 (question text, answer text)''')
    for key, value in answers.items():
        c.execute("INSERT INTO answers VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
    return '提交成功！'


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)
