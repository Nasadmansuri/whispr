from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    following = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='followers')
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(blank=True)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

    def follower_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()


class Board(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boards')
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, blank=True, related_name='joined_boards')

    def __str__(self):
        return f"b/{self.name}"

    def member_count(self):
        return self.members.count()

    def confession_count(self):
        return self.confessions.count()


class Confession(models.Model):
    MOOD_CHOICES = [
        ('happy', '😊 Happy'),
        ('sad', '😢 Sad'),
        ('angry', '😠 Angry'),
    ]
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='confessions')
    board = models.ForeignKey(Board, on_delete=models.SET_NULL, null=True, blank=True, related_name='confessions')
    message = models.TextField()
    is_anonymous = models.BooleanField(default=True)
    mood = models.CharField(max_length=10, choices=MOOD_CHOICES, default='happy')
    posted_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='confessions/', null=True, blank=True)
    video = CloudinaryField('video', resource_type='video', null=True, blank=True)

    def __str__(self):
        name = 'Anonymous' if self.is_anonymous else self.author.username
        return f"{name}: {self.message[:40]}"

    def vote_score(self):
        return self.votes.filter(value=1).count() - self.votes.filter(value=-1).count()

    def upvote_count(self):
        return self.votes.filter(value=1).count()

    def downvote_count(self):
        return self.votes.filter(value=-1).count()

    def user_vote(self, user):
        v = self.votes.filter(user=user).first()
        return v.value if v else 0

    def reaction_summary(self, user=None):
        emojis = ['❤️', '😂', '😮', '😢', '😡']
        summary = []
        for emoji in emojis:
            count = self.reactions.filter(emoji=emoji).count()
            user_reacted = False
            if user and user.is_authenticated:
                user_reacted = self.reactions.filter(emoji=emoji, user=user).exists()
            summary.append({'emoji': emoji, 'count': count, 'user_reacted': user_reacted})
        return summary


class Vote(models.Model):
    confession = models.ForeignKey(Confession, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    value = models.IntegerField()

    class Meta:
        unique_together = ('confession', 'user')

    def __str__(self):
        return f"{self.user.username} voted {self.value} on #{self.confession.id}"


class Report(models.Model):
    REASON_CHOICES = [
        ('spam', '🚫 Spam'),
        ('harassment', '😡 Harassment'),
        ('hate', '💢 Hate Speech'),
        ('false', '❌ False Information'),
        ('other', '📝 Other'),
    ]
    confession = models.ForeignKey(Confession, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('confession', 'reporter')

    def __str__(self):
        return f"{self.reporter.username} reported #{self.confession.id} for {self.reason}"


class Comment(models.Model):
    confession = models.ForeignKey(Confession, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    posted_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        name = 'Anonymous' if self.is_anonymous else self.author.username
        return f"{name} on #{self.confession.id}: {self.body[:40]}"

    def top_level_replies(self):
        return self.replies.order_by('posted_at')

class Reaction(models.Model):
    EMOJI_CHOICES = [
        ('❤️', '❤️ Love'),
        ('😂', '😂 Haha'),
        ('😮', '😮 Wow'),
        ('😢', '😢 Sad'),
        ('😡', '😡 Angry'),
    ]
    confession = models.ForeignKey(Confession, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    emoji = models.CharField(max_length=10, choices=EMOJI_CHOICES)

    class Meta:
        unique_together = ('confession', 'user', 'emoji')

    def __str__(self):
        return f"{self.user.username} reacted {self.emoji} on #{self.confession.id}"


def get_karma(user):
    return sum(c.upvote_count() for c in Confession.objects.filter(author=user))