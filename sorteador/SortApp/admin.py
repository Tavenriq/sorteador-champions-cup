from django.contrib import admin
from .models import Jogo, Gol, Jogador, EdicaoCampeonato, JogadorCampeao


class GolTimeAInline(admin.TabularInline):
    model = Gol
    extra = 1
    verbose_name = "Gol - Time A"
    verbose_name_plural = "Gols - Time A"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(jogador__time__isnull=False)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "jogador":
            jogo_id = request.resolver_match.kwargs.get("object_id")
            if jogo_id:
                jogo = Jogo.objects.get(pk=jogo_id)
                kwargs["queryset"] = Jogador.objects.filter(time=jogo.time_a)
            else:
                kwargs["queryset"] = Jogador.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class GolTimeBInline(admin.TabularInline):
    model = Gol
    extra = 1
    verbose_name = "Gol - Time B"
    verbose_name_plural = "Gols - Time B"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "jogador":
            jogo_id = request.resolver_match.kwargs.get("object_id")
            if jogo_id:
                jogo = Jogo.objects.get(pk=jogo_id)
                kwargs["queryset"] = Jogador.objects.filter(time=jogo.time_b)
            else:
                kwargs["queryset"] = Jogador.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Jogo)
class JogoAdmin(admin.ModelAdmin):
    inlines = [GolTimeAInline, GolTimeBInline]

class JogadorCampeaoInline(admin.TabularInline):
    model = JogadorCampeao
    extra = 5


@admin.register(EdicaoCampeonato)
class EdicaoCampeonatoAdmin(admin.ModelAdmin):
    list_display = (
        'ano',
        'campeao',
        'vice_campeao',
    )

    list_filter = ('ano',)

    search_fields = (
        'campeao',
        'vice_campeao',
    )

    inlines = [JogadorCampeaoInline]