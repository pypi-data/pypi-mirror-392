# Easy Django CSV

Memory-efficient CSV export library for Django with support for both traditional and streaming exports.

## Installation
```bash
pip install easy-django-csv
```

## Quick Start

### Basic CSV Export

The simplest way to export data with manual row management:
```python
from easy_django_csv.exporters import CSVExporter

def export_users(request):
    exporter = CSVExporter(
        headers=['ID', 'Name', 'Email'],
        filename='users_export'
    )
    
    for user in User.objects.all():
        exporter.add_row([user.id, user.name, user.email])
    
    return exporter.export()
```

### Model CSV Export

Automatically export a Django model with custom serializer:
```python
from easy_django_csv.exporters import ModelCSVExport

def export_users(request):
    def user_serializer(user):
        return [user.id, user.name, user.email, user.date_joined]
    
    exporter = ModelCSVExport(
        headers=['ID', 'Name', 'Email', 'Joined'],
        filename='users',
        serializer=user_serializer,
        queryset=User.objects.all()
    )
    
    return exporter.export()
```

### Auto-Generated Headers

Let the exporter generate headers from model fields:
```python
from easy_django_csv.exporters import ModelCSVExport

def export_users(request):
    exporter = ModelCSVExport(
        filename='users',
        serializer=lambda u: [u.id, u.name, u.email],
        queryset=User.objects.all()
        # headers will be auto-generated from model fields
    )
    
    return exporter.export()
```

### Streaming Export (Large Datasets)

For datasets with thousands of rows, use streaming to reduce memory usage:
```python
from easy_django_csv.exporters import StreamingModelCSVExport

def export_users(request):
    exporter = StreamingModelCSVExport(
        headers=['ID', 'Name', 'Email'],
        filename='users_large',
        serializer=lambda u: [u.id, u.name, u.email],
        iterator=User.objects.all().iterator(chunk_size=1000)
    )
    
    return exporter.export()
```

### Auto Export Model (Convenience Function)

Export all fields from a model automatically:
```python
from easy_django_csv.exporters import export_model

def export_users(request):
    return export_model(User.objects.all())
```

## API Reference

### CSVExporter

Traditional CSV exporter with manual row management.

**Parameters:**
- `headers` (List[str]): Column headers
- `filename` (str): Output filename without .csv extension (default: "export")
- `validation` (bool): Validate row lengths match headers (default: True)

**Methods:**
- `add_row(row: List)`: Add a single row
- `add_rows(rows: List[List])`: Add multiple rows
- `export()`: Returns HttpResponse

**Example:**
```python
exporter = CSVExporter(headers=['Name', 'Age'])
exporter.add_row(['Alice', 30])
exporter.add_row(['Bob', 25])
return exporter.export()
```

### ModelCSVExport

Export Django querysets with automatic iteration.

**Parameters:**
- `headers` (List[str], optional): Column headers (auto-generated if None)
- `filename` (str): Output filename (default: "export")
- `serializer` (callable): Function to convert model instance to list
- `queryset` (QuerySet): Django queryset to export
- `hide_headers` (bool): Skip writing headers (default: False)

**Example:**
```python
exporter = ModelCSVExport(
    headers=['ID', 'Email'],
    filename='newsletter',
    serializer=lambda n: [n.id, n.email],
    queryset=Newsletter.objects.filter(active=True)
)
return exporter.export()
```

### StreamingModelCSVExport

Memory-efficient streaming export for large datasets.

**Parameters:**
- `headers` (List[str], optional): Column headers
- `filename` (str): Output filename (default: "export")
- `serializer` (callable): Function to convert model instance to list
- `iterator` (iterator): Django queryset with .iterator() called

**Example:**
```python
exporter = StreamingModelCSVExport(
    headers=['ID', 'Name', 'Email'],
    serializer=lambda u: [u.id, u.name, u.email],
    iterator=User.objects.all().iterator(chunk_size=2000)
)
return exporter.export()
```

### export_model()

Convenience function to export all model fields automatically.

**Parameters:**
- `queryset` (QuerySet): Django queryset to export

**Returns:** HttpResponse with CSV data

**Example:**
```python
return export_model(User.objects.filter(is_active=True))
```

## Advanced Examples

### Custom Serializer with Formatting
```python
from datetime import datetime

def user_serializer(user):
    return [
        user.id,
        user.get_full_name(),
        user.email,
        'Active' if user.is_active else 'Inactive',
        user.date_joined.strftime('%Y-%m-%d')
    ]

exporter = ModelCSVExport(
    headers=['ID', 'Full Name', 'Email', 'Status', 'Joined'],
    serializer=user_serializer,
    queryset=User.objects.all()
)
```

### Filtered Export
```python
from django.utils import timezone
from datetime import timedelta

# Export users who joined in the last 30 days
last_month = timezone.now() - timedelta(days=30)
recent_users = User.objects.filter(date_joined__gte=last_month)

exporter = ModelCSVExport(
    filename='recent_users',
    serializer=lambda u: [u.id, u.email, u.date_joined],
    queryset=recent_users
)
return exporter.export()
```

### Export with Related Fields
```python
def order_serializer(order):
    return [
        order.id,
        order.customer.name,  # ForeignKey
        order.customer.email,
        order.total,
        order.created_at.strftime('%Y-%m-%d')
    ]

# Use select_related for performance
queryset = Order.objects.select_related('customer').all()

exporter = ModelCSVExport(
    headers=['Order ID', 'Customer', 'Email', 'Total', 'Date'],
    serializer=order_serializer,
    queryset=queryset
)
```

### Method Chaining with CSVExporter
```python
def export_products(request):
    return (
        CSVExporter(headers=['ID', 'Name', 'Price'])
        .add_row([1, 'Product A', 19.99])
        .add_row([2, 'Product B', 29.99])
        .add_row([3, 'Product C', 39.99])
        .export()
    )
```

## Performance Tips

1. **Use streaming for large datasets** (more than 10,000 rows)
2. **Always use .iterator()** with StreamingModelCSVExport
3. **Use .select_related()** and .prefetch_related() to avoid N+1 queries
4. **Set appropriate chunk_size** in iterator (1000-2000 is usually good)
```python
# Good: Efficient for large datasets
queryset = User.objects.select_related('profile').iterator(chunk_size=1000)
exporter = StreamingModelCSVExport(
    serializer=lambda u: [u.id, u.profile.bio],
    iterator=queryset
)

# Bad: Loads everything into memory
queryset = User.objects.all()  # Don't pass this to StreamingModelCSVExport
```

## When to Use Each Exporter

| Exporter | Use Case | Dataset Size |
|----------|----------|--------------|
| CSVExporter | Manual row control, simple exports | Small (< 1000 rows) |
| ModelCSVExport | Standard Django model exports | Small to Medium (< 10,000 rows) |
| StreamingModelCSVExport | Large exports, memory efficient | Large (> 10,000 rows) |
| export_model() | Quick exports with all fields | Any size |

## Requirements

- Python >= 3.8
- Django >= 3.2

## License

MIT License