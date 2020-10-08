from functools import wraps

def login_required(f):
    """ Decorator to require login """
    @wraps(f)
    def decorated_functions(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_functions
