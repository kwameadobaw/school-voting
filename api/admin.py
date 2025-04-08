from django.contrib import admin
from .models import Student, Position, Candidate, Vote

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'has_voted')
    search_fields = ('student_id', 'name')

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'votes')
    list_filter = ('position',)

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('student', 'position', 'candidate', 'timestamp')
    list_filter = ('position', 'timestamp')