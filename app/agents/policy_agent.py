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

    def get_all_policies(self, db: Session) -> dict:
        policies = PolicyRepository.get_all(db)

        results = []

        for policy in policies:
            results.append({
                column.name: getattr(policy, column.name)
                for column in policy.__table__.columns
            })

        return {
            "success": True,
            "agent": self.name,
            "count": len(results),
            "policies": results
        }

    def search_policy(
        self,
        db: Session,
        keyword: str
    ) -> dict:

        if not keyword or not keyword.strip():
            return {
                "success": False,
                "agent": self.name,
                "message": "Please provide a policy topic to search."
            }

        policies = PolicyRepository.search(
            db,
            keyword.strip()
        )

        results = []

        for policy in policies:
            results.append({
                column.name: getattr(policy, column.name)
                for column in policy.__table__.columns
            })

        if not results:
            return {
                "success": True,
                "agent": self.name,
                "count": 0,
                "message": (
                    f"No HR policy was found for "
                    f"'{keyword}'."
                ),
                "policies": []
            }

        return {
            "success": True,
            "agent": self.name,
            "count": len(results),
            "policies": results
        }

    def get_policy_by_category(
        self,
        db: Session,
        category: str
    ) -> dict:

        if not category or not category.strip():
            return {
                "success": False,
                "agent": self.name,
                "message": "Please provide a policy category."
            }

        policies = PolicyRepository.search(
            db,
            category.strip()
        )

        results = []

        for policy in policies:
            results.append({
                column.name: getattr(policy, column.name)
                for column in policy.__table__.columns
            })

        return {
            "success": True,
            "agent": self.name,
            "category": category,
            "count": len(results),
            "policies": results
        }


policy_agent = PolicyAgent()