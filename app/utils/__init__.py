from functools import wraps
from flask import session, flash
from flask.helpers import url_for
from werkzeug.utils import redirect

def login_is_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if( session.get('logged') is None ):
      flash("É necessário estar logado para ter acesso a essa funcionalidade!", "warning")
      
      return redirect(url_for("signin_suap"))
    
    return f(*args, **kwargs)
  
  return decorated_function
