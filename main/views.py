import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse


from main.forms import CreateVotingForm, EditProfileForm
from main.forms import RegistrationForm, EditVotingForm
from main.models import VoteFact, VoteVariant, Voting, User, VoteFactVariant


def get_menu_context():
    return [
        {'url_name': 'index', 'name': 'Главная'},
        {'url_name': 'voting_list', 'name': 'Список голосований'},
        {'url_name': 'voting_add', 'name': 'Добавить голосование'},
    ]


def get_base_context(pagename):
    return {
        'pagename': pagename,
        'menu': get_menu_context()
    }


def index_page(request):
    context = get_base_context('Главная')
    context['author'] = 'Andrew'
    context['pages'] = 4
    return render(request, 'pages/index.html', context)


@login_required
def voting_edit_page(request, id):
    voting = get_object_or_404(Voting, id=id)
    variants = VoteVariant.objects.filter(voting=voting)

    if not (request.user.is_staff or request.user == voting.author):
        messages.error(request, "Голосование может редактировать только его автор или модератор", extra_tags='alert-danger')

    context = {
        'menu': get_menu_context(),
        'voting': voting,
        'variants': variants,
        'pagename': 'Редактирование голосования',
        'form': EditVotingForm()
    }

    if request.method == "POST":
        form = EditVotingForm(request.POST)

        if form.is_valid():

            voting.title = form.cleaned_data['title']
            voting.description = form.cleaned_data['description']
            voting.published_at = datetime.datetime.now()
            voting.save()

            return redirect(reverse('voting_public', kwargs={'id': voting.id}))

        context['form'] = form
        context['count'] = len(variants)

    return render(request, 'pages/voting_edit.html', context)


def voting_list_page(request):
    context = get_base_context('Список голосований')
    context['votings'] = Voting.objects.all().order_by('-published_at')
    return render(request, 'pages/list_vote.html', context)


def profile_page(request):
    context = {
        'menu': get_menu_context(),
        'pagename': 'Профиль',
        'votings_count': Voting.objects.filter(author=request.user).count(),
        'votefact_count': VoteFact.objects.filter(user=request.user).count()
    }
    return render(request, 'pages/profile.html', context)


def profile_edit_page(request, id):
    user = get_object_or_404(User, id=id)
    context = {
        'menu': get_menu_context(),
        'pagename': ' Редактирование профиля',
        'votings_count': Voting.objects.filter(author=request.user).count(),
        'votefact_count': VoteFact.objects.filter(user=request.user).count()
    }

    if request.method == "POST":
        form = EditProfileForm(request.POST)

        if form.is_valid():
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.save()

        return redirect('profile')
    return render(request, 'pages/profile_edit.html', context)


def voting_page(request):
    context = get_base_context('Голосование - детали')
    records_voting = []
    records_votevariants = []
    records = []
    if request.user.is_authenticated:
        records_voting = Voting.objects.filter(author=request.user).last()
        records = VoteVariant.objects.filter(voting=records_voting)

    for i in records:
        records_votevariants.append(i.description)

    context.update({
        'description': records_voting.description,
        'author': records_voting.author,
        'variants': records_votevariants,
        'type': records_voting.type,
        'publication_date': records_voting.published_at,
        'menu': get_menu_context()
    })

    return render(request, '', context)  # Внести название файла


def get_template_name_by_voting_type(voting):
    names = {
        1: 'one_of_many.html',
        2: 'some_of_many.html',
        3: 'discrete.html'
    }
    return f'pages/voting/public/{names[voting.type]}'


@login_required
def voting_public_page(request, id):
    context = get_base_context('Оставление голоса')
    voting = get_object_or_404(Voting, id=id)
    context['voting'] = voting

    if request.method == 'POST':
        try:
            variant_ids_list = request.POST.getlist('variant', [])
            variant_ids_list = [int(variant) for variant in variant_ids_list]
            voting.make_votefact(request.user, variant_ids_list)
            messages.success(request, "Вы успешно проголосовали", extra_tags='alert-success')
            return redirect(reverse('index'))
        except ValueError:
            messages.error(request, "Что-то пошло не так...", extra_tags='alert-danger')
        except PermissionError as ex:
            context['error'] = ex
            messages.error(request, "Вы уже оставляли свой голос в текущем голосовании", extra_tags='alert-info')
    return render(request, get_template_name_by_voting_type(voting), context)


@login_required
def voting_add_page(request):
    context = get_base_context('Добавление голосования')
    form = CreateVotingForm()
    context['form'] = form

    if request.method == "POST":
        form = CreateVotingForm(request.POST)

        if form.is_valid():

            count_variants = 0
            for key in request.POST.keys():
                if key.startswith('add_answer_'):
                    count_variants += 1
            factor = False if form.cleaned_data['type'] == 3 and count_variants > 2 else True

            if factor:
                voting = Voting(
                    title=form.cleaned_data['title'],
                    description=form.cleaned_data['description'],
                    type=form.cleaned_data['type'],
                    author=request.user,
                    published_at=datetime.datetime.now()
                )
                voting.save()

                for key in request.POST.keys():
                    if key.startswith('add_answer_'):
                        variant_str = request.POST[key]
                        variant_object = VoteVariant(
                            voting=voting,
                            description=variant_str
                        )
                        variant_object.save()

                return redirect(reverse('voting_public', kwargs={'id': voting.id}))
            else:
                messages.error(request, "В дискретном голосовании не может быть больше 2-х вариантов", extra_tags='alert-danger')

        context['form'] = form
    return render(request, 'pages/vote_add.html', context)


def registration_page(request):
    if request.user.is_authenticated:
        messages.error(request, "Залогиненный пользователь не может регистрироваться", extra_tags='alert-danger')

    context = {
        'pagename': 'Регистрация',
        'menu': get_menu_context()
    }
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.save()
            raw_pass = form.cleaned_data.get('password1')

            user = authenticate(username=user.username, password=raw_pass)
            login(request, user)
            return redirect(reverse('index'))
    else:
        form = RegistrationForm()
    context['form'] = form
    return render(request, 'registration/registration.html', context)


def complaint_page(request, id):
    if not request.user.is_authenticated:
        messages.error(request, "Незалогиненный пользователь не может отправлять жалобы!!!", extra_tags='alert-danger')
    voting = get_object_or_404(Voting, id=id)
    context = {
        'menu': get_menu_context(),
        'pagename': 'Добавление жалобы',
        'voting': voting,
        'user': request.user,
        'datetime': datetime.datetime.now()
    }

    return render(request, 'pages/complaint.html', context)


def variant_change(request, voting_id, variant_id):
    variant = get_object_or_404(VoteVariant, id=variant_id)
    if variant.voting.id != voting_id:
        messages.error(request, "Этот вариант не от этого голосования", extra_tags='alert-danger')
    if variant.voting.author != request.user and not request.user.is_staff:
        messages.error(request, "Только автор может редактировать варианты", extra_tags='alert-danger')

    if request.method == "POST":
        var_value = request.POST.get('add_answer')
        variant.description = var_value
        variant.save()

    return redirect(reverse('voting_edit', kwargs={'id': voting_id}))


def variant_delete(request, voting_id, variant_id):
    variant = get_object_or_404(VoteVariant, id=variant_id)
    if variant.voting.id != voting_id:
        messages.error(request, "Этот вариант не от этого голосования", extra_tags='alert-danger')
    if variant.voting.author != request.user and not request.user.is_staff:
        messages.error(request, "Только автор может удалять варианты", extra_tags='alert-danger')
    variant.delete()
    return redirect(reverse('voting_edit', kwargs={'id': voting_id}))

def voting_delete(request, id):
    voting = get_object_or_404(Voting, id=id)
    if voting.author.id != request.user.id and not request.user.is_staff or not request.user.is_authenticated:
        messages.error(request, "Только автор может удалять голосование", extra_tags='alert-danger')
    elif voting.author.id == request.user.id or request.user.is_staff and request.user.is_authenticated:
        voting.delete()
        messages.error(request, "Голосование удалено", extra_tags='alert-success')
    return redirect(reverse('voting_list'))


def view_vote_page(request, id):
    voting = get_object_or_404(Voting, id=id)

def voting_results_page(request, id):
    context = {}
    variants = VoteVariant.objects.filter(voting=id)
    voting = get_object_or_404(Voting, id=id)
    count = []
    sum = 0
    for i in range(len(variants)):
        count.append(len(VoteFactVariant.objects.filter(variant_id=variants[i].id)))
        sum += len(VoteFactVariant.objects.filter(variant_id=variants[i].id))
    for i in range(len(variants)):
        if sum!=0:
            variants[i].procent = int(count[i] / sum * 100)
            variants[i].count = int(count[i])
        else:
            variants[i].procent = 0
            variants[i].count = 0
    #variant.procent - процент проголосовавших за вариант
    #variant.count - количество проголосовавших за варинт
    context = {
        'pagename': 'Просмотр результатов голосования',
        'menu': get_menu_context(),
        'voting': voting,
        'user': request.user,
        'variants': variants
    }
    return render(request, 'pages/voting_results.html', context)
