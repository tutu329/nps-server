"""nps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
# from app_nps import views
from app_chatgpt import chatgpt_views
from app_chatgpt import redis_monitor

urlpatterns = [
    # path('', chatgpt_views.index_test),
    # path('nps_io', views.nps_io),
    # path('upload', views.upload_file),
    # path('phaser_io', views.phaser_io),

    path('monitor', redis_monitor.monitor),
    path('monitor/', redis_monitor.monitor),
    path('pull_monitor_data', redis_monitor.pull_monitor_data),
    path('pull_monitor_data/', redis_monitor.pull_monitor_data),

    path('chatgpt_sync', chatgpt_views.chatgpt_sync),
    path('chatgpt_sync/', chatgpt_views.chatgpt_sync),
    path('start_chatgpt_stream', chatgpt_views.start_chatgpt_stream),
    path('start_chatgpt_stream/', chatgpt_views.start_chatgpt_stream),
    path('get_chatgpt_stream_chunk', chatgpt_views.get_chatgpt_stream_chunk),
    path('get_chatgpt_stream_chunk/', chatgpt_views.get_chatgpt_stream_chunk),
    path('user_request_started', chatgpt_views.user_request_started),
    path('user_request_started/', chatgpt_views.user_request_started),
    path('user_start_chatgpt_stream', chatgpt_views.user_start_chatgpt_stream),
    path('user_start_chatgpt_stream/', chatgpt_views.user_start_chatgpt_stream),
    path('user_get_chatgpt_stream_chunk', chatgpt_views.user_get_chatgpt_stream_chunk),
    path('user_get_chatgpt_stream_chunk/', chatgpt_views.user_get_chatgpt_stream_chunk),
    path('get_role_template_list', chatgpt_views.get_role_template_list),
    path('get_role_template_list/', chatgpt_views.get_role_template_list),

    path('user_set_vip', chatgpt_views.user_set_vip),
    path('user_set_vip/', chatgpt_views.user_set_vip),
    path('user_set_prompt', chatgpt_views.user_set_prompt),
    path('user_set_prompt/', chatgpt_views.user_set_prompt),
    path('user_clear_role_memory', chatgpt_views.user_clear_role_memory),
    path('user_clear_role_memory/', chatgpt_views.user_clear_role_memory),
    path('user_get_chat_list', chatgpt_views.user_get_chat_list),
    path('user_get_chat_list/', chatgpt_views.user_get_chat_list),
    path('user_clear_chat_list', chatgpt_views.user_clear_chat_list),
    path('user_clear_chat_list/', chatgpt_views.user_clear_chat_list),
    path('user_cancel_current_response', chatgpt_views.user_cancel_current_response),
    path('user_cancel_current_response/', chatgpt_views.user_cancel_current_response),

    path('db_update_user_info', chatgpt_views.db_update_user_info),
    path('db_update_user_info/', chatgpt_views.db_update_user_info),
    path('db_reset_role_parameters', chatgpt_views.db_reset_role_parameters),
    path('db_reset_role_parameters/', chatgpt_views.db_reset_role_parameters),
    path('db_update_role_data', chatgpt_views.db_update_role_data),
    path('db_update_role_data/', chatgpt_views.db_update_role_data),
    path('db_update_role_parameters', chatgpt_views.db_update_role_parameters),
    path('db_update_role_parameters/', chatgpt_views.db_update_role_parameters),
    path('db_get_server_role_config', chatgpt_views.db_get_server_role_config),
    path('db_get_server_role_config/', chatgpt_views.db_get_server_role_config),
    path('db_get_server_user_config', chatgpt_views.db_get_server_user_config),
    path('db_get_server_user_config/', chatgpt_views.db_get_server_user_config),
    path('user_update_current_role', chatgpt_views.user_update_current_role),
    path('user_update_current_role/', chatgpt_views.user_update_current_role),
    path('pay_success_callback', chatgpt_views.pay_success_callback),
    path('pay_success_callback/', chatgpt_views.pay_success_callback),
    path('pay_query', chatgpt_views.pay_query),
    path('pay_query/', chatgpt_views.pay_query),
    path('pay', chatgpt_views.pay),
    path('pay/', chatgpt_views.pay),
    path('email_verify_page', chatgpt_views.email_verify_page),
    path('email_verify_page/', chatgpt_views.email_verify_page),
    path('user_login', chatgpt_views.user_login),
    path('user_login/', chatgpt_views.user_login),
    path('db_user_login', chatgpt_views.db_user_login),
    path('db_user_login/', chatgpt_views.db_user_login),
    path('db_user_has_logined', chatgpt_views.db_user_has_logined),
    path('db_user_has_logined/', chatgpt_views.db_user_has_logined),
    path('db_get_user_data', chatgpt_views.db_get_user_data),
    path('db_get_user_data/', chatgpt_views.db_get_user_data),
    path('db_get_user_and_roles', chatgpt_views.db_get_user_and_roles),
    path('db_get_user_and_roles/', chatgpt_views.db_get_user_and_roles),
    path('', chatgpt_views.index_test),
    path('/', chatgpt_views.index_test),


    path('web_search', chatgpt_views.web_search),
    path('web_search/', chatgpt_views.web_search),

    path('mac_console_ask_server', chatgpt_views.mac_console_ask_server),
    path('mac_console_ask_server/', chatgpt_views.mac_console_ask_server),

    path('gpu_llm_proxy', chatgpt_views.gpu_llm_proxy),
    path('gpu_llm_proxy/', chatgpt_views.gpu_llm_proxy),

    path('gpu_sd_proxy', chatgpt_views.gpu_sd_proxy),
    path('gpu_sd_proxy/', chatgpt_views.gpu_sd_proxy),


    # path('chatgpt', views.chatgpt),
    # path('chatgpt/', views.chatgpt),

    path('admin/', admin.site.urls),
]
