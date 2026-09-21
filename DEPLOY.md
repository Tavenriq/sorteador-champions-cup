# Deploy na Vercel — Cedro Champions Cup

## 1. Banco de dados (obrigatório)

A Vercel roda em serverless com disco **somente leitura**. O `db.sqlite3` não
aceita gravação lá, então o projeto precisa de um Postgres externo.

Opções gratuitas: [Neon](https://neon.tech) ou [Supabase](https://supabase.com).

Crie o banco e copie a connection string, algo como:

```
postgresql://usuario:senha@host.neon.tech/nomedobanco?sslmode=require
```

## 2. Rodar as migrations no Postgres (do seu PC)

```bash
cd sorteador
pip install -r ../requirements.txt

# Linux/Mac
export DATABASE_URL="postgresql://..."
# Windows PowerShell
# $env:DATABASE_URL="postgresql://..."

python manage.py migrate
python manage.py createsuperuser
```

Os dados que já estão no SQLite podem ser migrados assim:

```bash
# sem DATABASE_URL definido (usa o sqlite local)
python manage.py dumpdata --natural-foreign --natural-primary \
  -e contenttypes -e auth.Permission -e sessions > dados.json

# com DATABASE_URL definido (aponta pro Postgres)
python manage.py loaddata dados.json
```

## 3. Subir para o GitHub

```bash
git init
git add .
git commit -m "Acesso público + deploy Vercel"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/Sorteador-Champions-Cup.git
git push -u origin main
```

## 4. Criar o projeto na Vercel

1. vercel.com → **Add New → Project** → importe o repositório.
2. **Framework Preset:** Other. Root Directory: `./` (a raiz, onde está o `vercel.json`).
3. Em **Environment Variables**, adicione:

| Nome | Valor |
|---|---|
| `SECRET_KEY` | uma chave longa e aleatória |
| `DEBUG` | `False` |
| `DATABASE_URL` | a connection string do Postgres |
| `SITE_URL` | `https://seu-projeto.vercel.app` (depois do 1º deploy) |

4. **Deploy**.

Para gerar a SECRET_KEY:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## 5. Observações

- **Upload de escudos não funciona na Vercel.** O `ImageField` tenta gravar em
  disco, o que é bloqueado. Os escudos que já estão em `sorteador/media/escudos/`
  continuam aparecendo normalmente (são servidos do repositório). Para permitir
  uploads novos, use Cloudinary (`django-cloudinary-storage`) ou S3.
- Arquivos estáticos são servidos pelo WhiteNoise, sem precisar de
  `collectstatic` no build.
- O `/admin/` do Django continua exigindo usuário **staff/superusuário** — isso é
  do próprio Django e não foi alterado.
