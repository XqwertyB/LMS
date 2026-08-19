def parse_test_text(raw_text):
    """
    Универсальный парсер тестов:
    - raw_text может быть строкой (вопросы через ++++)
    - или списком строк (каждый элемент — вопрос)
    """

    # Нормализация формата
    if isinstance(raw_text, str):
        raw_text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
        questions_raw = [q.strip() for q in raw_text.split("++++") if q.strip()]
    elif isinstance(raw_text, list):
        questions_raw = [
            q.replace("\r\n", "\n").replace("\r", "\n").strip()
            for q in raw_text if q.strip()
        ]
    else:
        raise ValueError("text noto'g'ri formatda (str yoki list bo'lishi kerak)")

    results = []
    order = 1

    for block in questions_raw:
        parts = [p.strip() for p in block.split("====") if p.strip()]

        if len(parts) < 2:
            continue

        question_text = parts[0]
        options_parts = parts[1:]

        options = []
        correct_count = 0

        for opt in options_parts:
            is_correct = opt.startswith("#")
            if is_correct:
                correct_count += 1
            option_text = opt[1:].strip() if is_correct else opt.strip()
            options.append({
                "option_text": option_text,
                "is_correct": is_correct,
            })

        # Валидации
        if correct_count == 0 or len(options) < 2:
            continue

        question_type = "multiple_choice" if correct_count > 1 else "single_choice"

        results.append({
            "question_text": question_text,
            "question_type": question_type,
            "order": order,
            "points": 1,
            "options": options,
        })
        order += 1

    return results
