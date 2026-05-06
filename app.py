from flask import Flask, render_template, request


app = Flask(__name__)


PLATFORM_HINTS = {
    "Telegram": "коротко, живо и с сильным первым абзацем",
    "VK": "с понятной пользой, легким тоном и вовлекающим вопросом",
    "Блог": "структурно, глубже и с акцентом на экспертность",
}

STYLE_SETTINGS = {
    "Экспертный": {
        "opening": "Разберите тему через опыт, факты и практические выводы.",
        "cta": "Сохраните пост и используйте этот подход в ближайшей публикации.",
    },
    "Дружелюбный": {
        "opening": "Покажите тему простым языком, будто объясняете ее хорошему знакомому.",
        "cta": "Напишите в комментариях, какая мысль оказалась самой полезной.",
    },
    "Продающий": {
        "opening": "Сразу покажите проблему, ценность решения и следующий шаг для читателя.",
        "cta": "Оставьте заявку или напишите в личные сообщения, если хотите разобрать это под вашу задачу.",
    },
    "Вдохновляющий": {
        "opening": "Свяжите тему с личным ростом, переменами и маленькими действиями.",
        "cta": "Выберите один шаг из поста и попробуйте применить его уже сегодня.",
    },
}


def normalize_text(value, fallback):
    cleaned = " ".join(value.strip().split())
    return cleaned if cleaned else fallback


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

    title = f"{topic}: как раскрыть тему для аудитории «{audience}»"
    intro = (
        f"Этот пост можно начать с наблюдения: аудитории «{audience}» важно быстро понять, "
        f"почему тема «{topic}» касается их работы, целей или повседневных решений. "
        f"Для площадки {platform} лучше подать материал {platform_hint}."
    )
    structure = [
        f"Зацепка: обозначьте знакомую ситуацию или боль, связанную с темой «{topic}».",
        f"Контекст: объясните, почему это особенно важно для аудитории «{audience}».",
        f"Польза: дайте 2-3 практических вывода, которые читатель сможет применить.",
        f"Пример: добавьте короткий сценарий, кейс или личное наблюдение без персональных данных.",
        "Финал: подведите к простому действию, вопросу или следующему шагу.",
    ]
    cta = style_data["cta"]
    hashtags = [
        make_hashtag(topic),
        "#личныйбренд",
        f"#{platform.lower()}посты".replace("блогпосты", "блог"),
    ]
    full_post = "\n\n".join(
        [
            title,
            f"Вступление:\n{style_data['opening']} {intro}",
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
        "intro": f"{style_data['opening']} {intro}",
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
        topic = normalize_text(request.form.get("topic", ""), "личный бренд")
        audience = normalize_text(request.form.get("audience", ""), "начинающие эксперты")
        platform = request.form.get("platform", "Telegram")
        style = request.form.get("style", "Экспертный")
        result = generate_post(topic, audience, platform, style)
        return render_template("result.html", result=result)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
