#!/bin/bash
set -e

echo "🍨 Django CRUD Sundae - Local Demo Test"
echo "========================================"
echo ""

# Create temporary directory
DEMO_DIR="/tmp/django-crud-sundae-test"
echo "📁 Creating demo directory: $DEMO_DIR"
rm -rf "$DEMO_DIR"
mkdir -p "$DEMO_DIR"
cd "$DEMO_DIR"

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Django and local django-crud-sundae
echo "📦 Installing Django and django-crud-sundae from source..."
pip install --quiet --upgrade pip
pip install --quiet django django-filter django-widget-tweaks
pip install --quiet -e /home/user/django-crud-sundae

# Create Django project
echo "🚀 Creating Django project..."
django-admin startproject demo .
python manage.py startapp articles

# Create model
echo "📝 Setting up Article model..."
cat > articles/models.py << 'EOF'
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('published', 'Published'),
        ],
        default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
EOF

# Create view
echo "🎨 Setting up CRUD views..."
cat > articles/views.py << 'EOF'
from sundae.views import CRUDSundaeView, bulk_action
from .models import Article

class ArticleView(CRUDSundaeView):
    model = Article
    lookup_field = 'pk'
    fields = ['title', 'content', 'status']
    list_fields = ['title', 'status', 'created_at']
    search_fields = ['title', 'content']
    filterset_fields = ['status']
    paginate_by = 10

    @bulk_action(display_name="Mark as Published", confirmation_required=True)
    def publish_selected(self, request, queryset):
        queryset.update(status='published')
        return len(queryset), "published"

    bulk_edit_actions = ['publish_selected']
EOF

# Create URLs
echo "🔗 Configuring URLs..."
cat > articles/urls.py << 'EOF'
from django.urls import path, include
from .views import ArticleView

urlpatterns = [
    path('', include(ArticleView.get_urls())),
]
EOF

# Update project URLs
cat > demo/urls.py << 'EOF'
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    html = '''
    <html>
    <head>
        <title>Django CRUD Sundae Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #2c3e50; }
            .links { background: #f8f9fa; padding: 20px; border-radius: 8px; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
            li { margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>🍨 Django CRUD Sundae Demo</h1>
        <p>Welcome to the Django CRUD Sundae demonstration!</p>
        <div class="links">
            <h2>Quick Links:</h2>
            <ul>
                <li><a href="/articles/article/">📋 Articles List</a> - View all articles</li>
                <li><a href="/articles/article/create/">➕ Create Article</a> - Add a new article</li>
                <li><a href="/admin/">⚙️ Admin Interface</a> - Django admin (admin/admin)</li>
            </ul>
            <h2>Features to Try:</h2>
            <ul>
                <li>🔍 Search articles by title or content</li>
                <li>🎯 Filter by status (Draft/Published)</li>
                <li>☑️ Select multiple articles and use bulk actions</li>
                <li>✏️ Create, edit, and delete articles</li>
            </ul>
        </div>
    </body>
    </html>
    '''
    return HttpResponse(html)

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('articles/', include('articles.urls')),
]
EOF

# Update settings
python << 'EOF'
import os
import sys

settings_file = 'demo/settings.py'
with open(settings_file, 'r') as f:
    content = f.read()

# Add apps to INSTALLED_APPS
if "'sundae'" not in content:
    content = content.replace(
        "INSTALLED_APPS = [",
        "INSTALLED_APPS = [\n    'sundae',\n    'articles',"
    )

# Update ALLOWED_HOSTS
content = content.replace(
    "ALLOWED_HOSTS = []",
    "ALLOWED_HOSTS = ['*']"
)

with open(settings_file, 'w') as f:
    f.write(content)

print("✅ Updated settings.py")
EOF

# Create migrations and run them
echo "🗄️  Setting up database..."
python manage.py makemigrations articles --noinput
python manage.py migrate --noinput

# Create some sample data
echo "📊 Creating sample data..."
python manage.py shell << 'EOF'
from articles.models import Article

# Create sample articles
articles = [
    {
        'title': 'Getting Started with Django CRUD Sundae',
        'content': 'This is a comprehensive guide to getting started with Django CRUD Sundae. It covers all the basics you need to know to build powerful CRUD interfaces quickly.',
        'status': 'published'
    },
    {
        'title': 'Advanced Features and Custom Actions',
        'content': 'Explore advanced features like bulk actions, custom actions, HTMX integration, and permission-based access control.',
        'status': 'published'
    },
    {
        'title': 'Building a Blog with CRUD Sundae',
        'content': 'Learn how to build a complete blog application using Django CRUD Sundae with minimal code.',
        'status': 'published'
    },
    {
        'title': 'Draft Article - Work in Progress',
        'content': 'This is a draft article that demonstrates the draft status filtering feature.',
        'status': 'draft'
    },
    {
        'title': 'Search and Filter Tutorial',
        'content': 'Understanding how to implement powerful search and filtering capabilities in your CRUD views.',
        'status': 'published'
    },
]

for article_data in articles:
    Article.objects.get_or_create(
        title=article_data['title'],
        defaults=article_data
    )

print(f"✅ Created {Article.objects.count()} sample articles")
EOF

# Create superuser
echo "👤 Creating admin user..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print("✅ Created superuser: admin / admin")
EOF

echo ""
echo "✅ Demo setup complete!"
echo ""
echo "📍 Demo location: $DEMO_DIR"
echo ""

# Start the server in background
echo "🚀 Starting development server..."
python manage.py runserver 8000 > /tmp/django-server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Test if server is running
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Server is running at http://localhost:8000"
    echo ""
    echo "Server PID: $SERVER_PID"
    echo "Log file: /tmp/django-server.log"
else
    echo "❌ Server failed to start. Check /tmp/django-server.log"
    exit 1
fi
