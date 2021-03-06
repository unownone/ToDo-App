from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
#Flask imports 
from decouple import config
import string,random
from flask_mongoengine import MongoEngine
from datetime import datetime
import traceback,math
from dataclasses import dataclass,field
import bson
app = Flask(__name__)
#DB CONFIG
app.config['MONGODB_HOST'] = config('DBURI')
app.config['SECRET_KEY'] = config('SECRET_KEY')

db = MongoEngine(app)

@dataclass
class Values:
    CURR_PAGE:int = 1
    TOT_PAGE:int = 1

class Todos(db.Document):
    title = db.StringField(required=True,unique=False)
    notes = db.StringField(required=True,blank=True,unique=False)
    is_completed = db.BooleanField(default=False,unique=False)
    created_at = db.DateTimeField(default=datetime.now(),unique=False)
    uid = db.StringField(required=True,unique=False)
    
    def to_json(self):
        return {
            'title': self.title,
            'notes': self.notes,
            'is_completed': self.is_completed,
            'created_at': self.created_at,
            'uid': self.uid,
            '_id':str(self.pk)
        }




@app.route('/',methods=['GET'])
def index():
    try:
        return render_template('index.html',title='home',uid=request.cookies.get('uid',None),page=Values.CURR_PAGE)
    except:
        print(traceback.format_exc())
        return render_template('index.html',title='home',uid=request.cookies.get('uid',None),page=Values.CURR_PAGE)



@app.route('/todos/create',methods=['POST'])
def create_todos():
    req = dict(request.form)
    try:
        if req.get('title') == '':
            return jsonify(message='Title is required'),403
        tod = Todos(**req,uid=request.cookies.get('uid')).save()
        return jsonify(success=True)
    except:
        print(traceback.format_exc())
        return jsonify(success=False)


#Method to handle update of todos
@app.route('/todos/edit/<string:id>',methods=['PATCH'])
def edit_todos(id:str):
    req = dict(request.form)
    if 'is_completed' in req:
        req['is_completed']=True if req['is_completed']=='true' else False 
    try:
        tod = Todos.objects(id=id).first()
        tod.update(**req)
        return jsonify(success=True)
    except:
        print(traceback.format_exc())
        return jsonify(success=False)



#Method to delete a todo
@app.route('/todos/delete/<string:id>',methods=['DELETE'])
def delete_todos(id:str):
    try:
        print(id)
        tod = Todos.objects(id=id).first()
        tod.delete()
        return jsonify(success=True)
    except:
        return jsonify(success=False)


#Method to get all todos
@app.route('/todos/get/<int:page>',methods=['GET'])
def get_todos(page:int=1):
    try:
        # if (10*(page-1))%100 == 0:
        #     print(Todos.objects(uid=request.cookies.get('uid')).order_by('-created_at').paginate(per_page=100,page=page))
        #     page_count = len(Todos.objects(uid=request.cookies.get('uid')).order_by('-created_at').paginate(per_page=100,page=page).items())
        #     Values.FETCH_PAGE = [i for i in range(page,(page_count//10)+1)]
        tod:Todos = Todos.objects(uid=request.cookies.get('uid')).order_by('-created_at').paginate(per_page=10,page=page)
        Values.TOT_PAGE = tod.pages
        Values.CURR_PAGE = page
        pages = [i for i in range(1,tod.pages+1)]
        return render_template('todos.html',todos=tod,page=Values.CURR_PAGE,pages=pages)
    except:
        print(traceback.format_exc())
        return jsonify(success=False)


if __name__ == '__main__':
    app.run(debug=False)