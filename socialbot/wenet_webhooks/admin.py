from django.contrib import admin

# Register your models here.
from .models import User, Question, Answer,Best_Answer

admin.site.register(User)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Best_Answer)