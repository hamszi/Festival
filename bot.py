import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from database import init_db, add_spectator, add_participant

load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

class SpectatorStates(StatesGroup):
    waiting_for_date = State()
    waiting_for_family_size = State()
    waiting_for_name_age = State()

class ParticipantStates(StatesGroup):
    waiting_for_team_size = State()
    waiting_for_team_name = State()
    waiting_for_location = State()
    waiting_for_participants_info = State()
    waiting_for_special_status = State()
    waiting_for_phone = State()
    waiting_for_accommodation = State()

def get_role_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎣 Я ПРИДУ КАК ЗРИТЕЛЬ", callback_data="spectator"),
            InlineKeyboardButton(text="🏆 ХОЧУ ПРИНЯТЬ УЧАСТИЕ", callback_data="participant")
        ]
    ])
    return keyboard

def get_family_size_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 Приду один", callback_data="family_size_1"),
            InlineKeyboardButton(text="👨‍👩‍👧‍👦 Приду с семьёй", callback_data="family_size_family")
        ]
    ])
    return keyboard

def get_special_status_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data="special_status_yes"),
            InlineKeyboardButton(text="❌ Нет", callback_data="special_status_no")
        ]
    ])
    return keyboard

def get_accommodation_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🏠 Ночуем дома", callback_data="accommodation_home")
        ],
        [
            InlineKeyboardButton(text="⛺ Ночуем в своей палатке", callback_data="accommodation_own_tent")
        ],
        [
            InlineKeyboardButton(text="⛺ Нужна аренда палатки", callback_data="accommodation_rent_tent")
        ],
        [
            InlineKeyboardButton(text="🏨 Размещение в номере", callback_data="accommodation_room")
        ]
    ])
    return keyboard

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = """🎣 Приветствуем вас на регистрации Международного семейного рыболовного фестиваля 2025 «Папа,мама,я-рыболовная семья»! 🎣

📅 Дата фестиваля:
31 мая (1 тур)
1 июня (2 тур)

📍 Место проведения: Залив р.Волги, п.Займище

Выберите, как вы хотите участвовать в фестивале:"""
    
    await message.answer(welcome_text, reply_markup=get_role_keyboard())

@dp.callback_query(lambda c: c.data in ["spectator", "participant"])
async def process_role_selection(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "spectator":
        date_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 31 мая", callback_data="date_31"),
                InlineKeyboardButton(text="📅 1 июня", callback_data="date_1")
            ],
            [InlineKeyboardButton(text="📅 Буду 2 дня", callback_data="date_both")]
        ])
        await callback.message.answer("📅 Выберите дату посещения:", reply_markup=date_keyboard)
        await state.set_state(SpectatorStates.waiting_for_date)
    else:
        # Создаем клавиатуру для выбора количества участников
        team_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"👥 {i} человек", callback_data=f"team_{i}") for i in range(2, 6)]
        ])
        await callback.message.answer("👥 Какое количество человек в вашей команде (от 2 до 5)?", reply_markup=team_keyboard)
        await state.set_state(ParticipantStates.waiting_for_team_size)

@dp.callback_query(lambda c: c.data.startswith("date_"), SpectatorStates.waiting_for_date)
async def process_date_selection(callback: types.CallbackQuery, state: FSMContext):
    date_text = {
        "date_31": "31 мая",
        "date_1": "1 июня",
        "date_both": "31 мая и 1 июня"
    }
    await state.update_data(selected_date=date_text[callback.data])
    await callback.message.answer(f"📅 Вы выбрали дату: {date_text[callback.data]}")
    await callback.message.answer("👥 Выберите, как вы планируете прийти:", reply_markup=get_family_size_keyboard())
    await state.set_state(SpectatorStates.waiting_for_family_size)

@dp.callback_query(lambda c: c.data.startswith("family_size_"), SpectatorStates.waiting_for_family_size)
async def process_family_size(callback: types.CallbackQuery, state: FSMContext):
    family_text = {
        "family_size_1": "один",
        "family_size_family": "с семьёй"
    }
    await state.update_data(family_size=family_text[callback.data])
    await callback.message.answer(f"👥 Вы выбрали прийти {family_text[callback.data]}")
    await callback.message.answer("📝 Укажите Ваше имя и возраст (или возраст членов вашей семьи):")
    await state.set_state(SpectatorStates.waiting_for_name_age)

@dp.message(SpectatorStates.waiting_for_name_age)
async def process_name_age(message: types.Message, state: FSMContext):
    data = await state.get_data()
    success = add_spectator(
        user_id=message.from_user.id,
        date=data['selected_date'],
        family_size=data['family_size'],
        name_age=message.text
    )
    
    if success:
        await message.answer("""✅ Регистрация успешно завершена!

📞 По любым организационным вопросам вы можете обращаться по номеру тел.: 89……….

🎣 Благодарим Вас за регистрацию! И ждём Вас/вашу семью на Фестивале!""")
    else:
        await message.answer("❌ Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.")
    
    await state.clear()

@dp.callback_query(lambda c: c.data.startswith("team_"), ParticipantStates.waiting_for_team_size)
async def process_team_size(callback: types.CallbackQuery, state: FSMContext):
    team_size = callback.data.split("_")[1]
    await state.update_data(team_size=team_size)
    await callback.message.answer(f"👥 Вы выбрали команду из {team_size} человек")
    await callback.message.answer("📝 Укажите название вашей команды:")
    await state.set_state(ParticipantStates.waiting_for_team_name)

@dp.message(ParticipantStates.waiting_for_team_name)
async def process_team_name(message: types.Message, state: FSMContext):
    await state.update_data(team_name=message.text)
    await message.answer("📍 Какой населенный пункт/регион/страну вы представляете?")
    await state.set_state(ParticipantStates.waiting_for_location)

@dp.message(ParticipantStates.waiting_for_location)
async def process_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer("📝 Укажите ФИО участников и их даты рождения:")
    await state.set_state(ParticipantStates.waiting_for_participants_info)

@dp.message(ParticipantStates.waiting_for_participants_info)
async def process_participants_info(message: types.Message, state: FSMContext):
    await state.update_data(participants_info=message.text)
    await message.answer("""❓ Есть ли в семье дети-инвалиды или является ли кто-то из членов семьи участником/ветераном СВО?""", 
                        reply_markup=get_special_status_keyboard())
    await state.set_state(ParticipantStates.waiting_for_special_status)

@dp.callback_query(lambda c: c.data.startswith("special_status_"), ParticipantStates.waiting_for_special_status)
async def process_special_status(callback: types.CallbackQuery, state: FSMContext):
    status = callback.data.split("_")[2]
    await state.update_data(special_status=status)
    
    if status == "yes":
        await callback.message.answer("""✅ Ваша семья примет участие в фестивале на льготных условиях.
        
📞 Пожалуйста, укажите ваш контактный номер телефона для связи с вами:""")
    else:
        await callback.message.answer("📞 Пожалуйста, укажите ваш контактный номер телефона:")
    
    await state.set_state(ParticipantStates.waiting_for_phone)

@dp.message(ParticipantStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("""🏠 Выберите подходящий пакет с пребыванием в ночное время:""", 
                        reply_markup=get_accommodation_keyboard())
    await state.set_state(ParticipantStates.waiting_for_accommodation)

@dp.callback_query(lambda c: c.data.startswith("accommodation_"), ParticipantStates.waiting_for_accommodation)
async def process_accommodation(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    accommodation = callback.data.split("_")[1]

    prices = {
        "home": {"adult": 1500, "child": 750},
        "own_tent": {"adult": 1600, "child": 850},
        "rent_tent": {"adult": 2000, "child": 1200},
        "room": {"adult": 4000, "child": 2500}
    }
    
    price = prices[accommodation]
    await callback.message.answer(f"""💰 Стоимость размещения:
Взрослый: {price['adult']}₽
Ребенок: {price['child']}₽""")

    success = add_participant(
        user_id=callback.from_user.id,
        team_size=data['team_size'],
        team_name=data['team_name'],
        location=data['location'],
        participants_info=data['participants_info'],
        special_status=data['special_status'],
        phone=data['phone'],
        accommodation=accommodation
    )
    
    if success:
        await callback.message.answer("""✅ Поздравляем, Ваша семья примет участие в Международном семейном рыболовном фестивале 2025 «Папа, мама, я - рыболовная семья»!

🎣 Благодарим Вас за регистрацию и до встречи на незабываемом событии этого года!""")
    else:
        await callback.message.answer("❌ Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.")
    
    await state.clear()

@dp.startup()
async def startup():
    init_db()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main()) 