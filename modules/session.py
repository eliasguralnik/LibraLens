import time
import uuid
from server import database


sessions = {}


def create_session(client_socket):
    session_id = str(uuid.uuid4())
    session = {
        "session_id": session_id,
        "client_socket": client_socket,
        "created_at": time.time(),
        "last_activity": time.time(),
        "authenticated": False,
        "username": None
    }
    sessions[session_id] = session

    print(sessions)
    database.create_sessions_json(session)
    return session_id


def update_session(session_id, username):
    sessions[session_id] = {
        "last_activity": time.time(),
        "authenticated": True,
        "username": username
    }
    print(sessions)
    database.update_session_json(session_id, username)


def unauthenticated_session(session_id):

    sessions[session_id] = {
        "last_activity": time.time(),
        "authenticated": False
    }
    print(sessions)
    database.unauthenticated_session_json(session_id)
