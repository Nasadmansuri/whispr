from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from .models import Confession, Vote, Report, Comment, UserProfile, Board, get_karma
from .forms import ConfessionForm, BoardForm
from django.core.paginator import Paginator

def is_user_banned(user):
    try:
        return user.profile.is_banned
    except UserProfile.DoesNotExist:
        return False


def is_email_verified(user):
    try:
        return user.profile.email_verified
    except UserProfile.DoesNotExist:
        return False


def get_post_count_last_hour(user):
    one_hour_ago = timezone.now() - timedelta(hours=1)
    return Confession.objects.filter(author=user, posted_at__gte=one_hour_ago).count()


from django.core.paginator import Paginator

def home(request):
    sort = request.GET.get('sort', 'new')
    confessions = Confession.objects.all()

    if sort == 'new':
        confessions = confessions.order_by('-posted_at')
    elif sort == 'top':
        confessions = sorted(confessions, key=lambda c: c.vote_score(), reverse=True)
    elif sort == 'hot':
        cutoff = timezone.now() - timedelta(hours=24)
        recent = confessions.filter(posted_at__gte=cutoff)
        older = confessions.filter(posted_at__lt=cutoff)
        recent_sorted = sorted(recent, key=lambda c: c.vote_score(), reverse=True)
        older_sorted = sorted(older, key=lambda c: c.vote_score(), reverse=True)
        confessions = list(recent_sorted) + list(older_sorted)

    paginator = Paginator(confessions, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    boards = Board.objects.all()
    return render(request, 'home.html', {
        'confessions': page_obj,
        'sort': sort,
        'boards': boards,
        'page_obj': page_obj,
    })

def trending(request):
    cutoff = timezone.now() - timedelta(hours=48)
    recent_confessions = Confession.objects.filter(posted_at__gte=cutoff)
    scored = []
    for c in recent_confessions:
        score = (c.upvote_count() * 2) + c.comments.count()
        scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    confessions = [c for score, c in scored[:10]]
    return render(request, 'trending.html', {'confessions': confessions})

def search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results = Confession.objects.filter(
            message__icontains=query
        ).order_by('-posted_at')
    return render(request, 'search.html', {
        'query': query,
        'results': results,
    })

def board_detail(request, board_name):
    board = get_object_or_404(Board, name=board_name)
    sort = request.GET.get('sort', 'new')
    confessions = Confession.objects.filter(board=board)

    if sort == 'new':
        confessions = confessions.order_by('-posted_at')
    elif sort == 'top':
        confessions = sorted(confessions, key=lambda c: c.vote_score(), reverse=True)
    elif sort == 'hot':
        cutoff = timezone.now() - timedelta(hours=24)
        recent = list(confessions.filter(posted_at__gte=cutoff))
        older = list(confessions.filter(posted_at__lt=cutoff))
        recent_sorted = sorted(recent, key=lambda c: c.vote_score(), reverse=True)
        older_sorted = sorted(older, key=lambda c: c.vote_score(), reverse=True)
        confessions = recent_sorted + older_sorted

    is_member = False
    if request.user.is_authenticated:
        is_member = board.members.filter(id=request.user.id).exists()

    return render(request, 'board.html', {
        'board': board,
        'confessions': confessions,
        'sort': sort,
        'is_member': is_member,
    })


@login_required
def create_board(request):
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.created_by = request.user
            board.save()
            board.members.add(request.user)
            return redirect('board_detail', board_name=board.name)
    else:
        form = BoardForm()
    return render(request, 'create_board.html', {'form': form})


@login_required
def join_board(request, board_name):
    board = get_object_or_404(Board, name=board_name)
    if board.members.filter(id=request.user.id).exists():
        board.members.remove(request.user)
    else:
        board.members.add(request.user)
    return redirect('board_detail', board_name=board_name)


def confession_detail(request, confession_id):
    confession = get_object_or_404(Confession, id=confession_id)
    comments = confession.comments.filter(parent=None).order_by('posted_at')
    already_reported = False
    if request.user.is_authenticated:
        already_reported = Report.objects.filter(confession=confession, reporter=request.user).exists()
    return render(request, 'confession.html', {
        'confession': confession,
        'comments': comments,
        'already_reported': already_reported,
        'sort': request.GET.get('sort', 'new'),
    })


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_profile, created = UserProfile.objects.get_or_create(user=profile_user)
    confessions = Confession.objects.filter(author=profile_user).order_by('-posted_at')
    total_confessions = confessions.count()
    total_upvotes = sum(c.upvote_count() for c in confessions)
    total_comments = Comment.objects.filter(author=profile_user).count()
    karma = get_karma(profile_user)
    public_confessions = confessions.filter(is_anonymous=False)

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        my_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        is_following = my_profile.following.filter(user=profile_user).exists()

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'user_profile': user_profile,
        'confessions': public_confessions,
        'total_confessions': total_confessions,
        'total_upvotes': total_upvotes,
        'total_comments': total_comments,
        'karma': karma,
        'is_following': is_following,
    })


@login_required
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    if request.user == target_user:
        return redirect('profile', username=username)
    my_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    target_profile, _ = UserProfile.objects.get_or_create(user=target_user)
    if my_profile.following.filter(user=target_user).exists():
        my_profile.following.remove(target_profile)
    else:
        my_profile.following.add(target_profile)
    return redirect('profile', username=username)


@login_required
def upload_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_profile.avatar = request.FILES['avatar']
        user_profile.save()
    return redirect('profile', username=request.user.username)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = request.POST.get('email', '').strip()
            if email:
                user.email = email
                user.save()
            user_profile, _ = UserProfile.objects.get_or_create(user=user)

            if email:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                token_encoded = urlsafe_base64_encode(force_bytes(token))
                uid_str = uid if isinstance(uid, str) else uid.decode()
                token_str = token_encoded if isinstance(token_encoded, str) else token_encoded.decode()
                token_str = token_str.rstrip('=')
                verify_url = f"https://whisprapp.pythonanywhere.com/verify-email/{uid_str}/{token_str}/"
                print(f"\n\nVERIFY URL: {verify_url}\n\n")
                send_mail(
                    subject='Verify your ChupChapBaas email',
                    message=f'Verify link: {verify_url}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
                return render(request, 'email_verify_sent.html', {'email': email})

            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        padding = 4 - len(token) % 4
        token_padded = token + '=' * (padding % 4)
        real_token = force_str(urlsafe_base64_decode(token_padded))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        real_token = None

    if user and real_token and default_token_generator.check_token(user, real_token):
        user_profile, _ = UserProfile.objects.get_or_create(user=user)
        user_profile.email_verified = True
        user_profile.save()
        login(request, user)
        return render(request, 'email_verified.html', {'success': True})
    return render(request, 'email_verified.html', {'success': False})


@login_required
def post_confession(request):
    if is_user_banned(request.user):
        profile = UserProfile.objects.get(user=request.user)
        return render(request, 'banned.html', {'ban_reason': profile.ban_reason})

    RATE_LIMIT = 5
    post_count = get_post_count_last_hour(request.user)
    rate_limited = post_count >= RATE_LIMIT

    if request.method == 'POST':
        if rate_limited:
            form = ConfessionForm()
            return render(request, 'post.html', {
                'form': form,
                'rate_limited': True,
                'post_count': post_count,
                'rate_limit': RATE_LIMIT,
            })
        form = ConfessionForm(request.POST, request.FILES)
        if form.is_valid():
            confession = form.save(commit=False)
            confession.author = request.user
            confession.save()
            return redirect('home')
    else:
        form = ConfessionForm()

    return render(request, 'post.html', {
        'form': form,
        'rate_limited': rate_limited,
        'post_count': post_count,
        'rate_limit': RATE_LIMIT,
    })


@login_required
def delete_confession(request, confession_id):
    confession = get_object_or_404(Confession, id=confession_id)
    if confession.author == request.user:
        confession.delete()
    return redirect('home')


@login_required
def vote(request, confession_id, value):
    if is_user_banned(request.user):
        profile = UserProfile.objects.get(user=request.user)
        return render(request, 'banned.html', {'ban_reason': profile.ban_reason})
    confession = get_object_or_404(Confession, id=confession_id)
    existing = Vote.objects.filter(confession=confession, user=request.user).first()
    if existing:
        if existing.value == value:
            existing.delete()
        else:
            existing.value = value
            existing.save()
    else:
        Vote.objects.create(confession=confession, user=request.user, value=value)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def report(request, confession_id):
    confession = get_object_or_404(Confession, id=confession_id)
    already_reported = Report.objects.filter(confession=confession, reporter=request.user).exists()
    if request.method == 'POST' and not already_reported:
        reason = request.POST.get('reason')
        if reason:
            Report.objects.create(confession=confession, reporter=request.user, reason=reason)
        return redirect('home')
    return render(request, 'report.html', {
        'confession': confession,
        'already_reported': already_reported,
        'reason_choices': Report.REASON_CHOICES,
    })


@login_required
def add_comment(request, confession_id):
    if is_user_banned(request.user):
        profile = UserProfile.objects.get(user=request.user)
        return render(request, 'banned.html', {'ban_reason': profile.ban_reason})
    confession = get_object_or_404(Confession, id=confession_id)
    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        parent_id = request.POST.get('parent_id')
        parent = None
        if parent_id:
            parent = get_object_or_404(Comment, id=parent_id)
        if body:
            Comment.objects.create(
                confession=confession,
                author=request.user,
                body=body,
                is_anonymous=is_anonymous,
                parent=parent
            )
    return redirect('confession_detail', confession_id=confession_id)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    confession_id = comment.confession.id
    if comment.author == request.user:
        comment.delete()
    return redirect('confession_detail', confession_id=confession_id)
