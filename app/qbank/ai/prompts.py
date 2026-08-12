"""
قوالب الـprompt لتوليد الأسئلة بالـAI.

قاعدة أساسية (رد على متطلب المستخدم الصريح): إذا تم تمرير نصوص مصادر
موثوقة (source_texts)، يُطلب من النموذج التأسيس عليها حصريًا وعدم اختراع
معلومات خارجها. إذا لم تُمرَّر أي مصادر، يُطلب من النموذج الاعتماد على
معرفته العامة الموثوقة بمعايير STCW/IMO فقط في نطاق الموضوع المحدد، مع
تحذير صريح في الـprompt نفسه أن يمتنع عن الإجابة إذا لم يكن واثقًا —
وهذا الفرق (مصادر محددة مقابل معرفة عامة) يُسجَّل في generation_batch
عبر عمود source_document_ids (فارغ = بلا مصادر محددة).

PROMPT_VERSION: يُستخدم في تتبّع كل دفعة توليد (qbank_generation_batches.
prompt_version) — أي تعديل جوهري على القالب يجب أن يرفع هذا الرقم حتى
يمكن تتبّع أي إصدار من الـprompt أنتج أي سؤال.
"""

PROMPT_VERSION = "v1"

_INTERACTION_TYPE_INSTRUCTIONS = {
    "mcq": "MCQ: أربعة خيارات، واحد صحيح فقط.",
    "true_false": "True/False: خياران فقط (True, False).",
    "multiple_response": "Multiple response: أربعة إلى ستة خيارات، أكثر من إجابة صحيحة (2-3).",
    "matching": (
        "Matching: أربعة إلى ستة أزواج. أعد كل زوج كخيار بحقلين: "
        '"text" (العنصر الأيسر) و"match_text" (تطابقه الصحيح على اليمين).'
    ),
    "ordering": (
        "Ordering: أربعة إلى ستة عناصر بترتيب صحيح واحد. أعد كل عنصر كخيار "
        'بحقل "text" وحقل "order_position" (رقم صحيح يبدأ من 1).'
    ),
}

_CONTENT_TYPE_INSTRUCTIONS = {
    "text": "سؤال نصي بحت، بدون أي إشارة لصورة أو صوت.",
    "image": (
        'سؤال يعتمد على صورة. لا تُنشئ الصورة نفسها — فقط اكتب في حقل '
        '"required_image_description" وصفًا دقيقًا لما يجب أن تُظهره الصورة '
        "(سيُرفق لاحقًا بواسطة مؤلف بشري)."
    ),
    "audio": (
        'سؤال يعتمد على مقطع صوتي (مثال: نداء استغاثة، محادثة راديو). اكتب '
        'في حقل "required_audio_transcript" النص الكامل الذي يجب أن يُسجَّل صوتيًا.'
    ),
    "text_image": "نص + صورة معًا — استخدم نفس تعليمات content_type=image بالإضافة لنص سياقي.",
    "text_audio": "نص + صوت معًا — استخدم نفس تعليمات content_type=audio بالإضافة لنص سياقي.",
    "image_audio": "صورة + صوت معًا — استخدم تعليمات كليهما.",
}


def build_generation_prompt(
    *,
    course_title: str,
    learning_objective: str,
    competency_title: str | None,
    difficulty: str,
    interaction_type: str,
    content_type: str,
    is_scenario_based: bool,
    count: int,
    source_texts: list[str],
    existing_stems: list[str],
) -> str:
    """يبني نص الـprompt الكامل. لا يستدعي أي AI هنا — دالة نقية بدون آثار
    جانبية، سهلة الاختبار بمعزل عن الشبكة."""

    grounding_block = ""
    if source_texts:
        joined = "\n---\n".join(source_texts)
        grounding_block = (
            "مصادر موثوقة يجب التأسيس عليها حصريًا (لا تخترع أي معلومة خارج هذا النص):\n"
            f"{joined}\n\n"
            "كل سؤال يجب أن يكون قابلاً للاستنتاج مباشرة من النص أعلاه فقط."
        )
    else:
        grounding_block = (
            "لا توجد مصادر محددة مرفقة لهذه الدفعة. استخدمك معرفتك الموثوقة "
            "بمعايير STCW/IMO الخاصة بالموضوع فقط. إذا لم تكن واثقً من دقة "
            "معلومة معينة، لا تُدرجها — الدقة أهم من العدد."
        )

    avoid_block = ""
    if existing_stems:
        joined = "\n".join(f"- {s}" for s in existing_stems[:30])
        avoid_block = (
            "\n\nأسئلة موجودة بالفعل لنفس الهدف التعليمي — أنشئ صياغات/سيناريوهات "
            f"مختلفة جوهريًا عنها، وليس مجرد إعادة صياغة سطحية:\n{joined}"
        )

    scenario_line = (
        "كل سؤال يجب أن يبدأ بسيناريو واقعي قصير (2-4 جمل) قبل السؤال الفعلي."
        if is_scenario_based
        else "أسئلة مباشرة بدون سيناريو تمهيدي."
    )

    return f"""أنت خبير تأليف أسئلة تقييم بحري معتمد وفق معايير STCW.

الكورس: {course_title}
الكفاءة المستهدفة: {competency_title or "غير محددة"}
الهدف التعليمي: {learning_objective}
مستوى الصعوبة: {difficulty}
نوع السؤال: {_INTERACTION_TYPE_INSTRUCTIONS.get(interaction_type, interaction_type)}
نوع المحتوى: {_CONTENT_TYPE_INSTRUCTIONS.get(content_type, content_type)}
{scenario_line}

{grounding_block}
{avoid_block}

أنشئ {count} سؤالًا مختلفًا جوهريًا عن بعضه (ليس مجرد تبديل كلمات) لنفس
الهدف التعليمي. أعد النتيجة كـJSON صِرف (بدون أي نص قبله أو بعده) على هذا الشكل بالضبط:

{{
  "questions": [
    {{
      "stem_text": "نص السؤال",
      "scenario_text": "نص السيناريو أو null",
      "options": [
        {{"text": "...", "is_correct": true, "match_text": null, "order_position": null}}
      ],
      "explanation": "شرح مختصر للإجابة الصحيحة",
      "source_reference": "إشارة قصيرة للمصدر (بند STCW أو اسم الدليل)",
      "required_image_description": null,
      "required_audio_transcript": null
    }}
  ]
}}"""
