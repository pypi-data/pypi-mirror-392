# Flask-ImageKit

**Automatic image optimization for Flask** - Transform 5MB uploads into ~200KB optimized images with WebP support, multiple sizes, and zero configuration.

[![PyPI version](https://badge.fury.io/py/flask-imagekit.svg)](https://pypi.org/project/flask-imagekit/)
[![Python Support](https://img.shields.io/pypi/pyversions/flask-imagekit.svg)](https://pypi.org/project/flask-imagekit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why Flask-ImageKit?

User-uploaded images can kill your site's performance. This package automatically:
- ✅ **Reduces file sizes by 95%** - 5MB → 200KB
- ✅ **Creates WebP versions** - Modern format with better compression
- ✅ **Generates multiple sizes** - Thumbnail, small, medium
- ✅ **Fixes orientation** - EXIF auto-rotation
- ✅ **Battle-tested** at [WallMarkets](https://wallmarkets.store)

## The Problem

```python
# User uploads a 5MB product photo
# Your server stores it as-is
# Every page load downloads 5MB
# Site is slow, bandwidth costs skyrocket
```

## The Solution

```python
# Flask-ImageKit automatically:
# 1. Resizes to 3 sizes (thumbnail, small, medium)
# 2. Creates WebP versions (better compression)
# 3. Optimizes JPEG quality
# 4. Fixes EXIF orientation
# Result: 6 variants, ~200KB total
```

## Features

### 📦 Multiple Sizes Automatically
- **Thumbnail** (150×150) - Perfect for lists and grids
- **Small** (400×400) - Product cards and previews
- **Medium** (800×800) - Detail pages and lightboxes

### 🖼️ WebP + JPEG
- WebP for modern browsers (30-50% smaller)
- JPEG fallback for older browsers
- Automatic format detection in templates

### 🔄 EXIF Auto-Rotation
Fixes sideways photos from phones automatically

### ⚡ Progressive JPEG
Loads faster with progressive rendering

### 🎯 Smart Compression
Aggressive compression without visible quality loss

## Installation

```bash
pip install flask-imagekit
```

Requires Pillow (automatically installed).

## Quick Start

```python
from flask import Flask, request
from flask_imagekit import ImageOptimizer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

optimizer = ImageOptimizer(app)

@app.route('/upload', methods=['POST'])
def upload_product_image():
    if 'image' not in request.files:
        return {'error': 'No image provided'}, 400
    
    file = request.files['image']
    result = optimizer.save_product_image(file)
    
    if result.get('success'):
        return {
            'thumbnail': result['thumbnail'],
            'small': result['small'],
            'medium': result['medium'],
            'thumbnail_webp': result['thumbnail_webp'],
            'small_webp': result['small_webp'],
            'medium_webp': result['medium_webp']
        }
    
    return {'error': result.get('error')}, 400
```

## Usage Examples

### Product Images

```python
@app.route('/products/create', methods=['POST'])
def create_product():
    # Upload and optimize product image
    result = optimizer.save_product_image(request.files['image'])
    
    if not result.get('success'):
        return {'error': result['error']}, 400
    
    # Save to database
    product = Product(
        name=request.form['name'],
        image=result['medium'],  # Main image
        image_webp=result['medium_webp'],
        thumbnail=result['thumbnail'],
        thumbnail_webp=result['thumbnail_webp']
    )
    db.session.add(product)
    db.session.commit()
    
    return {'id': product.id, 'image': result['medium']}
```

### User Avatars

```python
@app.route('/profile/avatar', methods=['POST'])
def upload_avatar():
    result = optimizer.save_avatar_image(request.files['avatar'])
    
    if result.get('success'):
        current_user.avatar = result['small']
        current_user.avatar_webp = result['small_webp']
        db.session.commit()
        return {'avatar_url': result['small']}
    
    return {'error': result['error']}, 400
```

### Blog Post Images

```python
@app.route('/blog/upload-image', methods=['POST'])
def upload_blog_image():
    result = optimizer.save_product_image(request.files['image'])
    
    # Return URL for rich text editor
    return {'url': result['medium']}
```

## Output Structure

For each uploaded image, you get **6 optimized variants**:

| Variant | Size | Format | Typical File Size | Use Case |
|---------|------|--------|-------------------|----------|
| `thumbnail` | 150×150 | JPEG | 5-10 KB | Product grids, lists |
| `thumbnail_webp` | 150×150 | WebP | 3-7 KB | Modern browsers |
| `small` | 400×400 | JPEG | 20-40 KB | Product cards |
| `small_webp` | 400×400 | WebP | 15-30 KB | Modern browsers |
| `medium` | 800×800 | JPEG | 80-150 KB | Detail pages |
| `medium_webp` | 800×800 | WebP | 50-100 KB | Modern browsers |

**Total**: ~200 KB (vs original 5 MB = **96% reduction**)

## Template Usage

### Responsive Images with WebP

```html
<!-- Product card -->
<picture>
    <source srcset="{{ product.small_webp }}" type="image/webp">
    <img src="{{ product.small }}" 
         alt="{{ product.name }}" 
         loading="lazy"
         width="400" 
         height="400">
</picture>

<!-- Thumbnail in list -->
<picture>
    <source srcset="{{ product.thumbnail_webp }}" type="image/webp">
    <img src="{{ product.thumbnail }}" 
         alt="{{ product.name }}" 
         loading="lazy"
         width="150" 
         height="150">
</picture>

<!-- Full size on detail page -->
<picture>
    <source srcset="{{ product.medium_webp }}" type="image/webp">
    <img src="{{ product.medium }}" 
         alt="{{ product.name }}" 
         loading="lazy"
         width="800" 
         height="800">
</picture>
```

### Responsive Srcset

```html
<img src="{{ product.medium }}"
     srcset="{{ product.thumbnail }} 150w,
             {{ product.small }} 400w,
             {{ product.medium }} 800w"
     sizes="(max-width: 400px) 150px,
            (max-width: 800px) 400px,
            800px"
     alt="{{ product.name }}"
     loading="lazy">
```

## Configuration

```python
# Upload directory
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Maximum file size (5MB)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# Allowed file extensions
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Image sizes (optional - these are defaults)
app.config['IMAGE_SIZES'] = {
    'thumbnail': (150, 150),
    'small': (400, 400),
    'medium': (800, 800)
}

# JPEG quality (optional - default is 85)
app.config['JPEG_QUALITY'] = 85

# WebP quality (optional - default is 80)
app.config['WEBP_QUALITY'] = 80
```

## Real-World Performance

### Before Flask-ImageKit
```
Original upload: 5.2 MB
Page load time: 8.3 seconds
Bandwidth cost: $0.52 per 100 views
```

### After Flask-ImageKit
```
Optimized images: 187 KB total (6 variants)
Page load time: 1.2 seconds
Bandwidth cost: $0.02 per 100 views
Savings: 96% file size, 85% faster, 96% cheaper
```

## API Reference

### `ImageOptimizer(app)`
Initialize the optimizer with your Flask app.

### `save_product_image(file, filename=None)`
Save and optimize a product image.

**Returns:**
```python
{
    'success': True,
    'thumbnail': 'uploads/products/abc123_thumbnail.jpg',
    'thumbnail_webp': 'uploads/products/abc123_thumbnail.webp',
    'small': 'uploads/products/abc123_small.jpg',
    'small_webp': 'uploads/products/abc123_small.webp',
    'medium': 'uploads/products/abc123_medium.jpg',
    'medium_webp': 'uploads/products/abc123_medium.webp',
    'original_size': 5242880,
    'optimized_size': 187392,
    'savings_percent': 96.4
}
```

### `save_avatar_image(file, filename=None)`
Save and optimize a user avatar (same as product image).

### `delete_image_variants(base_path)`
Delete all variants of an image.

```python
# Delete old product image when updating
optimizer.delete_image_variants(old_product.image)
```

## Error Handling

```python
result = optimizer.save_product_image(file)

if not result.get('success'):
    error = result.get('error')
    
    if 'File type not allowed' in error:
        return {'error': 'Please upload a JPG, PNG, or WebP image'}, 400
    
    if 'File too large' in error:
        return {'error': 'Image must be under 5MB'}, 400
    
    if 'Invalid image' in error:
        return {'error': 'The file is corrupted or not a valid image'}, 400
    
    return {'error': 'Image upload failed'}, 500
```

## Best Practices

### 1. Use WebP with JPEG Fallback

```html
<picture>
    <source srcset="{{ product.small_webp }}" type="image/webp">
    <img src="{{ product.small }}" alt="{{ product.name }}">
</picture>
```

### 2. Add Lazy Loading

```html
<img src="{{ product.thumbnail }}" loading="lazy" alt="{{ product.name }}">
```

### 3. Specify Dimensions

```html
<img src="{{ product.small }}" width="400" height="400" alt="{{ product.name }}">
```

### 4. Use Appropriate Sizes

- **Thumbnails** for grids and lists
- **Small** for cards and previews
- **Medium** for detail pages

### 5. Clean Up Old Images

```python
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    
    # Delete all image variants
    optimizer.delete_image_variants(product.image)
    
    db.session.delete(product)
    db.session.commit()
```

## Testing

```python
import pytest
from flask_imagekit import ImageOptimizer

def test_image_optimization(app):
    optimizer = ImageOptimizer(app)
    
    # Create test image
    from PIL import Image
    import io
    
    img = Image.new('RGB', (2000, 2000), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    # Upload and optimize
    result = optimizer.save_product_image(img_bytes, 'test.jpg')
    
    assert result['success'] is True
    assert 'thumbnail' in result
    assert 'medium_webp' in result
    assert result['savings_percent'] > 50
```

## Production Usage

This package is used in production at:
- [WallMarkets](https://wallmarkets.store) - Multi-vendor marketplace
- Processing 1000+ product images daily
- Reduced storage costs by 95%
- Improved page load times by 70%
- Saved $500/month in bandwidth costs

## Troubleshooting

### "Pillow not installed"
```bash
pip install Pillow
```

### "File type not allowed"
Check `ALLOWED_EXTENSIONS` config and file extension.

### "Images not optimizing"
Verify `UPLOAD_FOLDER` exists and is writable:
```python
import os
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
```

### "WebP not working"
Ensure Pillow is compiled with WebP support:
```python
from PIL import features
print(features.check('webp'))  # Should be True
```

## Performance Tips

1. **Use CDN** - Serve images from a CDN for faster delivery
2. **Enable caching** - Set proper cache headers
3. **Lazy load** - Use `loading="lazy"` attribute
4. **Async processing** - Process images in background for large uploads

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- 📚 [Documentation](https://github.com/wallmarkets/flask-imagekit)
- 🐛 [Issue Tracker](https://github.com/wallmarkets/flask-imagekit/issues)
- 💬 [Discussions](https://github.com/wallmarkets/flask-imagekit/discussions)

## Related Packages

- [flask-supercache](https://pypi.org/project/flask-supercache/) - Cache optimized images
- [flask-ratelimit-simple](https://pypi.org/project/flask-ratelimit-simple/) - Rate limit uploads
- [flask-security-headers](https://pypi.org/project/flask-security-headers/) - Secure file uploads

---

**Made with ❤️ by the WallMarkets team**
