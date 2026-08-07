from .skills_db import SKILL_KNOWLEDGE_BASE, get_skill_knowledge
from .all_skills import GLOBAL_SKILL_DATABASE, search_global_skills, get_all_skills_summary


def query_skill_bank_data(query_text):
    """
    Search both developer skills and global skills (creative, business, health, trades, etc.)
    and format a rich response context.
    """
    query_lower = query_text.lower()
    matches = search_global_skills(query_lower)

    if not matches:
        # Fallback to dev skills search
        dev_res = get_skill_knowledge(query_text)
        if dev_res and "Available Skills" not in dev_res:
            return dev_res

        # Format a complete overview of all skills across all categories
        all_cats = get_all_skills_summary()
        summary_lines = ["Skill Bank supports learning & advice across ALL domain skills:\n"]
        for cat, titles in all_cats.items():
            summary_lines.append(f"**{cat}**: {', '.join(titles)}")
        return "\n".join(summary_lines)

    output = []
    for skill in matches:
        output.append(f"### 🎯 Skill: {skill['title']} ({skill['category']})")
        output.append(f"**Overview**: {skill['description']}")
        output.append(f"**Learning Roadmap**: {' ➔ '.join(skill['roadmap'])}")
        if 'tools_and_software' in skill:
            output.append(f"**Tools & Software**: {', '.join(skill['tools_and_software'])}")
        if 'career_roles' in skill:
            output.append(f"**Career Roles**: {', '.join(skill['career_roles'])}")
        if 'project_ideas' in skill:
            output.append(f"**Project / Practice Ideas**: {', '.join(skill['project_ideas'])}\n")

    return "\n".join(output)


__all__ = [
    'SKILL_KNOWLEDGE_BASE',
    'GLOBAL_SKILL_DATABASE',
    'get_skill_knowledge',
    'search_global_skills',
    'get_all_skills_summary',
    'query_skill_bank_data'
]
