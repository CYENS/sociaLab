from django.db import models

# Create your models here.

class User(models.Model):
    # username = models.CharField()
    id = models.PositiveBigIntegerField('ID', primary_key=True)
    telegram_id = models.PositiveBigIntegerField('telegram ID', unique=True, default=0)
    name = models.CharField(max_length=50)
    language = models.CharField(max_length=5) # GR, TR
    access_token = models.CharField(max_length=128, default="")
    refresh_token = models.CharField(max_length=128, default="")

    # class Meta:
    #     unique_together = ['id', 'telegram_id']

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