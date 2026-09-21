from django.db import models
from django.core.exceptions import ValidationError

class Time(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    escudo = models.ImageField(upload_to='escudos/')
    grupo = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.nome


class Jogador(models.Model):
    nome = models.CharField(max_length=100)
    classificacao = models.PositiveIntegerField()
    overall = models.PositiveIntegerField()
    time = models.ForeignKey(Time, on_delete=models.SET_NULL,related_name='jogadores', null=True, blank=True)

    def __str__(self):
        return self.nome


class Jogo(models.Model):
    STATUS_CHOICES = (('PENDENTE', 'Pendente'), ('FINALIZADO', 'Finalizado'),)

    time_a = models.ForeignKey('Time', on_delete=models.CASCADE, related_name='jogos_como_a')
    time_b = models.ForeignKey('Time', on_delete=models.CASCADE, related_name='jogos_como_b')

    gols_time_a = models.PositiveIntegerField(default=0)
    gols_time_b = models.PositiveIntegerField(default=0)

    teve_penaltis = models.BooleanField(default=False)
    penaltis_time_a = models.PositiveIntegerField(null=True, blank=True)
    penaltis_time_b = models.PositiveIntegerField(null=True, blank=True)

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDENTE')

    ordem = models.PositiveIntegerField()

    def clean(self):
        if self.time_a == self.time_b:
            raise ValidationError('Os times do jogo devem ser diferentes.')

        if self.teve_penaltis:
            if self.gols_time_a != self.gols_time_b:
                raise ValidationError(
                    'Só pode haver disputa de pênaltis em caso de empate.'
                )

            if self.penaltis_time_a is None or self.penaltis_time_b is None:
                raise ValidationError(
                    'Informe o placar dos pênaltis.'
                )

        if not self.teve_penaltis:
            if self.penaltis_time_a or self.penaltis_time_b:
                raise ValidationError('Marque que houve pênaltis para informar o placar.')

    def __str__(self):
        return f"{self.time_a} x {self.time_b}"

class Gol(models.Model):
    jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name='gols')
    jogador = models.ForeignKey(Jogador, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    def clean(self):
        if self.jogador.time not in [self.jogo.time_a, self.jogo.time_b]:
            raise ValidationError('O jogador deve pertencer a um dos times do jogo.')

    def __str__(self):
        return f"{self.jogador.nome} ({self.quantidade})"

