import random, json, os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from collections import defaultdict
from django.contrib import messages
from .models import Jogador, Time, Jogo
from .forms import JogadorForm, TimeForm
from itertools import product
from django.db import models
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.decorators import login_required
import math

# Páginas de gestão agora exigem apenas usuário logado (não mais superusuário).

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    next_url = request.GET.get('next')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if next_url and next_url != "None" and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
                return redirect(next_url)

            return redirect('dashboard')

        else:
            messages.error(request, 'Usuário ou senha inválidos')

    return render(request, 'login.html', {'next': next_url})

def logout_view(request):
    logout(request)
    return redirect('dashboard')

# 🔒 Autocadastro removido: contas agora só são criadas pelos responsáveis
# do sistema, via /admin/ do Django (ou "python manage.py createsuperuser").

def root_redirect(request):
    return redirect('dashboard')

def dashboard(request):
    total_jogadores = Jogador.objects.count()
    total_times = Time.objects.count()
    return render(request, 'dashboard.html', {
        'total_jogadores': total_jogadores,
        'total_times': total_times
    })

@login_required
def listar_jogadores(request):
    jogadores = (
        Jogador.objects
        .select_related('time')
        .order_by('classificacao', 'nome')
    )
    return render(request, 'listar_jogadores.html', {
        'jogadores': jogadores
    })


def listar_times(request):
    times = Time.objects.all()
    return render(request, 'listar_times.html', {'times': times})


@login_required
def cadastrar_jogador(request):
    if request.method == 'POST':
        form = JogadorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_jogadores')
    else:
        form = JogadorForm()
    return render(request, 'cadastrar_jogador.html', {'form': form})


@login_required
def cadastrar_time(request):
    if request.method == 'POST':
        form = TimeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_times')
    else:
        form = TimeForm()
    return render(request, 'cadastrar_time.html', {'form': form})


@login_required
def editar_jogador(request, jogador_id):
    jogador = get_object_or_404(Jogador, id=jogador_id)
    if request.method == 'POST':
        form = JogadorForm(request.POST, instance=jogador)
        if form.is_valid():
            form.save()
            return redirect('listar_jogadores')
    else:
        form = JogadorForm(instance=jogador)
    return render(request, 'cadastrar_jogador.html', {'form': form, 'editando': True})


@login_required
def sortear_times(request):
    jogadores = list(Jogador.objects.all())
    times = list(Time.objects.all())

    if not jogadores or not times:
        return render(request, 'sorteador/resultado.html', {'erro': 'Cadastre jogadores e times antes de sortear.'})

    potes = defaultdict(list)
    for jogador in jogadores:
        potes[jogador.classificacao].append(jogador)

    num_times = len(times)
    for pote, lista in potes.items():
        if len(lista) < num_times:
            return render(request, 'sorteador/resultado.html', {
                'erro': f'Pote {pote} tem apenas {len(lista)} jogadores. São necessários {num_times}.'})

    MAX_TENTATIVAS = 100
    MARGEM_MAXIMA = 30

    for tentativa in range(MAX_TENTATIVAS):
        sorteio = {time.id: {'time': time, 'jogadores': [], 'overall': 0} for time in times}
        usado_por_time = {time.id: set() for time in times}
        sucesso = True

        for pote, jogadores_pote in potes.items():
            jogadores_disp = jogadores_pote[:]
            random.shuffle(jogadores_disp)

            for jogador in jogadores_disp:
                pesos, candidatos = [], []

                for time_id, info in sorteio.items():
                    if pote not in usado_por_time[time_id]:
                        peso = 1 / (info['overall'] + 1)
                        candidatos.append(time_id)
                        pesos.append(peso)

                if not candidatos:
                    sucesso = False
                    break

                time_escolhido = random.choices(candidatos, weights=pesos, k=1)[0]
                sorteio[time_escolhido]['jogadores'].append(jogador)
                sorteio[time_escolhido]['overall'] += jogador.overall
                usado_por_time[time_escolhido].add(pote)

            if not sucesso:
                break

        if not sucesso:
            continue

        overalls = [info['overall'] for info in sorteio.values()]
        margem = max(overalls) - min(overalls)

        if margem <= MARGEM_MAXIMA:
            break
    else:
        return render(request, 'sorteador/resultado.html', {
            'erro': f'Não foi possível gerar um sorteio com margem menor que {MARGEM_MAXIMA} após {MAX_TENTATIVAS} tentativas.'})

    aviso = None
    if margem > MARGEM_MAXIMA:
        aviso = f'Atenção: diferença de overall entre os times é de {margem} pontos, acima da margem ideal de {MARGEM_MAXIMA}.'

    request.session['sorteio_atual'] = {
        str(tid): [j.id for j in info['jogadores']]
        for tid, info in sorteio.items()
    }

    return render(request, 'sorteador/resultado.html', {
        'sorteio': sorteio,
        'aviso': aviso
    })


@login_required
@csrf_exempt
def salvar_sorteio(request):
    if request.method == 'POST':
        sorteio_atual = request.session.get('sorteio_atual')

        if not sorteio_atual:
            return render(request, 'sorteador/resultado.html', {
                'erro': 'Nenhum sorteio ativo para salvar.'
            })

        Jogador.objects.update(time=None)

        for time_id, jogadores_ids in sorteio_atual.items():
            time = Time.objects.get(id=int(time_id))
            jogadores = Jogador.objects.filter(id__in=jogadores_ids)
            overall_total = sum(j.overall for j in jogadores)

            time.overall = overall_total
            time.save()

            for j in jogadores:
                j.time = time
                j.save()

        if 'sorteio_atual' in request.session:
            del request.session['sorteio_atual']

    return redirect('listar_times')


@login_required
@csrf_exempt
def refazer_sorteio(request):
    if request.method == 'POST':
        if 'sorteio_atual' in request.session:
            del request.session['sorteio_atual']
    return redirect('sortear_times')


def detalhes_time(request, time_id):
    time = get_object_or_404(Time, id=time_id)
    jogadores = time.jogadores.all().order_by('classificacao', '-overall')
    overall_total = sum(j.overall for j in jogadores)
    return render(request, 'detalhes_time.html', {
        'time': time,
        'jogadores': jogadores,
        'overall_total': overall_total,
    })


@login_required
@csrf_exempt
def excluir_todos_jogadores(request):
    if request.method == 'POST':
        Jogador.objects.all().delete()
        messages.success(request, 'Todos os jogadores foram excluídos com sucesso!')
    return redirect('listar_jogadores')


def listar_times_completos(request):
    times = Time.objects.prefetch_related('jogadores').all()
    times_com_overall = []

    for time in times:
        jogadores = time.jogadores.all()
        if jogadores.exists():
            soma = sum(j.overall for j in jogadores)
            media = round(soma / len(jogadores), 1)
        else:
            media = 0

        times_com_overall.append({
            'obj': time,
            'overall_total': media
        })

    context = {
        'times_com_overall': times_com_overall,
    }
    return render(request, 'times_completos.html', context)


@login_required
def sortear_grupos(request):
    times = list(Time.objects.prefetch_related('jogadores').all())

    if not times:
        return render(request, 'sorteador/grupos.html', {
            'erro': 'Cadastre os times antes de sortear os grupos.'
        })

    NUM_GRUPOS = 2
    MAX_TENTATIVAS = 100
    MARGEM_MAXIMA = 5

    if len(times) < NUM_GRUPOS:
        return render(request, 'sorteador/grupos.html', {
            'erro': 'Quantidade de times insuficiente para formar os grupos.'
        })

    times_info = []
    for time in times:
        jogadores = time.jogadores.all()
        if jogadores.exists():
            media = sum(j.overall for j in jogadores) / jogadores.count()
        else:
            media = 0

        times_info.append({
            'time': time,
            'media': round(media, 1)
        })

    for tentativa in range(MAX_TENTATIVAS):
        grupos = {
            f'Grupo {chr(65+i)}': {
                'times': [],
                'soma_media': 0
            }
            for i in range(NUM_GRUPOS)
        }

        sucesso = True
        times_disp = times_info[:]
        random.shuffle(times_disp)

        for info_time in times_disp:
            pesos = []
            candidatos = []

            MAX_POR_GRUPO = len(times) // NUM_GRUPOS

            for grupo, dados in grupos.items():
                if len(dados['times']) < MAX_POR_GRUPO:
                    peso = 1 / (dados['soma_media'] + 1)
                    candidatos.append(grupo)
                    pesos.append(peso)

            if not candidatos:
                sucesso = False
                break

            grupo_escolhido = random.choices(candidatos, weights=pesos, k=1)[0]
            grupos[grupo_escolhido]['times'].append(info_time)
            grupos[grupo_escolhido]['soma_media'] += info_time['media']

        if not sucesso:
            continue

        medias = [
            dados['soma_media'] / len(dados['times'])
            for dados in grupos.values()
            if dados['times']
        ]

        margem = max(medias) - min(medias)

        if margem <= MARGEM_MAXIMA:
            break
    else:
        return render(request, 'sorteador/grupos.html', {
            'erro': f'Não foi possível gerar grupos equilibrados após {MAX_TENTATIVAS} tentativas.'
        })

    request.session['grupos_sorteados'] = {
        grupo: [t['time'].id for t in dados['times']]
        for grupo, dados in grupos.items()
    }

    return render(request, 'sorteador/grupos.html', {
        'grupos': grupos,
        'margem': round(margem, 2)
    })


@login_required
@csrf_exempt
def salvar_grupos(request):
    if request.method == 'POST':
        grupos_sorteados = request.session.get('grupos_sorteados')

        if not grupos_sorteados:
            messages.error(request, 'Nenhum sorteio de grupos ativo para salvar.')
            return redirect('sortear_grupos')

        Time.objects.update(grupo=None)

        for grupo, times_ids in grupos_sorteados.items():
            for time_id in times_ids:
                time = Time.objects.get(id=time_id)
                time.grupo = grupo
                time.save()

        Jogo.objects.all().delete()

        grupo_a = list(Time.objects.filter(grupo='Grupo A').order_by('id'))
        grupo_b = list(Time.objects.filter(grupo='Grupo B').order_by('id'))

        if len(grupo_a) != 3 or len(grupo_b) != 3:
            messages.error(request, 'Os grupos precisam ter exatamente 3 times.')
            return redirect('listar_grupos')

        A1, A2, A3 = grupo_a
        B1, B2, B3 = grupo_b

        jogos = [
            # Rodada 1
            (A1, B1),
            (A2, B2),
            (A3, B3),

            # Rodada 2
            (A2, B1),
            (A1, B3),
            (A3, B2),

            # Rodada 3
            (A2, B3),
            (A1, B2),
            (A3, B1),
        ]

        for ordem, (time_a, time_b) in enumerate(jogos, start=1):
            Jogo.objects.create(
                time_a=time_a,
                time_b=time_b,
                ordem=ordem
            )

        del request.session['grupos_sorteados']

        messages.success(request, 'Grupos e jogos salvos com sucesso!')

    return redirect('listar_grupos')

def listar_grupos(request):
    grupos = {}

    for grupo in ['Grupo A', 'Grupo B']:
        grupos[grupo] = calcular_classificacao(grupo)

    return render(request, 'sorteador/listar_grupos.html', {
        'grupos': grupos
    })

def listar_jogos(request):
    jogos = list(
        Jogo.objects
        .select_related('time_a', 'time_b')
        .order_by('ordem')
    )

    JOGOS_POR_RODADA = 3
    jogos_por_rodada = defaultdict(list)

    for index, jogo in enumerate(jogos):
        rodada = math.ceil((index + 1) / JOGOS_POR_RODADA)
        jogos_por_rodada[rodada].append(jogo)

    return render(request, 'sorteador/listar_jogos.html', {
        'jogos_por_rodada': dict(jogos_por_rodada)
    })

def detalhes_jogo(request, jogo_id):
    jogo = get_object_or_404(Jogo, id=jogo_id)

    gols_time_a = jogo.gols.filter(jogador__time=jogo.time_a)
    gols_time_b = jogo.gols.filter(jogador__time=jogo.time_b)


    return render(request, 'sorteador/detalhes_jogo.html', {
        'jogo': jogo,
        'gols_time_a': gols_time_a,
        'gols_time_b': gols_time_b,
    })

def calcular_classificacao(grupo_nome):
    times = Time.objects.filter(grupo=grupo_nome)

    tabela = {}

    for time in times:
        tabela[time.id] = {
            'time': time,
            'J': 0,
            'V': 0,
            'E': 0,
            'D': 0,
            'GP': 0,
            'GC': 0,
            'SG': 0,
            'PTS': 0,
        }

    jogos = (
        Jogo.objects
        .filter(status='FINALIZADO')
        .filter(
            models.Q(time_a__grupo=grupo_nome) |
            models.Q(time_b__grupo=grupo_nome)
        )
    )

    for jogo in jogos:
        for lado, adversario in [
            (jogo.time_a, jogo.time_b),
            (jogo.time_b, jogo.time_a),
        ]:
            if lado.id not in tabela:
                continue

            dados = tabela[lado.id]
            dados['J'] += 1

            gols_feitos = jogo.gols_time_a if lado == jogo.time_a else jogo.gols_time_b
            gols_sofridos = jogo.gols_time_b if lado == jogo.time_a else jogo.gols_time_a

            dados['GP'] += gols_feitos
            dados['GC'] += gols_sofridos

            if gols_feitos > gols_sofridos:
                dados['V'] += 1
                dados['PTS'] += 3
            elif gols_feitos < gols_sofridos:
                dados['D'] += 1
            else:
                dados['E'] += 1
                dados['PTS'] += 1

                if jogo.teve_penaltis:
                    venceu_penalti = (
                        jogo.penaltis_time_a > jogo.penaltis_time_b
                        if lado == jogo.time_a
                        else jogo.penaltis_time_b > jogo.penaltis_time_a
                    )
                    if venceu_penalti:
                        dados['PTS'] += 1

    for dados in tabela.values():
        dados['SG'] = dados['GP'] - dados['GC']

    return sorted(
        tabela.values(),
        key=lambda x: (x['PTS'], x['SG'], x['GP']),
        reverse=True
    )
