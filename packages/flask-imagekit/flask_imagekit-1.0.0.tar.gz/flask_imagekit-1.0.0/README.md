# Flask-ImageKit

Image optimization for Flask. Reduces 5MB uploads to ~200KB.

## What it does

- Creates 6 optimized variants per upload (JPEG + WebP for 3 sizes)
- EXIF auto-orientation
- Progressive JPEG encoding
- Aggressive compression without visible quality loss

Built while working on [wallmarkets](https://wallmarkets.store).

## Installation

```bash
pip install flask-imagekit
```

## Usage

```python
from flask import Flask, request
from flask_imagekit import ImageOptimizer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

optimizer = ImageOptimizer(app)

@app.route('/upload', methods=['POST'])
def upload():
    result = optimizer.save_product_image(request.files['image'])
    
    if result.get('success'):
        return {'url': result['image_path']}
    
    return {'error': result.get('error')}, 400
```

## Output

For each image, you get 6 variants:

- `thumbnail` (150x150): ~5-10KB JPEG
- `thumbnail_webp`: ~3-7KB WebP
- `small` (400x400): ~20-40KB JPEG  
- `small_webp`: ~15-30KB WebP
- `medium` (800x800): ~80-150KB JPEG
- `medium_webp`: ~50-100KB WebP

Total: ~200KB vs original 5MB

## Configuration

```python
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
```

## Template usage

```html
<picture>
    <source srcset="{{ product.image_webp }}" type="image/webp">
    <img src="{{ product.image }}" alt="{{ product.name }}" loading="lazy">
</picture>
```

## License

MIT

## Contributing

Pull requests welcome. Please add tests.
