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
# Retry migrate up to 3 times to handle concurrent startup race conditions
for i in $(seq 1 3); do
    python manage.py migrate --noinput && break
    if [ $i -lt 3 ]; then
        echo "⚠️ Migration attempt $i failed, retrying in 3 seconds..."
        sleep 3
    else
        echo "❌ Migration failed after 3 attempts."
        exit 1
    fi
done

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
