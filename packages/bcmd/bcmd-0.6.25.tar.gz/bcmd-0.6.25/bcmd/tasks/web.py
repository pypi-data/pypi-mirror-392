import webbrowser
from typing import Final

import pyperclip
import typer
from beni import btask
from beni.bfunc import syncCall

app: Final = btask.newSubApp('web 工具')


@app.command()
@syncCall
async def open_amazon(
    asin: list[str] = typer.Argument(None, help='支持多个 ASIN 如果不填写则使用剪贴板内容')
):
    asin = asin or []
    if not asin:
        content = pyperclip.paste().strip()
        for line in content.splitlines():
            line = line.strip()
            if line:
                asin.extend(line.split(' '))
        asin = [x for x in asin if x]
    btask.assertTrue(asin, '没有提供任何 ASIN')
    for x in asin:
        webbrowser.open_new_tab(f'https://www.amazon.com/dp/{x}')
