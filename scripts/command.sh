#!/bin/sh

# O shell irá encerrar a execução do script quando um comando falhar
set -e

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo "🟡 Waiting for Postgres Database Startup ($POSTGRES_HOST $POSTGRES_PORT) ..."
  sleep 2
done

echo "✅ Postgres Database Started Successfully ($POSTGRES_HOST:$POSTGRES_PORT)"

python manage.py collectstatic --noinput
## python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Criar superusuário padrão para desenvolvimento se não existir
cat <<EOF | python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='ocpcps').exists():
    User.objects.create_superuser('ocpcps', 'brasilcondo.br@gmail.com', 'brasilcondo123')
    print("✅ Superusuário 'ocpcps' criado com sucesso.")
else:
    user = User.objects.get(username='ocpcps')
    user.set_password('brasilcondo123')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print("✅ Superusuário 'ocpcps' atualizado com sucesso.")
EOF

exec "$@"
