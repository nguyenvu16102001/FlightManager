from flightmanager import app, db
from flightmanager.utils import Account
from flask import redirect
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose
from flask_login import current_user, logout_user


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated


class AuthenticatedBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        logout_user()

        return redirect('/admin')


admin = Admin(app=app, name='Trang quan tri', template_mode='bootstrap4')
admin.add_views(AuthenticatedModelView(Account, db.session, name='Tài Khoản'))
admin.add_views(LogoutView(name='Đăng Xuất'))