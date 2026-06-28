"""
Content Factory — Generates promotional visual content for Mrmakmax.
Creates: audio visualizers, quote cards, promo banners.
Uses FFmpeg for video generation and Pillow for images.
"""
import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("content-factory")

OUTPUT_DIR = Path(os.getenv("CONTENT_OUTPUT_DIR", str(Path.home() / "promo-content")))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_audio_visualizer(
    audio_path: str = None,
    cover_path: str = None,
    text: str = "OUT NOW",
    artist: str = "Mrmakmax",
    duration: int = 30,
) -> dict:
    """
    Generate a short video with audio waveform visualization + cover art.
    Perfect for TikTok, Instagram Reels, YouTube Shorts.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"visualizer_{timestamp}.mp4"

    if not cover_path:
        # Generate a gradient background
        cover_path = _generate_gradient_bg(artist)

    # FFmpeg command: waveform + coverart overlay
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=#0a0a1a:s=1080x1920:d={duration}:r=30",
        "-i", str(cover_path),
        "-filter_complex",
        (
            f"[1:v]scale=800:800,format=rgba[cover];"
            f"[0:v][cover]overlay=(W-w)/2:200:shortest=1[bg];"
            f"[bg]drawtext=text='{text}':fontcolor=#FF6B35:fontsize=48:"
            f"x=(w-text_w)/2:y=1100:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf[out]"
        ),
        "-map", "[out]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "28",
        "-pix_fmt", "yuv420p",
        "-an",
        str(output_path),
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)
        logger.info(f"Visualizer generated: {output_path}")
        return {
            "type": "visualizer",
            "path": str(output_path),
            "size": output_path.stat().st_size,
            "timestamp": timestamp,
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed: {e.stderr.decode()}")
        # Fallback: generate a simple image instead
        return _generate_fallback_image(text, artist, timestamp)
    except FileNotFoundError:
        logger.warning("FFmpeg not found — generating image fallback")
        return _generate_fallback_image(text, artist, timestamp)


def generate_quote_card(
    quote: str,
    author: str = "Mrmakmax",
    style: str = "dark",
) -> dict:
    """
    Generate a quote/lyric card for Instagram stories.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"quote_{timestamp}.png"

        # 1080x1920 (story format)
        img = Image.new("RGB", (1080, 1920), "#0a0a1a")
        draw = ImageDraw.Draw(img)

        # Gradient effect — simple bars
        for i in range(10):
            color = (255 - i * 20, 107 - i * 5, 53 - i * 3)
            draw.rectangle([0, i * 30, 1080, (i + 1) * 30], fill=color)

        # Quote text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        except OSError:
            font = ImageFont.load_default()
            small_font = font

        # Draw quote centered
        lines = _wrap_text(quote, 40)
        y = 500
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            draw.text(((1080 - w) / 2, y), line, fill="#FFFFFF", font=font)
            y += 60

        # Author
        bbox = draw.textbbox((0, 0), f"— {author}", font=small_font)
        w = bbox[2] - bbox[0]
        draw.text(((1080 - w) / 2, y + 80), f"— {author}", fill="#FFD166", font=small_font)

        # Brand
        draw.text((40, 1840), "nonamesbeats", fill="#FF6B35", font=small_font)

        img.save(str(output_path), "PNG")
        logger.info(f"Quote card generated: {output_path}")

        return {
            "type": "quote_card",
            "path": str(output_path),
            "size": output_path.stat().st_size,
            "quote": quote,
            "timestamp": timestamp,
        }
    except ImportError:
        logger.warning("Pillow not installed — skipping quote card")
        return {"type": "quote_card", "path": "", "error": "Pillow not installed"}


def generate_promo_banner(
    title: str,
    subtitle: str = "",
    cta: str = "STREAM NOW",
) -> dict:
    """
    Generate a promotional banner for a release or announcement.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"promo_{timestamp}.png"

        # 1200x630 (optimal for link previews)
        img = Image.new("RGB", (1200, 630), "#0a0a1a")
        draw = ImageDraw.Draw(img)

        # Diagonal gradient strips
        for i in range(0, 1200, 40):
            alpha = 0.05 + (i / 1200) * 0.1
            r = int(255 * alpha)
            g = int(107 * alpha)
            b = int(53 * alpha)
            draw.polygon([(i, 0), (i + 40, 0), (0, i + 40), (0, i)], fill=(r, g, b))

        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
            sub_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        except OSError:
            title_font = ImageFont.load_default()
            sub_font = title_font

        # Title
        bbox = draw.textbbox((0, 0), title, font=title_font)
        w = bbox[2] - bbox[0]
        draw.text(((1200 - w) / 2, 180), title, fill="#FF6B35", font=title_font)

        # Subtitle
        if subtitle:
            bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
            w = bbox[2] - bbox[0]
            draw.text(((1200 - w) / 2, 280), subtitle, fill="#FFFFFF", font=sub_font)

        # CTA box
        cta_w = 300
        cta_h = 60
        cta_x = (1200 - cta_w) / 2
        cta_y = 400
        draw.rounded_rectangle(
            [cta_x, cta_y, cta_x + cta_w, cta_y + cta_h],
            radius=15,
            fill="#FF6B35",
        )
        bbox = draw.textbbox((0, 0), cta, font=sub_font)
        tw = bbox[2] - bbox[0]
        draw.text(
            (cta_x + (cta_w - tw) / 2, cta_y + 12),
            cta,
            fill="#FFFFFF",
            font=sub_font,
        )

        # Brand
        draw.text((40, 570), "Mrmakmax • nonamesbeats", fill="#FFD166", font=sub_font)

        img.save(str(output_path), "PNG")
        logger.info(f"Promo banner generated: {output_path}")

        return {
            "type": "promo_banner",
            "path": str(output_path),
            "size": output_path.stat().st_size,
            "title": title,
            "timestamp": timestamp,
        }
    except ImportError:
        logger.warning("Pillow not installed — skipping promo banner")
        return {"type": "promo_banner", "path": "", "error": "Pillow not installed"}


def generate_social_pack(audio_path: str = None, cover_path: str = None) -> list:
    """
    Generate a complete pack of content for a release:
    - 1 visualizer video (30s)
    - 2 quote cards (different quotes)
    - 1 promo banner
    """
    results = []

    # Visualizer
    viz = generate_audio_visualizer(audio_path=audio_path, cover_path=cover_path, text="NOUVEAU SON 🔥")
    results.append(viz)

    # Quote cards
    quotes = [
        "Born to make the world dance",
        "Afro pop is not just music, it's a vibration",
    ]
    for quote in quotes:
        qc = generate_quote_card(quote=quote)
        results.append(qc)

    # Promo banner
    banner = generate_promo_banner(
        title="NOUVEAU SON DISPONIBLE",
        subtitle="Mrmakmax • nonamesbeats",
        cta="ÉCOUTER MAINTENANT",
    )
    results.append(banner)

    return results


def _generate_gradient_bg(artist: str) -> str:
    """Generate a simple gradient image as fallback cover art."""
    try:
        from PIL import Image, ImageDraw

        path = OUTPUT_DIR / f"gradient_bg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        img = Image.new("RGB", (800, 800), "#0a0a1a")
        draw = ImageDraw.Draw(img)

        for i in range(800):
            r = int(10 + (i / 800) * 30)
            g = int(10 + (i / 800) * 20)
            b = int(30 + (i / 800) * 40)
            draw.line([(i, 0), (i, 800)], fill=(r, g, b))

        # Artist name
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except (OSError, NameError):
            from PIL import ImageFont
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), artist, font=font)
        w = bbox[2] - bbox[0]
        draw.text(((800 - w) / 2, 360), artist, fill="#FF6B35", font=font)

        img.save(str(path), "PNG")
        return str(path)
    except ImportError:
        return ""


def _generate_fallback_image(text: str, artist: str, timestamp: str) -> dict:
    """Generate a simple image when FFmpeg is unavailable."""
    try:
        from PIL import Image, ImageDraw, ImageFont

        path = OUTPUT_DIR / f"fallback_{timestamp}.png"
        img = Image.new("RGB", (1080, 1920), "#0a0a1a")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        draw.text(((1080 - w) / 2, 900), text, fill="#FF6B35", font=font)
        draw.text((40, 1840), f"@{artist} • nonamesbeats", fill="#FFD166", font=font)

        img.save(str(path), "PNG")

        return {
            "type": "fallback_image",
            "path": str(path),
            "size": path.stat().st_size,
            "timestamp": timestamp,
        }
    except ImportError:
        return {"type": "fallback", "path": "", "error": "No image generation available"}


def _wrap_text(text: str, max_chars: int) -> list:
    """Simple text wrapping."""
    words = text.split()
    lines = []
    current_line = []
    current_len = 0

    for word in words:
        if current_len + len(word) + 1 <= max_chars:
            current_line.append(word)
            current_len += len(word) + 1
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_len = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return lines if lines else [text]


# === CLI Entry Point ===
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Mrmakmax Content Factory")
    parser.add_argument("--mode", choices=["visualizer", "quote", "banner", "pack", "all"],
                        default="pack", help="What to generate")
    parser.add_argument("--audio", help="Path to audio file")
    parser.add_argument("--cover", help="Path to cover art image")
    parser.add_argument("--text", default="OUT NOW", help="Text for visualizer")
    parser.add_argument("--title", default="NOUVEAU SON", help="Title for promo banner")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.mode == "visualizer":
        result = generate_audio_visualizer(audio_path=args.audio, cover_path=args.cover, text=args.text)
    elif args.mode == "quote":
        result = generate_quote_card(quote=args.text)
    elif args.mode == "banner":
        result = generate_promo_banner(title=args.title)
    elif args.mode in ("pack", "all"):
        results = generate_social_pack(audio_path=args.audio, cover_path=args.cover)
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            for r in results:
                print(f"✅ {r['type']}: {r.get('path', 'N/A')}")
        sys.exit(0)
    else:
        print("Unknown mode")
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"✅ {result['type']}: {result.get('path', 'N/A')}")
