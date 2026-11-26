import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
import asyncio,json,datetime
from playwright.async_api import async_playwright
URL=(ROOT/'dist'/'booking.html').as_uri()
async def run(b,when,label):
    ctx=await b.new_context(viewport={'width':390,'height':844})
    pg=await ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:m.type=='error' and errs.append(m.text))
    await pg.clock.install(time=when)
    async def c(sel,n=0):
        await pg.locator(sel).nth(n).click();await pg.wait_for_timeout(60)
    notes=[]
    await pg.goto(URL);await pg.wait_for_timeout(300)
    # guest flow
    t1=await pg.locator('.chip.on').all_inner_texts();notes.append(('guest default',t1[:3]))
    await c('[data-act=dur][data-v="240"]') if await pg.locator('[data-act=dur][data-v="240"]').count() else None
    for i in range(10): await c('[data-act="g+"]')
    await c('[data-act=go][data-v="2"]')
    ok=await pg.locator('g.tbl.ok, g.tbl.mg').count();notes.append(('free for 12',ok))
    if ok:
        await c('g.tbl.ok, g.tbl.mg');await c('[data-act=pick]')
        await c('[data-act=book]');notes.append(('err empty',await pg.locator('.err').inner_text()))
        await pg.fill('#f-name','<b>Тест</b>');await pg.fill('#f-phone','87001112233');await c('[data-act=book]')
        notes.append(('done',(await pg.locator('h1').inner_text())))
    # host
    await c('[data-act=mode][data-v=admin]');await pg.fill('#pin','1234');await c('[data-act=pin]')
    await pg.locator('#trange').fill('1200');await pg.wait_for_timeout(50)
    notes.append(('host chips',(await pg.locator('.chips .chip').all_inner_texts())[:3]))
    await c('[data-act=tsort][data-v=free]');await c('[data-act=tview][data-v=map]');await c('[data-act=tview][data-v=cards]')
    await c('[data-act=tsheet]');
    if await pg.locator('[data-act=walkin]:not([disabled])').count():
        await c('[data-act=walkin]');notes.append(('walkin',await pg.locator('.sheet h2').inner_text()))
        await c('[data-act=move]');n=await pg.locator('[data-act=moveto]').count();notes.append(('move opts',n))
        if n: await c('[data-act=moveto]')
        await c('[data-act=btime]');await c('[data-act=tadj][data-v="e:0"]');await c('[data-act=tadj][data-v="s:-30"]')
        if await pg.locator('[data-act=tsave]:not([disabled])').count(): await c('[data-act=tsave]')
        else: await c('.sheet [data-act=bsheet]')
        await c('[data-act=bstatus][data-v=closed]');await c('[data-act=bcancel]');await c('[data-act=bcancel]')
        await c('[data-act=bstatus][data-v=new]')
        await c('[data-act=bguests][data-v="1"]')
        await c('[data-act=close]')
    await c('[data-act=atab][data-v=list]')
    await c('[data-act=bseg][data-v=done]');await c('[data-act=bseg][data-v=act]');await c('[data-act=banq]');await c('[data-act=banq]')
    await c('[data-act=bf][data-v=new]');await pg.fill('#q','7000');await pg.fill('#q','');
    await c('[data-act=nb-open]');await c('[data-act=nb-save]');notes.append(('nb err',await pg.locator('.sheet .err').inner_text()))
    if await pg.locator('[data-act=nb-t]').count():
        await c('[data-act=nb-t]');await pg.fill('#nb-name','Звонок');await pg.select_option('#nb-time',index=2);await c('[data-act=nb-dur][data-v="0"]');await c('[data-act=nb-save]')
    # editor
    await c('[data-act=atab][data-v=edit]')
    for i in range(17):
        await c('[data-act=add]');await c(f'[data-act=add-item][data-v="{i}"]')
        await c('[data-act=rot]');await c('[data-act=dup]');await c('[data-act="p-size"]') if await pg.locator('[data-act="p-size"]').count() else None
    await c('g.tbl[data-k=t]');
    if await pg.locator('[data-act=p-join]').count(): await c('[data-act=p-join]')
    await c('[data-act=props]');await pg.set_input_files('#p-photo','/mnt/user-data/uploads/1810c217-image.jpg');await pg.wait_for_timeout(800)
    await c('[data-act=props-save]')
    await c('[data-act=del]');await c('[data-act=del]')
    for i in range(5): await c('[data-act=undo]')
    await c('[data-act=z-add]');await pg.fill('#z-name','Терраса');await pg.locator('#z-name').blur();await c('[data-act=z-h][data-v="40"]');await c('[data-act=z-del]');await c('[data-act=z-del]')
    await c('[data-act=copy-json]');j=await pg.locator('#j-out').input_value()
    await c('[data-act=show-in]');await pg.fill('#j-in',j);await c('[data-act=load-json]')
    await c('[data-act=show-in]');await pg.fill('#j-in','мусор');await c('[data-act=load-json]')
    await c('[data-act=atab][data-v=set]');await pg.fill('#s-close','23:00');await c('[data-act=save-set]')
    await c('[data-act=atab][data-v=tables]');await c('[data-act=atab][data-v=list]')
    size=await pg.evaluate("(localStorage.getItem('rest-booking-v4')||'').length")
    notes.append(('storage KB',size//1024))
    # reload persists
    await pg.reload();await pg.wait_for_timeout(300)
    notes.append(('reload title',await pg.locator('h1').inner_text()))
    print(label,'ERRORS:',errs);[print('  ',n) for n in notes]
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        await run(b,datetime.datetime(2026,11,22,1,4),'01:04')
        await run(b,datetime.datetime(2026,11,22,14,0),'14:00')
        await run(b,datetime.datetime(2026,11,22,23,50),'23:50')
        await b.close()
asyncio.run(main())
