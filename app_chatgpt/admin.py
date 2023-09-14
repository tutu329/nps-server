from django.contrib import admin

from .models import UserProfile, Role, Payment_Record

class userprofile_model_admin(admin.ModelAdmin):
    list_display = (
        'user',
        'nickname',
        'gender',
        'user_level',
        'vip_expired',
        'vip_start_time',
        'vip_days',
        'current_vip_type',
        'current_role_id',
        'gpt4_invoke_num_left_today',
        'gpt3_invoke_num_left_today',
        'user_api_key'
    )

class role_model_admin(admin.ModelAdmin):
    list_display = (
        'user_profile',
        'role_id',
        'nickname',
        'description',
        'temperature',
        'presence_penalty',
        'frequency_penalty',
        'prompt',
        'active_talk_prompt',
        'chat_list',
    )

class payment_record_model_admin(admin.ModelAdmin):
    list_display = (
        'user_profile',
        'order_id',
        'payment_type',
        'amount',
        'time',
    )

admin.site.register(
    UserProfile,
    userprofile_model_admin
)
admin.site.register(
    Role,
    role_model_admin
)
admin.site.register(
    Payment_Record,
    payment_record_model_admin
)
