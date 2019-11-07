from flask import request, jsonify
from todo.models import User, Todo, Tasks
from todo import app, db


@app.route("/")
def home():
    return "<h1>Todo-API</h1> \
            <p>visit /user to get user info</p> \
            <p>visit /user/user_id/todo to access todo lists</p> \
            <p>visit /user/user_id/todo/todo_id to access individual todo tasks</p> \
            <p>exmaple /user/1/todo </p>"

######## ----- begin user routes ----- ########
# ----- get all the list of users in the portal -----
@app.route("/user", methods=['GET'])
def get_all_users():
    users = User.query.all()
    all_users = []
    for each_user in users:
        user_data = {}
        user_data['id'] = each_user.id
        user_data['name'] = each_user.name
        user_data['email'] = each_user.email
        all_users.append(user_data)
    return jsonify(all_users)
    
# ----- to create new user -----
@app.route("/user", methods=['POST'])
def create_new_user():
    user_data = request.get_json()
    new_user = User(name=user_data['name'], email=user_data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message':'New user created'})
    # return f"Created new user"

# ----- To update name or email of existing user -----
@app.route("/user", methods=['PUT'])
def update_user():
    user_data = request.get_json()
    user = User.query.filter_by(id=user_data['id']).first()
    if not user:
        return jsonify({'message':'Invalid user id. user not found'})
    else:       
        user.name = user_data['name']
        user.email = user_data['email']
        db.session.commit()
        return jsonify({'message': 'User details updated successfully'})


#----- for deleting user - todo and tasks associated with the user is also deleted
@app.route("/user", methods=['DELETE'])
def delete_user():
    user_data = request.get_json()
    user = User.query.filter_by(id=user_data['id']).first()
    if not user:
        return jsonify({'message':'No user found'})
    else:
        todos = Todo.query.filter_by(user_id=user_data['id']).all()
        for each_todo in todos:
            tasks = Tasks.query.filter_by(todo_id=each_todo.id).all()
            for each_task in tasks:
                db.session.delete(each_task)
            db.session.delete(each_todo)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message':'Deleted user and associated todos'})

# ----- get the details of specific user -----
@app.route("/user/<user_id>", methods=['GET'])
def get_one_user(user_id):
    user = User.query.filter_by(id = user_id).first()
    if not user:
        return jsonify({'message': 'No user found. Invalid user_id'})
    else:
        user_data = {}
        user_data['id'] = user.id
        user_data['name'] = user.name
        user_data['email'] = user.email
        return jsonify(user_data)

######## ----- end of user routes ----- ########

######## ----- begin todo routes ----- ########
# ----- get all todos and corresponding task associated with the user id -----
@app.route("/user/<user_id>/todo", methods=['GET'])
def get_user_todo(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'message':'Invalid user id. No user found'})
    else:
        todos = Todo.query.filter_by(user_id=user_id).all()
        output = []
        for each_todo in todos:
            todo_data={}
            tasks=[]
            todo_data['id'] = each_todo.id
            todo_data['title'] = each_todo.title
            todo_data['tasks'] = []
            tasks_list = Tasks.query.filter_by(todo_id=each_todo.id).all()
            for each_task in tasks_list:   
                task_data={}        
                task_data['id'] = each_task.id         
                task_data['content'] = each_task.content
                task_data['is_completed'] = each_task.is_completed
                tasks.append(task_data)
                todo_data['tasks'] = tasks
            output.append(todo_data)
        return jsonify({'user-todos':output})

#---- To create new todo and corresponding tasks for a user -----
@app.route("/user/<user_id>/todo", methods=['POST'])
def create_todo(user_id):
    data = request.get_json()
    title = data['title']    
    tasks = data['tasks']
    new_todo = Todo(title=title, user_id=user_id)
    db.session.add(new_todo)
    db.session.commit()
    for each_task in tasks:
        task = Tasks(content=each_task['content'], is_completed=each_task['is_completed'], todo_id=new_todo.id)
        db.session.add(task)
        db.session.commit()
    return jsonify({'message':'New todo and tasks added for the user'})

# ----- to update a todo title of corresponding user -----
@app.route("/user/<user_id>/todo", methods=['PUT'])
def update_todo_title(user_id):
    datas = request.get_json()
    id_value = datas['id']
    todo = Todo.query.filter_by(id=id_value, user_id=user_id).first()
    if todo:
        todo.title = datas['title']
        db.session.commit()
        return jsonify({'message':'Todo title updated successfully'})
    else:
        return jsonify({'message':'Invalid user_id/todo_id. No data found'})

# ----- to delete a todo and corresponding tasks ------
@app.route("/user/<user_id>/todo", methods=['DELETE'])
def delete_todo_and_tasks(user_id):
    data = request.get_json()
    id_value = data['id']
    todo = Todo.query.filter_by(id=id_value, user_id=user_id).first()
    if todo:
        tasks = Tasks.query.filter_by(todo_id=id_value).all()
        for each_task in tasks:
            db.session.delete(each_task)
            db.session.commit()
        db.session.delete(todo)
        db.session.commit()
        return jsonify({'message':'Todo and corresponding tasks deleted successfully'})
    else:
        return jsonify({'message':'Invalid user_id/todo_id. No data found'})
    
# ----- get task associated with todo id of corresponding user -----
@app.route("/user/<user_id>/todo/<todo_id>", methods=['GET'])
def get_user_todo_lists(user_id, todo_id):
    todo = Todo.query.filter_by(user_id=user_id, id=todo_id).all()
    if not todo:
        return jsonify({'message':'Invalid user_id/todo_id. No data found'})
    else:
        tasks = Tasks.query.filter_by(todo_id=todo_id).all()
        output=[]
        for each_task in tasks:
            lists={}
            lists['id']=each_task.id
            lists['content']=each_task.content
            lists['is_completed']=each_task.is_completed
            output.append(lists)
        return jsonify({'todo-tasks': output})  

# ---- to insert new task for corresponding todo of a user -----
@app.route("/user/<user_id>/todo/<todo_id>", methods=['POST'])  
def insert_todo_task_lists(user_id, todo_id):
    todo = Todo.query.filter_by(user_id=user_id, id=todo_id).all()
    if not todo:
        return jsonify({'message':'Invalid user_id/todo_id. No data found'})
    else:
        datas = request.get_json()
        for each_data in datas['todo-tasks']:
            new_task = Tasks(content=each_data['content'], todo_id=todo_id)
            db.session.add(new_task)
            db.session.commit()
        return jsonify({'message':'New tasks inserted successfully'})


# ----- to update tasks of corresponding todo of a user -----
@app.route('/user/<user_id>/todo/<todo_id>',methods=['PUT'])
def update_todo(user_id, todo_id):
    todo = Todo.query.filter_by(user_id=user_id, id=todo_id).all()
    if not todo:
        return jsonify({'message':'Invalid user_id/todo_id. No data found'})
    else:
        datas = request.get_json()
        for each_data in datas['todo-tasks']:
            tasks = Tasks.query.filter_by(todo_id=todo_id).all()
            for each_task in tasks:
                if each_data['id'] == each_task.id:
                    each_task.content = each_data['content']
                    each_task.is_completed = each_data['is_completed']  
                    db.session.commit()      
        return jsonify({'message': 'Todo tasks updated successfully'})

# ----- to delete task of corresponding todo of the user ------
@app.route("/user/<user_id>/todo/<todo_id>", methods=['DELETE'])
def delete_todo_tasks(user_id, todo_id):
    todo = Todo.query.filter_by(user_id=user_id, id=todo_id).first()
    if not todo:
        return jsonify({'message': 'Invalid user_id/todo_id. No data found'})
    else:
        datas = request.get_json()
        for each_data in datas['todo-tasks']:
            task = Tasks.query.filter_by(id=each_data['id']).first()
            if task:
                db.session.delete(task)
                db.session.commit()
            else:
                return jsonify({'message':'No task exist for that id'})
        return jsonify({'message':'Deleted todo tasks successfully'})

######## ----- end of todo routes ----- ########


