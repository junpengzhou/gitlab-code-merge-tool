# -*- coding: utf-8 -*-
from io import StringIO
from typing import Optional, List, Any

import gitlab
from gitlab import GitlabError, base
from requests.exceptions import RequestException


class GitlabManager:
    def __init__(self, gitlab_url: str, api_token: str):
        self.gl = gitlab.Gitlab(
            url=gitlab_url,
            private_token=api_token
        )
        self.gl.auth()
        self.output_buffer = None

    def get_username(self) -> str:
        """获取当前用户名"""
        return self.gl.user.username

    def get_user_email(self) -> str:
        """获取当前用户邮箱"""
        return self.gl.user.email

    def get_project_name_list(self) -> List[str]:
        """获取项目列表"""
        projects = self.gl.projects.list(
            membership=True,
            all=True,
            iterator=True
        )
        return list([project.name for project in projects])

    def create_merge_requests(
            self,
            source_branch: str,
            target_branch: str,
            reviewer_usernames: List[str] = None,
            assignee_usernames: List[str] = None,
            start_with: str = None,
            specific_projects: Optional[List[str]] = None
    ) -> tuple[dict[Any, Any], str]:
        """创建合并请求"""
        merge_results: dict[Any, Any] = {}
        # 操作人姓名
        oper_username = self.gl.user.username
        # 将审阅者用户名转换为用户ID
        reviewer_ids = self._get_gitlab_ids(reviewer_usernames)
        assignee_ids = self._get_gitlab_ids(assignee_usernames)

        projects = self.get_special_projects(specific_projects, start_with)

        for idx, project in enumerate(projects, 1):
            project_name = project.name

            try:
                is_user_specific_pj = specific_projects and project_name in specific_projects
                # 检查源分支是否存在
                if not self._branch_exists(project, source_branch):
                    if is_user_specific_pj:
                        src_not_exist = f"来源分支 {source_branch} 不存在"
                        self._output_write(f"❌ {project_name} (ID: {project.id}) {src_not_exist}")
                        merge_results[project_name] = self._result_build(
                            status='error', status_name=src_not_exist, url='-'
                        )
                    continue

                # 检查目标分支是否存在
                if not self._branch_exists(project, target_branch):
                    if is_user_specific_pj:
                        target_not_exist = f"目标分支 {target_branch} 不存在"
                        self._output_write(f"❌ {project_name} (ID: {project.id}) {target_not_exist}")
                        merge_results[project_name] = self._result_build(
                            status='error', status_name=target_not_exist, url='-'
                        )
                    continue

                # 检查是否现有合并请求
                existing_mr = self._get_existing_merge_request(project, source_branch, target_branch)
                if existing_mr:
                    merge_results[project_name] = self._result_build(
                        status='success', status_name='复用原有请求', url=existing_mr.web_url
                    )
                    continue

                # 创建合并请求
                mr = self._create_merge_request(
                    project=project,
                    source_branch=source_branch,
                    target_branch=target_branch,
                    reviewer_ids=reviewer_ids,
                    assignee_ids=assignee_ids,
                )
                merge_results[project_name] = self._result_build(
                    status='success', status_name='创建合并请求', url=mr.web_url
                )

            except GitlabError as e:
                self._output_write(f"🔥 处理失败: {str(e)}")
                merge_results[project_name] = self._result_build(
                    status='error', status_name='未知错误', url=str(e)
                )
        # 有效的合并结果集合
        merge_result_items = merge_results.items()

        self._output_write(f"📊{oper_username}提交的批量创建合并请求结果汇总:")
        self._output_write("=" * 50)
        self._output_write(f"来源分支:{source_branch} -> 目标分支:{target_branch}")

        have_merge_result = False
        for project, result in merge_result_items:
            if result['status'] == 'success':
                merge_url = result['url']
                self._output_write(f" - {project}: {merge_url}")
                have_merge_result = True

        if not have_merge_result:
            self._output_write(f"🧐没有创建任何合并请求，请检查是否分支名称有误！")

        self._output_write("=" * 50)

        return merge_results, self.output_buffer.getvalue()

    def get_special_projects(
            self,
            special_project_list: List[str] = None,
            start_with: str = None
    ) -> List[base.RESTObject]:
        """获取特定项目列表"""
        projects = self.gl.projects.list(
            membership=True,
            all=True,
            iterator=True
        )

        if start_with:
            projects = [p for p in projects if p.name.startswith(start_with)]
        if special_project_list:
            projects = [p for p in projects if p.name in special_project_list]

        return list(projects)

    def _get_project(self, project_id: str):
        """统一获取项目对象，带异常处理"""
        try:
            return self.gl.projects.get(project_id)
        except gitlab.exceptions.GitlabGetError as e:
            raise ValueError(f"项目不存在或无权访问: {str(e)}")
        except RequestException as e:
            raise ConnectionError(f"GitLab连接失败: {str(e)}")

    def _get_gitlab_ids(self, usernames: List[str]) -> List[int]:
        """将用户名转换为用户ID列表"""
        user_ids = []
        for username in usernames:
            users = self.gl.users.list(username=username)
            if users:
                user_ids.append(users[0].id)
            else:
                raise ValueError(f"指定的Git用户不存在: {username}")
        return user_ids

    def _output_write(self, *args):
        """包装写入详细报告Buffer中"""
        if self.output_buffer is None:
            self.output_buffer = StringIO()
        output = " ".join(str(arg) for arg in args)
        self.output_buffer.write(output + "\n")

    @staticmethod
    def _result_build(status: str, status_name: str, url: str) -> dict[str, str]:
        """构建结果"""
        return {
            "status": status,
            "status_name": status_name,
            "url": url
        }

    @staticmethod
    def _branch_exists(project, branch_name: str) -> bool:
        """检查分支是否存在"""
        try:
            project.branches.get(branch_name)
            return True
        except gitlab.exceptions.GitlabGetError:
            return False

    @staticmethod
    def _get_existing_merge_request(project, source: str, target: str):
        """获取已存在的合并请求"""
        mrs = project.mergerequests.list(
            state='opened',
            source_branch=source,
            target_branch=target
        )
        return mrs[0] if mrs else None

    @staticmethod
    def _create_merge_request(
            project,
            source_branch: str,
            target_branch: str,
            reviewer_ids: List[int],
            assignee_ids: List[int],
    ):
        """创建合并请求并指定审阅者"""
        mr = project.mergerequests.create({
            'source_branch': source_branch,
            'target_branch': target_branch,
            'title': f'合并 {source_branch} 到 {target_branch}',
            'description': 'FrankAutoGitlab Tools 2.0.0(Web) - 自动创建的合并请求',
            'remove_source_branch': False,
            'reviewer_ids': reviewer_ids,
            'assignee_ids': assignee_ids,
        })
        return mr
