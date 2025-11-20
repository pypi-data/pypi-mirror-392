# django-crud-sundae

A useful view class for creating CRUD views in Django (With Tailwind & HTMX). Following the ice-cream metaphor established by Django Neapolitan and Django Vanilla views. This offers a few extras: a banana, squirt of cream and a drizzle of chocolate sauce!

## Quick Start for Busy People

Want to try it out immediately? Here are the fastest ways to get started:

### Option 1: Using UV

[UV](https://github.com/astral-sh/uv) is a Python package manager. Perfect for quick testing:

```bash
# Install UV if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a new Django project with django-crud-sundae
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Django and django-crud-sundae
uv pip install django django-crud-sundae django-filter

# Create a test project
django-admin startproject myproject .
cd myproject
python manage.py startapp articles

# Create a simple model in articles/models.py
cat > articles/models.py << 'EOF'
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
EOF

# Create a view in articles/views.py
cat > articles/views.py << 'EOF'
from sundae.views import CRUDSundaeView
from .models import Article

class ArticleView(CRUDSundaeView):
    model = Article
    lookup_field = 'pk'
    fields = ['title', 'content']
EOF

# Update settings.py to include the apps
# Add 'sundae' and 'articles' to INSTALLED_APPS

# Create URLs
cat > articles/urls.py << 'EOF'
from django.urls import path, include
from .views import ArticleView

urlpatterns = [
    path('', include(ArticleView.get_urls())),
]
EOF

# Run migrations and start server
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

# Visit http://localhost:8000/article/ to see your CRUD interface!
```

### Option 2: Using Docker

For a completely isolated environment with zero setup:

```bash
# Clone the repository
git clone https://github.com/leonh/django-crud-sundae.git
cd django-crud-sundae

# Build and run with docker-compose
docker-compose up --build

# Visit http://localhost:8000 for the demo!
```

That's it! The Docker setup includes:
- ✅ Complete Django project with sample Article model
- ✅ Pre-configured CRUD views with search and filtering
- ✅ Sample data to explore
- ✅ Admin interface (login: admin/admin)
- ✅ All dependencies installed

**Useful Docker commands:**
```bash
# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down

# Access Django shell
docker-compose exec web python manage.py shell

# Create a superuser
docker-compose exec web python manage.py createsuperuser
```

### Option 3: One-Command Demo Script

Use a automated setup script that creates everything for you (read it before running!):

```bash
# Download and run the demo script
curl -sSL https://raw.githubusercontent.com/leonh/django-crud-sundae/main/demo.sh | bash

# Or clone and run locally
git clone https://github.com/leonh/django-crud-sundae.git
cd django-crud-sundae
./demo.sh
```

The script will:
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Set up a complete Django project
- ✅ Create sample models and views
- ✅ Generate sample data
- ✅ Create an admin user (admin/admin)

Just follow the printed instructions to start the server!

## Regular Installation (pip)

Install from PyPI (once published):

```bash
pip install django-crud-sundae
```

Or install from source for the heros:

```bash
git clone https://github.com/leonh/django-crud-sundae.git
cd django-crud-sundae
pip install -e .
```

## Quick Start

1. Add `sundae` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'sundae',
    ...
]
```

2. Use CRUDSundae in your Django app:

```python
from sundae.views import CRUDSundaeView
from .models import Article

class ArticleView(CRUDSundaeView):
    model = Article
    lookup_field = 'pk'  # Use standard primary keys (recommended for most users)
    fields = ['title', 'content', 'author']
```

**Note**: The default `lookup_field` is `'sqid'` which requires django-sqids. For a simpler setup without extra dependencies, use `lookup_field = 'pk'` as shown above.

3. Wire up your URLs (automatic URL generation):

```python
from django.urls import path, include
from .views import ArticleView

urlpatterns = [
    path('', include(ArticleView.get_urls())),
]
```

This automatically generates all CRUD URLs:
- `/article/` - List articles
- `/article/create/` - Create article
- `/article/<int:pk>/` - View article detail
- `/article/<int:pk>/update/` - Edit article
- `/article/<int:pk>/delete/` - Delete article

## How CRUDSundae Works

CRUDSundae provides a single base view class (`CRUDSundaeView`) that handles all CRUD operations through a unified interface. Instead of creating separate view classes for list, create, update, and delete operations, you define one view class and CRUDSundae automatically generates all the necessary URL patterns and view handlers.

### Core Concepts

1. **Single View Class**: Define your model and fields once, get complete CRUD functionality
2. **Automatic URL Generation**: URLs are automatically generated following the pattern `{model-name}-{action}` (e.g., `article-list`, `article-create`)
3. **Convention-Based Templates**: Templates are resolved automatically based on your model name, with fallback to default templates
4. **Decorator-Based Actions**: Add custom actions using simple `@action` and `@bulk_action` decorators

### URL Structure

When you call `MyView.get_urls()`, CRUDSundae automatically generates these URL patterns:

**Using standard primary keys (default Django, no extra dependencies):**
- `{model}/` - List view
- `{model}/create/` - Create view
- `{model}/<int:pk>/` - Detail view
- `{model}/<int:pk>/update/` - Update view
- `{model}/<int:pk>/delete/` - Delete view
- `{model}/bulk-update/` - Bulk action processing

**Using sqids (optional, requires django-sqids for URL-safe IDs):**
- `{model}/` - List view
- `{model}/create/` - Create view
- `{model}/<slug:sqid>/` - Detail view
- `{model}/<slug:sqid>/update/` - Update view
- `{model}/<slug:sqid>/delete/` - Delete view
- `{model}/bulk-update/` - Bulk action processing

The lookup field is configured via the `lookup_field` attribute (default: `'sqid'`). Set to `'pk'` to use primary keys instead.

### Template Resolution

Templates are resolved in this order:
1. Explicitly defined `template_name`
2. `{app_label}/{model_name}{suffix}.html` (e.g., `articles/article_list.html`)
3. `sundae/object{suffix}.html` (default fallback templates)

## Features

### Core CRUD Operations

- **List View**: Paginated listing with search and filter support
- **Create View**: Form-based object creation with validation
- **Detail View**: Single object display
- **Update View**: Form-based object editing
- **Delete View**: Confirmation-based deletion

### Search & Filtering

- **Full-Text Search**: Search across multiple fields using `search_fields` attribute
- **Django-Filter Integration**: Advanced filtering using django-filter library
- **Active Filter Display**: Shows currently applied filters with remove links
- **Preserved Query Strings**: Filters are preserved across pagination

```python
class ArticleListView(CRUDSundaeView):
    model = Article
    search_fields = ['title', 'content', 'author__name']  # Search across these fields
    filterset_fields = ['status', 'category']  # Enable filtering
```

### Pagination

- **Automatic Pagination**: Configure with `paginate_by` attribute
- **Filter Preservation**: Pagination links preserve search and filter parameters
- **Customizable**: Override `get_paginator()` for custom pagination logic

### Bulk Actions

Register bulk actions using the `@bulk_action` decorator to operate on multiple selected objects:

```python
@bulk_action(display_name="Archive Selected", confirmation_required=True)
def archive_selected(self, request, queryset):
    queryset.update(archived=True)
    return len(queryset), "archived"

@bulk_action(display_name="Delete Selected", use_transaction=True)
def delete_selected(self, request, queryset):
    count = queryset.count()
    queryset.delete()
    return count, "deleted"
```

Features:
- Optional confirmation dialogs
- Permission checks
- Transaction support (all-or-nothing operations)
- Automatic success/error messaging
- Logging integration

### Custom Actions

Add custom actions using the `@action` decorator:

```python
# Detail action (operates on single object)
@action(detail=True, url_path="approve", permission_required="myapp.approve_article")
def approve_item(self, request, pk):  # Parameter name matches lookup_field
    obj = self.get_object()
    obj.approved = True
    obj.save()
    messages.success(request, f"{obj} has been approved!")
    return HttpResponseRedirect(self.get_list_url())

# List action (operates on list view)
@action(detail=False, url_path="export", methods=["GET"])
def export_list(self, request):
    # Export logic...
    return HttpResponse(csv_data, content_type='text/csv')
```

**Note**: The URL parameter name in your action method should match your `lookup_field` setting (e.g., `pk`, `sqid`, `slug`).

### Validation Hooks

CRUDSundae provides comprehensive hooks for customizing behavior at every stage:

```python
class ArticleView(CRUDSundaeView):
    model = Article

    def clean_object(self, obj):
        """Custom validation before saving"""
        if obj.publish_date < obj.created_date:
            raise ValidationError("Publish date cannot be before creation date")

    def before_save(self, form):
        """Called before both create and update"""
        form.instance.modified_by = self.request.user

    def after_save(self, obj, created):
        """Called after both create and update"""
        action = "created" if created else "updated"
        self.logger.info(f"Article {obj.pk} was {action}")

    def before_create(self, form):
        """Called only before creating new objects"""
        form.instance.author = self.request.user

    def after_create(self, obj):
        """Called only after creating new objects"""
        send_notification_email(obj)
```

### HTMX Integration

Built-in support for HTMX dynamic interactions:

- **Automatic Detection**: Detects HTMX requests via `HX-Request` header
- **Client-Side Redirects**: `htmx_redirect()` for seamless navigation
- **Page Refresh**: `htmx_refresh()` to reload current page
- **Custom Events**: `htmx_trigger()` to fire client-side events
- **Partial Rendering**: Returns partial templates for HTMX requests

```python
# In your view methods
if self.is_htmx_request():
    headers = self.htmx_redirect(self.get_success_url())
    return HttpResponse(status=204, headers=headers)
```

### Permission & Authentication

Flexible permission system with multiple levels:

```python
class ArticleView(CRUDSundaeView):
    model = Article
    login_required = True  # Require authentication
    permission_required = ['articles.view_article']  # Global permission

    # Per-action permissions
    create_permission_required = ['articles.add_article']
    update_permission_required = ['articles.change_article']
    delete_permission_required = ['articles.delete_article']

    # Custom permission logic
    def has_permission(self):
        if not super().has_permission():
            return False
        # Add custom checks
        return self.request.user.is_staff
```

### Error Handling

Comprehensive error handling with user-friendly messages:

- **Database Errors**: IntegrityError, OperationalError automatically caught
- **Validation Errors**: Form and model validation errors displayed
- **Permission Errors**: PermissionDenied handled gracefully
- **User-Friendly Messages**: Technical errors converted to readable messages
- **Logging**: All errors logged with context

### Success Messages

Automatic success messages for all operations:

```python
class ArticleView(CRUDSundaeView):
    model = Article
    success_message_create = "{verbose_name} '{obj}' was created successfully!"
    success_message_update = "{verbose_name} was updated successfully."
    success_message_delete = "{verbose_name} was deleted successfully."
    enable_success_messages = True  # Enable/disable globally
```

### Tailwind CSS & Styling

- **Pre-built Templates**: Default templates styled with Tailwind CSS
- **Customizable**: Override templates or extend base templates
- **Responsive**: Mobile-friendly out of the box
- **Accessible**: ARIA labels and semantic HTML

### Additional Features

- **Field-Level Customization**: Specify different fields for list, create, update views
- **Context Object Names**: Automatic or custom context variable names
- **Logging Integration**: Built-in logger for all view operations
- **List Display Links**: Configure which fields link to detail view
- **Empty State Handling**: Customizable empty state with `allow_empty`
- **Widget Customization**: Override form widgets per field

## Complete Usage Example

### Standard Example (Using Primary Keys)

Here's a complete example using standard Django primary keys (no extra dependencies):

```python
# models.py
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ])
    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
```

```python
# views.py
from sundae.views import CRUDSundaeView, action, bulk_action
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Article

class ArticleView(CRUDSundaeView):
    model = Article
    lookup_field = 'pk'  # Use primary key for URLs (default is 'sqid')

    # Field configuration
    fields = ['title', 'content', 'category', 'status']
    list_fields = ['title', 'author', 'status', 'created_at']
    search_fields = ['title', 'content', 'author__username']

    # Pagination and filtering
    paginate_by = 20
    filterset_fields = ['status', 'category']

    # Permissions
    login_required = True
    create_permission_required = ['articles.add_article']

    # Validation hooks
    def clean_object(self, obj):
        if obj.status == 'published' and not obj.content:
            raise ValidationError("Published articles must have content")

    def before_create(self, form):
        form.instance.author = self.request.user

    def after_create(self, obj):
        messages.info(self.request, f"New article '{obj.title}' created!")

    # Custom action for single objects
    @action(detail=True, url_path="publish", permission_required="articles.publish_article")
    def publish_article(self, request, pk):
        article = self.get_object()
        article.status = 'published'
        article.save()
        messages.success(request, f"'{article.title}' has been published!")
        return HttpResponseRedirect(self.get_list_url())

    # Bulk action for multiple objects
    @bulk_action(display_name="Archive Selected", confirmation_required=True)
    def archive_selected(self, request, queryset):
        queryset.update(status='archived')
        return len(queryset), "archived"

    # Enable bulk actions
    bulk_edit_actions = ['archive_selected']
```

```python
# urls.py
from django.urls import path, include
from .views import ArticleView

urlpatterns = [
    path('', include(ArticleView.get_urls())),
]
```

This generates the following URLs automatically:
- `/article/` - List all articles (with search and filters)
- `/article/create/` - Create new article
- `/article/<int:pk>/` - View article detail
- `/article/<int:pk>/update/` - Edit article
- `/article/<int:pk>/delete/` - Delete article (with confirmation)
- `/article/<int:pk>/publish/` - Custom publish action
- `/article/bulk-update/` - Process bulk actions

### Alternative Example (Using Sqids)

If you want obfuscated, URL-safe IDs instead of sequential integers:

```bash
pip install django-sqids
```

```python
# models.py
from django.db import models
from django_sqids import SqidsField

class Article(models.Model):
    sqid = SqidsField(real_field_name='id')  # Add sqid field
    title = models.CharField(max_length=200)
    content = models.TextField()
    # ... other fields ...
```

```python
# views.py
class ArticleView(CRUDSundaeView):
    model = Article
    lookup_field = 'sqid'  # Use sqid for URLs (this is the default)

    # ... rest of configuration ...

    @action(detail=True, url_path="publish")
    def publish_article(self, request, sqid):  # Parameter matches lookup_field
        article = self.get_object()
        # ... action logic ...
```

This generates URLs with sqids:
- `/article/` - List all articles
- `/article/create/` - Create new article
- `/article/<slug:sqid>/` - View article detail (e.g., `/article/abc123/`)
- `/article/<slug:sqid>/update/` - Edit article
- `/article/<slug:sqid>/delete/` - Delete article
- `/article/<slug:sqid>/publish/` - Custom publish action

**Benefits of sqids**: Non-sequential IDs, URL-safe, obfuscated from users, prevents enumeration attacks.

## Available Views

For those who prefer separate view classes for each action, CRUDSundae also provides individual view classes:

- `SundaeListView` - For listing objects
- `SundaeDetailView` - For displaying a single object
- `SundaeCreateView` - For creating new objects
- `SundaeUpdateView` - For updating existing objects
- `SundaeDeleteView` - For deleting objects

**Note**: Using `CRUDSundaeView` with `get_urls()` is the recommended approach as it provides the complete feature set including custom actions and bulk operations.

## Examples

Check out the `examples/` directory for more detailed usage examples.

## Requirements

### Core Requirements

- **Python 3.8+**: Minimum Python version
- **Django 3.2+**: Compatible with Django 3.2, 4.0, 4.1, 4.2, and 5.0+
- **django-filter 2.0+**: Required dependency for filtering functionality
- **django-widget-tweaks**: optional used in the example demo
All core requirements are automatically installed when you install django-crud-sundae.

### Optional Dependencies

- **HTMX**: For dynamic, AJAX-like interactions without writing JavaScript
  ```html
  <script src="https://unpkg.com/htmx.org@1.9.10"></script>
  ```

- **Tailwind CSS**: For styling the default templates
  ```html
  <script src="https://cdn.tailwindcss.com"></script>
  ```

- **django-sqids**: Only required if you set `lookup_field = 'sqid'` for obfuscated, URL-safe IDs
  ```bash
  pip install django-sqids
  ```
  **Note**: Most users can skip this and use `lookup_field = 'pk'` instead (standard Django primary keys)

### Configuration Requirements

Add `sundae` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'sundae',
    'django_filters',  # If using filters
    # ...
]
```

### Model Requirements

CRUDSundae works with any Django model, but certain features have specific requirements:

1. **Lookup Field**: Configure which field to use for URL object lookups via `lookup_field`:
   - **`'pk'`** (recommended for most users): Uses Django's standard primary key - no extra setup required
   - **`'sqid'`** (default in CRUDSundaeView): Requires adding `django-sqids` and a `sqid` field to your model - provides URL-safe, obfuscated IDs
   - **`'slug'`**, **`'uuid'`**, or any unique field: Use any unique model field for URLs

   **Example configurations:**
   ```python
   # Using primary key (most common, no dependencies)
   class ArticleView(CRUDSundaeView):
       model = Article
       lookup_field = 'pk'

   # Using slug
   class ArticleView(CRUDSundaeView):
       model = Article
       lookup_field = 'slug'

   # Using sqid (requires django-sqids)
   class ArticleView(CRUDSundaeView):
       model = Article
       lookup_field = 'sqid'  # This is the default
   ```

2. **String Representation**: Define `__str__()` method for readable object names in messages and lists

3. **Permissions**: If using permission-based access, ensure your model has appropriate permissions defined

### Template Requirements

CRUDSundae provides default templates that work out of the box, but you can customize by creating templates in your app:

```
your_app/
├── templates/
│   └── your_app/
│       ├── modelname_list.html
│       ├── modelname_form.html
│       ├── modelname_detail.html
│       └── modelname_confirm_delete.html
```

Templates can extend `sundae/base.html` or your own base template.

## Configuration Reference

### Essential Attributes

```python
class MyView(CRUDSundaeView):
    # Model configuration
    model = MyModel                    # Required: The Django model to use
    queryset = MyModel.objects.all()   # Optional: Custom base queryset

    # Field configuration
    fields = ['field1', 'field2']      # Fields to show in forms
    list_fields = ['field1', 'field3'] # Fields to show in list view
    create_fields = ['field1']         # Fields for create form (overrides fields)
    update_fields = ['field1']         # Fields for update form (overrides fields)

    # Search and filtering
    search_fields = ['title', 'content__icontains']  # Fields to search
    filterset_fields = ['status', 'category']        # Fields to filter on
    filterset_class = MyFilterSet                    # Custom FilterSet class

    # Pagination
    paginate_by = 25                   # Items per page (None = no pagination)
    allow_empty = True                 # Allow empty list views

    # Object lookup
    lookup_field = 'pk'                # Field to use for URL lookups
                                       # Common values: 'pk', 'slug', 'uuid', 'sqid'
                                       # Default: 'sqid' (requires django-sqids)
    lookup_url_kwarg = 'pk'            # URL parameter name (usually matches lookup_field)

    # Templates
    template_name = 'my_template.html' # Override template
    context_object_name = 'article'    # Context variable name

    # Permissions
    login_required = True              # Require authentication
    permission_required = ['app.view_model']  # Global permissions
    create_permission_required = ['app.add_model']
    update_permission_required = ['app.change_model']
    delete_permission_required = ['app.delete_model']
    raise_exception = False            # Raise PermissionDenied vs redirect

    # Actions
    list_item_actions = ['update', 'delete', 'detail']  # Actions shown per item
    bulk_edit_actions = ['delete_selected']             # Enabled bulk actions
    excluded_actions = ['detail']                       # Actions to exclude

    # Messages
    enable_success_messages = True
    success_message_create = "{verbose_name} was created successfully."
    success_message_update = "{verbose_name} was updated successfully."
    success_message_delete = "{verbose_name} was deleted successfully."

    # HTMX
    enable_htmx_support = True         # Enable HTMX integration
```

### Validation Hooks (in execution order)

```python
def clean_object(self, obj):           # Custom validation before save
def before_save(self, form):           # Called before create AND update
def before_create(self, form):         # Called only before create
def before_update(self, form):         # Called only before update
# --- Object is saved to database ---
def after_create(self, obj):           # Called only after create
def after_update(self, obj):           # Called only after update
def after_save(self, obj, created):    # Called after create AND update
def before_delete(self, obj):          # Called before delete
# --- Object is deleted from database ---
def after_delete(self, obj_id):        # Called after delete
```

### Custom Methods to Override

```python
def get_queryset(self):                # Customize base queryset
def get_context_data(self, **kwargs):  # Add custom context variables
def get_form_class(self):              # Use custom form class
def get_success_url(self):             # Customize redirect after success
def get_template_names(self):          # Customize template resolution
def has_permission(self):              # Custom permission logic
```

## License

MIT License - see LICENSE file for details.    
