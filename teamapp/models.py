from django.db import models

class Hit_and_blow_PlayerScore(models.Model):
    username = models.CharField(max_length=255, unique=True)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.username

class SugorokuRoom(models.Model):
    """双六ゲームのルーム情報"""
    name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name