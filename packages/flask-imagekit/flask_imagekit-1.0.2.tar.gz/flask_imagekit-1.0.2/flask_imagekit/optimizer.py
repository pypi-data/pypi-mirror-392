"""
Image optimization utilities.

Production-tested image processing that reduces 5MB uploads to ~200KB
without visible quality loss.
"""

import hashlib
import os
import uuid
from typing import Any, Dict, Tuple

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


class ImagePresets:
    """Standard image size presets."""

    SIZES = {
        "avatar": (56, 56),
        "thumbnail": (150, 150),
        "small": (400, 400),
        "medium": (800, 800),
    }

    JPEG_QUALITY = {
        "avatar": 80,
        "thumbnail": 75,
        "small": 80,
        "medium": 85,
    }

    WEBP_QUALITY = {
        "avatar": 75,
        "thumbnail": 70,
        "small": 75,
        "medium": 80,
    }


class ImageConfig:
    """Configuration for image optimizer."""

    def __init__(self):
        self.upload_folder = "static/uploads"
        self.allowed_extensions = {"png", "jpg", "jpeg", "gif", "webp"}
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.max_dimension = 2000
        self.max_upload_dimension = 10000


class ImageOptimizer:
    """
    Production-grade image optimizer for Flask.

    Features:
    - Multiple size variants with WebP support
    - EXIF auto-orientation
    - Aggressive compression (75-85% quality)
    - Progressive JPEG encoding
    - Memory-safe dimension validation
    """

    def __init__(self, app=None, config=None):
        self.config = config or ImageConfig()
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize with Flask app."""
        if hasattr(app.config, 'get'):
            self.config.upload_folder = app.config.get('UPLOAD_FOLDER', self.config.upload_folder)
            self.config.allowed_extensions = app.config.get('ALLOWED_EXTENSIONS', self.config.allowed_extensions)
            self.config.max_file_size = app.config.get('MAX_CONTENT_LENGTH', self.config.max_file_size)

    def allowed_file(self, filename):
        """Check if file extension is allowed."""
        return ('.' in filename and
                filename.rsplit('.', 1)[1].lower() in self.config.allowed_extensions)

    @staticmethod
    def get_file_hash(file_stream):
        """Generate hash of file content."""
        file_stream.seek(0)
        file_hash = hashlib.md5(file_stream.read()).hexdigest()
        file_stream.seek(0)
        return file_hash

    @staticmethod
    def prepare_image(img: Image.Image) -> Image.Image:
        """
        Prepare image: auto-orient, convert to RGB.
        """
        # Auto-orient using EXIF
        img = ImageOps.exif_transpose(img)

        # Convert RGBA/P to RGB with white background
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            if img.mode in ("RGBA", "LA"):
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        return img

    @staticmethod
    def enhance_image(img: Image.Image) -> Image.Image:
        """Apply sharpening and contrast enhancement."""
        # Subtle sharpening
        img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))

        # Slight contrast boost
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)

        return img

    @staticmethod
    def create_variant(img: Image.Image, size: Tuple[int, int],
                      is_thumbnail: bool = False) -> Image.Image:
        """
        Create image variant.

        Args:
            img: PIL Image
            size: Target (width, height)
            is_thumbnail: If True, square crop; else maintain aspect ratio
        """
        if is_thumbnail:
            return ImageOps.fit(img, size, Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        else:
            img_copy = img.copy()
            img_copy.thumbnail(size, Image.Resampling.LANCZOS)
            return img_copy

    @staticmethod
    def save_as_jpeg(img: Image.Image, path: str, quality: int = 90,
                     progressive: bool = True):
        """Save as optimized JPEG with progressive encoding."""
        img.save(path, "JPEG", quality=quality, optimize=True,
                progressive=progressive, subsampling=0)

    @staticmethod
    def save_as_webp(img: Image.Image, path: str, quality: int = 85):
        """Save as WebP (30-50% smaller than JPEG)."""
        img.save(path, "WEBP", quality=quality, method=6)

    def save_product_image(self, file) -> Dict[str, Any]:
        """
        Save uploaded product image with optimization.

        Creates 6 variants:
        - Thumbnail (150x150): ~5-10KB JPEG + ~3-7KB WebP
        - Small (400x400): ~20-40KB JPEG + ~15-30KB WebP
        - Medium (800x800): ~80-150KB JPEG + ~50-100KB WebP

        Total: ~200KB vs original 5MB

        Returns:
            dict: Image paths or error message
        """
        try:
            # Validate
            if not file or not hasattr(file, 'filename') or file.filename == "":
                return {"error": "No file selected"}

            if not self.allowed_file(file.filename):
                return {"error": f"Invalid file type. Allowed: {', '.join(self.config.allowed_extensions).upper()}"}

            # Check size
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)

            if file_size > self.config.max_file_size:
                return {"error": f"File too large. Max: {self.config.max_file_size // (1024*1024)}MB"}

            # Create folders
            folders = {
                "thumbnail": os.path.join(self.config.upload_folder, "thumbnails"),
                "small": os.path.join(self.config.upload_folder, "small"),
                "medium": os.path.join(self.config.upload_folder, "medium"),
                "webp": os.path.join(self.config.upload_folder, "webp"),
            }

            for folder in folders.values():
                os.makedirs(folder, exist_ok=True)

            # Generate filename
            base_name = str(uuid.uuid4())
            temp_path = os.path.join(folders["medium"], f"temp_{base_name}.jpg")
            file.save(temp_path)

            # Validate image
            try:
                with Image.open(temp_path) as img:
                    img.verify()

                with Image.open(temp_path) as img_check:
                    width, height = img_check.size
                    if width > self.config.max_upload_dimension or height > self.config.max_upload_dimension:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        return {"error": f"Image too large. Max: {self.config.max_upload_dimension}x{self.config.max_upload_dimension}px"}

                img = Image.open(temp_path)
            except Exception:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return {"error": "Invalid image file"}

            # Prepare
            img = self.prepare_image(img)

            # Auto-downsize if needed
            width, height = img.size
            if width > self.config.max_dimension or height > self.config.max_dimension:
                ratio = min(self.config.max_dimension / width, self.config.max_dimension / height)
                new_size = (int(width * ratio), int(height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # Enhance
            img = self.enhance_image(img)

            # Create variants
            variants = {}

            # Thumbnail
            thumb = self.create_variant(img, ImagePresets.SIZES["thumbnail"], is_thumbnail=True)
            thumb_path = os.path.join(folders["thumbnail"], f"{base_name}.jpg")
            self.save_as_jpeg(thumb, thumb_path, quality=ImagePresets.JPEG_QUALITY["thumbnail"])
            variants["thumbnail"] = f"uploads/thumbnails/{base_name}.jpg"

            thumb_webp_path = os.path.join(folders["webp"], f"{base_name}_thumb.webp")
            self.save_as_webp(thumb, thumb_webp_path, quality=ImagePresets.WEBP_QUALITY["thumbnail"])
            variants["thumbnail_webp"] = f"uploads/webp/{base_name}_thumb.webp"

            # Small
            small = self.create_variant(img, ImagePresets.SIZES["small"])
            small_path = os.path.join(folders["small"], f"{base_name}.jpg")
            self.save_as_jpeg(small, small_path, quality=ImagePresets.JPEG_QUALITY["small"])
            variants["small"] = f"uploads/small/{base_name}.jpg"

            small_webp_path = os.path.join(folders["webp"], f"{base_name}_small.webp")
            self.save_as_webp(small, small_webp_path, quality=ImagePresets.WEBP_QUALITY["small"])
            variants["small_webp"] = f"uploads/webp/{base_name}_small.webp"

            # Medium
            medium = self.create_variant(img, ImagePresets.SIZES["medium"])
            medium_path = os.path.join(folders["medium"], f"{base_name}.jpg")
            self.save_as_jpeg(medium, medium_path, quality=ImagePresets.JPEG_QUALITY["medium"])
            variants["medium"] = f"uploads/medium/{base_name}.jpg"

            medium_webp_path = os.path.join(folders["webp"], f"{base_name}_medium.webp")
            self.save_as_webp(medium, medium_webp_path, quality=ImagePresets.WEBP_QUALITY["medium"])
            variants["medium_webp"] = f"uploads/webp/{base_name}_medium.webp"

            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)

            return {
                "image_path": variants["medium"],
                "thumbnail_path": variants["thumbnail"],
                "filename": base_name,
                "variants": variants,
                "success": True,
            }

        except Exception as e:
            return {"error": f"Error processing image: {str(e)}"}

    def save_avatar_image(self, file) -> Dict[str, Any]:
        """
        Save avatar image (56x56px square).

        Output: ~2-4KB total
        """
        try:
            if not file or not hasattr(file, 'filename') or file.filename == "":
                return {"error": "No file selected"}

            if not self.allowed_file(file.filename):
                return {"error": f"Invalid file type"}

            # Create folders
            avatar_folder = os.path.join(self.config.upload_folder, "avatars")
            webp_folder = os.path.join(self.config.upload_folder, "webp")
            os.makedirs(avatar_folder, exist_ok=True)
            os.makedirs(webp_folder, exist_ok=True)

            base_name = str(uuid.uuid4())
            temp_path = os.path.join(avatar_folder, f"temp_{base_name}.jpg")
            file.save(temp_path)

            try:
                with Image.open(temp_path) as img:
                    img.verify()
                img = Image.open(temp_path)
            except Exception:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return {"error": "Invalid image file"}

            img = self.prepare_image(img)
            img = self.enhance_image(img)

            avatar = self.create_variant(img, ImagePresets.SIZES["avatar"], is_thumbnail=True)

            avatar_path = os.path.join(avatar_folder, f"{base_name}.jpg")
            self.save_as_jpeg(avatar, avatar_path, quality=ImagePresets.JPEG_QUALITY["avatar"])

            avatar_webp_path = os.path.join(webp_folder, f"{base_name}_avatar.webp")
            self.save_as_webp(avatar, avatar_webp_path, quality=ImagePresets.WEBP_QUALITY["avatar"])

            if os.path.exists(temp_path):
                os.remove(temp_path)

            return {
                "image_path": f"uploads/avatars/{base_name}.jpg",
                "webp_path": f"uploads/webp/{base_name}_avatar.webp",
                "filename": base_name,
                "success": True,
            }

        except Exception as e:
            return {"error": f"Error processing avatar: {str(e)}"}
