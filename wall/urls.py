from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('post/', views.post_confession, name='post'),
    path('delete/<int:confession_id>/', views.delete_confession, name='delete'),
    path('vote/<int:confession_id>/<int:value>/', views.vote, name='vote'),
    path('react/<int:confession_id>/<str:emoji>/', views.react, name='react'),
    path('report/<int:confession_id>/', views.report, name='report'),
    path('confession/<int:confession_id>/', views.confession_detail, name='confession_detail'),
    path('confession/<int:confession_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('boards/create/', views.create_board, name='create_board'),
    path('boards/join/<str:board_name>/', views.join_board, name='join_board'),
    path('b/<str:board_name>/', views.board_detail, name='board_detail'),
    path('verify-email/<uidb64>/<path:token>/', views.verify_email, name='verify_email'),
    path('search/', views.search, name='search'),
    path('trending/', views.trending, name='trending'),
]