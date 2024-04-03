
#  Create superuser by call function or something (or database update)

# @app.on_event('startup')
# async def populate_admin():
#     if "admin" not in await User.all():
#         test_user_admin = await User.create(
#             'full_name': 'admin',
#             'email': 'admin@com.com'
#              'phone': '+79999999999'
#             'password': hash(config.ADMIN_PASS)
#         )
#           test_user_admin.is_staff = True
#            test_user_admin.is_superuser = True
#            await test_user_admin.save()
#
#  or
# @app.on_event('startup')
# async def populate_admin():
#    user = await User.filter(full_name='admin').first():
#    if user:
#       if not user.is_superuser:
#           user.is_staff = True
#           user.is_superuser = True
#           await user.save()
#

#  More tests (100% don't need)(update user don't work cause jwt have email field - email=constant)
#  Test directory (remember path import)??
#  Output must be same serializer (return Status or Pydantic obj not obj)
#  Router url must be same style
#  What can I use for input the pydantic data or the url params
#  More Models for sale's logic (Basket??)
#  Pydantic response everywhere (orm_mode = True??)
#  CBV??
#  Readme update more
#  requirements.txt rework (delete unused)
#  config rework (delete unused)
#  update field for product don't work?
#  All english
#  Need deploy?
#
