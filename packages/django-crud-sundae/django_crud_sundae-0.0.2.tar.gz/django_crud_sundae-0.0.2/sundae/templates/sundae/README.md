# Sundae Templates

This directory contains base templates for Django CRUD Sundae views.

## Available Templates

- `base.html` - Base template with Tailwind CSS and HTMX included

## Usage

Override these templates in your project's templates directory, or extend them:

```django
{% extends "sundae/base.html" %}

{% block content %}
    <!-- Your content here -->
{% endblock %}
```
