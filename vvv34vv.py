from telethon import TelegramClient, events, functions, errors
import asyncio
from datetime import datetime, timedelta
import random
import json
import os

# معلومات الحساب
api_id = '23399686'
api_hash = '44a2fb20b0851fe8c21418e0a5d55d24'
phone = '+905312573135'
group_username = 'mffkck'
message = 'ومضه'
interval = 190  # الوقت بين كل رسالة بالثواني

# معرف المستخدم المصرح له
authorized_user_id = 578828566

# ملفات التخزين
responses_file = 'responses.json'
special_users_file = 'special_users.json'

# تحميل الردود من الملف أو إنشاء ملف جديد
if os.path.exists(responses_file):
    with open(responses_file, 'r', encoding='utf-8') as file:
        responses = json.load(file)
else:
    responses = {
        "بتحبني": ["اي اكيد", "اموت فيك 🙃", "أهلاً وسهلاً، تكرم بحبك", "بحاول لا تلح", "تحبك حيه"],
        "ماكس": ["يي حكا بدري", "شبو مكــس", "شو", "اي يا قلبي", "عيونه"],
        "ممكن نتعرف": ["اكيد لا"],
        "مساء الخير": ["فل وياسمين"],
        "صباح الخير": ["يسعدلي صباحك كيفك يا قلبي"],
        "مرحبا": ["مراحب شو اخبارك"],
        "مسائوو": ["وعليكم السلام نورت"],
        "بونجور": ["وعليكم السلام نورت"],
        "كيفكن": ["تمام كيفك انت"],
        "كيفكم": ["تمام كيفك انت"]
    }
    with open(responses_file, 'w', encoding='utf-8') as file:
        json.dump(responses, file, ensure_ascii=False, indent=4)

# تحميل المستخدمين المميزين من الملف أو إنشاء ملف جديد
if os.path.exists(special_users_file):
    with open(special_users_file, 'r', encoding='utf-8') as file:
        special_user_ids = json.load(file)
else:
    special_user_ids = [authorized_user_id]
    with open(special_users_file, 'w', encoding='utf-8') as file:
        json.dump(special_user_ids, file, ensure_ascii=False, indent=4)

# تعريف الدالة لإرسال الرسالة إلى المجموعة
async def send_message_to_group(client, group_username, message, interval):
    while True:
        try:
            # تعديل الاسم وإضافة التوقيت بجانبه
            current_time = datetime.now().strftime('%I:%M')
            new_name = f"so.. {current_time}"  # استبدل "so.." باسمك الحالي
            await client(functions.account.UpdateProfileRequest(
                first_name=new_name
            ))
            print(f"Name updated to {new_name}")
            
            await client.send_message(group_username, message)
            print("Message sent successfully")
        except errors.ChatWriteForbiddenError:
            print("You can't write in this chat")
            break  # توقف عن المحاولة إذا لم يكن لديك صلاحيات الكتابة
        except errors.FloodWaitError as e:
            print(f"Flood wait error: You need to wait {e.seconds} seconds.")
            await asyncio.sleep(e.seconds)  # انتظر الوقت المطلوب إذا كان هناك خطأ في الانتظار
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        await asyncio.sleep(interval)  # انتظر الفترة المحددة قبل إرسال الرسالة التالية

# إنشاء جلسة العميل
client = TelegramClient('session_name', api_id, api_hash)

# Dictionary to keep track of message counts
user_message_counts = {}
auto_responses_enabled = True  # متغير لتتبع حالة الردود التلقائية
blocking_enabled = True  # متغير لتتبع حالة الحظر

# Dictionary to keep track of the last welcome time for special users
last_welcome_time = {}

@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    global auto_responses_enabled, blocking_enabled, last_welcome_time, responses, special_user_ids
    sender_id = event.sender_id
    message_text = event.raw_text
    print(f"Received message: {message_text}")  # طباعة الرسالة المستلمة للتتبع

    # التعامل مع الرسائل الخاصة
    if event.is_private:
        if sender_id in user_message_counts:
            user_message_counts[sender_id] += 1
        else:
            user_message_counts[sender_id] = 1

        # إرسال رسالة تحذير عند إرسال 3 رسائل
        if user_message_counts[sender_id] == 3:
            try:
                await event.respond("عذرا اذا واصلت في ارسال هكذا سوف يتم حظرك. اكتب في جملة واحدة وانتظر الرد.")
                print(f"Sent warning to user {sender_id}.")
            except Exception as e:
                print(f"Failed to send warning to user {sender_id}: {e}")

        # حظر المستخدم إذا أرسل أكثر من 5 رسائل
        if blocking_enabled and user_message_counts[sender_id] > 5:
            try:
                await client(functions.contacts.BlockRequest(id=sender_id))
                await event.respond("عزيزي، لديك 3 ثواني. هذه آخر فرصة لك. إذا لم تلتزم بما قلته لك، إذا لديك استفسار راجع المطور وتكلم @SY_X_MAN.")
                print(f"Blocked user {sender_id} for spamming.")
            except Exception as e:
                print(f"Failed to block user {sender_id}: {e}")

        # إيقاف الحظر وبدء الحظر
        if sender_id == authorized_user_id:
            if message_text.lower() == "إيقاف الحظر":
                blocking_enabled = False
                await event.respond("تم إيقاف الحظر.")
                print("Blocking disabled.")
            elif message_text.lower() == "بدء الحظر":
                blocking_enabled = True
                await event.respond("تم تشغيل الحظر.")
                print("Blocking enabled.")

    # التعامل مع الرسائل في المجموعة
    if event.is_group and event.chat.username == group_username:
        sender = await event.get_sender()
        sender_name = sender.first_name if sender.first_name else "مستخدم"

        # الترحيب بالمستخدمين المميزين
        if sender_id in special_user_ids:
            now = datetime.now()
            if sender_id not in last_welcome_time or now - last_welcome_time[sender_id] > timedelta(hours=24):
                await event.reply(f"وين غايب  نورت يا  {sender_name}!")
                last_welcome_time[sender_id] = now
                print(f"Welcomed special user {sender_name}.")

        if sender_id == authorized_user_id:
            if message_text == "قف":
                auto_responses_enabled = False
                await event.reply("امرك .")
                return

            if message_text == "بدء":
                auto_responses_enabled = True
                await event.reply("تكرم يا قلبي ")
                return

            if message_text.startswith("اضف رد "):
                try:
                    parts = message_text[len("اضف رد "):].strip().split(':')
                    if len(parts) == 2:
                        keyword = parts[0].strip()
                        response = parts[1].strip()
                        if keyword in responses:
                            responses[keyword].append(response)
                        else:
                            responses[keyword] = [response]
                        with open(responses_file, 'w', encoding='utf-8') as file:
                            json.dump(responses, file, ensure_ascii=False, indent=4)
                        await event.reply(f"تم إضافة الرد '{response}' للكلمة '{keyword}'.")
                        print(f"Added response '{response}' for keyword '{keyword}'.")
                    else:
                        await event.reply("الرجاء استخدام الصيغة الصحيحة: اضف رد الكلمة:الرد")
                except Exception as e:
                    await event.reply("حدث خطأ أثناء إضافة الرد.")
                    print(f"Error adding response: {e}")
                return

            if message_text.startswith("أضف مميز "):
                try:
                    new_special_user_id = int(message_text[len("أضف مميز "):].strip())
                    if new_special_user_id not in special_user_ids:
                        special_user_ids.append(new_special_user_id)
                        with open(special_users_file, 'w', encoding='utf-8') as file:
                            json.dump(special_user_ids, file, ensure_ascii=False, indent=4)
                        await event.reply(f"تم إضافة المستخدم المميز بمعرف {new_special_user_id}.")
                        print(f"Added special user with ID {new_special_user_id}.")
                    else:
                        await event.reply("المستخدم المميز موجود بالفعل.")
                except Exception as e:
                    await event.reply("حدث خطأ أثناء إضافة المستخدم المميز.")
                    print(f"Error adding special user: {e}")
                return

            if message_text == "عرض الردود":
                try:
                    response_list = [f"{key}: {', '.join(value)}" for key, value in responses.items()]
                    response_text = "\n".join(response_list)
                    await event.reply(f"الردود الموجودة:\n{response_text}")
                    print("Displayed all responses.")
                except Exception as e:
                    await event.reply("حدث خطأ أثناء عرض الردود.")
                    print(f"Error displaying responses: {e}")
                return

            if message_text == "الأوامر":
                commands = [
                    "قف - إيقاف الردود التلقائية",
                    "بدء - بدء الردود التلقائية",
                    "اضف رد الكلمة:الرد - لإضافة رد جديد",
                    "عرض الردود - لعرض جميع الردود الموجودة",
                    "أضف مميز <معرف المستخدم> - لإضافة مستخدم مميز",
                    "الأوامر - لعرض جميع الأوامر"
                ]
                await event.reply("الأوامر المتاحة:\n" + "\n".join(commands))
                print("Displayed all commands.")
                return

        if auto_responses_enabled:
            message_text = event.message.message.lower()

            # الرد على سؤال "كم الساعة"
            if "الساعة" in message_text:
                response = f"الساعة الآن {datetime.now().strftime('%I:%M')}."
                await event.reply(response)

            # الرد على كلمات محددة
            for keyword, keyword_responses in responses.items():
                if keyword in message_text:
                    response = random.choice(keyword_responses)
                    await event.reply(response)
                    print(f"Replied with: {response}")
                    break

async def main():
    await client.start(phone)
    print("Client Created")
    await send_message_to_group(client, group_username, message, interval)

# تشغيل الدالة لإرسال الرسالة بفاصل زمني
with client:
    client.loop.run_until_complete(main())
