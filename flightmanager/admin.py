from flightmanager import app, db
from flightmanager.models import Account, User, Employee, UserRole, Flight, Schedule, TicketPrice, SeatClass, Regulations
from flask import redirect, request
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_login import current_user, logout_user
import utils


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


class StatsView(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        month = request.args.get('month')
        year = request.args.get('year')
        sales_starts = utils.sales_stats(month=month, year=year)
        quantity_starts = utils.quantity_stats(month=month, year=year)
        total = utils.total_sales(month=month, year=year)
        return self.render('admin/stats.html',
                           sales_starts=sales_starts, quantity_starts=quantity_starts, total=total)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


admin = Admin(app=app, name='Trang quan tri', template_mode='bootstrap4')
admin.add_views(AuthenticatedModelView(Account, db.session, name='Tài Khoản'))
admin.add_views(AuthenticatedModelView(User, db.session, name='Người Dùng'))
admin.add_views(AuthenticatedModelView(Employee, db.session, name='Nhân Viên'))
admin.add_views(AuthenticatedModelView(Schedule, db.session, name='Tuyến bay'))
admin.add_views(AuthenticatedModelView(Flight, db.session, name='Chuyến Bay'))
admin.add_views(AuthenticatedModelView(SeatClass, db.session, name='Bảng Hạng Vé'))
admin.add_views(AuthenticatedModelView(TicketPrice, db.session, name='Bảng Đơn Giá Vé'))
admin.add_views(AuthenticatedModelView(Regulations, db.session, name='Quy Định'))
admin.add_view(StatsView(name='Thống kê báo cáo'))
admin.add_views(LogoutView(name='Đăng Xuất'))