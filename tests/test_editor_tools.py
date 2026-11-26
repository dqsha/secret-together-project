import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();ctx=await b.new_context(**p.devices['iPhone 13']);pg=await ctx.new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto((ROOT/'dist'/'editor.html').as_uri());await pg.wait_for_timeout(600);await pg.click('[data-a=help-ok]')
    cdp=await ctx.new_cdp_session(pg)
    async def drag(x0,y0,x1,y1,steps=8,hold=0):
      await cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x0,'y':y0}]})
      if hold: await pg.wait_for_timeout(hold)
      for i in range(1,steps+1):
        await cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x0+(x1-x0)*i/steps,'y':y0+(y1-y0)*i/steps}]})
      await cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});await pg.wait_for_timeout(120)
    async def tap(x,y):
      await cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
      await cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});await pg.wait_for_timeout(120)
    pos=lambda oid:pg.evaluate(f"""()=>{{const g=document.querySelector('[data-oid="{oid}"] .hit');const r=g.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}}""")
    T=lambda i:pg.evaluate(f"(t=>[t.x,t.y,t.rot||0,t.lock||false])(S.tables.find(t=>t.id==='{i}'))")
    # long press drag
    x,y=await pos('t:5');a=await T('5')
    await drag(x,y,x,y+40,hold=600);print('longpress move',a,'->',await T('5'))
    # lock then drag -> should not move
    await pg.click('[data-a=lock]');x,y=await pos('t:5');a=await T('5')
    await drag(x,y,x+40,y);print('locked drag',a,'->',await T('5'))
    await pg.click('[data-a=lock]')
    # nudge
    await pg.click('[data-a=nudge]');a=await T('5')
    await pg.click('#nudge [data-n="r+15"]');print('nudge rot',a,'->',await T('5'),'undo',await pg.evaluate('U.length'))
    await pg.click('[data-a=undo]');print('after undo',await T('5'))
    # multi + align
    await pg.evaluate("ui.sel=[];ui.nudge=false;render()")
    await pg.click('[data-a=multi]')
    for i in ['5','7','8']:
      x,y=await pos('t:'+i);await tap(x,y)
    print('multi sel',await pg.evaluate('ui.sel.length'))
    await pg.click('[data-a=align]');await pg.wait_for_timeout(200);await pg.click('[data-a=al][data-v=aL]')
    print('aligned x',[ (await T(i))[0] for i in '578'])
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'f1.png'))
    await pg.click('[data-a=multi-done]')
    # join mode
    x,y=await pos('t:9');await tap(x,y);await pg.click('[data-a=props]');await pg.wait_for_timeout(200)
    await pg.click('[data-a=join]');await pg.wait_for_timeout(100)
    i18=await pg.evaluate("S.tables.find(t=>t.n==='18'&&t.zone==='hall').id");x,y=await pos('t:'+i18);await tap(x,y)
    print('join',await pg.evaluate("[S.tables.find(t=>t.id==='9').join,S.tables.find(t=>t.n==='18').join]"))
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'f2.png'))
    await pg.click('[data-a=join-done]')
    # hall switch and edit
    await pg.click('.hchip[data-v=vip1]');await pg.wait_for_timeout(200);await pg.screenshot(path=str(ROOT/'tests'/'shots'/'f3.png'))
    await pg.click('.hchip[data-v=vip1]');await pg.wait_for_timeout(200);await pg.screenshot(path=str(ROOT/'tests'/'shots'/'f4.png'))
    await pg.click('#sheet [data-a=close]');await pg.wait_for_timeout(200)
    # copy export
    await pg.click('[data-a=menu]');await pg.click('[data-a=copy]');await pg.wait_for_timeout(200)
    j=await pg.evaluate("document.querySelector('#jout').value");import json;d=json.loads(j);print('export',len(d['tables']),len(d['decor']))
    print('errs',errs);await b.close()
asyncio.run(main())
