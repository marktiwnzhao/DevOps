import json

from fastapi import FastAPI, Request
import os
import requests

from api.api import api_merge_diff, api_get_source_branch, api_AI_post, api_get_sha, api_post_diffNote
from service.cache import get_prompt, set_list
from service.discussion_handler import post_discussion_note
from service.utils import get_suffix, get_single_diff, match_string, get_diffNote_postion
from service.content_handler import get_gitlab_file_content, get_new_func

server = "https://git.nju.edu.cn/api/v4"
token = "glpat-B_N6oxwmDtPM8U1hD9Wf"

app = FastAPI()


def comment_merge_request(proj_id, request_id, content):
    return requests.post(server + f"/projects/{proj_id}/merge_requests/{request_id}/notes", headers={
        "PRIVATE-TOKEN": token,
        "Content-Type": "multipart/form-data"
    }, data={"body": content})


def close_merge_request(proj_id, request_id):
    return requests.put(server + f"/projects/{proj_id}/merge_requests/{request_id}", headers={
        "PRIVATE-TOKEN": token,
        "Content-Type": "multipart/form-data"
    }, data={"state_event": "close"})


def reopen_merge_request(proj_id, request_id):
    return requests.put(server + f"/projects/{proj_id}/merge_requests/{request_id}", headers={
        "PRIVATE-TOKEN": token,
        "Content-Type": "multipart/form-data"
    }, data={"state_event": "reopen"})


def merge_merge_request(proj_id, request_id):
    return requests.put(server + f"/projects/{proj_id}/merge_requests/{request_id}/merge", headers={
        "PRIVATE-TOKEN": token
    })


@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()

    # print("Received webhook data:")
    # print(data)

    if data["object_kind"] == 'merge_request' and data["object_attributes"]["state"] == 'opened':
        # 实现 merge_request 相关操作的代码
        project_id = data["project"]["id"]
        merge_request_iid = data["object_attributes"]["iid"]
        # print("project_id: " + str(project_id))
        # print("merge_request_iid: " + str(merge_request_iid))
        diffs = api_merge_diff(project_id, merge_request_iid)
        length = 0
        # diff_list = []  # single-diff和其所属函数的映射关系列表
        for diff in diffs:
            old_path = diff["old_path"]
            new_path = diff["new_path"]
            # 过滤非 java 文件的 diff
            if get_suffix(old_path) != '.java':
                continue
            file_diff = diff["diff"]
            # single_diffs = get_single_diff(file_diff)   # 分离file-diff至多个single-diff
            version = api_get_source_branch(project_id, merge_request_iid)
            # temp_file_path = get_gitlab_file_content(project_id, file_path, version)    # 获取发生改变的文件的全部内容并生成临时文件保存服务器
            # get_new_func调用了get_single_diff和get_gitlab_file_content
            diff_list = get_new_func(project_id, version, file_diff, old_path)  # 获取新增的函数
            for item in diff_list:
                length += len(item[0])
            print(f'length: {length}')
            # 单次发送涉及的函数代码的字节数不应超过8192
            if length > 8192:
                comment_merge_request(project_id, merge_request_iid, "from GenAI: 单次PR涉及的函数代码的过多")
                close_merge_request(project_id, merge_request_iid)
                return {"status": "ok"}
            # 调用大模型
            sha = api_get_sha(project_id, merge_request_iid)
            print("AI评审中...")
            close = False
            for item in diff_list:
                content = ('请你用简要的中文语言评审以下代码，如果存在问题，给出具体的问题描述（注意不能是格式化或增加注释这类无意义的话）和解决方案。'
                          + '用Markdown格式返回，并在最后建议是否接受这次merge request'
                          + '（注意仅回答一个字“是”或者“否”并保证这是整片回答的最后一个字）\n'
                          + '```待评审函数开始' + item[0] + '```待评审函数结束')
                rs = api_AI_post(content)
                if rs is None:
                    comment_merge_request(project_id, merge_request_iid, "from GenAI: 大模型评审失败")
                    close_merge_request(project_id, merge_request_iid)
                    return {"status": "ok"}
                # 推送到评论区
                flag = get_diffNote_postion(item[1])
                tmp = api_post_diffNote(project_id, merge_request_iid, sha.get("base_commit_sha"),
                                        sha.get("head_commit_sha"),
                                        sha.get("start_commit_sha"), new_path, old_path,
                                        flag[0] if flag[1] == 1 else None,
                                        flag[0] if flag[1] == 0 else None, 'from GenAI: \n' + rs)
                set_list(json.loads(tmp).get("id"), content)
                # 提取AI的建议
                if rs[-1] == '否':
                    close = True
                print(rs)
            if close:
                comment_merge_request(project_id, merge_request_iid, "from GenAI: 大模型建议拒绝这次merge request")
                close_merge_request(project_id, merge_request_iid)
            else:
                comment_merge_request(project_id, merge_request_iid, "from GenAI: 大模型建议接受这次merge request")
                reopen_merge_request(project_id, merge_request_iid)

    if data["object_kind"] == 'note':
        # 实现 note 相关操作的代码
        project_id = data["project_id"]
        merge_request_iid = data["merge_request"]["iid"]
        discussion_id = data["object_attributes"]["discussion_id"]
        description = data["object_attributes"]["description"]
        if match_string(description) == 1:  # 过滤AI的回复
            print("Received note from AI")
            return {"status": "ok"}
        post_discussion_note(project_id, merge_request_iid, discussion_id, description)

    return {"status": "ok"}
