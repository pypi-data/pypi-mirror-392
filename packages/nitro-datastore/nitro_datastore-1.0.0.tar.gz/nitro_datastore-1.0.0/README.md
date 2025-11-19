# Nitro DataStore

Nitro DataStore makes working with JSON data efficient and enjoyable. Access your data however you want - dot notation, dictionary style, or path-based - no schema required.

## Quick Start

```python
from nitro_datastore import NitroDataStore

# Create from a dictionary
data = NitroDataStore({
    'site': {
        'name': 'Nitro',
        'url': 'https://nitro.sh'
    }
})

# Multiple ways to access the same value
data.site.name                    # Dot notation
data['site']['name']              # Dictionary access
data.get('site.name')             # Path-based access
```

## Why Nitro DataStore?

You've probably written code like this before:

```python
config.get('site', {}).get('theme', {}).get('colors', {}).get('primary', '#000')
```

It works, but it's ugly and fragile. With Nitro DataStore, it's just:

```python
config.get('site.theme.colors.primary', '#000')
```

We built this because we were tired of writing the same nested dictionary code over and over. No schemas, no ORM complexity, just JSON that doesn't fight back.

## Table of Contents

1. [Installation](#installation)
2. [Creating a DataStore](#creating-a-datastore)
3. [Access Patterns](#access-patterns)
4. [Basic Operations](#basic-operations)
5. [File Operations](#file-operations)
6. [Path Introspection](#path-introspection)
7. [Deep Search](#deep-search)
8. [Bulk Operations](#bulk-operations)
9. [Query Builder](#query-builder)
10. [Transformations](#transformations)
11. [Data Introspection](#data-introspection)
12. [Comparison](#comparison)
13. [Security Features](#security-features)
14. [Best Practices](#best-practices)
15. [API Reference](#api-reference)

## Installation

Install via pip:

```bash
pip install nitro-datastore
```

For development:

```bash
git clone https://github.com/nitro-sh/nitro-datastore.git
cd nitro-datastore
pip install -e .
```

## Creating a DataStore

### From a Dictionary

```python
data = NitroDataStore({
    'title': 'Welcome',
    'settings': {
        'theme': 'dark',
        'language': 'en'
    }
})
```

### From a JSON File

```python
data = NitroDataStore.from_file('data/config.json')
```

### From a Directory (Auto-merge)

Load and merge all JSON files from a directory. Files are merged alphabetically, with later files overriding earlier ones:

```python
data = NitroDataStore.from_directory('data/')
```

**Example:**

**data/site.json:**
```json
{
  "site": {
    "name": "Nitro",
    "url": "https://nitro.sh"
  }
}
```

**data/theme.json:**
```json
{
  "site": {
    "name": "Updated Site Name"
  },
  "theme": {
    "colors": {
      "primary": "#007bff"
    }
  }
}
```

**Result:**
```python
data.site.name  # "Updated Site Name" (overridden by theme.json)
data.site.url   # "https://example.com" (preserved from site.json)
data.theme.colors.primary  # "#007bff" (added by theme.json)
```

## Access Patterns

NitroDataStore supports three access patterns - use whichever feels most natural:

### 1. Dot Notation (Recommended)

```python
data = NitroDataStore({
    'user': {
        'name': 'Sean',
        'email': 'sean@nitro.sh'
    }
})

# Read
print(data.user.name)  # "Sean"

# Write
data.user.name = 'Sean Nieuwoudt'
```

### 2. Dictionary Access

DataStore instances behave like nested dictionaries:

```python
# Read
print(data['user']['name'])  # "Sean"

# Write
data['user']['email'] = 'sean@underwulf.com'

# Check existence
if 'user' in data:
    print("User data exists")

# Delete
del data['user']['email']
```

### 3. Path-based Access

Best for dynamic paths and defaults:

```python
# Get with defaults
name = data.get('user.name', 'Anonymous')
theme = data.get('user.settings.theme', 'light')

# Set nested values (creates intermediate dicts)
data.set('config.cache.ttl', 3600)

# Delete nested values
deleted = data.delete('config.cache.ttl')

# Check existence
if data.has('user.settings.notifications'):
    print("Notifications setting exists")
```

## Basic Operations

### Setting Values

```python
data = NitroDataStore()

# Simple values
data.set('title', 'Home Page')
data.set('count', 42)

# Nested values (auto-creates intermediate dicts)
data.set('config.theme.colors.primary', '#007bff')

# Lists and complex structures
data.set('tags', ['python', 'web', 'static-site'])
```

### Getting Values

```python
# With defaults
title = data.get('title', 'Untitled')
color = data.get('config.theme.colors.primary', '#000000')

# Check before accessing
if data.has('featured.post'):
    featured = data.get('featured.post')
```

### Merging Data

```python
base = NitroDataStore({'site': {'name': 'Original', 'url': 'nitro.sh'}})
updates = NitroDataStore({'site': {'name': 'New Name'}, 'theme': 'dark'})

base.merge(updates)

# Result: site.name updated, site.url preserved, theme added
```

### Iteration

```python
# Iterate over top-level keys
for key in data.keys():
    print(key)

# Iterate over values
for value in data.values():
    print(value)

# Iterate over items
for key, value in data.items():
    print(f"{key}: {value}")
```

## File Operations

### Loading Data

```python
# From JSON file
config = NitroDataStore.from_file('config.json')

# From directory with custom pattern
data = NitroDataStore.from_directory('data/', pattern='*.config.json')

# Using load_data() helper
from nitro import load_data

data = load_data('data/site.json')  # Returns NitroDataStore
raw = load_data('data/site.json', wrap=False)  # Returns plain dict
```

### Saving Data

```python
data = NitroDataStore({'site': {'name': 'My Site'}})

# Save to JSON file (creates parent directories if needed)
data.save('output/config.json')

# Custom indentation
data.save('output/config.json', indent=4)
```

## Path Introspection

Don't know the structure of your JSON? No problem. These tools let you explore and discover your data structure on the fly - perfect for working with third-party APIs or inherited codebases.

### list_paths()

List all paths in your data structure:

```python
data = NitroDataStore({
    'site': {'name': 'Test', 'url': 'example.com'},
    'posts': [{'title': 'A'}, {'title': 'B'}]
})

paths = data.list_paths()
# ['site', 'site.name', 'site.url', 'posts', 'posts.0', 'posts.0.title', 'posts.1', 'posts.1.title']

# Filter by prefix
site_paths = data.list_paths(prefix='site')
# ['site', 'site.name', 'site.url']
```

### find_paths()

Find paths matching glob-like patterns:

```python
# Find all titles
titles = data.find_paths('posts.*.title')
# ['posts.0.title', 'posts.1.title']

# Find all 'url' keys anywhere
urls = data.find_paths('**.url')
```

**Wildcards:**
- `*` - Matches any single path segment
- `**` - Matches any number of path segments

### get_many()

Get multiple values at once:

```python
values = data.get_many(['site.name', 'site.url', 'theme', 'missing'])
# {
#     'site.name': 'Nitro',
#     'site.url': 'nitro.sh',
#     'theme': None,
#     'missing': None
# }
```

## Deep Search

Find values anywhere in your structure based on criteria.

### find_all_keys()

Find all occurrences of a key name:

```python
data = NitroDataStore({
    'site': {'url': 'nitro.sh'},
    'social': {
        'github': {'url': 'github.com/sn'},
        'twitter': {'url': 'twitter.com/ghstcode'}
    }
})

urls = data.find_all_keys('url')
# {
#     'site.url': 'nitro.sh',
#     'social.github.url': 'github.com/sn',
#     'social.twitter.url': 'twitter.com/ghstcode'
# }
```

### find_values()

Find values matching a predicate:

```python
# Find all .jpg images
jpgs = data.find_values(lambda v: isinstance(v, str) and v.endswith('.jpg'))

# Find all numbers greater than 100
big_nums = data.find_values(lambda v: isinstance(v, (int, float)) and v > 100)

# Find all email addresses
emails = data.find_values(lambda v: isinstance(v, str) and '@' in v)
```

## Bulk Operations

Perform operations on multiple values at once.

### update_where()

Update all values matching a condition:

```python
# Upgrade all HTTP URLs to HTTPS
count = data.update_where(
    condition=lambda path, value: isinstance(value, str) and 'http://' in value,
    transform=lambda value: value.replace('http://', 'https://')
)
# Returns: number of values updated
```

### remove_nulls()

Remove all `None` values:

```python
data = NitroDataStore({
    'user': {'name': 'Sean', 'email': None},
    'items': [1, None, 2, None, 3]
})

count = data.remove_nulls()  # Returns: 3

# Result: {'user': {'name': 'Sean'}, 'items': [1, 2, 3]}
```

### remove_empty()

Remove all empty dictionaries and lists:

```python
data = NitroDataStore({
    'config': {},
    'tags': [],
    'nested': {'value': 1, 'empty': {}}
})

count = data.remove_empty()  # Returns: 3

# Result: {'nested': {'value': 1}}
```

## Query Builder

The Query Building helps you filter and transform your data with a query interface that actually makes sense. Chain operations together like you would in SQL or Pandas.

### Basic Usage

```python
data = NitroDataStore({
    'posts': [
        {'title': 'Python Tips', 'category': 'python', 'views': 150, 'published': True},
        {'title': 'Web Dev', 'category': 'web', 'views': 200, 'published': True},
        {'title': 'Draft', 'category': 'python', 'views': 0, 'published': False}
    ]
})

# Get published posts
published = data.query('posts').where(lambda p: p.get('published')).execute()
```

### Filtering with where()

```python
# Multiple conditions (AND logic)
popular_python = (data.query('posts')
    .where(lambda p: p.get('category') == 'python')
    .where(lambda p: p.get('views') > 100)
    .execute())
```

### Sorting

```python
# Ascending
by_views = data.query('posts').sort(key=lambda p: p.get('views')).execute()

# Descending
popular_first = data.query('posts').sort(key=lambda p: p.get('views'), reverse=True).execute()
```

### Pagination

```python
# First page (10 items)
page1 = data.query('posts').limit(10).execute()

# Second page
page2 = data.query('posts').offset(10).limit(10).execute()
```

### Complex Queries

```python
# Published Python posts, sorted by views, top 5
top_python = (data.query('posts')
    .where(lambda p: p.get('category') == 'python')
    .where(lambda p: p.get('published'))
    .sort(key=lambda p: p.get('views'), reverse=True)
    .limit(5)
    .execute())
```

### Utility Methods

```python
# Count without fetching
count = data.query('posts').where(lambda p: p.get('published')).count()

# Get first result only
first = data.query('posts').sort(key=lambda p: p.get('views'), reverse=True).first()

# Extract single field
titles = data.query('posts').pluck('title')
# ['Python Tips', 'Web Dev', 'Draft']

# Group by field
by_category = data.query('posts').group_by('category')
# {'python': [...], 'web': [...]}
```

## Transformations

Need to clean up messy data? Transform keys from kebab-case to snake_case? These methods create new versions of your data without mutating the original.

### transform_all()

Transform all values:

```python
data = NitroDataStore({
    'user': {'name': 'sean', 'email': 'sean@nitro.sh'}
})

# Uppercase all strings
upper = data.transform_all(lambda path, value: value.upper() if isinstance(value, str) else value)

# Original unchanged
print(data.user.name)  # 'sean'
print(upper.user.name)  # 'SEAN'
```

### transform_keys()

Transform all keys:

```python
data = NitroDataStore({
    'user-info': {'first-name': 'Sean', 'last-name': 'Nieuwoudt'}
})

# Convert kebab-case to snake_case
snake = data.transform_keys(lambda k: k.replace('-', '_'))

# Result: {'user_info': {'first_name': 'Sean', 'last_name': 'Nieuwoudt'}}
```

## Data Introspection

Understand the structure of your data.

### describe()

Get structural description:

```python
data = NitroDataStore({
    'site': {'name': 'My Site', 'year': 2024},
    'posts': [{'title': 'A'}, {'title': 'B'}],
    'active': True
})

description = data.describe()
# {
#     'site': {
#         'type': 'dict',
#         'keys': ['name', 'year'],
#         'structure': {...}
#     },
#     'posts': {
#         'type': 'list',
#         'length': 2,
#         'item_types': ['dict']
#     },
#     'active': {'type': 'bool', 'value': True}
# }
```

### stats()

Get statistics:

```python
stats = data.stats()
# {
#     'total_keys': 3,
#     'max_depth': 3,
#     'total_dicts': 3,
#     'total_lists': 1,
#     'total_values': 4
# }
```

## Comparison

Compare datastores and detect differences.

### equals()

Check equality:

```python
data1 = NitroDataStore({'name': 'Alice', 'age': 30})
data2 = NitroDataStore({'name': 'Alice', 'age': 30})
data3 = NitroDataStore({'name': 'Bob', 'age': 25})

data1.equals(data2)  # True
data1.equals(data3)  # False
data1.equals({'name': 'Alice', 'age': 30})  # True (works with dicts)
```

### diff()

Find differences:

```python
old = NitroDataStore({'site': {'name': 'Old', 'url': 'example.com'}, 'theme': 'light'})
new = NitroDataStore({'site': {'name': 'New', 'url': 'example.com'}, 'version': '2.0'})

diff = old.diff(new)

# diff['added']: {'version': '2.0'}
# diff['removed']: {'theme': 'light'}
# diff['changed']: {'site.name': {'old': 'Old', 'new': 'New'}}
```

## Security Features

I've added basic protections to commong security gotchas when working directly with files.

### 1. Path Traversal Protection

Prevent directory traversal attacks when loading files by restricting access to a specific directory.

**Use the `base_dir` parameter:**

```python
# Restrict file access to a specific directory
safe_dir = '/var/app/data'
config = NitroDataStore.from_file(user_provided_path, base_dir=safe_dir)
```

**How it works:**
- Resolves and validates file paths before loading
- Blocks attempts to access files outside `base_dir` using `../` or absolute paths
- Raises `ValueError` if path traversal is detected

**Example:**

```python
from pathlib import Path

data_dir = Path('/var/app/uploads')

# Safe: file is within base_dir
data = NitroDataStore.from_file(data_dir / 'config.json', base_dir=data_dir)

# Blocked: path traversal attempt
try:
    evil_path = data_dir / '..' / '..' / 'etc' / 'passwd'
    data = NitroDataStore.from_file(evil_path, base_dir=data_dir)
except ValueError as e:
    print(f"Security violation: {e}")
```

**When to use:**
- Loading files from user-supplied paths
- Working with uploaded files
- Multi-tenant applications
- Any scenario with untrusted file paths

### 2. File Size Limits

Prevent someone from uploading a 5GB JSON file and causing server issues on render.

**Use the `max_size` parameter (in bytes):**

```python
# Limit file size to 10 MB
max_bytes = 10 * 1024 * 1024
config = NitroDataStore.from_file(user_file, max_size=max_bytes)
```

**How it works:**
- Checks file size before loading content
- Raises `ValueError` with human-readable error message if file exceeds limit
- Works with both `from_file()` and `from_directory()`

**Example:**

```python
# Safe limits for different use cases
LIMITS = {
    'config': 1024 * 1024,          # 1 MB for config files
    'data': 50 * 1024 * 1024,       # 50 MB for data files
    'upload': 100 * 1024 * 1024,    # 100 MB for uploads
}

try:
    data = NitroDataStore.from_file(path, max_size=LIMITS['config'])
except ValueError as e:
    if "exceeds maximum" in str(e):
        print("File too large!")
```

### 3. Path Validation

Catch typos and malformed paths before they cause weird bugs.

**Validation rules:**
- Path cannot be empty or whitespace-only
- Path cannot contain leading, trailing, or consecutive dots
- Applied to: `get()`, `set()`, `delete()`, `has()`

**Example:**

```python
data = NitroDataStore({'user': {'name': 'Alice'}})

# Valid paths - work as expected
data.get('user.name')          # OK
data.set('user.email', '...')  # OK

# Invalid paths - raise ValueError
data.get('')                   # ValueError: empty path
data.get('  ')                 # ValueError: whitespace only
data.get('.user')              # ValueError: leading dot
data.get('user.')              # ValueError: trailing dot
data.get('user..name')         # ValueError: consecutive dots
```

**Why this matters:**
- Catches typos immediately (typed `'user..name'` by accident? We'll let you know)
- No more mysterious bugs from empty or malformed paths
- Consistent behavior everywhere - no surprises
- Error messages that actually help you fix the problem

### 4. Circular Reference Protection

Detects circular references to prevent infinite recursion and stack overflow.

**Protected operations:**
- Deep copying (`to_dict()`, `copy.deepcopy()`)
- Deep merging (`merge()`)
- Transformations (`transform_all()`, `transform_keys()`)

**Example:**

```python
# Normal nested structures work fine
data = NitroDataStore({
    'level1': {'level2': {'level3': {'value': 'deep'}}}
})
copied = data.to_dict()  # [OK] OK

# Circular references are detected
circular = {'a': 1}
circular['self'] = circular  # Creates circular reference

try:
    data = NitroDataStore(circular)
    data.to_dict()  # Would cause infinite recursion
except ValueError as e:
    print(f"Circular reference detected: {e}")
```

**Protection applies to:**
- Dict-to-dict circular references
- List-to-list circular references
- Mixed dict/list circular structures

### Combined Security Example

Layer your security - one protection is good, multiple is better:

```python
from pathlib import Path
from nitro_datastore import NitroDataStore

def load_user_config(user_id: str, file_name: str) -> NitroDataStore:
    """Safely load user configuration with multiple security layers."""

    base_dir = Path(f'/var/app/users/{user_id}/configs')
    max_size = 5 * 1024 * 1024  # 5 MB limit

    if not file_name.endswith('.json'):
        raise ValueError("Only JSON files allowed")

    file_path = base_dir / file_name

    try:
        config = NitroDataStore.from_file(
            file_path,
            base_dir=base_dir,    # Prevent path traversal
            max_size=max_size     # Prevent DoS
        )

        # Path validation is automatic
        # Circular reference protection is automatic

        return config

    except FileNotFoundError:
        return NitroDataStore({})
    except ValueError as e:
        log_security_event(user_id, str(e))
        raise
```

See `examples/09_security_features.py` for comprehensive demonstrations.

## Best Practices

### 1. Use Dot Notation for Static Keys

When you know the key names, just use dot notation - it's clean and obvious:

```python
data.site.name  # Clear and concise

# Save .get() for when you need a default
data.get('site.name')  # Works, but unnecessary here
```

### 2. Use Path-based get() for Dynamic Keys

Dynamic paths? That's where `.get()` shines:

```python
# Perfect - safe with defaults
user_name = data.get(f'user.{user_id}.name', 'Anonymous')

# Don't do this - it'll blow up if the path doesn't exist
name = getattr(data.user, user_id).name
```

### 3. Load Data Once, Reuse

Don't repeatedly load the same file - your disk will thank you:

```python
# Load once at module level
SITE_DATA = NitroDataStore.from_file('data/site.json')

def process_data():
    return SITE_DATA.site.name  # Fast - already in memory
```

### 4. Merge Configuration Hierarchically

Build up config from defaults + environment overrides:

```python
# Start with defaults
config = NitroDataStore.from_file('data/defaults.json')

# Layer in environment-specific settings
if env == 'production':
    config.merge(NitroDataStore.from_file('data/production.json'))
```

### 5. Use has() Before Accessing Optional Data

Check before you leap - especially with optional fields:

```python
# Safe - won't blow up
if data.has('featured.image'):
    image = data.get('featured.image')

# Risky - raises error if featured.image doesn't exist
image = data.featured.image
```

## API Reference

### Construction & Loading

| Method                                                                 | Description                                                      |
|------------------------------------------------------------------------|------------------------------------------------------------------|
| `NitroDataStore(data)`                                                 | Create from dictionary                                           |
| `from_file(path, base_dir=None, max_size=None)`                        | Load from JSON file with optional security constraints           |
| `from_directory(path, pattern='*.json', base_dir=None, max_size=None)` | Load and merge from directory with optional security constraints |

### Basic Operations

| Method                   | Description                  | Returns |
|--------------------------|------------------------------|---------|
| `get(key, default=None)` | Get value by path            | `Any`   |
| `set(key, value)`        | Set value by path            | `None`  |
| `delete(key)`            | Delete value by path         | `bool`  |
| `has(key)`               | Check if key exists          | `bool`  |
| `merge(other)`           | Deep merge another datastore | `None`  |
| `to_dict()`              | Export as plain dictionary   | `dict`  |
| `save(path, indent=2)`   | Save to JSON file            | `None`  |

### Path Introspection

| Method                  | Description                 | Returns          |
|-------------------------|-----------------------------|------------------|
| `list_paths(prefix='')` | List all paths              | `List[str]`      |
| `find_paths(pattern)`   | Find paths matching pattern | `List[str]`      |
| `get_many(paths)`       | Get multiple values         | `Dict[str, Any]` |

### Deep Search

| Method                   | Description                    | Returns          |
|--------------------------|--------------------------------|------------------|
| `find_all_keys(key)`     | Find all occurrences of key    | `Dict[str, Any]` |
| `find_values(predicate)` | Find values matching predicate | `Dict[str, Any]` |

### Bulk Operations

| Method                               | Description              | Returns |
|--------------------------------------|--------------------------|---------|
| `update_where(condition, transform)` | Update matching values   | `int`   |
| `remove_nulls()`                     | Remove all None values   | `int`   |
| `remove_empty()`                     | Remove empty dicts/lists | `int`   |

### Query Builder

| Method                      | Description          | Returns        |
|-----------------------------|----------------------|----------------|
| `query(path)`               | Start query builder  | `QueryBuilder` |
| `.where(predicate)`         | Filter items         | `QueryBuilder` |
| `.sort(key, reverse=False)` | Sort results         | `QueryBuilder` |
| `.limit(count)`             | Limit results        | `QueryBuilder` |
| `.offset(count)`            | Skip results         | `QueryBuilder` |
| `.execute()`                | Run query            | `List[Any]`    |
| `.count()`                  | Count results        | `int`          |
| `.first()`                  | Get first result     | `Any \| None`  |
| `.pluck(key)`               | Extract field values | `List[Any]`    |
| `.group_by(key)`            | Group by field       | `dict`         |

### Transformations

| Method               | Description          | Returns          |
|----------------------|----------------------|------------------|
| `transform_all(fn)`  | Transform all values | `NitroDataStore` |
| `transform_keys(fn)` | Transform all keys   | `NitroDataStore` |

### Introspection

| Method       | Description                | Returns          |
|--------------|----------------------------|------------------|
| `describe()` | Get structural description | `Dict[str, Any]` |
| `stats()`    | Get statistics             | `Dict[str, int]` |

### Comparison

| Method          | Description      | Returns          |
|-----------------|------------------|------------------|
| `equals(other)` | Check equality   | `bool`           |
| `diff(other)`   | Find differences | `Dict[str, Any]` |

### Iteration

| Method                   | Description             | Returns           |
|--------------------------|-------------------------|-------------------|
| `keys()`                 | Get top-level keys      | `Iterator[str]`   |
| `values()`               | Get top-level values    | `Iterator[Any]`   |
| `items()`                | Get top-level items     | `Iterator[tuple]` |
| `flatten(separator='.')` | Flatten to dot-notation | `dict`            |

### Collection Utilities

| Method                         | Description         | Returns     |
|--------------------------------|---------------------|-------------|
| `filter_list(path, predicate)` | Filter list at path | `List[Any]` |

## Practical Examples

### Example 1: Cleaning Up Messy JSON

```python
# Load messy data
data = NitroDataStore.from_file('messy_data.json')

# Clean it up
data.remove_nulls()
data.remove_empty()

# Standardize URLs
data.update_where(
    lambda p, v: isinstance(v, str) and 'http://' in v,
    lambda v: v.replace('http://', 'https://')
)

# Save cleaned data
data.save('cleaned_data.json')
```

### Example 2: Finding Recent Blog Posts

```python
blog = NitroDataStore.from_directory('content/posts/')

# Get recent published posts
recent = (blog.query('posts')
    .where(lambda p: p.get('published'))
    .sort(key=lambda p: p.get('date'), reverse=True)
    .limit(10)
    .execute())

# Get all unique categories
categories = set(blog.query('posts').pluck('category'))
```

### Example 3: Migrating Old Config Files

```python
old_config = NitroDataStore.from_file('old_config.json')

# Transform to new schema
new_config = old_config.transform_keys(lambda k: k.replace('_', '-'))

# Detect changes
changes = old_config.diff(new_config)
print(f"Changed {len(changes['changed'])} keys")

new_config.save('new_config.json')
```

### Example 4: Exploring Unknown Data Structures

```python
data = NitroDataStore.from_file('unknown_structure.json')

# Understand the structure
print("Stats:", data.stats())
print("Description:", data.describe())

# Find specific data
emails = data.find_values(lambda v: isinstance(v, str) and '@' in v)
images = data.find_values(lambda v: isinstance(v, str) and v.endswith(('.jpg', '.png')))
```

## Performance Tips

1. **Use the query builder instead of loops** - It's faster and cleaner.
2. **Pattern match with find_paths()** - Don't manually traverse the tree if you can pattern match.
3. **Batch updates with update_where()** - One pass through your data beats a thousand individual updates.
4. **Use count() instead of len(execute())** - No need to fetch everything when you need a count.
5. **Load once, use everywhere** - File I/O is slow, load your data once where possible.

## License

GNU General Public License v3.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please file an issue on the GitHub repository.

## Author

[github.com/sn](https://github.com/sn)
