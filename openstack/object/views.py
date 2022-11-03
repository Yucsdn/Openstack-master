import json

import requests
from django.shortcuts import render, redirect


def login(request):
    return render(request, 'login.html')


def get_token(request):
    domain = request.POST['domain']
    username = request.POST['username']
    password = request.POST['password']
    data = {
        "auth": {
            "identity": {
                "methods": [
                    "password"
                ],
                "password": {
                    "user": {
                        "domain": {
                            "name": domain
                        },
                        "name": username,
                        "password": password
                    }
                }
            },
            "scope": {
                "project": {
                    "domain": {
                        "name": domain
                    },
                    "name": username
                }
            }
        }
    }
    url = 'http://192.168.174.10:5000/v3/auth/tokens'
    result = requests.post(url, json=data)
    token = result.headers['X-Subject-Token']
    print('获取的token：', token)
    request.session['token'] = token
    return redirect('/openstack/home/')

def get_project_token(request):
    domain_token = request.session.get('token')
    data = {
        "auth": {
            "identity": {
                "methods": [
                    "token"
                ],
                "token": {
                    "id": domain_token
                }
            },
            "scope": {
                "project": {
                    "domain": {
                        "name": "default"
                    },
                    "name": "admin"
                }
            }
        }
    }
    url = "http://192.168.119.128:5000/v3/auth/tokens"
    result = requests.post(url, data=json.dumps(data)).headers.get("X-Subject-Token")
    # 返回的token在 response header 里面
    return result


def size_get(num):
    if num < 1024:
        return str(num) + ' ' + 'B'
    elif 1024 <= num < 1024**2:
        x = round(num/1024, 1)
        return str(x) + ' ' + 'KB'
    else:
        x = round(num/(1024**2), 1)
        return str(x) + ' ' + 'MB'


def home(request):
    return render(request, 'index.html')


def console(request):
    token = request.session.get('token')
    data = {
        "auth": {
            "identity": {
                "methods": [
                    "token"
                ],
                "token": {
                    "id": token
                }
            },
            "scope": {
                "project": {
                    "domain": {
                        "name": "default"
                    },
                    "name": "admin"
                }
            }
        }
    }
    url1 = "http://192.168.174.10:5000/v3/auth/tokens"
    result1 = requests.post(url1, json=data)
    token1 = result1.headers['X-Subject-Token']
    print('获取的token：', token1)
    request.session['token'] = token1
    return render(request, 'console.html')


def notwork(request):

    return render(request, 'notwork.html')


def instance(request):
    token = request.session.get('token')
    url = "http://192.168.174.10:8774/v2.1/servers"
    headers = {'X-Auth-Token': token}
    result = requests.get(url, headers=headers)
    datas = result.json()
    print(datas)
    data_key = "servers"
    for key in datas:
        if key == data_key:
            servers = datas[key]
    dat = []
    for d in servers:
        data = {}
        name = d['name']
        id = d['id']

        data["name"] = name
        data["id"] = id
        dat.append(data)
    return render(request, 'instance.html', {'dat': dat})


def instance_revise_delete(request):
    token = request.session.get('token')
    headers = {'X-Auth-Token': token}
    if "delete" in request.POST:
        instance_id = request.POST['instance_id']
        url = "http://192.168.174.10:8774/v2.1/servers/" + instance_id
        result = requests.delete(url, headers=headers)
        print('删除实例状态码：', result.status_code)
        return redirect('/openstack/home/instance/')
    elif "revise" in request.POST:
        id = request.POST['id']
        name = request.POST['name']
        password = request.POST['password']
        email = request.POST['email']
        description = request.POST['description']
        url = "http://192.168.174.10:5000/v3/users/" + id
        data = {
            "user": {
                "enabled": True,
                "options": {
                    "ignore_lockout_failure_attempts": True
                },
                "name": name,
                "password": password,
                "description": description,
                "email": email,
            }
        }
        result = requests.patch(url, headers=headers, json=data)
        print('修改用户状态码：', result.status_code)
        return redirect('/openstack/home/users/')
    else:
        print("error!!")
        return redirect('/openstack/home/users/')


def instance_add(request):
    token = request.session.get('token1')
    name = request.POST['name']
    image = request.POST['image']
    fla = request.POST['fla']
    if image == "cirros":
        im = "3576df26-889d-4ce3-87cf-fa73fec54c4d"
    if fla == "CPU=1/RAM=512MB/ROM=1GB":
        fl = "http://192.168.174.10:8774/v2.32/flavors/1"
    url = "http://192.168.174.10:8774/v2.32/servers"
    data = {
        "server": {
            "name": name,
            "imageRef": im,
            "flavorRef": fl,
            "networks": "auto"
        }
    }
    headers = {'X-Auth-Token': token}
    result = requests.post(url, json=data, headers=headers)
    print('创建实例状态码：', result.status_code)
    return redirect('/openstack/home/instance/')


def image(request):
    token = request.session.get('token')
    url = "http://192.168.174.10:9292/v2/images"
    headers = {'X-Auth-Token': token}
    result = requests.get(url, headers=headers)
    datas = result.json()
    print(datas)
    data_key = "images"
    for key in datas:
        if key == data_key:
            images = datas[key]
    dat = []
    for d in images:
        data = {}
        name = d['name']
        id = d['id']
        disk_format = d['disk_format']
        size = size_get(d['size'])
        status = d['status']

        data["name"] = name
        data["id"] = id
        data["disk_format"] = disk_format
        data["size"] = size
        data["status"] = status
        dat.append(data)
    return render(request, 'image.html', {'dat': dat})


def images_revise_delete(request):
    token = request.session.get('token')
    headers = {'X-Auth-Token': token}
    if "delete" in request.POST:
        image_id = request.POST['image_id']
        url = "http://192.168.174.10:9292/v2/images/" + image_id
        result = requests.delete(url, headers=headers)
        print('删除镜像状态码：', result.status_code)
        return redirect('/openstack/home/image/')
    elif "revise" in request.POST:
        id = request.POST['id']
        name = request.POST['name']
        password = request.POST['password']
        email = request.POST['email']
        description = request.POST['description']
        url = "http://192.168.174.10:5000/v3/users/" + id
        data = {
            "user": {
                "enabled": True,
                "options": {
                    "ignore_lockout_failure_attempts": True
                },
                "name": name,
                "password": password,
                "description": description,
                "email": email,
            }
        }
        result = requests.patch(url, headers=headers, json=data)
        print('修改用户状态码：', result.status_code)
        return redirect('/openstack/home/users/')
    else:
        print("error!!")
        return redirect('/openstack/home/users/')


def images_add(request):
    token = request.session.get('token')
    url = "http://192.168.174.10:9292/v2/images"
    headers = {'X-Auth-Token': token}


def flavors(request):
    token = request.session.get('token')
    url = "http://192.168.174.10:8774/v2.1/flavors"
    headers = {'X-Auth-Token': token}
    result = requests.get(url, headers=headers)
    data = result.json()
    return render(request, 'flavors.html')


def users(request):
    token = request.session.get('token')
    url = "http://192.168.174.10:5000/v3/users"
    headers = {'X-Auth-Token': token}
    param = {'format': 'json'}
    result = requests.get(url, headers=headers, params=param)
    datas = result.json()
    data_key = "users"
    for key in datas:
        if key == data_key:
            user = datas[key]
    dat = []
    for d in user:
        data = {}
        name = d['name']
        ids = d['id']
        enabled = d['enabled']

        data["name"] = name
        data["id"] = ids
        data["enabled"] = enabled
        dat.append(data)
    return render(request, 'users.html', {'dat': dat})


def users_revise_delete(request):
    token = request.session.get('token')
    headers = {'X-Auth-Token': token}
    if "delete" in request.POST:
        user_id = request.POST['user_id']
        url = "http://192.168.174.10:5000/v3/users/" + user_id
        result = requests.delete(url, headers=headers)
        print('删除用户状态码：', result.status_code)
        return redirect('/openstack/home/users/')
    elif "revise" in request.POST:
        id = request.POST['id']
        name = request.POST['name']
        password = request.POST['password']
        email = request.POST['email']
        description = request.POST['description']
        url = "http://192.168.174.10:5000/v3/users/" + id
        data = {
            "user": {
                "enabled": True,
                "options": {
                    "ignore_lockout_failure_attempts": True
                },
                "name": name,
                "password": password,
                "description": description,
                "email": email,
            }
        }
        result = requests.patch(url, headers=headers, json=data)
        print('修改用户状态码：', result.status_code)
        return redirect('/openstack/home/users/')
    else:
        print("error!!")
        return redirect('/openstack/home/users/')


def users_add(request):
    token = request.session.get('token')
    name = request.POST['name']
    password =request.POST['password']
    email = request.POST['email']
    description = request.POST['description']
    headers = {'X-Auth-Token': token}
    url = "http://192.168.174.10:5000/v3/users"
    data = {
    "user": {
        "default_project_id": "263fd9",
        "domain_id": "93539fb88cc047b3a7923b93b9951d2b",
        "enabled": True,
        "federated": [
            {
                "idp_id": "efbab5a6acad4d108fec6c63d9609d83",
                "protocols": [
                    {
                        "protocol_id": "mapped",
                        "unique_id": "test@example.com"
                    }
                ]
            }
        ],
        "name": name,
        "password": password,
        "description": description,
        "email": email,
        "options": {
            "ignore_password_expiry": True
        }
    }
}
    result = requests.post(url, headers=headers, json=data)
    print('添加用户状态码：', result.status_code)
    return redirect('/openstack/home/users/')


def groups(request):  #用户组
    token = request.session.get('token')
    url = "http://192.168.174.10:5000/v3/groups"
    headers = {'X-Auth-Token': token}
    param = {'format': 'json'}
    result = requests.get(url, headers=headers, params=param)
    datas = result.json()
    data_key = "groups"
    for key in datas:
        if key == data_key:
            groups = datas[key]
    dat = []
    for d in groups:
        data = {}
        name = d['name']
        description = d['description']
        id = d['id']

        data["name"] = name
        data["description"] = description
        data["id"] = id
        dat.append(data)
    return render(request, 'groups.html', {'dat': dat})


def groups_revise_delete(request):
    token = request.session.get('token')
    headers = {'X-Auth-Token': token}
    if "delete" in request.POST:
        group_id = request.POST['group_id']
        url = "http://192.168.174.10:5000/v3/groups/" + group_id
        result = requests.delete(url, headers=headers)
        print('删除组状态码：', result.status_code)
        return redirect('/openstack/home/groups/')
    elif "revise" in request.POST:
        id = request.POST['id']
        name = request.POST['name']
        description = request.POST['description']
        data = {
            "group": {
                "description": description,
                "name": name
            }
        }
        url = "http://192.168.174.10:5000/v3/groups/" + id
        result = requests.patch(url, headers=headers, json=data)
        print('修改组状态码：', result.status_code)
        return redirect('/openstack/home/groups/')
    else:
        print("error!!")
        return redirect('/openstack/home/groups/')


def groups_add(request):
    token = request.session.get('token')
    name = request.POST['name']
    description = request.POST['description']
    headers = {'X-Auth-Token': token}
    url = "http://192.168.174.10:5000/v3/groups"
    data = {
        "group": {
            "description": description,
            "domain_id": "93539fb88cc047b3a7923b93b9951d2b",
            "name": name
        }
    }
    result = requests.post(url, headers=headers, json=data)
    print('添加组状态码：', result.status_code)
    return redirect('/openstack/home/groups/')


def roles(request):  #角色
    token = request.session.get('token')
    url = "http://192.168.174.10:5000/v3/roles"
    headers = {'X-Auth-Token': token}
    param = {'format': 'json'}
    result = requests.get(url, headers=headers, params=param)
    datas = result.json()
    data_key = "roles"
    for key in datas:
        if key == data_key:
            roles = datas[key]
    dat = []
    for d in roles:
        data = {}
        name = d['name']
        id = d['id']

        data["name"] = name
        data["id"] = id
        dat.append(data)
    return render(request, 'roles.html', {'dat': dat})


def roles_revise_delete(request):
    token = request.session.get('token')
    headers = {'X-Auth-Token': token}
    if "delete" in request.POST:
        role_id = request.POST['role_id']
        url = "http://192.168.174.10:5000/v3/roles/" + role_id
        result = requests.delete(url, headers=headers)
        print('删除角色状态码：', result.status_code)
        return redirect('/openstack/home/roles/')
    elif "revise" in request.POST:
        id = request.POST['id']
        name = request.POST['name']
        description = request.POST['description']
        url = "http://192.168.174.10:5000/v3/roles/" + id
        data = {
            "role": {
                "description": description,
                "name": name
            }
        }
        result = requests.patch(url, headers=headers, json=data)
        print('修改角色状态码：', result.status_code)
        return redirect('/openstack/home/roles/')
    else:
        print("error!!")
        return redirect('/openstack/home/roles/')


def roles_add(request):
    token = request.session.get('token')
    name = request.POST['name']
    description = request.POST['description']
    headers = {'X-Auth-Token': token}
    url = "http://192.168.174.10:5000/v3/roles"
    data = {
        "role": {
            "description": description,
            "name": name
        }
    }
    result = requests.post(url, headers=headers, json=data)
    print('添加角色状态码：', result.status_code)
    return redirect('/openstack/home/roles/')


def projects(request): #项目
    token = request.session.get('token')
    url = "http://192.168.174.10:5000/v3/projects"
    headers = {'X-Auth-Token': token}
    param = {'format': 'json'}
    result = requests.get(url, headers=headers, params=param)
    datas = result.json()
    data_key = "projects"
    for key in datas:
        if key == data_key:
            projects = datas[key]
    dat = []
    for d in projects:
        data = {}
        name = d['name']
        description = d['description']
        id = d['id']
        enabled = d['enabled']

        data["name"] = name
        data["description"] = description
        data["id"] = id
        data["enabled"] = enabled
        dat.append(data)
    return render(request, 'projects.html', {'dat': dat})


def projects_revise_delete(request):
    token = request.session.get('token')
    headers = {'X-Auth-Token': token}
    if "delete" in request.POST:
        project_id = request.POST['project_id']
        url = "http://192.168.174.10:5000/v3/projects/" + project_id
        result = requests.delete(url, headers=headers)
        print('删除项目状态码：', result.status_code)
        return redirect('/openstack/home/projects/')
    elif "revise" in request.POST:
        id = request.POST['id']
        name = request.POST['name']
        description = request.POST['description']
        url = "http://192.168.174.10:5000/v3/projects/" + id
        data = {
            "project": {
                "description": description,
                "name": name
            }
        }
        result = requests.patch(url, headers=headers, json=data)
        print('修改项目状态码：', result.status_code)
        return redirect('/openstack/home/projects/')
    else:
        print("error!!")
        return redirect('/openstack/home/projects/')


def projects_add(request):
    token = request.session.get('token')
    name = request.POST['name']
    description = request.POST['description']
    headers = {'X-Auth-Token': token}
    url = "http://192.168.174.10:5000/v3/projects"
    data = {
        "project": {
            "description": description,
            "domain_id": "93539fb88cc047b3a7923b93b9951d2b",
            "enabled": True,
            "is_domain": False,
            "name": name,
            "options": {}
        }
    }
    result = requests.post(url, headers=headers, json=data)
    print('添加项目状态码：', result.status_code)
    return redirect('/openstack/home/projects/')