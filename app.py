import asyncio, json, os
from datetime import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = os.getenv('BOT_TOKEN', '')
PUBLIC_URL = os.getenv('PUBLIC_URL', 'http://localhost:8080').rstrip('/')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '')
BOT = None

SERVICES = {
    'support': ('Поддерживающая уборка', 2500, 45),
    'general': ('Генеральная уборка', 4500, 75),
    'repair': ('Уборка после ремонта', 6500, 100),
    'office': ('Уборка офиса', 3500, 55),
}

HTML = r'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><script src="https://telegram.org/js/telegram-web-app.js"></script><style>
*{box-sizing:border-box}body{font-family:Arial,sans-serif;margin:0;background:#f3f6f4;color:#17201b}.wrap{padding:16px;max-width:650px;margin:auto}.box{background:#fff;border-radius:22px;padding:20px;margin-bottom:14px;box-shadow:0 6px 24px #0000000b}h1{font-size:27px;margin:4px 0 8px}.green{color:#20a464;font-weight:800;font-size:12px;letter-spacing:.08em}.muted{color:#6f7972;font-size:14px;line-height:1.4}.step{display:none}.step.active{display:block}.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.card{border:2px solid #edf0ee;background:#fff;border-radius:17px;padding:15px;cursor:pointer;min-height:108px}.card.selected{border-color:#20a464;background:#effbf4}.card b{display:block;margin-bottom:6px}.price{color:#20a464;font-weight:800;margin-top:8px}.btn{width:100%;border:0;border-radius:15px;padding:15px;background:#20a464;color:#fff;font-size:16px;font-weight:800;margin-top:14px;cursor:pointer}.btn.secondary{background:#edf3ef;color:#17201b}.btn:disabled{opacity:.45}.field{margin:12px 0}.field label{font-size:13px;font-weight:700;display:block;margin-bottom:6px}.field input,.field select,.field textarea{width:100%;border:1px solid #dce3de;border-radius:13px;padding:13px;font-size:16px;background:#fff}.extras label{display:flex;justify-content:space-between;gap:10px;padding:12px 0;border-bottom:1px solid #eee}.total{font-size:25px;font-weight:900;color:#20a464}.row{display:flex;justify-content:space-between;gap:12px;margin:8px 0}.ok{text-align:center;padding:20px}.error{color:#b42318;font-size:14px;margin-top:10px}.progress{font-size:13px;color:#778078;margin-bottom:10px}</style></head><body><div class="wrap">
<div class="box"><div class="green">CLEANING SERVICE</div><h1>Заказ уборки</h1><div class="muted">Оформите заказ за несколько шагов. Итоговую заявку получит менеджер.</div></div>
<div class="box step active" id="s1"><div class="progress">Шаг 1 из 5</div><h2>Выберите уборку</h2><div class="grid">
<div class="card service" data-id="support" data-name="Поддерживающая уборка" data-base="2500" data-rate="45"><b>Поддерживающая</b><span class="muted">Регулярная уборка</span><div class="price">от 2 500 ₽</div></div>
<div class="card service" data-id="general" data-name="Генеральная уборка" data-base="4500" data-rate="75"><b>Генеральная</b><span class="muted">Глубокая уборка</span><div class="price">от 4 500 ₽</div></div>
<div class="card service" data-id="repair" data-name="После ремонта" data-base="6500" data-rate="100"><b>После ремонта</b><span class="muted">Строительная пыль</span><div class="price">от 6 500 ₽</div></div>
<div class="card service" data-id="office" data-name="Уборка офиса" data-base="3500" data-rate="55"><b>Офисы</b><span class="muted">Для бизнеса</span><div class="price">от 3 500 ₽</div></div></div><button class="btn" id="next1" disabled>Продолжить</button></div>
<div class="box step" id="s2"><div class="progress">Шаг 2 из 5</div><h2>Параметры помещения</h2><div class="field"><label>Площадь, м²</label><input id="area" type="number" min="10" max="1000" value="50"></div><div class="field"><label>Количество комнат</label><select id="rooms"><option>1</option><option>2</option><option selected>3</option><option>4</option><option>5+</option></select></div><div class="extras"><label><span>Помыть окна</span><span><input class="extra" type="checkbox" data-price="1500" value="Окна"> +1 500 ₽</span></label><label><span>Духовка</span><span><input class="extra" type="checkbox" data-price="700" value="Духовка"> +700 ₽</span></label><label><span>Холодильник</span><span><input class="extra" type="checkbox" data-price="700" value="Холодильник"> +700 ₽</span></label><label><span>Балкон</span><span><input class="extra" type="checkbox" data-price="1000" value="Балкон"> +1 000 ₽</span></label></div><button class="btn" id="next2">Продолжить</button><button class="btn secondary back" data-to="1">Назад</button></div>
<div class="box step" id="s3"><div class="progress">Шаг 3 из 5</div><h2>Адрес и время</h2><div class="field"><label>Адрес</label><input id="address" placeholder="Улица, дом, квартира"></div><div class="field"><label>Дата</label><input id="date" type="date"></div><div class="field"><label>Время</label><input id="time" type="time" value="10:00"></div><div id="e3" class="error"></div><button class="btn" id="next3">Продолжить</button><button class="btn secondary back" data-to="2">Назад</button></div>
<div class="box step" id="s4"><div class="progress">Шаг 4 из 5</div><h2>Контактные данные</h2><div class="field"><label>Имя</label><input id="name" placeholder="Ваше имя"></div><div class="field"><label>Телефон</label><input id="phone" type="tel" placeholder="+7 999 000-00-00"></div><div class="field"><label>Комментарий</label><textarea id="comment" rows="3" placeholder="Домофон, особенности уборки и т.д."></textarea></div><div id="e4" class="error"></div><button class="btn" id="next4">Проверить заказ</button><button class="btn secondary back" data-to="3">Назад</button></div>
<div class="box step" id="s5"><div class="progress">Шаг 5 из 5</div><h2>Ваш заказ</h2><div id="summary"></div><div class="row"><b>Ориентировочно</b><span class="total" id="total"></span></div><div class="muted">Менеджер подтвердит финальную стоимость после уточнения деталей.</div><div id="sendError" class="error"></div><button class="btn" id="send">Отправить заявку</button><button class="btn secondary back" data-to="4">Изменить данные</button></div>
<div class="box step" id="done"><div class="ok"><h2>Заявка отправлена ✅</h2><p class="muted">Менеджер получил заказ и свяжется с вами для подтверждения.</p><button class="btn" onclick="window.Telegram&&Telegram.WebApp?Telegram.WebApp.close():location.reload()">Закрыть</button></div></div>
</div><script>
const tg=window.Telegram&&window.Telegram.WebApp?window.Telegram.WebApp:null;if(tg){tg.ready();tg.expand();}let order={};
function show(n){document.querySelectorAll('.step').forEach(x=>x.classList.remove('active'));document.getElementById(n==='done'?'done':'s'+n).classList.add('active');window.scrollTo(0,0)}
function money(n){return Math.round(n).toLocaleString('ru-RU')+' ₽'}
function calc(){let a=Math.max(10,Number(document.getElementById('area').value)||10);let p=Math.max(order.base,a*order.rate);document.querySelectorAll('.extra:checked').forEach(x=>p+=Number(x.dataset.price));return p}
document.querySelectorAll('.service').forEach(c=>c.onclick=()=>{document.querySelectorAll('.service').forEach(x=>x.classList.remove('selected'));c.classList.add('selected');order.service=c.dataset.name;order.service_id=c.dataset.id;order.base=+c.dataset.base;order.rate=+c.dataset.rate;document.getElementById('next1').disabled=false;if(tg&&tg.HapticFeedback)tg.HapticFeedback.selectionChanged()});
document.getElementById('next1').onclick=()=>show(2);document.getElementById('next2').onclick=()=>show(3);
document.querySelectorAll('.back').forEach(b=>b.onclick=()=>show(+b.dataset.to));
const today=new Date();document.getElementById('date').min=today.toISOString().slice(0,10);document.getElementById('date').value=today.toISOString().slice(0,10);
document.getElementById('next3').onclick=()=>{let a=document.getElementById('address').value.trim(),d=document.getElementById('date').value,t=document.getElementById('time').value;if(!a||!d||!t){document.getElementById('e3').textContent='Заполните адрес, дату и время';return}document.getElementById('e3').textContent='';show(4)};
document.getElementById('next4').onclick=()=>{let n=document.getElementById('name').value.trim(),p=document.getElementById('phone').value.trim();if(n.length<2||p.replace(/\D/g,'').length<10){document.getElementById('e4').textContent='Укажите имя и корректный телефон';return}document.getElementById('e4').textContent='';order.area=+document.getElementById('area').value;order.rooms=document.getElementById('rooms').value;order.extras=[...document.querySelectorAll('.extra:checked')].map(x=>x.value);order.address=document.getElementById('address').value.trim();order.date=document.getElementById('date').value;order.time=document.getElementById('time').value;order.name=n;order.phone=p;order.comment=document.getElementById('comment').value.trim();order.price=calc();document.getElementById('summary').innerHTML='<div class="row"><span>Услуга</span><b>'+order.service+'</b></div><div class="row"><span>Площадь</span><b>'+order.area+' м²</b></div><div class="row"><span>Дополнительно</span><b>'+(order.extras.join(', ')||'Нет')+'</b></div><div class="row"><span>Когда</span><b>'+order.date+' '+order.time+'</b></div><div class="row"><span>Адрес</span><b>'+order.address+'</b></div><div class="row"><span>Телефон</span><b>'+order.phone+'</b></div>';document.getElementById('total').textContent=money(order.price);show(5)};
document.getElementById('send').onclick=async()=>{let b=document.getElementById('send'),e=document.getElementById('sendError');b.disabled=true;b.textContent='Отправляем...';e.textContent='';try{let r=await fetch('/api/order',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...order,telegram_user:tg&&tg.initDataUnsafe&&tg.initDataUnsafe.user?tg.initDataUnsafe.user:null})});let j=await r.json();if(!r.ok||!j.ok)throw new Error(j.error||'Ошибка отправки');if(tg&&tg.HapticFeedback)tg.HapticFeedback.notificationOccurred('success');show('done')}catch(x){e.textContent='Не удалось отправить заявку. Попробуйте еще раз.';b.disabled=false;b.textContent='Отправить заявку'}};
</script></body></html>'''

async def index(request):
    return web.Response(text=HTML, content_type='text/html', headers={'Cache-Control': 'no-store, no-cache, must-revalidate'})

async def submit_order(request):
    try:
        data = await request.json()
        required = ['service', 'area', 'address', 'date', 'time', 'name', 'phone']
        if any(not data.get(x) for x in required):
            return web.json_response({'ok': False, 'error': 'missing fields'}, status=400)
        phone_digits = ''.join(c for c in str(data['phone']) if c.isdigit())
        if len(phone_digits) < 10:
            return web.json_response({'ok': False, 'error': 'invalid phone'}, status=400)
        extras = ', '.join(data.get('extras') or []) or 'нет'
        tg_user = data.get('telegram_user') or {}
        username = ('@' + tg_user.get('username')) if tg_user.get('username') else 'не указан'
        text = (
            '🧹 НОВАЯ ЗАЯВКА НА УБОРКУ\n\n'
            f"Услуга: {data['service']}\nПлощадь: {data['area']} м²\nКомнат: {data.get('rooms','—')}\n"
            f"Допуслуги: {extras}\nОриентировочно: {int(data.get('price',0)):,} ₽\n\n"
            f"📍 Адрес: {data['address']}\n📅 Дата: {data['date']}\n🕐 Время: {data['time']}\n\n"
            f"👤 Клиент: {data['name']}\n📞 Телефон: {data['phone']}\nTelegram: {username}\n"
            f"Комментарий: {data.get('comment') or 'нет'}"
        ).replace(',', ' ')
        delivered = False
        if BOT:
            chat_id = ADMIN_CHAT_ID or str(tg_user.get('id') or '')
            if chat_id:
                await BOT.send_message(chat_id, text)
                delivered = True
            if tg_user.get('id') and str(tg_user.get('id')) != str(chat_id):
                await BOT.send_message(tg_user['id'], 'Заявка принята ✅\nМенеджер свяжется с вами для подтверждения заказа.')
        print('ORDER', json.dumps(data, ensure_ascii=False))
        return web.json_response({'ok': True, 'delivered': delivered})
    except Exception as e:
        print('ORDER ERROR', repr(e))
        return web.json_response({'ok': False, 'error': 'server error'}, status=500)

async def run_web():
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_post('/api/order', submit_order)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', 8080).start()

async def main():
    global BOT
    if TOKEN and not TOKEN.startswith('PASTE_'):
        BOT = Bot(TOKEN)
    await run_web()
    if not BOT:
        print('BOT_TOKEN not configured; Mini App web server is running on :8080')
        while True: await asyncio.sleep(3600)
    dp = Dispatcher()
    @dp.message(CommandStart())
    async def start(m: Message):
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Открыть приложение', web_app=WebAppInfo(url=PUBLIC_URL))]])
        await m.answer('Добро пожаловать. Нажмите кнопку ниже, чтобы оформить уборку.', reply_markup=kb)
    await dp.start_polling(BOT)

if __name__ == '__main__':
    asyncio.run(main())
