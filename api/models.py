from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    has_voted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.student_id})"

class Position(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)  # Added for ordering positions in progress bar

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']  # Order positions by the order field

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='candidates')
    votes = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='candidate_photos/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.position.title}"

class Vote(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'position')
    
    def __str__(self):
        return f"{self.student.name} voted for {self.candidate.name} as {self.position.title}"

class Admin(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)  # In production, use proper password hashing
    
    def __str__(self):
        return self.username