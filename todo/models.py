from todo import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    td = db.relationship('Todo', backref='author', lazy=True)

    def __repr__(self):
        return f"User(UserID={self.id}, Name={self.name}, Email={self.email})"

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), default="Default ToDo Title")
    td_list = db.relationship('Tasks', backref='tdlist_title', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    

    def __repr__(self):
        return f"Todo(TodoID={self.id}, Title={self.title}, UserID={self.user_id})"


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(120), nullable=False)
    is_completed = db.Column(db.Integer, nullable=False, default=0)
    todo_id = db.Column(db.Integer, db.ForeignKey('todo.id'), nullable=False)

    def __repr__(self):
        return f"Tasks(ListID={self.id}, Content={self.content}, IsCompleted={self.is_completed}, TodoID={self.todo_id})"
