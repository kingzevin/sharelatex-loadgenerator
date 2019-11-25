* State 0: Start
  * index: / GET -> /login | /project
* State 1: /login 
  * register: /register GET
  * login: /login POST -> /project
  * forget: /user/password/reset GET -> /user/password/reset POST
* State 2: /project 
  * create project: /project/new POST
  * delete projcet: /project/id DELETE
  * settings: /user/settings GET -> /user/settings POST
  * download: /project/id/download/zip
  * add to folders: /tag/tagid/project/projectid POST
  * create a folder: /tag POST
  * rename: /project/id/rename POST
  * make a copy: /project/id/clone POST
  * select: /project/id GET -> /project/id
* State 3: /project/id
  * chat: project/id/messages?limit=50 GET
    * send message: /project/id/messages POST <INTERNAL ERROR>
  * edit_document: /editingSession/id PUT 
    * spell_check: /spelling/check POST <INTERNAL ERROR>
  * file_upload: /project/id/upload POST
  * show_history: 
    * /project/id/updates?min_count=10 GET
    * /project/id/doc/id/diff?from=5&to=19 GET <INTERNAL ERROR>
  * compile: /project/id/compile POST
    * if not too-recently-compiled:
      * /project/id/user/id/build/id/output/output.log?compileGroup=standard GET
      * /project/id/user/id/build/id/output/output.pdf?compileGroup=standard&pdfng=true GET
  * download pdf: /project/id/output/output.pdf?compileGroup=standard&popupDownload=true GET
  * clear caches: project/id/output DELETE <INTERNAL ERROR>
  * share_project:
    * /user/contacts GET 
    * /project/id/invite POST




















# States
No. State|url
--|--
0|/
1|

* 0: /
``` flow
0=>start: 0: /
cond1=>condition: logined?
1=>end: 1: projects
2=>end: 2: login

0->cond1
cond1(yes)->1
cond1(no)->2
```
