from flask import Blueprint, request, jsonify, session
from app.models import User, Post, Comment, Vote
from app.db import get_db
from app.utils.auth import login_required

import sys

bp = Blueprint('api', __name__, url_prefix='/api')

# SIGNUP ROUTE
@bp.route('/users', methods=['POST'])
def signup():
    data = request.get_json()
    db = get_db()
    
    try:
        newUser = User(
            username = data['username'],
            email = data['email'],
            password = data['password']
    )
    
        # save in database
        db.add(newUser)
        db.commit()
    except:
        # insert failed, so send error to front end
        print(sys.exc_info()[0])
        # insert failed, so rollback and send error to front end
        db.rollback()
        return jsonify(message = 'Signup failed'), 500
    
    session.clear()
    session['user_id'] = newUser.id
    session['loggedIn'] = True
    return jsonify(id = newUser.id)

# LOGOUT ROUTE
@bp.route('/users/logout', methods=['POST'])
def logout():
    # remove session variables
    session.clear()
    return '', 204

# LOGIN ROUTE
@bp.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    db = get_db()
    
    try:
        user = db.query(User).filter(User.email == data['email']).one()
    except:
        print(sys.exc_info()[0])
        return jsonify(message = 'Incorrect email'), 400
    
    if user.verify_password(data['password']) == False:
        return jsonify(message = 'Incorrect password'), 400
    
    session.clear()
    session['user_id'] = user.id
    session['loggedIn'] = True
    
    return jsonify(id = user.id)

# COMMENT ROUTE
@bp.route('/comments', methods=['POST'])
@login_required
def comment():
    data = request.get_json()
    db = get_db()
    
    try:
        # create new comment
        newComment = Comment(
            comment_text = data['comment_text'],
            post_id = data['post_id'],
            user_id = session.get('user_id')
        )
        
        db.add(newComment)
        db.commit()
    except:
        print(sys.exc_info()[0])
        
        db.rollback()
        return jsonify(message = 'Comment failed'), 500
    
    return jsonify(id = newComment.id)

# UPVOTE ROUTE
@bp.route('/posts/upvote', methods=['PUT'])
@login_required
def upvote():
    data = request.get_json()
    db = get_db()
    
    try:
        # create new vote with incoming id and session id
        newVote = Vote(
            post_id = data['post_id'],
            user_id = session.get('user_id')
        )
        
        db.add(newVote)
        db.commit()
    except:
        print(sys.exc_info()[0])
        
        db.rollback()
        return jsonify(message = 'Upvote failed'), 500
    
    return '', 204

# CREATE POST ROUTE
@bp.route('/posts', methods=['POST'])
@login_required
def create():
    data = request.get_json()
    db = get_db()
    
    try:
        newPost = Post(
            title = data['title'],
            post_url = data['post_url'],
            user_id = session.get('user_id')
        )
        
        db.add(newPost)
        db.commit()
    except:
        print(sys.exc_info()[0])
        
        db.rollback()
        return jsonify(message = 'Post failed'), 500
    
    return jsonify(id = newPost.id)

# UPDATE POST ROUTE
@bp.route('/posts/<id>', methods=['PUT'])
@login_required
def update(id):
    data = request.get_json()
    db = get_db()
    
    try:
        post = db.query(Post).filter(Post.id == id).one()
        post.title = data['title']
        db.commit()
    except:
        print(sys.exc_info()[0])
        
        db.rollback()
        return jsonify(message = 'Post not found'), 404
    
    return '', 204

# DELETE POST ROUTE
@bp.route('/posts/<id>', methods=['DELETE'])
@login_required
def delete(id):
    db = get_db()
    
    try:
        db.delete(db.query(Post).filter(Post.id == id).one())
        db.commit()
    except:
        print(sys.exc_info()[0])
        
        db.rollback()
        return jsonify(message = 'Post not found'), 404
    
    return '', 204