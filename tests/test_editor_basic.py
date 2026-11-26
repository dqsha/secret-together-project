import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
import asyncio,json
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    ctx=await b.new_context(**p.devices['iPhone 13'])
    pg=await ctx.new_page()
    errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('console',lambda m:errs.append('console:'+m.text) if m.type=='error' else None)
    await pg.goto((ROOT/'dist'/'editor.html').as_uri())
    await pg.wait_for_timeout(800)
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'e1.png'))
    await pg.click('[data-a=help-ok]')
    # find table 1 position on screen
    box=await pg.evaluate("""()=>{const g=document.querySelector('[data-oid="t:1"]');const r=g.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}""")
    print('t1',box)
    pos0=await pg.evaluate("()=>{const t=S.tables.find(t=>t.id==='1');return [t.x,t.y]}")
    # swipe over unselected table: should pan, not move
    cdp=await ctx.new_cdp_session(pg)
    async def drag(x0,y0,x1,y1,steps=8,hold=0):
      await cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x0,'y':y0}]})
      if hold: await pg.wait_for_timeout(hold)
      for i in range(1,steps+1):
        await cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x0+(x1-x0)*i/steps,'y':y0+(y1-y0)*i/steps}]})
      await cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
      await pg.wait_for_timeout(100)
    async def tap(x,y):
      await cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
      await cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
      await pg.wait_for_timeout(120)
    cam0=await pg.evaluate("()=>({...ui.cam})")
    await drag(box[0],box[1],box[0]+60,box[1]+40)
    pos1=await pg.evaluate("()=>{const t=S.tables.find(t=>t.id==='1');return [t.x,t.y]}")
    cam1=await pg.evaluate("()=>({...ui.cam})")
    print('swipe unselected: moved?',pos0!=pos1,'cam moved',cam0!=cam1, 'sel',await pg.evaluate('ui.sel'))
    box=await pg.evaluate("""()=>{const g=document.querySelector('[data-oid="t:1"]');const r=g.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}""")
    await tap(*box)
    print('after tap sel',await pg.evaluate('ui.sel'))
    await drag(box[0],box[1],box[0]+50,box[1]+10)
    pos2=await pg.evaluate("()=>{const t=S.tables.find(t=>t.id==='1');return [t.x,t.y]}")
    print('drag selected: ',pos1,'->',pos2,'undo',await pg.evaluate('U.length'))
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'e2.png'))
    # rotate handle
    h=await pg.evaluate("""()=>{const g=document.querySelector('[data-h=rot] circle');const r=g.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}""")
    t1=await pg.evaluate("""()=>{const t=S.tables.find(t=>t.id==='1');return toS(t.x,t.y)}""")
    await drag(h[0],h[1],t1[0]+80,t1[1])
    print('rot',await pg.evaluate("S.tables.find(t=>t.id==='1').rot"))
    # resize se
    h=await pg.evaluate("""()=>{const g=document.querySelector('[data-h=se] circle');const r=g.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}""")
    await drag(h[0],h[1],h[0]+20,h[1]+20)
    print('size',await pg.evaluate("(t=>[t.w,t.h,t.x,t.y])(S.tables.find(t=>t.id==='1'))"))
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'e3.png'))
    # props sheet
    await pg.click('[data-a=props]');await pg.wait_for_timeout(300)
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'e4.png'))
    await pg.click('#sheet [data-a=st][data-f=seats][data-d="1"]')
    print('seats',await pg.evaluate("S.tables.find(t=>t.id==='1').seats"))
    await pg.click('#sheet [data-a=close]');await pg.wait_for_timeout(200);print('sheet',await pg.evaluate('ui.sheet'),errs)
    # add library
    await pg.click('[data-a=multi-done]') if await pg.query_selector('[data-a=multi-done]') else None
    print('at', await pg.evaluate('(()=>{const e=document.elementFromPoint(30,600);return e.outerHTML.slice(0,120)+" | "+(e.closest("[data-oid]")?.dataset.oid)})()'), await pg.evaluate('lastTap'))
    print('after tap30', await pg.evaluate('[ui.sheet,JSON.stringify(ui.sel),document.querySelector("#sheet").className]'))
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'e45.png'))
    await pg.evaluate("ui.sel=[];render()")
    await pg.click('[data-a=add]');await pg.wait_for_timeout(300)
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'e5.png'))
    await pg.click('.cat[data-v="1"]');await pg.wait_for_timeout(100)
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'e6.png'))
    await pg.click('.tile[data-v="1"]');await pg.wait_for_timeout(300)
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'e7.png'))
    # pinch
    await cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':150,'y':400,'id':1},{'x':250,'y':400,'id':2}]})
    for i in range(1,8):
      await cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':150-i*10,'y':400,'id':1},{'x':250+i*10,'y':400,'id':2}]})
    await cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    await pg.wait_for_timeout(200)
    print('zoom k',await pg.evaluate('ui.cam.k'))
    await pg.screenshot(path=str(ROOT/'tests'/'shots'/'e8.png'))
    # menu
    await pg.click('[data-a=menu]');await pg.wait_for_timeout(200);await pg.screenshot(path=str(ROOT/'tests'/'shots'/'e9.png'))
    print('errs',errs)
    await b.close()
asyncio.run(main())
