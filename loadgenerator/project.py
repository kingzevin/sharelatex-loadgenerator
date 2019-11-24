# -*- coding: UTF-8 -*-
import socketio
import gevent
import random
import os
import re
import string
import uuid
import json
from . import ROOT_PATH, csrf, randomwords
from locust import TaskSet, task

## zevin
from inspect import currentframe, getframeinfo
def LINE():
    # print "Enter:" + str(getframeinfo(currentframe()).filename + ":" + getframeinfo(currentframe()).function) + "-LINE:" + str(getframeinfo(currentframe()).lineno)
    return "LINE:" + str(getframeinfo(currentframe()).filename) + ":" + str(getframeinfo(currentframe()).lineno)
##

class Websocket():
    def __init__(self, locust, project_id):
        self.c = socketio.Client(locust)
        self.pending_text = None
        self.c.on("clientTracking.clientUpdated", self.noop)
        self.c.on("clientTracking.clientDisconnected", self.noop)
        self.c.on("new-chat-message", self.noop)
        self.c.on("reciveNewFile", self.noop)

        self.c.on("otUpdateApplied", self.update_version)
        self.c.emit("joinProject", [{"project_id": project_id}], id=1)
        with gevent.Timeout(30, False):
            m = self.c.recv()
            while len(m["args"]) == 0:
                m = self.c.recv()
            self.root_folder =  m["args"][1]["rootFolder"][0]
            self.main_tex = m["args"][1]["rootDoc_id"]
            self.c.emit("joinDoc", [self.main_tex], id=2)
            old_doc = self.c.recv()
            # print("old_doc{",old_doc["args"],"}old_doc")
            while len(old_doc["args"]) == 0:
                old_doc = self.c.recv()
                # print("ARGS{",old_doc["args"],"}ARGS")
            self.doc_text = "\n".join(old_doc["args"][1])
            self.doc_version = old_doc["args"][2]
            self.c.emit("clientTracking.getConnectedUsers", [], id=3)
            self.c.recv()
        assert hasattr(self, "doc_version")

    def recv(self): self.c.recv()

    def update_version(self, args):
        # print "Enter:" + str(getframeinfo(currentframe()).filename + ":" + getframeinfo(currentframe()).function) + "-LINE:" + str(getframeinfo(currentframe()).lineno)
        self.doc_version = args[0]["v"] + 1
        if self.pending_text is not None:
            self.doc_text = self.pending_text
            self.pending_text = None

    def noop(self, args):
        pass

    def update_document(self, new_text):
        # print "Enter:" + str(getframeinfo(currentframe()).filename + ":" + getframeinfo(currentframe()).function) + "-LINE:" + str(getframeinfo(currentframe()).lineno)
        update = [ self.main_tex,
                  {"doc": self.main_tex,
                   "op": [{"d": self.doc_text, "p":0},
                          {"i": new_text, "p":0}],
                   "v": self.doc_version}]
        self.c.emit("applyOtUpdate", update)
        self.pending_text = new_text

    def close(self):
        self.c.close()

def template(path):
    # print "Enter:" + str(getframeinfo(currentframe()).filename + ":" + getframeinfo(currentframe()).function) + "-LINE:" + str(getframeinfo(currentframe()).lineno)
    with open(os.path.join(ROOT_PATH, path), "r") as f:
        return string.Template(f.read())

def chat(l):
    # print "Enter:" + str(getframeinfo(currentframe()).filename + ":" + getframeinfo(currentframe()).function) + "-LINE:" + str(getframeinfo(currentframe()).lineno)
    msg = "".join( [random.choice(string.letters) for i in range(30)] )
    p = dict(_csrf=l.csrf_token, content=msg)
    l.client.post("/project/%s/messages" % l.project_id, params=p, name="/project/[id]/messages")

DOCUMENT_TEMPLATE = template("document.tex")
def edit_document(l):
    # print "Enter:" + str(getframeinfo(currentframe()).filename + ":" + getframeinfo(currentframe()).function) + "-LINE:" + str(getframeinfo(currentframe()).lineno)
    params = dict(paragraph=random.randint(0, 1000))
    doc = DOCUMENT_TEMPLATE.safe_substitute(params)
    l.websocket.update_document(doc)
    spell_check(l)

def stop(l):
    # print "Enter:" + str(getframeinfo(currentframe()).filename + ":" + getframeinfo(currentframe()).function) + "-LINE:" + str(getframeinfo(currentframe()).lineno)
    l.interrupt()

def share_project(l):
    # print "Enter:" + str(getframeinfo(currentframe()).filename + ":" + getframeinfo(currentframe()).function) + "-LINE:" + str(getframeinfo(currentframe()).lineno)
    l.client.get("/user/contacts")
    p = dict(_csrf=l.csrf_token, email="joerg.2@higgsboson.tk", privileges="readAndWrite")
    l.client.post("/project/%s/invite" % l.project_id, data=p, name="/project/[id]/users")

def spell_check(l):
    # print "Enter:" + str(getframeinfo(currentframe()).filename + ":" + getframeinfo(currentframe()).function) + "-LINE:" + str(getframeinfo(currentframe()).lineno)
    data = dict(language="en", _csrf=l.csrf_token, words=randomwords.sample(1, 1), token=l.user_id)
    r = l.client.post("/spelling/check", json=data, name="/spelling/check" + str(dict))

def file_upload(l):
    # print "Enter:" + str(getframeinfo(currentframe()).filename + ":" + getframeinfo(currentframe()).function) + "-LINE:" + str(getframeinfo(currentframe()).lineno)
    path = os.path.join(ROOT_PATH, "tech-support.jpg")
    p = dict(folder_id=l.websocket.root_folder['_id'],
             _csrf=l.csrf_token,
             qquuid=str(uuid.uuid1()),
             qqtotalfilesize=os.stat(path).st_size)
    files = { "qqfile": ('tech-support.jpg', open(path, "rb"), 'image/jpeg')}
    resp = l.client.post("/project/%s/upload" % l.project_id, params=p, files=files, name="/project/[id]/upload")

def show_history(l):
    # print "Enter:" + str(getframeinfo(currentframe()).filename + ":" + getframeinfo(currentframe()).function) + "-LINE:" + str(getframeinfo(currentframe()).lineno)
    l.client.get("/project/%s/updates?min_count=10" % l.project_id, name="/project/[id]/updates")
    u =  "/project/%s/doc/%s/diff?from=1&to=2" % (l.project_id, l.websocket.root_folder['_id'])
    l.client.get(u, name="/project/[id]/doc/[id]/diff")

def compile(l):
    # print "Enter:" + str(getframeinfo(currentframe()).filename + ":" + getframeinfo(currentframe()).function) + "-LINE:" + str(getframeinfo(currentframe()).lineno)
    d = {"rootDoc_id": l.websocket.root_folder['_id'] ,"draft": False,"_csrf": l.csrf_token}
    r1 = l.client.post("/project/%s/compile" % l.project_id,
                       json=d,
                       name="/project/[id]/compile")
    resp = r1.json()
    if resp["status"] == "too-recently-compiled":
        return
    files = resp["outputFiles"]
    l.client.get("/project/%s/output/output.log" % l.project_id,
            params={"build": files[0]["build"]},
            name="/project/[id]/output/output.log?build=[id]")
    l.client.get("/project/%s/output/output.pdf" % l.project_id,
            params={"build": files[4]["build"], "compileGroup": "standard", "pdfng": True},
            name="/project/[id]/output/output.pdf")

def download_pdf(l):
    l.client.get("project/%s/output/output.pdf?compileGroup=standard&popupDownload=true" % l.project_id)

def clear_cache(l):
    l.client.delete("project/%s/output" % l.project_id)

def find_user_id(doc):
    # print "Enter:" + str(getframeinfo(currentframe()).filename + ":" + getframeinfo(currentframe()).function) + "-LINE:" + str(getframeinfo(currentframe()).lineno)
    # window.csrfToken = "DwSsXuVc-uECsSv6dW5ifI4025HacsODuhb8"
    # print("doc[:\n", doc.decode("utf-8"), "\n]doc")
    user = re.search('"user":{"id":"([^"]+)', doc.decode("utf-8") , re.IGNORECASE)
    # user = re.search('window.user = ({[^;]+);', doc.decode("utf-8") , re.IGNORECASE)
    assert user, "No user found in response"
    return user.group(1)

class Page(TaskSet): # 怎么执行到这的
    tasks = { stop: 1, chat: 2, edit_document: 2, file_upload: 2, show_history: 2, compile: 2, share_project: 1}
    def on_start(self):
        # print "Enter:" + str(getframeinfo(currentframe()).filename + ":" + getframeinfo(currentframe()).function) + "-LINE:" + str(getframeinfo(currentframe()).lineno)
        projects = self.parent.projects
        assert len(projects) > 0
        self.project_id = random.choice(projects)['id']

        page = self.client.get("/project/%s" % self.project_id, name="/project/[id]")
        self.csrf_token = csrf.find_in_page(page.content)
        self.user_id = find_user_id(page.content)

        self.websocket = Websocket(self.locust, self.project_id)
        def _receive():
            try:
                while True:
                    self.websocket.recv()
            except gevent.socket.error:
                print("websocket closed")
        gevent.spawn(_receive)

    def interrupt(self,reschedule=True):
        # print "Enter:" + str(getframeinfo(currentframe()).filename + ":" + getframeinfo(currentframe()).function) + "-LINE:" + str(getframeinfo(currentframe()).lineno)
        self.websocket.close()
        super(Page, self).interrupt(reschedule=reschedule)
