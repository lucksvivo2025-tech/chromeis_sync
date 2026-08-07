class RepairPlan:

    @staticmethod
    def create():

        return {
            "actions": [],
        }

    @staticmethod
    def add(
        plan,
        action,
        doctype,
        document,
        field,
        old,
        new,
    ):

        plan["actions"].append({

            "action": action,

            "doctype": doctype,

            "document": document,

            "field": field,

            "old": old,

            "new": new,
        })

    @staticmethod
    def count(plan):

        return len(
            plan["actions"]
        )

    @staticmethod
    def empty(plan):

        return (
            RepairPlan.count(plan)
            == 0
        )

    @staticmethod
    def summary(plan):

        return {

            "actions": RepairPlan.count(
                plan
            ),

            "empty": RepairPlan.empty(
                plan
            ),

            "plan": plan["actions"],
        }
