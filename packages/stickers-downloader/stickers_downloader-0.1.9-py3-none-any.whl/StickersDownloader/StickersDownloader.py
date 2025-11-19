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
import imageio
from rlottie_python import LottieAnimation

console = Console()

def _convert_tgs_to_gif_sync(tgs_path, gif_path, scale=1.0):
    anim = LottieAnimation.from_tgs(tgs_path)
    frames = []
    for i in range(anim.frame_count):
        img = anim.render(i, scale=scale)
        frames.append(img.astype('uint8'))
    imageio.mimsave(gif_path, frames, duration=1/anim.frame_rate)

def load_lottie_auto(path: str):
    with open(path, "rb") as f:
        data = f.read()

    if data[:2] == b"\x1f\x8b":
        return LottieAnimation.from_tgs(path)

    try:
        return LottieAnimation.from_json(data.decode("utf-8"))
    except:
        pass

    try:
        txt = gzip.decompress(data).decode("utf-8")
        return LottieAnimation.from_json(txt)
    except:
        pass

    try:
        idx = data.find(b"{")
        if idx != -1:
            txt = data[idx:].decode("utf-8")
            return LottieAnimation.from_json(txt)
    except Exception as e:
        raise Exception(f"Brutal mode failed: {e}")

    raise Exception(f"Invalid TGS/JSON file: {path}")


class TelegramStickerDownloader:
    def __init__(self, token: str, sticker_pack_link: str, sticker_type: str):
        if sticker_type not in ["animated", "static"]:
            raise ValueError("sticker_type must be 'animated' or 'static'")

        self.token = token
        self.sticker_type = sticker_type
        self.sticker_pack_link = sticker_pack_link
        self.sticker_set = self._extract_sticker_set()

        self.output_dir = f"{self.sticker_set}_{sticker_type}"
        os.makedirs(self.output_dir, exist_ok=True)

    def _extract_sticker_set(self):
        return urlparse(self.sticker_pack_link).path.split('/')[-1]

    @staticmethod
    async def retry_request(func, *args, retries=3, delay=2, **kwargs):
        for attempt in range(retries):
            try:
                return await func(*args, **kwargs)
            except:
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(delay)

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
                data = await r.read()
                with open(save_path, "wb") as f:
                    f.write(data)

        return await TelegramStickerDownloader.retry_request(inner)
    
    async def convert_tgs_to_gif(self, tgs_path, gif_path, scale=1.0):
        await asyncio.to_thread(self._convert_tgs_to_gif_sync, tgs_path, gif_path, scale)


    async def process_sticker(self, session, sticker, progress, task):
        emoji = sticker["emoji"]
        unique_id = sticker["file_unique_id"]

        if self.sticker_type == "animated":
            file_name = f"{emoji}_{unique_id}.tgs"
            save_path = os.path.join(self.output_dir, file_name)
        else:
            file_name = f"{emoji}_{unique_id}.webp"
            save_path = os.path.join(self.output_dir, file_name)

        if os.path.exists(save_path):
            progress.update(task, advance=1)
            return

        try:
            await self.download_file(session, sticker["file_id"], save_path)
        except Exception as e:
            console.print(f"[red]❌ Download failed: {file_name} — {e}[/red]")
            progress.update(task, advance=1)
            return

        if self.sticker_type == "animated":
            gif_path = save_path.replace(".tgs", ".gif")
            await self.convert_tgs_to_gif(save_path, gif_path)

        progress.update(task, advance=1)

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
            console.print(f"[bold green]Type:[/bold green] {self.sticker_type}")
            console.print(f"[bold green]Count:[/bold green] {len(stickers)}\n")

            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeRemainingColumn(),
                console=console
            ) as progress:
                task = progress.add_task("[cyan]Processing...[/cyan]", total=len(stickers))

                await asyncio.gather(*[
                    self.process_sticker(session, s, progress, task)
                    for s in stickers
                ])


