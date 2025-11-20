#!/bin/bash
set -e

echo "🍨 Django CRUD Sundae - Quick Demo Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create temporary directory
DEMO_DIR="django-crud-sundae-demo"
echo "📁 Creating demo directory: $DEMO_DIR"
mkdir -p "$DEMO_DIR"
cd "$DEMO_DIR"

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install packages
echo "📦 Installing Django and dependencies..."
pip install --quiet --upgrade pip
pip install --quiet django django-filter django-widget-tweaks

# Note: When django-crud-sundae is published to PyPI, use:
# pip install --quiet django-crud-sundae
# For now, users should clone the repo and install from source

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

urlpatterns = [
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
        'content': 'This is a comprehensive guide to getting started with Django CRUD Sundae. It covers all the basics you need to know.',
        'status': 'published'
    },
    {
        'title': 'Advanced Features',
        'content': 'Explore advanced features like bulk actions, custom actions, and HTMX integration.',
        'status': 'published'
    },
    {
        'title': 'Draft Article',
        'content': 'This is a draft article that has not been published yet.',
        'status': 'draft'
    },
]

for article_data in articles:
    Article.objects.get_or_create(
        title=article_data['title'],
        defaults=article_data
    )

print(f"Created {Article.objects.count()} sample articles")
EOF

# Create superuser
echo "👤 Creating admin user..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print("Created superuser: admin / admin")
EOF

echo ""
echo "✅ Demo setup complete!"
echo ""
echo "🎉 Next steps:"
echo "   1. cd $DEMO_DIR"
echo "   2. source venv/bin/activate  (or venv\\Scripts\\activate on Windows)"
echo "   3. python manage.py runserver"
echo ""
echo "📱 Then visit:"
echo "   - Articles: http://localhost:8000/articles/article/"
echo "   - Admin: http://localhost:8000/admin/ (admin/admin)"
echo ""
echo "🍨 Enjoy your Django CRUD Sundae!"
