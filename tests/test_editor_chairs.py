import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();ctx=await b.new_context(**p.devices['iPhone 13']);pg=await ctx.new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto((ROOT/'dist'/'editor.html').as_uri());await pg.wait_for_timeout(600);await pg.click('[data-a=help-ok]')
    print('chairs',await pg.evaluate("S.decor.filter(d=>d.t==='chair').length"),'seats total',await pg.evaluate("S.tables.reduce((s,t)=>s+t.seats,0)"),'ch0',await pg.evaluate("S.tables.every(t=>t.ch===0)"))
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'i1.png'))
    await pg.click('[data-a=add]');await pg.click('.cat[data-v="2"]');await pg.wait_for_timeout(100);await pg.screenshot(path=str(ROOT/'tests'/'shots'/'i2.png'))
    await pg.click('.tile[data-v="0"]');await pg.wait_for_timeout(200)
    await pg.click('[data-a=st][data-f=cn][data-d="1"]');await pg.click('[data-a=st][data-f=cn][data-d="1"]')
    await pg.click('[data-a=lay][data-v=rows]');await pg.screenshot(path=str(ROOT/'tests'/'shots'/'i3.png'))
    await pg.click('[data-a=crowd-go]');await pg.wait_for_timeout(300)
    print('sel',await pg.evaluate("ui.sel.length"),'multi',await pg.evaluate("ui.multi"))
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'i4.png'))
    await pg.click('#bar [data-a=rot90]');await pg.wait_for_timeout(200);await pg.screenshot(path=str(ROOT/'tests'/'shots'/'i5.png'))
    await pg.click('#bar [data-a=multi-done]')
    await pg.evaluate("ui.sel=[{k:'t',id:'9'}];render();fit()")
    await pg.click('#bar [data-a=props]');await pg.wait_for_timeout(200)
    await pg.click('[data-a=withch]');await pg.wait_for_timeout(200);print('with chairs sel',await pg.evaluate("ui.sel.length"))
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'i6.png'))
    # import legacy text → split
    print('errs',errs);await b.close()
asyncio.run(main())
