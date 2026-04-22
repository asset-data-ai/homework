"""
AI Career Advisor Telegram Bot
================================
Stack : aiogram 3.x  |  LangChain-Groq  |  FSM for state routing
Author: Senior Python Developer
"""

import asyncio
import logging
from typing import Any

from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.exceptions import LangChainException

# ---------------------------------------------------------------------------
# 0. Bootstrap
# ---------------------------------------------------------------------------

load_dotenv()  # reads BOT_TOKEN and GROQ_API_KEY from .env

BOT_TOKEN: str = os.environ["BOT_TOKEN"]
GROQ_API_KEY: str = os.environ["GROQ_API_KEY"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 1. LLM client (shared, stateless – state lives in FSM)
# ---------------------------------------------------------------------------

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama3-70b-8192",   # swap to "llama-3.1-70b-versatile" if needed
    temperature=0.5,
    request_timeout=60,        # seconds before we raise a timeout error
    max_retries=2,
)

# ---------------------------------------------------------------------------
# 2. FSM state groups
#    Two completely separate flows → two StatesGroup classes.
# ---------------------------------------------------------------------------

class Resume(StatesGroup):
    """Flow 1: Resume Builder.
    Single-turn: user sends one message → we reply → clear state.
    """
    waiting_for_input = State()


class Interview(StatesGroup):
    """Flow 2: Mock Interview.
    Multi-turn: we keep chat history in FSM data under key 'history'.
    """
    in_progress = State()


# ---------------------------------------------------------------------------
# 3. System prompts
# ---------------------------------------------------------------------------

RESUME_SYSTEM_PROMPT = """
Ты — строгий, но справедливый Senior HR-директор и карьерный адвайзер,
специализирующийся на IT-рынке Казахстана (Kaspi, Kolesa Group, Halyk Bank, Beeline).

Пользователь пришлёт тебе:
1. Описание вакансии.
2. Свой текущий опыт / навыки.

Твоя задача — создать готовое резюме на русском языке в следующей структуре:
• Контакты (оставь плейсхолдер: Имя, Email, Телефон, LinkedIn/GitHub)
• Саммари (2-3 предложения — кто кандидат и что предлагает)
• Навыки (в виде компактного списка, только реальные навыки кандидата)
• Опыт / Пет-проекты (перепиши под вакансию методом STAR — Ситуация, Задача, Действие, Результат; используй сильные глаголы: разработал, оптимизировал, внедрил, настроил)
• Образование

ЖЁСТКОЕ ПРАВИЛО: Никогда не придумывай несуществующий опыт или навыки.
Если реального опыта мало — делай акцент на пет-проектах, учебных достижениях и готовности быстро обучаться.

В самом конце добавь раздел "💡 Чего не хватает" — 1-2 пункта: что кандидату стоит добавить или изучить для усиления резюме под эту вакансию.

Отвечай ТОЛЬКО на русском языке. Без вводных фраз, сразу резюме.
""".strip()

INTERVIEW_SYSTEM_PROMPT = """
Ты — HR-интервьюер в ведущей IT-компании Казахстана (например, Kaspi.kz или Kolesa Group).
Ты проводишь первичный скрининг Junior-специалиста.

Правила поведения:
1. Задавай по ОДНОМУ вопросу за раз — поведенческому или базовому техническому.
2. После каждого ответа кандидата дай краткую честную обратную связь:
   ✅ Что было хорошо
   ⚠️ Где ответ звучит неубедительно или неполно
3. Затем задай следующий вопрос. Учитывай контекст предыдущих ответов.
4. После 3–4 вопросов подведи итог: прошёл бы кандидат первичный скрининг или нет, и почему.

Тон: профессиональный, прямолинейный, без лишней воды.
Отвечай ТОЛЬКО на русском языке.
""".strip()

INTERVIEW_OPENER = """
Начни интервью: поприветствуй кандидата как HR-интервьюер и сразу задай первый вопрос
(поведенческий или общий «расскажи о себе»). Один вопрос — без списков.
""".strip()

# ---------------------------------------------------------------------------
# 4. Keyboards
# ---------------------------------------------------------------------------

def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 Создать резюме", callback_data="resume"),
                InlineKeyboardButton(text="🎤 Мок-интервью",  callback_data="interview"),
            ]
        ]
    )

def stop_interview_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛑 Завершить интервью", callback_data="stop_interview")]
        ]
    )

# ---------------------------------------------------------------------------
# 5. Helpers
# ---------------------------------------------------------------------------

async def call_llm(messages: list) -> str:
    """Invoke Groq LLM and return the text reply.

    Raises a user-friendly string on timeout or API error instead of crashing.
    """
    try:
        response = await asyncio.to_thread(llm.invoke, messages)
        return response.content
    except LangChainException as exc:
        logger.error("LangChain/Groq error: %s", exc)
        raise
    except TimeoutError as exc:
        logger.error("Groq API timeout: %s", exc)
        raise


def build_lc_history(raw: list[dict]) -> list:
    """Convert FSM-stored history (list of dicts) back to LangChain message objects.

    We serialise to plain dicts in FSM because aiogram's MemoryStorage
    can't pickle LangChain objects directly.
    """
    mapping = {"human": HumanMessage, "ai": AIMessage}
    return [mapping[item["role"]](content=item["content"]) for item in raw]


# ---------------------------------------------------------------------------
# 6. Handlers
# ---------------------------------------------------------------------------

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp  = Dispatcher(storage=MemoryStorage())


# ── /start ──────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Entry point. Clear any lingering state and show the main menu."""
    await state.clear()
    await message.answer(
        "👋 <b>Привет! Я — AI Career Advisor</b>\n\n"
        "Помогу тебе подготовиться к карьере в IT:\n"
        "• 📝 <b>Создать резюме</b> — адаптирую твой опыт под конкретную вакансию\n"
        "• 🎤 <b>Мок-интервью</b> — потренируемся отвечать на вопросы HR\n\n"
        "Выбери, с чего начнём 👇",
        reply_markup=main_menu_keyboard(),
    )


# ── /stop — universal escape hatch ──────────────────────────────────────────

@dp.message(Command("stop"))
async def cmd_stop(message: Message, state: FSMContext) -> None:
    """Let the user exit any active flow at any time."""
    current = await state.get_state()
    if current is None:
        await message.answer("Сейчас нет активного режима. Используй /start.")
        return
    await state.clear()
    await message.answer(
        "✅ Режим завершён. Используй /start, чтобы начать заново.",
        reply_markup=main_menu_keyboard(),
    )


# ── Callback: "stop_interview" inline button ────────────────────────────────

@dp.callback_query(F.data == "stop_interview")
async def cb_stop_interview(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer(
        "🛑 Интервью завершено. Хорошая работа! Используй /start для нового сеанса.",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


# ── Callback: "resume" button ────────────────────────────────────────────────

@dp.callback_query(F.data == "resume")
async def cb_resume(callback: CallbackQuery, state: FSMContext) -> None:
    """Transition → Resume.waiting_for_input."""
    await state.set_state(Resume.waiting_for_input)   # <── FSM state set
    await callback.message.answer(
        "📋 <b>Режим: Создание резюме</b>\n\n"
        "Пришли мне одним сообщением:\n"
        "1️⃣ <b>Текст вакансии</b> (можно скопировать с hh.kz или LinkedIn)\n"
        "2️⃣ <b>Твой опыт / навыки</b> — даже если это учебные проекты\n\n"
        "<i>Пример разделителя: «---» между вакансией и опытом</i>\n\n"
        "Введи /stop чтобы отменить."
    )
    await callback.answer()


# ── Resume: process user input ───────────────────────────────────────────────

@dp.message(Resume.waiting_for_input)   # <── FSM guard: only fires in this state
async def handle_resume_input(message: Message, state: FSMContext) -> None:
    """Send user data to Groq, stream back the tailored resume, clear state."""
    thinking = await message.answer("⏳ Анализирую вакансию и пишу резюме…")

    messages = [
        SystemMessage(content=RESUME_SYSTEM_PROMPT),
        HumanMessage(content=message.text or ""),
    ]

    try:
        resume_text = await call_llm(messages)
    except Exception:
        await thinking.delete()
        await message.answer(
            "❌ Не удалось получить ответ от AI (таймаут или ошибка API). "
            "Попробуй ещё раз через несколько секунд."
        )
        return  # keep state so user can retry without pressing the button again

    await thinking.delete()
    await message.answer(resume_text)

    # Flow complete → clear FSM state
    await state.clear()
    await message.answer(
        "✅ Резюме готово! Что дальше?",
        reply_markup=main_menu_keyboard(),
    )


# ── Callback: "interview" button ─────────────────────────────────────────────

@dp.callback_query(F.data == "interview")
async def cb_interview(callback: CallbackQuery, state: FSMContext) -> None:
    """Initialise interview: set FSM state + empty history, get first question."""
    await state.set_state(Interview.in_progress)      # <── FSM state set

    # Seed history: system prompt lives outside history; we store only turns.
    await state.update_data(history=[])               # <── memory init

    thinking = await callback.message.answer("⏳ Готовлю первый вопрос…")

    # Ask the LLM to produce the opening question
    messages = [
        SystemMessage(content=INTERVIEW_SYSTEM_PROMPT),
        HumanMessage(content=INTERVIEW_OPENER),
    ]

    try:
        first_question = await call_llm(messages)
    except Exception:
        await thinking.delete()
        await callback.message.answer(
            "❌ Ошибка подключения к AI. Попробуй снова через /start."
        )
        await state.clear()
        await callback.answer()
        return

    await thinking.delete()

    # Persist the opener as an AI turn so future calls have context
    await state.update_data(
        history=[{"role": "ai", "content": first_question}]
    )

    await callback.message.answer(
        f"🎤 <b>Мок-интервью началось!</b>\n\n{first_question}",
        reply_markup=stop_interview_keyboard(),
    )
    await callback.answer()


# ── Interview: process candidate answers ─────────────────────────────────────

@dp.message(Interview.in_progress)    # <── FSM guard: only fires in this state
async def handle_interview_answer(message: Message, state: FSMContext) -> None:
    """Evaluate the candidate's answer and ask the next question.

    Memory pattern:
      1. Load serialised history from FSM state.
      2. Convert to LangChain message objects.
      3. Append the new human turn.
      4. Call LLM with [SystemMessage] + full history.
      5. Append AI response to history and save back to FSM.
    """
    data: dict[str, Any] = await state.get_data()
    raw_history: list[dict] = data.get("history", [])

    # Reconstruct LangChain message objects from stored dicts
    lc_history = build_lc_history(raw_history)

    # Append the user's latest answer
    new_human = HumanMessage(content=message.text or "")
    lc_history.append(new_human)

    messages = [SystemMessage(content=INTERVIEW_SYSTEM_PROMPT)] + lc_history

    thinking = await message.answer("⏳ Оцениваю ответ…")

    try:
        ai_reply = await call_llm(messages)
    except Exception:
        await thinking.delete()
        await message.answer(
            "❌ AI недоступен (таймаут). Попробуй повторить ответ или введи /stop."
        )
        return

    await thinking.delete()

    # Persist updated history (serialise back to plain dicts for MemoryStorage)
    raw_history.append({"role": "human", "content": message.text or ""})
    raw_history.append({"role": "ai",    "content": ai_reply})
    await state.update_data(history=raw_history)

    await message.answer(ai_reply, reply_markup=stop_interview_keyboard())


# ── Fallback: message outside any FSM state ──────────────────────────────────

@dp.message()
async def fallback(message: Message) -> None:
    await message.answer(
        "Не понимаю команду. Используй /start чтобы открыть меню.",
        reply_markup=main_menu_keyboard(),
    )


# ---------------------------------------------------------------------------
# 7. Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    logger.info("Starting AI Career Advisor bot…")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())