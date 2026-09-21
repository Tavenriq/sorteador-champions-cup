from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('jogadores/', views.listar_jogadores, name='listar_jogadores'),
    path('times/', views.listar_times, name='listar_times'),
    path('jogadores/novo/', views.cadastrar_jogador, name='cadastrar_jogador'),
    path('times/novo/', views.cadastrar_time, name='cadastrar_time'),
    path('jogadores/editar/<int:jogador_id>/', views.editar_jogador, name='editar_jogador'),
    path('sortear/', views.sortear_times, name='sortear_times'),
    path('sortear/refazer/', views.refazer_sorteio, name='refazer_sorteio'),
    path('sortear/salvar/', views.salvar_sorteio, name='salvar_sorteio'),
    path('times/<int:time_id>/', views.detalhes_time, name='detalhes_time'),
    path('jogadores/excluir_todos/', views.excluir_todos_jogadores, name='excluir_todos_jogadores'),
    path('times_completos/', views.listar_times_completos, name='listar_times_completos'),
    path('sortear-grupos/', views.sortear_grupos, name='sortear_grupos'),
    path('salvar-grupos/', views.salvar_grupos, name='salvar_grupos'),
    path('grupos/', views.listar_grupos, name='listar_grupos'),
    path('jogos/', views.listar_jogos, name='listar_jogos'),
    path('jogos/<int:jogo_id>/', views.detalhes_jogo, name='detalhes_jogo'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.root_redirect),

]
