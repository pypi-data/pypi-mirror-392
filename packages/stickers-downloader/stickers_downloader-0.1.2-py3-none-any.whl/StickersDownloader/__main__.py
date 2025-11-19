from .StickersDownloader import TelegramStickerDownloader, console
import asyncio
import sys
from rich.prompt import Prompt, Confirm
import aiohttp

async def main(token: str, link: str):
    downloader = TelegramStickerDownloader(token, link)
    async with aiohttp.ClientSession() as session:
        try:
            all_stickers = await downloader.fetch_sticker_set_info(session)
        except Exception as e:
            console.print(f"[red]Failed to fetch stickers: {e}[/red]")
            return

        console.print("\n[bold]Sticker Index Preview:[/bold]")
        for idx, s in enumerate(all_stickers):
            console.print(f"{idx}: {s['emoji']}  {s.get('set_name', '')}")

        if Confirm.ask("Do you want to download all stickers?"):
            await downloader.run()
        else:
            indexes = Prompt.ask("Enter sticker indexes separated by comma", default="")
            selected = [int(i.strip()) for i in indexes.split(",") if i.strip().isdigit()]
            await downloader.run(selected_indexes=selected)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m StickersDownloader <TOKEN> <STICKER_PACK_LINK>")
        sys.exit(1)
    token = sys.argv[1]
    link = sys.argv[2]
    asyncio.run(main(token, link))
