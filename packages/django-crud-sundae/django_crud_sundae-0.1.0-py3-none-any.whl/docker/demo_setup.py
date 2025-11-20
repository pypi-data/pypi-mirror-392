#!/usr/bin/env python
"""
Setup script for Django CRUD Sundae Docker demo
"""
import os
import sys

# Add the app to Python path
sys.path.insert(0, '/app')

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demoproject.settings')

def setup_models():
    """Create the Article model"""
    models_content = """from django.db import models

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
"""
    with open('articles/models.py', 'w') as f:
        f.write(models_content)
    print("✅ Created Article model")

def setup_views():
    """Create the CRUD views"""
    views_content = """from sundae.views import CRUDSundaeView, bulk_action
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
"""
    with open('articles/views.py', 'w') as f:
        f.write(views_content)
    print("✅ Created CRUD views")

def setup_urls():
    """Configure URLs"""
    # Articles URLs
    articles_urls = """from django.urls import path, include
from .views import ArticleView

urlpatterns = [
    path('', include(ArticleView.get_urls())),
]
"""
    with open('articles/urls.py', 'w') as f:
        f.write(articles_urls)

    # Project URLs
    project_urls = """from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    html = '''
    <html>
    <head><title>Django CRUD Sundae Demo</title></head>
    <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
        <h1>🍨 Django CRUD Sundae Demo</h1>
        <p>Welcome to the Django CRUD Sundae demonstration!</p>
        <h2>Quick Links:</h2>
        <ul>
            <li><a href="/articles/article/">Articles List</a> - View all articles</li>
            <li><a href="/articles/article/create/">Create Article</a> - Add a new article</li>
            <li><a href="/admin/">Admin Interface</a> - Django admin (admin/admin)</li>
        </ul>
        <h2>Features to Try:</h2>
        <ul>
            <li>Search articles by title or content</li>
            <li>Filter by status (Draft/Published)</li>
            <li>Select multiple articles and use bulk actions</li>
            <li>Create, edit, and delete articles</li>
        </ul>
    </body>
    </html>
    '''
    return HttpResponse(html)

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('articles/', include('articles.urls')),
]
"""
    with open('demoproject/urls.py', 'w') as f:
        f.write(project_urls)
    print("✅ Configured URLs")

def update_settings():
    """Update Django settings"""
    settings_file = 'demoproject/settings.py'
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
        "ALLOWED_HOSTS = ['*']  # For demo purposes only"
    )

    with open(settings_file, 'w') as f:
        f.write(content)
    print("✅ Updated settings")

def main():
    print("🍨 Setting up Django CRUD Sundae demo...")
    print("=" * 50)

    setup_models()
    setup_views()
    setup_urls()
    update_settings()

    print("\n✨ Demo setup complete!")
    print("\nNext steps:")
    print("1. Run: docker-compose up")
    print("2. Visit: http://localhost:8000")

if __name__ == '__main__':
    main()
