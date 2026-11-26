import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();ctx=await b.new_context(**p.devices['iPhone 13']);pg=await ctx.new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto((ROOT/'dist'/'editor.html').as_uri());await pg.wait_for_timeout(600);await pg.click('[data-a=help-ok]')
    # select a door-like decor: wall d4 -> replace with sofa
    await pg.evaluate("ui.sel=[{k:'d',id:'d4'}];render()")
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'g1.png'))
    await pg.click('#bar [data-a=swap]');await pg.wait_for_timeout(300);await pg.screenshot(path=str(ROOT/'tests'/'shots'/'g2.png'))
    print('cat',await pg.evaluate('ui.cat'))
    await pg.click('.cat[data-v="1"]');await pg.click('.tile[data-v="0"]');await pg.wait_for_timeout(300)
    print('new',await pg.evaluate("JSON.stringify(get(ui.sel[0]))"))
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'g3.png'))
    # table -> table keeps number/join
    await pg.evaluate("ui.sel=[{k:'t',id:'1'}];render()")
    await pg.click('#bar [data-a=swap]');await pg.wait_for_timeout(200);print('cat t',await pg.evaluate('ui.cat'))
    await pg.click('.tile[data-v="8"]');print('t1',await pg.evaluate("JSON.stringify(tab('1'))"))
    # table -> plant removes joins
    await pg.evaluate("ui.sel=[{k:'t',id:'2'}];render()");await pg.click('#bar [data-a=swap]');await pg.click('.cat[data-v="6"]');await pg.click('.tile[data-v="0"]')
    print('t2 gone',await pg.evaluate("[!tab('2'),tab('1').join]"))
    await pg.click('#toast button');print('undo t2',await pg.evaluate("!!tab('2')"))
    print('errs',errs);await b.close()
asyncio.run(main())
