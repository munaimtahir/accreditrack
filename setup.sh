#!/bin/bash
# AccrediFy Setup Script

set -e

echo "🚀 Setting up AccrediFy..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.template .env
    
    # Generate a random Django secret key
    SECRET_KEY=$(python3 -c "import secrets; import string; chars = string.ascii_letters + string.digits + '-_'; print(''.join(secrets.choice(chars) for i in range(50)))")
    
    # Set default values
    sed -i "s/DB_PASSWORD=/DB_PASSWORD=accredify_password_change_me/" .env
    sed -i "s/DJANGO_SECRET_KEY=/DJANGO_SECRET_KEY=$SECRET_KEY/" .env
    
    echo "✅ .env file created. Please update DB_PASSWORD and GEMINI_API_KEY if needed."
fi

# Build frontend locally
echo "🔨 Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Build and start services
echo "🐳 Building and starting Docker services..."
docker compose build
docker compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run migrations
echo "📊 Running database migrations..."
docker compose exec -T backend python manage.py migrate

# Create superuser if needed
echo "👤 Creating superuser (admin/admin123)..."
docker compose exec -T backend python manage.py shell <<EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
else:
    user = User.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print('Superuser password updated')
EOF

echo ""
echo "✅ AccrediFy is ready!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend:  http://localhost/"
echo "   API Docs:  http://localhost/api/docs/"
echo "   Admin:     http://localhost/admin/"
echo ""
echo "🔑 Login credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📝 To stop: docker compose down"
echo "📝 To view logs: docker compose logs -f"
