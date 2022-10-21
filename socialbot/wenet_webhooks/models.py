from django.db import models

# Create your models here.

class User(models.Model):
    id = models.PositiveBigIntegerField('ID', primary_key=True)
    telegram_id = models.PositiveBigIntegerField('telegram ID', unique=True, default=0)
    name = models.CharField(max_length=50)
    language = models.CharField(max_length=5) # GR, TR
    access_token = models.CharField(max_length=128, default="")
    refresh_token = models.CharField(max_length=128, default="")

    def __str__(self) -> str:
        return f'ID: {self.id}, Telegram ID: {self.telegram_id}, Name: {self.name}.'

class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.JSONField('question')
    task_id = models.CharField(max_length=128, default="", unique=True)
    solved = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.content}, was solved: {self.solved}, by {self.user}'

class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.JSONField('answer')

    def __str__(self) -> str:
        return f'{self.content} by {self.user} on {self.question}'
class Best_Answer(models.Model):
    question = models.OneToOneField(
        Question,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.answer.__str__())

# class OnboardingQA(models.Model):
#     GENDERS = [
#         ('M', 'Male'),
#         ('F', 'Female'),
#         ('NB', 'Non Binary'),
#     ]
#     HOBBIES = [
#         ('M', 'Male'),
#         ('F', 'Female'),
#         ('NB', 'Non Binary'),
#     ]
#     AGEGROUPS = [
#         ('A', '18-24'),
#         ('B', '24-30'),
#         ('C', '30+'),
#     ]
#     FREQUENCY = [
#         ('low', '1-2 times a week'),
#         ('medium', '1-2 times a month'),
#         ('high', '1-2 times a year'),
#     ]
#     STUDIES = [
#         ('A', 'Engineering'),
#         ('B', 'Medicine'),
#         ('C', 'other'),
#     ]
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     gender_question = models.CharField(choices=GENDERS)
#     study_background_question=models.CharField(choices=STUDIES)
#     hobbies_question = models.MultipleChoiceField(choices=HOBBIES)
#     age_group_question = models.CharField(choices=AGEGROUPS)
#     culture_interaction_question = models.CharField(choices=AGEGROUPS)

