from app import app, db
from app.models import User, Post, Book, Borrow

@app.shell_context_processor
def make_shell_context():
    return{'db': db, 'User': User, 'Post': Post, 'Book': Book, 'Borrow': Borrow}
