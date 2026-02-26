import asyncio
import requests
from datetime import datetime  # Vaqt bilan ishlash uchun
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# --- SOZLAMALAR ---
API_TOKEN = '8071338659:AAHvGOdBtxxVhAihQpFwii4_dIDZehkW4fo' 
CBU_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- VALYUTA MA'LUMOTINI OLISH FUNKSIYASI ---
def get_exchange_rates():
    try:
        response = requests.get(CBU_URL)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
    return None

# --- ASOSIY MENYU ---
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🇺🇸 USD (Dollar)"))
    builder.row(types.KeyboardButton(text="🇪🇺 EUR (Evro)"), types.KeyboardButton(text="🇷🇺 RUB (Rubl)"))
    builder.row(types.KeyboardButton(text="🔄 Yangilash"))
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Salom! Markaziy Bank kurslarini ko'rsatuvchi botga xush kelibsiz.",
        reply_markup=main_menu()
    )

# --- XABARLARNI QAYTA ISHLASH ---
@dp.message(F.text.contains("USD") | F.text.contains("EUR") | F.text.contains("RUB") | (F.text == "🔄 Yangilash"))
async def send_rate(message: types.Message):
    data = get_exchange_rates()
    
    if not data:
        await message.answer("Ma'lumot olishda xatolik yuz berdi.")
        return

    # Hozirgi vaqtni olish (Toshkent vaqti bilan)
    now = datetime.now().strftime("%H:%M:%S")
    
    currency_code = ""
    if "USD" in message.text: currency_code = "USD"
    elif "EUR" in message.text: currency_code = "EUR"
    elif "RUB" in message.text: currency_code = "RUB"
    
    if currency_code:
        for item in data:
            if item['Ccy'] == currency_code:
                # Matnga soat va sana qo'shildi
                text = (f"🏦 **Markaziy Bank kursi**\n"
                        f"📅 Sana: {item['Date']}\n"
                        f"⏰ Yangilangan vaqt: {now}\n\n"
                        f"💰 1 {item['CcyNm_UZ']} = **{item['Rate']} so'm**\n"
                        f"📈 O'zgarish: {item['Diff']} so'm")
                await message.answer(text, parse_mode="Markdown")
                break
    else:
        await message.answer(f"Kurslar yangilandi! \nSoat: {now}", reply_markup=main_menu())

async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi.")
