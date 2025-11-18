"""
Flask-ImageKit
==============

Image optimization for Flask. Converts 5MB uploads to ~200KB.

Usage:
    from flask import Flask
    from flask_imagekit import ImageOptimizer

    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'static/uploads'

    optimizer = ImageOptimizer(app)

    result = optimizer.save_product_image(file)
    if result.get('success'):
        image_url = result['image_path']
"""

__version__ = "1.0.0"

from .optimizer import ImageOptimizer, ImagePresets, ImageConfig

__all__ = ["ImageOptimizer", "ImagePresets", "ImageConfig"]
