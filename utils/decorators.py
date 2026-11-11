from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def role_required(*roles):

    def decorator(view_function):

        @wraps(view_function)
        @login_required
        def wrapped_view(*args, **kwargs):

            if current_user.role not in roles:
                abort(403)

            return view_function(
                *args,
                **kwargs
            )

        return wrapped_view

    return decorator


def patient_required(view_function):
    return role_required("patient")(view_function)


def doctor_required(view_function):
    return role_required("doctor")(view_function)


def admin_required(view_function):
    return role_required("admin")(view_function)