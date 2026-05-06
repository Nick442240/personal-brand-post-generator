from flask import Flask, render_template, request


app = Flask(__name__)


PLATFORM_HINTS = {
    "Telegram": "коротко, живо и с сильным первым абзацем",
    "VK": "с понятной пользой, легким тоном и вовлекающим вопросом",
    "Блог": "структурно, глубже и с акцентом на экспертность",
}

STYLE_SETTINGS = {
    "Экспертный": {
        "title": "{topic}: что важно понять аудитории «{audience}»",
        "opening": (
            "Разберем тему спокойно и по делу. Для аудитории «{audience}» важно не просто узнать "
            "о теме «{topic}», а понять, как применить это в реальной работе."
        ),
        "structure": [
            "Кратко обозначьте проблему и почему она влияет на результат.",
            "Дайте контекст: где чаще всего возникает эта ситуация.",
            "Разберите 2-3 практических принципа без лишней теории.",
            "Добавьте нейтральный пример без персональных данных.",
            "Завершите выводом, который можно применить сразу.",
        ],
        "cta": "Сохраните пост и используйте этот подход в ближайшей публикации.",
    },
    "Дружелюбный": {
        "title": "{topic}: как разобраться без лишнего напряжения",
        "opening": (
            "Давайте простыми словами. Если вы относитесь к аудитории «{audience}», тема «{topic}» "
            "может казаться большой, но ее проще понять через несколько понятных шагов."
        ),
        "structure": [
            "Начните с ситуации, в которой читатель может узнать себя.",
            "Объясните тему простым языком, без сложных терминов.",
            "Покажите, какую маленькую пользу можно получить уже сейчас.",
            "Добавьте теплый пример или бытовую аналогию.",
            "Задайте вопрос, чтобы читателю было легко откликнуться.",
        ],
        "cta": "Напишите в комментариях, какая мысль оказалась самой полезной.",
    },
    "Продающий": {
        "title": "{topic}: как получить больше пользы без хаоса",
        "opening": (
            "У аудитории «{audience}» часто нет времени на долгие объяснения. Поэтому пост про "
            "«{topic}» должен быстро показать проблему, ценность решения и понятный следующий шаг."
        ),
        "structure": [
            "Назовите боль или потерю, которую читатель хочет избежать.",
            "Покажите, какую конкретную пользу дает правильный подход.",
            "Опишите короткий путь от проблемы к решению.",
            "Добавьте аргумент доверия: опыт, наблюдение или мини-кейс без личных данных.",
            "Завершите четким предложением действия.",
        ],
        "cta": "Оставьте заявку или напишите в личные сообщения, если хотите разобрать это под вашу задачу.",
    },
    "Вдохновляющий": {
        "title": "{topic}: маленький шаг, который может многое изменить",
        "opening": (
            "Иногда именно тема «{topic}» помогает аудитории «{audience}» увидеть новую точку роста. "
            "Не обязательно менять все сразу: достаточно начать с одного осознанного действия."
        ),
        "structure": [
            "Начните с эмоционального наблюдения или сильной мысли.",
            "Покажите, почему эта тема может стать точкой изменения.",
            "Поддержите читателя: путь можно проходить постепенно.",
            "Предложите 2-3 простых шага для первого движения вперед.",
            "Закончите мотивирующим выводом и приглашением к действию.",
        ],
        "cta": "Выберите один шаг из поста и попробуйте применить его уже сегодня.",
    },
}


def normalize_text(value):
    cleaned = " ".join(value.strip().split())
    return cleaned


def make_hashtag(text):
    words = [
        "".join(char for char in word.lower() if char.isalnum())
        for word in text.replace("-", " ").split()
    ]
    words = [word for word in words if word]
    return "#" + "".join(words[:3]) if words else "#личныйбренд"


def generate_post(topic, audience, platform, style):
    platform_hint = PLATFORM_HINTS.get(platform, PLATFORM_HINTS["Telegram"])
    style_data = STYLE_SETTINGS.get(style, STYLE_SETTINGS["Экспертный"])

    title = style_data["title"].format(topic=topic, audience=audience)
    intro = (
        f"{style_data['opening'].format(topic=topic, audience=audience)} "
        f"Для площадки {platform} подайте материал {platform_hint}."
    )
    structure = style_data["structure"]
    cta = style_data["cta"]
    hashtags = [
        make_hashtag(topic),
        "#личныйбренд",
        f"#{platform.lower()}посты".replace("блогпосты", "блог"),
    ]
    full_post = "\n\n".join(
        [
            title,
            f"Вступление:\n{intro}",
            "Структура:\n"
            + "\n".join(
                f"{index}. {item}" for index, item in enumerate(structure, start=1)
            ),
            f"Призыв к действию:\n{cta}",
            "Хэштеги:\n" + " ".join(hashtags),
        ]
    )

    return {
        "title": title,
        "intro": intro,
        "structure": structure,
        "cta": cta,
        "hashtags": hashtags,
        "full_post": full_post,
        "meta": {
            "topic": topic,
            "audience": audience,
            "platform": platform,
            "style": style,
        },
    }


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        topic = normalize_text(request.form.get("topic", ""))
        audience = normalize_text(request.form.get("audience", ""))
        platform = request.form.get("platform", "Telegram")
        style = request.form.get("style", "Экспертный")

        errors = []
        if not topic:
            errors.append("Введите тему поста, чтобы сайт мог собрать идею.")
        if not audience:
            errors.append("Введите целевую аудиторию, чтобы текст был точнее.")

        form_data = {
            "topic": topic,
            "audience": audience,
            "platform": platform,
            "style": style,
        }

        if errors:
            return render_template("index.html", errors=errors, form_data=form_data)

        result = generate_post(topic, audience, platform, style)
        return render_template("result.html", result=result)

    return render_template("index.html", errors=[], form_data={})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
