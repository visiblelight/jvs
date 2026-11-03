from datetime import datetime

import pytest

from app.models.todo import TodoItem

ALLOWED = {
    'pending': {'pending','paused','completed'},
    'paused': {'pending','paused','completed'},
    'completed': {'pending','paused','completed','archived'},
    'archived': {'archived','completed'},
}


@pytest.mark.parametrize('method', ['put','patch'])
@pytest.mark.parametrize('old', ALLOWED)
@pytest.mark.parametrize('new', ALLOWED)
def test_all_transitions(client, db, test_user, auth_headers, method, old, new):
    completed = datetime(2026, 1, 1) if old in {'completed','archived'} else None
    archived = datetime(2026, 1, 2) if old == 'archived' else None
    item=TodoItem(user_id=test_user.id,title='rule',status=old,completed_at=completed,archived_at=archived)
    db.add(item); db.commit()
    url=f'/api/admin/todo/items/{item.id}'+('/status' if method=='patch' else '')
    before=client.get(f'/api/admin/todo/items/{item.id}',headers=auth_headers).json()
    response=getattr(client,method)(url,headers=auth_headers,json={'status':new})
    if new not in ALLOWED[old]:
        assert response.status_code == 400
        assert client.get(f'/api/admin/todo/items/{item.id}',headers=auth_headers).json()['status'] == old
    else:
        assert response.status_code == 200
        data=response.json()
        assert data['status'] == new
        if new == old:
            assert data['completed_at'] == before['completed_at']
            assert data['archived_at'] == before['archived_at']
        elif new in {'pending','paused'}:
            assert data['completed_at'] is None
            assert data['archived_at'] is None
        elif new == 'archived':
            assert data['completed_at'] == before['completed_at']
            assert data['archived_at'] is not None


def test_purge_closes_all_access_paths(client, auth_headers):
    base='/api/admin/todo/items'
    item=client.post(base, headers=auth_headers, json={'title':'delete me'}).json()
    url=f"{base}/{item['id']}"
    comment=client.post(url+'/comments',headers=auth_headers,json={'content':'keep'}).json()
    assert client.delete(url+'/hard',headers=auth_headers).status_code == 400
    assert client.put(url,headers=auth_headers,json={'status':'unknown'}).status_code == 422
    assert client.put(url,headers=auth_headers,json={'status':None}).status_code == 422
    assert client.delete(url,headers=auth_headers).status_code == 204
    assert client.put(url,headers=auth_headers,json={'title':'cannot edit'}).status_code == 404
    assert client.post(url+'/comments',headers=auth_headers,json={'content':'cannot add'}).status_code == 404
    assert client.delete(url+'/hard',headers=auth_headers).status_code == 204
    for method,path,payload in [
        ('get',url,None),('put',url,{'title':'no'}),('delete',url,None),
        ('post',url+'/restore',None),('delete',url+'/hard',None),
        ('patch',url+'/status',{'status':'completed'}),('get',url+'/comments',None),
        ('post',url+'/comments',{'content':'no'}),
        ('put',url+f"/comments/{comment['id']}",{'content':'no'}),
        ('delete',url+f"/comments/{comment['id']}",None),
    ]:
        r=client.request(method,path,headers=auth_headers,**({'json':payload} if payload else {}))
        assert r.status_code == 404, (method,path,r.text)
    assert client.get(base+'?is_deleted=true',headers=auth_headers).json()['total'] == 0


def test_archived_item_can_be_found_in_trash_and_restored(client, auth_headers):
    base='/api/admin/todo/items'
    item=client.post(base,headers=auth_headers,json={'title':'archive'}).json()
    url=f"{base}/{item['id']}"
    for status in ('completed','archived'):
        assert client.put(url,headers=auth_headers,json={'status':status}).status_code == 200
    assert client.delete(url,headers=auth_headers).status_code == 204
    assert client.get(base+'?is_deleted=true',headers=auth_headers).json()['total'] == 1
    assert client.post(url+'/restore',headers=auth_headers).json()['status'] == 'archived'
    assert client.delete(url+'/hard',headers=auth_headers).status_code == 204
