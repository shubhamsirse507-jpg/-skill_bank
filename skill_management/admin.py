from django.contrib import admin
from .models import SkillCategory, Skill, SkillCertificate

@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'status', 'is_active', 'created_at')
    list_filter = ('status', 'is_active')
    search_fields = ('category_name', 'description')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'skill_type', 'level', 'status', 'is_featured', 'created_at')
    list_filter = ('skill_type', 'level', 'status', 'is_featured')
    search_fields = ('title', 'description', 'user__username')

@admin.register(SkillCertificate)
class SkillCertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'skill_title', 'student', 'teacher', 'grade_performance', 'issued_at')
    list_filter = ('grade_performance', 'issued_at')
    search_fields = ('certificate_id', 'skill_title', 'student__username', 'teacher__username')