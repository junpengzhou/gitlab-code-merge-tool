# -*- coding: utf-8 -*-
import logging
import os
import traceback
import uuid
from datetime import datetime
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from gitlab import GitlabAuthenticationError

from support.gitlab_manager import GitlabManager


def setup_error_handling(flask_app):
    # 文件日志记录
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/frank_gitlab_tool_err.log',
                                       maxBytes=10240,
                                       encoding='utf-8',
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.ERROR)
    flask_app.logger.addHandler(file_handler)
    flask_app.logger.setLevel(logging.ERROR)


# -----------------------------
# 初始化 Flask 应用
# -----------------------------
app = Flask(__name__)
app.secret_key = 'frank-gitlab-tool-v2.0.0'
setup_error_handling(app)


@app.route('/')
def page_index():
    return _page_merge()


@app.route('/health')
def heath():
    return jsonify({"message": "Application is working"}), 200


@app.route('/configuration')
def page_configuration():
    return render_template('configuration.html')


@app.route('/merge')
def page_merge():
    return _page_merge()


def _page_merge():
    """合并请求表单页面"""
    gitlab_url = session.get('gitlab_url')
    api_token = session.get('api_token')
    if not gitlab_url or not api_token:
        return redirect(url_for('page_configuration'))
    return render_template('index.html')


@app.route('/configure', methods=['POST'])
def configure():
    """保存GitLab配置"""
    gitlab_url = request.form['gitlab_url']
    api_token = request.form['api_token']

    try:
        # 创建GitlabManager测试是否正常
        manager = GitlabManager(gitlab_url, api_token)
        # 保存到session
        session['gitlab_url'] = gitlab_url
        session['api_token'] = api_token
        session['user_name'] = manager.get_username()
        session.permanent = True

        return redirect(url_for('page_merge'))
    except Exception as unknown_e:
        return render_template(
            'configuration.html',
            error=f"配置验证失败: {str(unknown_e)}"
        )


@app.route('/create-merge-requests', methods=['POST'])
def create_merge_requests():
    """执行合并请求创建"""
    gitlab_url = session['gitlab_url']
    api_token = session['api_token']

    if not gitlab_url or not api_token:
        return redirect(url_for('page_configuration'))

    # 获取表单数据
    source_branch = request.form['source_branch']
    target_branch = request.form['target_branch']
    start_with = request.form.get('start_with', '')
    reviewer_usernames = request.form.get('reviewer_usernames', '')
    assignee_usernames = request.form.get('assignee_usernames', '')
    specific_projects = request.form.get('specific_projects', '')

    # 创建GitLab管理器实例
    manager = GitlabManager(gitlab_url, api_token)
    username = manager.get_username()

    # 处理可选参数
    reviewer_list = [u.strip() for u in reviewer_usernames.split(',')] if reviewer_usernames else [username]
    assignee_list = [u.strip() for u in assignee_usernames.split(',')] if assignee_usernames else [username]
    specific_project_list = [p.strip() for p in specific_projects.split(',')] if specific_projects else None

    # 执行合并请求创建
    result, output = manager.create_merge_requests(
        source_branch=source_branch,
        target_branch=target_branch,
        reviewer_usernames=reviewer_list,
        assignee_usernames=assignee_list,
        start_with=start_with,
        specific_projects=specific_project_list
    )

    return render_template('result.html',
                           username=username,
                           output_text=output,
                           merge_results=result,
                           source_branch=source_branch,
                           target_branch=target_branch)


@app.route('/get_project_name_list', methods=['POST'])
def get_project_name_list():
    """获取项目列表"""
    gitlab_url = session['gitlab_url']
    api_token = session['api_token']
    manager = GitlabManager(gitlab_url, api_token)
    projects = manager.get_project_name_list()
    return {"projects": projects}


@app.route('/reset')
def reset():
    """重置配置"""
    session.clear()
    return redirect(url_for('page_index'))


@app.errorhandler(400)
def bad_request(error):
    return render_template('error.html',
                           error_code=400,
                           error_name="错误的请求",
                           error_description=f"错误的请求:{str(error)}"), 400


@app.errorhandler(401)
def bad_request(error):
    return render_template(
        'configuration.html',
        error=f"认证失败，请重新配置 GitLab 地址或 API Token: {str(error)}"), 401


@app.errorhandler(404)
def page_not_found(_error):
    return render_template('error.html',
                           error_code=404,
                           error_name="页面未找到",
                           error_description=f"您访问的页面不存在或已被移动。"), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html',
                           error_code=500,
                           error_name="服务器内部错误",
                           error_description=f"服务器遇到意外错误，请稍后重试。{str(error)}"), 500


@app.errorhandler(GitlabAuthenticationError)
def handle_gitlab_auth_error(error):
    # 认证失败进行过期session的处理
    session.pop('gitlab_url')
    session.pop('api_token')
    session.pop('user_name')
    return render_template(
        'configuration.html',
        error=f"认证失败，请重新配置 GitLab 地址或 API Token: {str(error)}"
    )


@app.errorhandler(Exception)
def handle_generic_error(error):
    error_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    app.logger.error(f'错误ID: {error_id} - 出现本服务500错误: {str(error)}')
    app.logger.error(f'错误ID: {error_id} - 堆栈跟踪: {traceback.format_exc()}')
    app.logger.error(f'错误ID: {error_id} - 发生时间: {timestamp}')
    return render_template('error.html',
                           error_id=error_id,
                           error_code=500,
                           error_name="未知错误",
                           error_description=f"未知错误,{str(error)}",
                           timestamp=timestamp), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
