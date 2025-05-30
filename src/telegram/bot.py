from aiogram import Bot, Dispatcher, F, types  
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.storage.user_storage import storage
from src.telegram.states import RegistrationStates
from src.telegram.bot_isntance import bot
from configs.config import HELP_MESSAGE,START_MESSAGE,\
FORGETME_MESSAGE,REGISTER_START_MESSAGE,REGISTER_TAKEN_MESSAGE,\
REGISTER_COMPLETE_MESSAGE,ADMIN_PWD_MESSAGE,ADMIN_COMPLETE_MESSAGE,\
FORGETME_TAKEN_MESSAGE, ADMIN_PWD,ADMIN_FORBIDDEN_MESSAGE, REMINDER_MESSAGE,\
LINK_MESSAGE,LINK_SUCCES_SEND,LINK_TEMPLATE,LINK_CONFIRM_MESSAGE


from pathlib import Path

dp = Dispatcher()


user_path=Path("./data/users.json")
users=storage(user_path)

attended=Path("./data/attended.json")
attended={}

admin_id=None
link=None

@dp.message(Command('start'))
async def start_command(message: types.Message):  
    await message.answer(START_MESSAGE)



@dp.message(Command('help'))
async def help_command(message: types.Message):  
    await message.answer(HELP_MESSAGE)



@dp.message(Command('register'))
async def register_command(message: types.Message, state:FSMContext): 
    id=str(message.from_user.id)
    if id in users.user_data.keys():
        await message.answer(REGISTER_TAKEN_MESSAGE%{"name":users.user_data[id]["full_name"]})
        return
 
    await message.answer(REGISTER_START_MESSAGE)
    await state.set_state(RegistrationStates.waiting_for_name)


@dp.message(RegistrationStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    user={}
    user["full_name"]=message.text
    user["chat_id"]=message.chat.id
    user["username"]=message.from_user.username
    users.add(user["chat_id"],user)
    
    #await bot.send_message(user["chat_id"],"hi")
    await message.answer(REGISTER_COMPLETE_MESSAGE%{"full_name":message.text})
    await state.clear()


@dp.message(Command('forgetme'))
async def forgetme_command(message: types.Message):  
    id=str(message.from_user.id)
    if not id in users.user_data.keys():
        await message.answer(FORGETME_TAKEN_MESSAGE)
        return 
    users.delete(id)
    await message.answer(FORGETME_MESSAGE)



#admin
@dp.message(Command('admin'))
async def admin_command(message: types.Message, state: FSMContext):  
    await message.answer(ADMIN_PWD_MESSAGE)
    await state.set_state(RegistrationStates.admin_login)

@dp.message(RegistrationStates.admin_login)
async def procces_pwd(message: types.Message, state: FSMContext):
    global admin_id
    if message.text!=ADMIN_PWD:
        await message.answer(ADMIN_FORBIDDEN_MESSAGE)
    
    admin_id=message.from_user.id
    await message.answer(ADMIN_COMPLETE_MESSAGE)
    await state.clear()


# send reminder
@dp.message(Command('send'))
async def send_command(message: types.Message):  
    if admin_id!=message.from_user.id:
        await message.answer(ADMIN_FORBIDDEN_MESSAGE)
        return
    
    for chat_id in users.user_data:
        try:
            await bot.send_message(int(chat_id),REMINDER_MESSAGE) 
        except TelegramForbiddenError as ex:
            print (ex)
            users.delete(chat_id)
    await message.answer("SENDED SUCCESFULLY")



@dp.message(Command('users'))
async def procces_users(message: types.Message):  
    if admin_id!=message.from_user.id:
        await message.answer(ADMIN_FORBIDDEN_MESSAGE)
        return
    
    answ=''
    for chat_id in users.user_data:
        answ+=f'{users.user_data[chat_id]}\n'
    await message.answer(answ)



#link
@dp.message(Command('link'))
async def link_command(message: types.Message, state: FSMContext):  
    if admin_id!=message.from_user.id:
        await message.answer(ADMIN_FORBIDDEN_MESSAGE)
        return
    await message.answer(LINK_MESSAGE)
    await state.set_state(RegistrationStates.link_send)

@dp.message(RegistrationStates.link_send)
async def procces_link(message: types.Message, state: FSMContext):
    global link 
    link=message.text

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="yes",
            callback_data=f"webinar_confirm"
        )]
    ])
    for chat_id in users.user_data:
        try:
            await bot.send_message(int(chat_id),LINK_CONFIRM_MESSAGE,reply_markup=keyboard) 
        except TelegramForbiddenError as ex:
            print (ex)
            users.delete(chat_id)
    await message.answer(LINK_SUCCES_SEND)
    await state.clear()


@dp.callback_query(F.data.startswith("webinar_confirm"))
async def send_link(callback: types.CallbackQuery):
    user_id=str(callback.message.chat.id)
    attended[user_id]=users.user_data[user_id]
    await callback.message.answer(LINK_TEMPLATE%link)
    await bot.send_message(int(admin_id),f'{attended[user_id]} joined')
    print(attended)