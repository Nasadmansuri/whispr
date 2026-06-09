from django.contrib import admin
from .models import Confession, Vote, Report, Comment, Board, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_banned', 'ban_reason']
    list_filter = ['is_banned']
    actions = ['ban_users', 'unban_users']

    def ban_users(self, request, queryset):
        queryset.update(is_banned=True)
    ban_users.short_description = '🔨 Ban selected users'

    def unban_users(self, request, queryset):
        queryset.update(is_banned=False, ban_reason='')
    unban_users.short_description = '✅ Unban selected users'

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'member_count', 'confession_count', 'created_at']

@admin.register(Confession)
class ConfessionAdmin(admin.ModelAdmin):
    list_display = ['author', 'board', 'is_anonymous', 'mood', 'posted_at']
    list_filter = ['is_anonymous', 'mood', 'board']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'confession', 'reason', 'reviewed', 'created_at']
    list_filter = ['reason', 'reviewed']
    actions = ['mark_reviewed']

    def mark_reviewed(self, request, queryset):
        queryset.update(reviewed=True)
    mark_reviewed.short_description = 'Mark selected reports as reviewed'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'is_anonymous', 'confession', 'posted_at']
    list_filter = ['is_anonymous']
    