from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.contrib.auth.hashers import check_password
from .models import Student, Position, Candidate, Vote, Admin
import json
import os

def index(request):
    if 'student_id' in request.session:
        return redirect('voting')
    if 'admin_id' in request.session:
        return redirect('admin_dashboard')
    return render(request, 'index.html')

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        student_id = data.get('student_id')
        
        try:
            student = Student.objects.get(student_id=student_id)
            if student.has_voted:
                return JsonResponse({'status': 'error', 'message': 'You have already voted'})
            
            request.session['student_id'] = student_id
            request.session['student_name'] = student.name  # Make sure this line exists
            return JsonResponse({'status': 'success', 'redirect': '/voting/'})
        except Student.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid Student ID'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def admin_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        # Check if the credentials match the admin credentials
        admin_username = "admin"
        admin_password = "admin123"
        
        if username == admin_username and password == admin_password:
            request.session['admin_id'] = 1  # Using a simple ID since we don't have an admin model
            return JsonResponse({'status': 'success', 'redirect': '/admin_dashboard/'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def voting(request):
    if 'student_id' not in request.session:
        return redirect('index')
    
    student_id = request.session['student_id']
    
    # Get student name from session or fetch from database if not in session
    if 'student_name' not in request.session:
        try:
            student = Student.objects.get(student_id=student_id)
            student_name = student.name
            request.session['student_name'] = student_name  # Store it for future requests
        except Student.DoesNotExist:
            return redirect('index')
    else:
        student_name = request.session['student_name']
    
    # Get all positions
    positions = Position.objects.all()
    
    # Get positions the student has already voted for
    voted_positions = Vote.objects.filter(
        student__student_id=student_id
    ).values_list('position_id', flat=True)
    
    # Get the next position to vote for
    next_position = None
    for position in positions:
        if position.id not in voted_positions:
            next_position = position
            break
    
    # Calculate progress
    total_positions = positions.count()
    voted_count = len(voted_positions)
    progress_percentage = (voted_count / total_positions) * 100 if total_positions > 0 else 0
    
    context = {
        'student_id': student_id,
        'student_name': student_name,
        'positions': positions,
        'voted_positions': list(voted_positions),
        'next_position': next_position,
        'progress_percentage': progress_percentage,
        'total_positions': total_positions,
        'voted_count': voted_count
    }
    
    return render(request, 'voting.html', context)

@csrf_exempt
def get_candidates(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        position_id = data.get('position_id')
        
        try:
            position = Position.objects.get(id=position_id)
            candidates = Candidate.objects.filter(position=position)
            
            candidates_list = []
            for candidate in candidates:
                candidate_data = {
                    'id': candidate.id,
                    'name': candidate.name,
                }
                if candidate.photo:
                    candidate_data['photo_url'] = candidate.photo.url
                candidates_list.append(candidate_data)
                
            return JsonResponse({'status': 'success', 'candidates': candidates_list})
        except Position.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Position not found'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def submit_vote(request):
    if request.method == 'POST':
        if 'student_id' not in request.session:
            return JsonResponse({'status': 'error', 'message': 'Not logged in'})
        
        data = json.loads(request.body)
        position_id = data.get('position_id')
        candidate_id = data.get('candidate_id')
        
        try:
            student = Student.objects.get(student_id=request.session['student_id'])
            position = Position.objects.get(id=position_id)
            candidate = Candidate.objects.get(id=candidate_id)
            
            # Check if student has already voted for this position
            if Vote.objects.filter(student=student, position=position).exists():
                return JsonResponse({'status': 'error', 'message': 'You have already voted for this position'})
            
            # Create vote
            Vote.objects.create(student=student, position=position, candidate=candidate)
            
            # Increment candidate votes
            candidate.votes += 1
            candidate.save()
            
            # Check if student has voted for all positions
            voted_positions = Vote.objects.filter(student=student).count()
            total_positions = Position.objects.count()
            
            if voted_positions == total_positions:
                student.has_voted = True
                student.save()
                return JsonResponse({
                    'status': 'success', 
                    'message': 'Thank you for voting!', 
                    'complete': True,
                    'progress': 100
                })
            
            # Calculate new progress
            progress = (voted_positions / total_positions) * 100
            
            # Get next position
            remaining_positions = Position.objects.exclude(
                id__in=Vote.objects.filter(student=student).values_list('position_id', flat=True)
            )
            next_position = None
            if remaining_positions.exists():
                next_position = {
                    'id': remaining_positions.first().id,
                    'title': remaining_positions.first().title
                }
            
            return JsonResponse({
                'status': 'success', 
                'message': 'Vote submitted successfully',
                'progress': progress,
                'next_position': next_position
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def admin_dashboard(request):
    if 'admin_id' not in request.session:
        return redirect('index')
    
    positions = Position.objects.all()
    position_data = []
    
    for position in positions:
        candidates = Candidate.objects.filter(position=position)
        candidate_data = []
        
        for candidate in candidates:
            vote_count = candidate.votes
            candidate_info = {
                'name': candidate.name,
                'votes': vote_count,
                'photo': candidate.photo.url if candidate.photo else None
            }
            candidate_data.append(candidate_info)
        
        position_info = {
            'title': position.title,
            'candidates': candidate_data
        }
        position_data.append(position_info)
    
    # Get voting statistics
    total_students = Student.objects.count()
    voted_students = Student.objects.filter(has_voted=True).count()
    voting_percentage = (voted_students / total_students) * 100 if total_students > 0 else 0
    
    context = {
        'positions': position_data,
        'total_students': total_students,
        'voted_students': voted_students,
        'voting_percentage': voting_percentage
    }
    
    return render(request, 'admin_dashboard.html', context)

def logout(request):
    if 'student_id' in request.session:
        del request.session['student_id']
        del request.session['student_name']
    if 'admin_id' in request.session:
        del request.session['admin_id']
    return redirect('index')