from socket import SocketIO
from flask import render_template, request, session, redirect, url_for, jsonify
from bson.objectid import ObjectId
from datetime import datetime
import pymongo
from app import app,conversations_collection,messages_collection
from app import alumini_collection, students_collection
# Initialize SocketIO
from flask_socketio import SocketIO, join_room, leave_room, emit
socketio = SocketIO(app, cors_allowed_origins="*")

# Connected users
connected_users = {}

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    # Remove user from connected users
    for user_id, sid in list(connected_users.items()):
        if sid == request.sid:
            del connected_users[user_id]
            break

@socketio.on('register')
def handle_register(data):
    user_id = data.get('user_id')
    if user_id:
        connected_users[user_id] = request.sid
        print(f"User {user_id} registered with session {request.sid}")

@socketio.on('join')
def handle_join(data):
    user_id = data.get('user_id')
    recipient_id = data.get('recipient_id')
    
    if user_id and recipient_id:
        # Create a unique room name for this conversation
        room = get_room_name(user_id, recipient_id)
        join_room(room)
        print(f"User {user_id} joined room {room}")

@socketio.on('send_message')
def handle_send_message(data):
    sender_id = data.get('sender_id')
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    
    if not sender_id or not recipient_id or not content:
        return
    
    # Save message to database
    now = datetime.now()
    
    # Find or create conversation
    conversation = conversations_collection.find_one({
        "participants": {"$all": [ObjectId(sender_id), ObjectId(recipient_id)]}
    })
    
    if not conversation:
        conversation_id = conversations_collection.insert_one({
            "participants": [ObjectId(sender_id), ObjectId(recipient_id)],
            "created_at": now,
            "last_message": content,
            "last_message_time": now
        }).inserted_id
    else:
        conversation_id = conversation["_id"]
        conversations_collection.update_one(
            {"_id": conversation_id},
            {"$set": {"last_message": content, "last_message_time": now}}
        )
    
    # Insert message
    message_id = messages_collection.insert_one({
        "conversation_id": conversation_id,
        "sender_id": ObjectId(sender_id),
        "recipient_id": ObjectId(recipient_id),
        "content": content,
        "timestamp": now,
        "read": False
    }).inserted_id
    
    # Send to recipient if online
    if recipient_id in connected_users:
        recipient_sid = connected_users[recipient_id]
        emit('new_message', {
            'message_id': str(message_id),
            'sender_id': sender_id,
            'sender_name': data.get('sender_name', 'User'),
            'content': content,
            'time': 'Just now'
        }, room=recipient_sid)

@socketio.on('mark_read')
def handle_mark_read(data):
    sender_id = data.get('sender_id')
    recipient_id = data.get('recipient_id')
    
    if not sender_id or not recipient_id:
        return
    
    # Find conversation
    conversation = conversations_collection.find_one({
        "participants": {"$all": [ObjectId(sender_id), ObjectId(recipient_id)]}
    })
    
    if conversation:
        # Mark messages as read
        messages_collection.update_many({
            "conversation_id": conversation["_id"],
            "sender_id": ObjectId(sender_id),
            "recipient_id": ObjectId(recipient_id),
            "read": False
        }, {"$set": {"read": True}})

# Helper function to get a unique room name for a conversation
def get_room_name(user1, user2):
    # Sort IDs to ensure the same room name regardless of who initiates
    ids = sorted([user1, user2])
    return f"chat_{ids[0]}_{ids[1]}"

# Routes
@app.route('/chat', methods=['GET'])
def chat():
    if 'student_id' in session:
        user_id = session['student_id']
        user_name = session['student_name']
        user_type = 'student'
    elif 'alumni_id' in session:
        user_id = session['alumni_id']
        user_name = session['alumni_name']
        user_type = 'alumni'
    else:
        return redirect(url_for('login'))
    
    return render_template('chat.html', 
                          current_user_id=user_id, 
                          current_user_name=user_name, 
                          user_type=user_type)

@app.route('/api/recent-chats')
def get_recent_chats():
    if 'student_id' in session:
        user_id = session['student_id']
        user_type = 'student'
    elif 'alumni_id' in session:
        user_id = session['alumni_id']
        user_type = 'alumni'
    else:
        return jsonify([])
    
    # Find conversations where the current user is a participant
    conversations = list(conversations_collection.find({
        "participants": ObjectId(user_id)
    }).sort("last_message_time", pymongo.DESCENDING))
    
    result = []
    for conv in conversations:
        # Get the other participant
        other_participant_id = next((str(p) for p in conv["participants"] if str(p) != user_id), None)
        
        if not other_participant_id:
            continue
            
        # Find the other user's details
        if user_type == 'student':
            other_user = alumini_collection.find_one({"_id": ObjectId(other_participant_id)})
            other_type = 'alumni'
        else:
            other_user = students_collection.find_one({"_id": ObjectId(other_participant_id)})
            other_type = 'student'
        
        if other_user:
            # Get unread count
            unread_count = messages_collection.count_documents({
                "conversation_id": conv["_id"],
                "sender_id": ObjectId(other_participant_id),
                "read": False
            })
            
            # Format time
            time_str = "Just now"
            if "last_message_time" in conv:
                time_diff = datetime.now() - conv["last_message_time"]
                if time_diff.days > 0:
                    time_str = f"{time_diff.days}d ago"
                elif time_diff.seconds > 3600:
                    time_str = f"{time_diff.seconds // 3600}h ago"
                elif time_diff.seconds > 60:
                    time_str = f"{time_diff.seconds // 60}m ago"
            
            result.append({
                "user_id": other_participant_id,
                "name": other_user["name"],
                "type": other_type,
                "last_message": conv.get("last_message", ""),
                "time": time_str,
                "unread": unread_count
            })
    
    return jsonify(result)

@app.route('/api/recommended-contacts')
def get_recommended_contacts():
    if 'student_id' in session:
        user_id = session['student_id']
        user_type = 'student'
        
        # Get current student's details
        student = students_collection.find_one({"_id": ObjectId(user_id)})
        
        if not student:
            return jsonify([])
            
        # Find alumni from the same university and department
        recommended = list(alumini_collection.find({
            "university_name": student["university_name"],
            "department": student["department"]
        }).limit(10))
        
        result = []
        for alumni in recommended:
            result.append({
                "id": str(alumni["_id"]),
                "name": alumni["name"],
                "department": alumni["department"],
                "type": "alumni"
            })
        
        return jsonify(result)
        
    elif 'alumni_id' in session:
        user_id = session['alumni_id']
        user_type = 'alumni'
        
        # Get current alumni's details
        alumni = alumini_collection.find_one({"_id": ObjectId(user_id)})
        
        if not alumni:
            return jsonify([])
            
        # Find students from the same university and department
        recommended = list(students_collection.find({
            "university_name": alumni["university_name"],
            "department": alumni["department"]
        }).limit(10))
        
        result = []
        for student in recommended:
            result.append({
                "id": str(student["_id"]),
                "name": student["name"],
                "department": student["department"],
                "type": "student"
            })
        
        return jsonify(result)
    
    return jsonify([])

@app.route('/api/messages/<recipient_id>')
def get_messages(recipient_id):
    if 'student_id' in session:
        user_id = session['student_id']
    elif 'alumni_id' in session:
        user_id = session['alumni_id']
    else:
        return jsonify([])
    
    # Find or create conversation
    conversation = conversations_collection.find_one({
        "participants": {"$all": [ObjectId(user_id), ObjectId(recipient_id)]}
    })
    
    if not conversation:
        return jsonify([])
    
    # Get messages
    messages = list(messages_collection.find({
        "conversation_id": conversation["_id"]
    }).sort("timestamp", pymongo.ASCENDING))
    
    # Mark messages as read
    messages_collection.update_many({
        "conversation_id": conversation["_id"],
        "sender_id": ObjectId(recipient_id),
        "read": False
    }, {"$set": {"read": True}})
    
    # Get sender names
    result = []
    for msg in messages:
        sender_id = msg["sender_id"]
        
        # Find sender
        if str(sender_id) == user_id:
            sender_name = session.get('student_name') if 'student_id' in session else session.get('alumni_name')
        else:
            if 'student_id' in session:
                sender = alumini_collection.find_one({"_id": sender_id})
            else:
                sender = students_collection.find_one({"_id": sender_id})
            sender_name = sender["name"] if sender else "Unknown"
        
        # Format time
        time_str = "Just now"
        time_diff = datetime.now() - msg["timestamp"]
        if time_diff.days > 0:
            time_str = f"{time_diff.days}d ago"
        elif time_diff.seconds > 3600:
            time_str = f"{time_diff.seconds // 3600}h ago"
        elif time_diff.seconds > 60:
            time_str = f"{time_diff.seconds // 60}m ago"
        
        result.append({
            "id": str(msg["_id"]),
            "sender_id": str(sender_id),
            "sender_name": sender_name,
            "content": msg["content"],
            "time": time_str
        })
    
    return jsonify(result)