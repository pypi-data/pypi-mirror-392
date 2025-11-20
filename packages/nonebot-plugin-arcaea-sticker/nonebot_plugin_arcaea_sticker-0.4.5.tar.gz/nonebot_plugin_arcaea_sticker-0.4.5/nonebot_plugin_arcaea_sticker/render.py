import base64
from pathlib import Path
from typing import Optional, Dict

from nonebot import logger, require
import anyio
import jinja2

require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import get_new_page

from .config import FONT_DIR, RESOURCE_DIR, PLUGIN_DIR
from .models import StickerInfo
from .text import TextSizeCalculator
from .resource import ResourceManager

DEFAULT_WIDTH = 296
DEFAULT_HEIGHT = 256
DEFAULT_STROKE_WIDTH = 9
DEFAULT_LINE_SPACING = 1.3
DEFAULT_STROKE_COLOR = "#ffffff"
TEMPLATES_DIR = PLUGIN_DIR / "templates"

class ImageRenderer:
    """处理表情图片的渲染"""
    
    def __init__(self, templates_dir: Path) -> None:
        """初始化渲染器,设置模板目录"""
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
            enable_async=True,
        )
        self.text_calculator = TextSizeCalculator(
            max_width=DEFAULT_WIDTH,
            max_height=DEFAULT_HEIGHT
        )
        # 缓存 base64 编码的字体，避免重复加载
        self._font_base64_cache = {}
    
    async def file_to_base64_url(self, path: Path, mime_type: str) -> str:
        """将文件转换为 base64 data URL - Python 3.12+ 兼容方案"""
        try:
            data = await anyio.Path(path).read_bytes()
            b64_data = base64.b64encode(data).decode('utf-8')
            data_url = f"data:{mime_type};base64,{b64_data}"
            logger.debug(f"文件转换: {path.name} -> base64 ({len(data)} bytes)")
            return data_url
        except Exception as e:
            logger.error(f"文件转换失败 {path}: {e}")
            raise
    
    async def get_font_base64(self, font_path: Path) -> str:
        """获取字体的 base64 编码（带缓存）"""
        font_name = font_path.name
        if font_name not in self._font_base64_cache:
            self._font_base64_cache[font_name] = await self.file_to_base64_url(
                font_path, "font/ttf"
            )
        return self._font_base64_cache[font_name]
    
    async def render_svg(self, info: StickerInfo, text: str, **params) -> str:
        """渲染SVG模板 - 使用 base64 内嵌资源"""
        try:
            render_params = info.get_render_params(text, **params)
            
            image_path = info.get_image_path(RESOURCE_DIR)
            font_path = FONT_DIR / "YurukaFangTang.ttf"
            
            logger.debug(f"资源路径 - 图片: {image_path}, 字体: {font_path}")
            
            # 转换为 base64
            image_base64 = await self.file_to_base64_url(image_path, "image/png")
            font_base64 = await self.get_font_base64(font_path)
            
            template_params = {
                "id": hash(info.img),
                "image": image_base64,
                "font": font_base64,
                "width": DEFAULT_WIDTH,
                "height": DEFAULT_HEIGHT,
                "line_spacing": params.get("line_spacing", DEFAULT_LINE_SPACING),
                **render_params
            }
            
            template = self.env.get_template("sticker.svg.jinja")
            svg_content = await template.render_async(**template_params)
            logger.debug(f"SVG渲染成功, 大小: {len(svg_content)} 字符")
            return svg_content
        except Exception as e:
            logger.exception("SVG渲染失败")
            raise RuntimeError(f"SVG渲染失败: {e}")
    
    async def render_to_png(self, svg: str) -> bytes:
        """将SVG渲染为PNG"""
        try:
            async with get_new_page(
                viewport={'width': DEFAULT_WIDTH, 'height': DEFAULT_HEIGHT, 'deviceScaleFactor': 2}
            ) as page:
                await page.set_content(svg, wait_until="load")
                element = await page.query_selector("svg")
                if not element:
                    raise ValueError("无法找到SVG元素")
                
                screenshot = await element.screenshot(
                    type="png",
                    omit_background=True,
                    scale="device"
                )
                logger.debug(f"PNG渲染成功, 大小: {len(screenshot)} bytes")
                return screenshot
        except Exception as e:
            logger.exception("PNG渲染失败")
            raise RuntimeError(f"PNG渲染失败: {e}")
    
    async def render(self, info: StickerInfo, text: str, **params) -> bytes:
        """渲染表情图片"""
        try:
            # 只在明确要求自动调整时才进行调整
            if params.get("auto_adjust", False):
                font_size = self.text_calculator.calc_text_size(
                    text,
                    info.default_text.font_size,  # 使用默认大小作为基准
                    params.get("rotate", info.default_text.rotate)
                )
                params["font_size"] = font_size
            elif "font_size" not in params:
                # 如果没有手动设置字体大小且不需要自动调整，使用默认值
                params["font_size"] = info.default_text.font_size
            
            # 渲染SVG
            svg = await self.render_svg(info, text, **params)
            
            # 转换为PNG
            return await self.render_to_png(svg)
        except Exception as e:
            logger.exception("表情图片渲染失败")
            raise RuntimeError(f"表情图片渲染失败: {e}")

renderer = ImageRenderer(TEMPLATES_DIR)
resource_manager = ResourceManager(RESOURCE_DIR)

async def generate_sticker_image(
    info: StickerInfo,
    text: str,
    **params
) -> bytes:
    """生成表情图片"""
    try:
        return await renderer.render(info, text, **params)
    except Exception as e:
        logger.exception("生成表情图片失败")
        raise Exception(f"生成表情图片失败: {str(e)}")