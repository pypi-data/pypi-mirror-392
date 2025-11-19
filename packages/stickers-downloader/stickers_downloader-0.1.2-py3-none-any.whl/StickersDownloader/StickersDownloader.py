import os
import aiohttp
import asyncio
import json
import gzip
from rlottie_python import LottieAnimation
from urllib.parse import urlparse
from typing import List
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.console import Console

console = Console()


# ========== AUTO TGS/JSON LOADER ==========
def load_lottie_auto(path: str):
    with open(path, "rb") as f:
        data = f.read()

    # Check gzip header
    if data[:2] == b"\x1f\x8b":
        # Real TGS (gzipped)
        return LottieAnimation.from_tgs(path)

    # Fake TGS (JSON)
    try:
        txt = data.decode("utf-8")
        return LottieAnimation.from_json(txt)
    except Exception:
        # fallback: try decompress
        try:
            txt = gzip.decompress(data).decode("utf-8")
            return LottieAnimation.from_json(txt)
        except Exception as e:
            raise Exception(f"Invalid TGS/JSON file: {path} — {e}")


# ========== MAIN CLASS ==========
class TelegramStickerDownloader:
    def __init__(self, token: str, sticker_pack_link: str):
        self.token = token
        self.sticker_pack_link = sticker_pack_link
        self.sticker_set = self._extract_sticker_set()

        self.tgs_dir = f"tgs/{self.sticker_set}_Stickers"
        self.gif_dir = f"{self.sticker_set}_GIFs"

        os.makedirs(self.tgs_dir, exist_ok=True)
        os.makedirs(self.gif_dir, exist_ok=True)

    def _extract_sticker_set(self):
        return urlparse(self.sticker_pack_link).path.split('/')[-1]

    @staticmethod
    async def retry_request(func, *args, retries=3, delay=2, **kwargs):
        for attempt in range(1, retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt < retries:
                    await asyncio.sleep(delay)
                else:
                    raise e

    async def fetch_sticker_set_info(self, session: aiohttp.ClientSession):
        async def inner():
            url = f"https://api.telegram.org/bot{self.token}/getStickerSet?name={self.sticker_set}"
            async with session.get(url, timeout=10) as resp:
                res = await resp.json()
                if not res.get("ok"):
                    raise Exception(f"Failed to get sticker set info: {res}")
                return res["result"]["stickers"]

        return await TelegramStickerDownloader.retry_request(inner)

    async def download_file(self, session: aiohttp.ClientSession, file_id: str, save_path: str):
        async def inner():
            url = f"https://api.telegram.org/bot{self.token}/getFile?file_id={file_id}"
            async with session.get(url, timeout=10) as resp:
                res = await resp.json()
                if not res.get("ok"):
                    raise Exception(f"Failed to get file info: {file_id}")
                file_path = res["result"]["file_path"]

            download_url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
            async with session.get(download_url, timeout=10) as r:
                with open(save_path, "wb") as f:
                    f.write(await r.read())

        return await TelegramStickerDownloader.retry_request(inner)

    async def convert_tgs_to_gif(self, tgs_path: str, gif_path: str):
        try:
            anim = load_lottie_auto(tgs_path)
            anim.save_animation(gif_path)
        except Exception as e:
            console.print(f"[red]❌ Failed to convert {tgs_path}: {e}[/red]")

    async def process_sticker(self, session: aiohttp.ClientSession, sticker, progress, progress_task):
        file_name = f"{sticker['emoji']}_{sticker['file_unique_id']}.tgs"
        tgs_path = os.path.join(self.tgs_dir, file_name)
        gif_path = os.path.join(self.gif_dir, file_name.replace(".tgs", ".gif"))

        # Already done
        if os.path.exists(tgs_path) and os.path.exists(gif_path):
            progress.update(progress_task, advance=1)
            return

        # Download
        if not os.path.exists(tgs_path):
            try:
                await self.download_file(session, sticker["file_id"], tgs_path)
            except Exception as e:
                console.print(f"[red]❌ Download failed: {file_name} — {e}[/red]")
                progress.update(progress_task, advance=1)
                return

        # Convert
        if not os.path.exists(gif_path):
            await self.convert_tgs_to_gif(tgs_path, gif_path)

        progress.update(progress_task, advance=1)

    async def run(self, selected_indexes: List[int] = None):
        async with aiohttp.ClientSession() as session:
            try:
                stickers = await self.fetch_sticker_set_info(session)
            except Exception as e:
                console.print(f"[red]{e}[/red]")
                return

            if selected_indexes:
                stickers = [stickers[i] for i in selected_indexes]

            console.print(f"[bold blue]Sticker pack:[/bold blue] {self.sticker_set}")
            console.print(f"[bold green]Total stickers:[/bold green] {len(stickers)}\n")

            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=None, complete_style="green"),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeRemainingColumn(),
                console=console
            ) as progress:
                task = progress.add_task("[cyan]Processing...[/cyan]", total=len(stickers))
                await asyncio.gather(*[
                    self.process_sticker(session, s, progress, task)
                    for s in stickers
                ])

            console.print("\n[bold green]⭐ Done! GIFs created![/bold green]")
