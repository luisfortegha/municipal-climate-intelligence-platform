def format_metric(value, suffix=""):

    if value is None:
        return "--"

    if value == "":
        return "--"

    try:
        value = float(value)

        if abs(value) >= 100:
            return f"{value:.1f}{suffix}"

        elif abs(value) >= 1:
            return f"{value:.1f}{suffix}"

        else:
            return f"{value:.3f}{suffix}"

    except (TypeError, ValueError):

        return f"{value}{suffix}"