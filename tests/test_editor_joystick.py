import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();ctx=await b.new_context(**p.devices['iPhone 13']);pg=await ctx.new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto((ROOT/'dist'/'editor.html').as_uri());await pg.wait_for_timeout(600);await pg.click('[data-a=help-ok]')
    await pg.click('[data-a=add]');await pg.click('.cat[data-v="2"]');await pg.click('.tile[data-v="1"]');await pg.wait_for_timeout(300)
    print('nudge shown',await pg.evaluate("document.querySelector('#nudge').classList.contains('show')"),'handles',await pg.evaluate("document.querySelectorAll('[data-h]').length"))
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'h1.png'))
    o0=await pg.evaluate("(o=>[o.x,o.y])(get(ui.sel[0]))")
    r=await pg.evaluate("(r=>[r.left+r.width/2,r.top+r.height/2])(document.querySelector('#joy').getBoundingClientRect())")
    cdp=await ctx.new_cdp_session(pg)
    await cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':r[0],'y':r[1]}]})
    for i in range(1,6):
      await cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':r[0]+i*12,'y':r[1]}]});await pg.wait_for_timeout(30)
    await pg.wait_for_timeout(600)
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'h2.png'))
    await cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});await pg.wait_for_timeout(200)
    o1=await pg.evaluate("(o=>[o.x,o.y])(get(ui.sel[0]))");print('moved',o0,'->',o1,'knob reset',await pg.evaluate("document.querySelector('.knob').style.transform"))
    await pg.click('[data-n="r+15"]');print('rot',await pg.evaluate("get(ui.sel[0]).rot"))
    await pg.click('[data-a=undo]');await pg.click('[data-a=undo]');print('undo',await pg.evaluate("(o=>[o.x,o.y,o.rot])(get(ui.sel[0]))"))
    # big object select: no auto joystick
    await pg.evaluate("ui.sel=[];ui.nudge=false;render();fit()")
    x,y=await pg.evaluate("""(()=>{const r=document.querySelector('[data-oid="t:1"] .hit').getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]})()""")
    await cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]});await cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});await pg.wait_for_timeout(150)
    print('table: nudge',await pg.evaluate('ui.nudge'),'handles',await pg.evaluate("document.querySelectorAll('[data-h]').length"))
    print('errs',errs);await b.close()
asyncio.run(main())
