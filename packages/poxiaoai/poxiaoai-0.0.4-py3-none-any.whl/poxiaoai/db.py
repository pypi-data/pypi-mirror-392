# -*- coding: utf-8 -*-
# @Time : 2025/11/18 20:16
# @Author : xiaoliu
# @Email : 2558949748@qq.com
# @File : db.py
# @Project : dev
# @function ：数据库接口操作
import requests

# 通用接口
def select(sql):
    url = "http://192.168.31.125:9999/select"
    params = {
        "sql": sql
    }
    resp = requests.get(url=url, params=params)
    data = resp.json()['data']
    print(f"调用接口：select,sql:{sql},返回数据：{data}")
    return data

# 返回单条数据  {"code":"1","data":"{}"}
def selectOne(sql):
    url = "http://192.168.31.125:9999/selectOne"
    params = {
        "sql": sql
    }
    resp = requests.get(url=url, params=params)
    data = resp.json()['data']
    print(f"调用接口：selectOne,sql:{sql},返回数据：{data}")
    return data

# 新增
def insert(tb,body):
    url = "http://192.168.31.125:9999/insert"
    params = {
        "tb": tb,
    }
    resp = requests.post(url=url, params=params,json=body)
    data = resp.json()['data']
    print(f"调用接口：insert,返回数据：{data}")
    return data

def save(tb,body):
    url = "http://192.168.31.125:9999/save"
    params = {
        "tb": tb,
    }
    resp = requests.post(url=url, params=params,json=body)
    data = resp.json()['data']
    print(f"调用接口：save,返回数据：{data}")
    return data

# 更新
# tb为库表,id为主键,body为请求体
def update(tb,body):
    url = "http://192.168.31.125:9999/update"
    params = {
        "tb": tb,
        # "id": id
    }
    resp = requests.post(url=url, params=params,json=body)
    data = resp.json()['data']
    print(f"调用接口：update,返回数据：{data}")
    return data