from pathlib import Path


POLICY_FILE = Path(__file__).resolve().parent.parent / "hr_policies.txt"


def get_hr_policies():
    """Load all HR policy information."""

    if not POLICY_FILE.exists():
        raise FileNotFoundError("hr_policies.txt not found.")

    return POLICY_FILE.read_text(encoding="utf-8")


def get_policy_section(section_name):
    """Retrieve a specific HR policy section."""

    policies = get_hr_policies()

    start_marker = f"{section_name}:"
    start = policies.find(start_marker)

    if start == -1:
        return "Requested policy section was not found."

    remaining_text = policies[start + len(start_marker):]

    next_section = remaining_text.find("\n\n")

    if next_section != -1:
        return remaining_text[:next_section].strip()

    return remaining_text.strip()


def search_hr_policy(query: str) -> str:
    """Search HR policies using keywords from the employee question."""

    policies = get_hr_policies()

    stop_words = {
    "what", "are", "the", "is", "a", "an", "of",
    "for", "to", "how", "can", "do", "does", "my",
    "company", "rules", "policy"
    }

    query_words = [
    word.strip("?,.!").lower()
    for word in query.split()
    if word.strip("?,.!").lower() not in stop_words
    ]

    sections = policies.split("\n\n")

    matches = []

    for section in sections:
        section_lower = section.lower()

        score = sum(
            1 for word in query_words
            if len(word) > 2 and word in section_lower
        )

        if score > 0:
            matches.append((score, section))

    matches.sort(reverse=True, key=lambda x: x[0])

    if not matches:
        return "No matching HR policy information was found."

    # Return the most relevant sections
    return "\n\n".join(section for score, section in matches[:2])