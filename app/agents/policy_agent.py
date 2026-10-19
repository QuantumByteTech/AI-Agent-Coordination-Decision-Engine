from sqlalchemy.orm import Session

from app.database.repository import PolicyRepository


class PolicyAgent:
    """
    Specialized enterprise agent responsible for HR policy
    retrieval, policy search, and policy category queries.
    """

    name = "HR Policy Agent"

    description = (
        "Retrieves and searches company HR policies from "
        "the enterprise policy knowledge base."
    )

    @staticmethod
    def _policy_dict(policy) -> dict:
        return {
            column.name: getattr(policy, column.name)
            for column in policy.__table__.columns
        }

    @staticmethod
    def _search_terms(keyword: str) -> list[str]:
        query = " ".join(keyword.lower().strip().split())
        candidates = [query]

        # Translate common employee wording into terms that may actually
        # appear in an HR policy title, category, or body.
        aliases = (
            (("work from home", "work-from-home", "wfh", "remote work",
              "remote working", "work at home", "working remotely"),
             ("work from home", "work-from-home", "wfh", "remote work",
              "remote working", "telecommuting")),
            (("leave balance", "available leave", "leave days"),
             ("leave", "leave policy")),
            (("holiday", "holidays", "day off"),
             ("holiday", "holidays", "leave")),
            (("attendance", "late arrival", "working hours"),
             ("attendance", "working hours")),
        )

        for triggers, terms in aliases:
            if any(trigger in query for trigger in triggers):
                candidates.extend(terms)

        # Full natural-language questions often fail a simple LIKE search.
        # Try meaningful words as a fallback, while skipping common filler.
        stop_words = {
            "how", "do", "i", "can", "could", "would", "should", "the",
            "a", "an", "is", "are", "am", "my", "me", "to", "for", "from",
            "what", "where", "when", "why", "who", "please", "tell", "show",
            "explain", "about", "request", "get", "have", "does", "company",
            "policy", "policies", "hr",
        }
        words = [
            word.strip(".,?!:;()[]{}\"'").lower()
            for word in query.split()
        ]
        candidates.extend(word for word in words if len(word) >= 3 and word not in stop_words)

        # Preserve order and avoid duplicate database calls.
        return list(dict.fromkeys(term for term in candidates if term))[:12]

    def get_all_policies(self, db: Session) -> dict:
        policies = PolicyRepository.get_all(db)
        results = [self._policy_dict(policy) for policy in policies]

        return {
            "success": True,
            "agent": self.name,
            "count": len(results),
            "policies": results,
        }

    def search_policy(self, db: Session, keyword: str) -> dict:
        if not keyword or not keyword.strip():
            return {
                "success": False,
                "agent": self.name,
                "message": "Please provide a policy topic to search.",
                "count": 0,
                "policies": [],
            }

        matches = []
        seen = set()

        for term in self._search_terms(keyword):
            try:
                policies = PolicyRepository.search(db, term)
            except Exception:
                # A bad/unsupported search term should not prevent trying
                # the other natural-language aliases.
                continue

            for policy in policies or []:
                values = self._policy_dict(policy)
                identity = values.get("id")
                if identity is None:
                    identity = tuple(sorted((key, str(value)) for key, value in values.items()))
                if identity not in seen:
                    seen.add(identity)
                    matches.append(values)

        if not matches:
            return {
                "success": True,
                "agent": self.name,
                "count": 0,
                "message": (
                    f"No matching HR policy was found for '{keyword}'. "
                    "The knowledge base may not contain this topic yet."
                ),
                "policies": [],
            }

        return {
            "success": True,
            "agent": self.name,
            "count": len(matches),
            "policies": matches[:10],
        }

    def get_policy_by_category(self, db: Session, category: str) -> dict:
        if not category or not category.strip():
            return {
                "success": False,
                "agent": self.name,
                "message": "Please provide a policy category.",
                "count": 0,
                "policies": [],
            }

        policies = PolicyRepository.search(db, category.strip())
        results = [self._policy_dict(policy) for policy in (policies or [])]

        return {
            "success": True,
            "agent": self.name,
            "category": category,
            "count": len(results),
            "policies": results,
        }


policy_agent = PolicyAgent()
