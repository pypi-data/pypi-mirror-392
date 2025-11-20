# Django Admin Trap 🔐

A completely fake Django admin login page that mimics the real Django admin perfectly. Perfect for security through obscurity, honeypots, or just confusing attackers.

**Warning**: This is a trap! It looks exactly like the real Django admin but doesn't actually log anyone in.

## 🚀 Features

- **Perfect Disguise**: Looks identical to the real Django admin login
- **No Database**: Zero database interactions - completely stateless
- **No Logging**: Doesn't store any credentials or attempt data
- **Always Fails**: Every login attempt shows "invalid credentials" error
- **Plug & Play**: Setup in 2 minutes
- **Django Native**: Uses Django's actual admin templates and styling

## 📦 Installation

```bash
pip install django-admin-trap
```

## ⚡ Quick Setup

1. **Add to INSTALLED_APPS** in `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'django_admin_trap',
]
```

2. **Include URLs** in your main `urls.py`:

**Option A**: Replace real admin (recommended for traps):

```python
urlpatterns = [
    path('admin/', include('django_admin_trap.urls')),  # Fake admin
    # ... your other URLs
]
```

**Option B**: Use alongside real admin:

```python
urlpatterns = [
    path('admin/', include('django_admin_trap.urls')),  # Fake admin
    path('real-admin/', admin.site.urls),  # Real admin (hidden)
    # ... your other URLs
]
```

**Option C**: Multiple trap endpoints:

```python
urlpatterns = [
    path('admin/', include('django_admin_trap.urls')),
    path('wp-admin/', include('django_admin_trap.urls')),
    path('administrator/', include('django_admin_trap.urls')),
    path('real-admin/', admin.site.urls),  # Your actual admin
]
```

## 🎯 How It Works

- Any URL under the trap path shows the fake login page
- All login attempts fail with "invalid credentials" error
- Shows proper username for authenticated non-staff users
- Uses Django's actual admin templates for perfect disguise
- No data is stored, logged, or processed

## 🛡️ Use Cases

### 1. **Honeypot Security**

```python
# Put traps on common admin URLs
urlpatterns = [
    path('admin/', include('django_admin_trap.urls')),  # Main trap
    path('wp-admin/', include('django_admin_trap.urls')),  # WordPress trap
    path('real-admin/', admin.site.urls),  # Your actual admin
]
```

### 2. **Development Mock**

```python
# settings.py
if DEBUG:
    urlpatterns = [
        path('admin/', include('django_admin_trap.urls')),  # Fake admin for dev
    ]
else:
    urlpatterns = [
        path('admin/', admin.site.urls),  # Real admin for production
    ]
```

### 3. **Client Demos**

```python
# Show clients the admin interface without giving access
urlpatterns = [
    path('demo-admin/', include('django_admin_trap.urls')),
]
```

## 🔧 Configuration

No configuration needed! The trap works out of the box.

### Optional: Custom Template

If you want to customize the login page, create your own template:

1. Create `templates/admin_trap/login.html` in your project
2. Extend the base template:

```html
{% extends "admin/login.html" %}
```

## ❓ FAQ

### Q: Does this store any data?

**A**: No. Zero database interactions. Completely stateless.

### Q: Can attackers detect this is a trap?

**A**: It uses Django's actual admin templates and responses, making it very hard to distinguish from a real admin.

### Q: What about performance?

**A**: Minimal performance impact - just template rendering.

### Q: Can I use this alongside the real admin?

**A**: Yes! Put the real admin on a different URL path.

## 🚨 Security Notes

- This is a **deterrent**, not a security solution
- Use in combination with proper security measures
- Keep your actual admin secure and hidden
- Monitor your traps for suspicious activity

## 📄 License

MIT License - feel free to use in any project.

## 🔗 Links

- **PyPI**: https://pypi.org/project/django-admin-trap/
- **GitHub**: https://github.com/jamil-codes/django-admin-trap
- **Documentation**: https://django-admin-trap.jamilcodes.com/
    