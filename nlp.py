def detect_priority(text):
    text = text.lower()

    high_keywords = [
        "rusak parah",
        "darurat",
        "bahaya",
        "kebakaran",
        "mati total",
        "keamanan"
    ]

    medium_keywords = [
        "rusak",
        "lambat",
        "gangguan",
        "error",
        "bermasalah"
    ]

    for word in high_keywords:
        if word in text:
            return "Tinggi"

    for word in medium_keywords:
        if word in text:
            return "Sedang"

    return "Rendah"