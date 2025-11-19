#!/usr/bin/env python3
"""
Graph Traversals Example

This example demonstrates various graph traversal patterns using
Ontologia's graph capabilities with KùzuDB backend.
"""

import os

from ontologia_sdk.client import OntologyClient

# Configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", "8000")
BASE_URL = f"http://{API_HOST}:{API_PORT}"


class GraphTraversalExamples:
    """Examples of graph traversals using Ontologia."""

    def __init__(self, base_url: str):
        self.client = OntologyClient(base_url)

    def setup_sample_data(self):
        """Create sample graph data for demonstrations."""
        print("🔧 Setting up sample graph data...")

        # Create object types
        employee_type = {
            "displayName": "Employee",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "required": True},
                "name": {"dataType": "string", "required": False},
                "department": {"dataType": "string", "required": False},
                "level": {"dataType": "integer", "required": False},
            },
            "implements": [],
        }

        project_type = {
            "displayName": "Project",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "required": True},
                "name": {"dataType": "string", "required": False},
                "status": {"dataType": "string", "required": False},
                "priority": {"dataType": "integer", "required": False},
            },
            "implements": [],
        }

        skill_type = {
            "displayName": "Skill",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "required": True},
                "name": {"dataType": "string", "required": False},
                "category": {"dataType": "string", "required": False},
            },
            "implements": [],
        }

        # Create link types
        works_on_type = {
            "displayName": "Works On",
            "fromObjectType": "employee",
            "toObjectType": "project",
            "cardinality": "MANY_TO_MANY",
            "properties": {
                "role": {"dataType": "string", "required": False},
                "since": {"dataType": "date", "required": False},
            },
        }

        has_skill_type = {
            "displayName": "Has Skill",
            "fromObjectType": "employee",
            "toObjectType": "skill",
            "cardinality": "MANY_TO_MANY",
            "properties": {"proficiency": {"dataType": "integer", "required": False}},
        }

        requires_skill_type = {
            "displayName": "Requires Skill",
            "fromObjectType": "project",
            "toObjectType": "skill",
            "cardinality": "MANY_TO_MANY",
            "properties": {"required_level": {"dataType": "integer", "required": False}},
        }

        # Create object types
        self.client.create_object_type("employee", employee_type)
        self.client.create_object_type("project", project_type)
        self.client.create_object_type("skill", skill_type)

        # Create link types
        self.client.create_link_type("works_on", works_on_type)
        self.client.create_link_type("has_skill", has_skill_type)
        self.client.create_link_type("requires_skill", requires_skill_type)

        # Create sample employees
        employees = [
            {"id": "emp1", "name": "Alice", "department": "Engineering", "level": 5},
            {"id": "emp2", "name": "Bob", "department": "Engineering", "level": 4},
            {"id": "emp3", "name": "Carol", "department": "Product", "level": 6},
            {"id": "emp4", "name": "David", "department": "Product", "level": 3},
            {"id": "emp5", "name": "Eve", "department": "Design", "level": 5},
        ]

        for emp in employees:
            self.client.create_object("employee", emp["id"], {"properties": emp})

        # Create sample projects
        projects = [
            {"id": "proj1", "name": "Mobile App", "status": "active", "priority": 1},
            {"id": "proj2", "name": "Website Redesign", "status": "planning", "priority": 2},
            {"id": "proj3", "name": "Data Platform", "status": "active", "priority": 1},
        ]

        for proj in projects:
            self.client.create_object("project", proj["id"], {"properties": proj})

        # Create sample skills
        skills = [
            {"id": "skill1", "name": "Python", "category": "Programming"},
            {"id": "skill2", "name": "JavaScript", "category": "Programming"},
            {"id": "skill3", "name": "UI Design", "category": "Design"},
            {"id": "skill4", "name": "Data Analysis", "category": "Analytics"},
        ]

        for skill in skills:
            self.client.create_object("skill", skill["id"], {"properties": skill})

        # Create relationships
        # Employees work on projects
        self.client.create_link(
            "works_on", "emp1", "proj1", {"properties": {"role": "Lead", "since": "2023-01-01"}}
        )
        self.client.create_link(
            "works_on",
            "emp2",
            "proj1",
            {"properties": {"role": "Developer", "since": "2023-02-01"}},
        )
        self.client.create_link(
            "works_on", "emp3", "proj2", {"properties": {"role": "Manager", "since": "2023-01-15"}}
        )
        self.client.create_link(
            "works_on", "emp4", "proj2", {"properties": {"role": "Designer", "since": "2023-03-01"}}
        )
        self.client.create_link(
            "works_on",
            "emp5",
            "proj2",
            {"properties": {"role": "Lead Designer", "since": "2023-01-20"}},
        )
        self.client.create_link(
            "works_on",
            "emp1",
            "proj3",
            {"properties": {"role": "Architect", "since": "2023-04-01"}},
        )

        # Employees have skills
        self.client.create_link("has_skill", "emp1", "skill1", {"properties": {"proficiency": 5}})
        self.client.create_link("has_skill", "emp1", "skill4", {"properties": {"proficiency": 4}})
        self.client.create_link("has_skill", "emp2", "skill1", {"properties": {"proficiency": 4}})
        self.client.create_link("has_skill", "emp2", "skill2", {"properties": {"proficiency": 3}})
        self.client.create_link("has_skill", "emp3", "skill4", {"properties": {"proficiency": 5}})
        self.client.create_link("has_skill", "emp4", "skill3", {"properties": {"proficiency": 4}})
        self.client.create_link("has_skill", "emp5", "skill3", {"properties": {"proficiency": 5}})

        # Projects require skills
        self.client.create_link(
            "requires_skill", "proj1", "skill1", {"properties": {"required_level": 3}}
        )
        self.client.create_link(
            "requires_skill", "proj1", "skill2", {"properties": {"required_level": 2}}
        )
        self.client.create_link(
            "requires_skill", "proj2", "skill3", {"properties": {"required_level": 4}}
        )
        self.client.create_link(
            "requires_skill", "proj3", "skill1", {"properties": {"required_level": 4}}
        )
        self.client.create_link(
            "requires_skill", "proj3", "skill4", {"properties": {"required_level": 3}}
        )

        print("✅ Sample data created successfully!")

    def basic_traversal(self):
        """Demonstrate basic graph traversals."""
        print("\n🔍 Basic Graph Traversals")
        print("=" * 40)

        # 1. Find all projects an employee works on
        print("\n1. Employee → Projects")
        alice_projects = self.client.traverse("employee", "emp1", "works_on")
        print(f"Alice works on {len(alice_projects.data)} projects:")
        for proj in alice_projects.data:
            print(f"   - {proj['properties']['name']} ({proj['properties']['status']})")

        # 2. Find all employees on a project
        print("\n2. Project ← Employees")
        mobile_devs = self.client.traverse("project", "proj1", "works_on", direction="reverse")
        print(f"Mobile App has {len(mobile_devs.data)} developers:")
        for emp in mobile_devs.data:
            print(f"   - {emp['properties']['name']} ({emp['properties']['department']})")

        # 3. Find skills of an employee
        print("\n3. Employee → Skills")
        alice_skills = self.client.traverse("employee", "emp1", "has_skill")
        print(f"Alice has {len(alice_skills.data)} skills:")
        for skill in alice_skills.data:
            link = self.client.get_link("has_skill", "emp1", skill["pkValue"])
            proficiency = link.get("linkProperties", {}).get("proficiency", 0)
            print(f"   - {skill['properties']['name']} (Proficiency: {proficiency})")

        # 4. Find employees with a specific skill
        print("\n4. Skill ← Employees")
        python_devs = self.client.traverse("skill", "skill1", "has_skill", direction="reverse")
        print("Python developers:")
        for emp in python_devs.data:
            link = self.client.get_link("has_skill", emp["pkValue"], "skill1")
            proficiency = link.get("linkProperties", {}).get("proficiency", 0)
            print(f"   - {emp['properties']['name']} (Proficiency: {proficiency})")

    def multi_hop_traversal(self):
        """Demonstrate multi-hop traversals."""
        print("\n🔗 Multi-hop Traversals")
        print("=" * 40)

        # 1. Employee → Project → Required Skills
        print("\n1. Employee → Projects → Required Skills")
        alice_projects = self.client.traverse("employee", "emp1", "works_on")

        for proj in alice_projects.data:
            proj_name = proj["properties"]["name"]
            required_skills = self.client.traverse("project", proj["pkValue"], "requires_skill")

            print(f"\n{proj_name} requires:")
            for skill in required_skills.data:
                link = self.client.get_link("requires_skill", proj["pkValue"], skill["pkValue"])
                level = link.get("linkProperties", {}).get("required_level", 0)
                print(f"   - {skill['properties']['name']} (Level: {level})")

        # 2. Find colleagues through projects
        print("\n2. Finding Colleagues Through Projects")
        bob_projects = self.client.traverse("employee", "emp2", "works_on")
        colleagues = set()

        for proj in bob_projects.data:
            proj_devs = self.client.traverse(
                "project", proj["pkValue"], "works_on", direction="reverse"
            )
            for dev in proj_devs.data:
                if dev["pkValue"] != "emp2":  # Exclude Bob himself
                    colleagues.add(dev["properties"]["name"])

        print(f"Bob's colleagues: {', '.join(colleagues)}")

        # 3. Skill → Projects → Employees (who can help)
        print("\n3. Skill → Projects → Employees")
        python_projects = self.client.traverse(
            "skill", "skill1", "requires_skill", direction="reverse"
        )

        print("Projects needing Python:")
        for proj in python_projects.data:
            proj_name = proj["properties"]["name"]
            proj_devs = self.client.traverse(
                "project", proj["pkValue"], "works_on", direction="reverse"
            )
            dev_names = [dev["properties"]["name"] for dev in proj_devs.data]
            print(f"   - {proj_name}: {', '.join(dev_names)}")

    def complex_queries(self):
        """Demonstrate complex graph queries."""
        print("\n🧮 Complex Graph Queries")
        print("=" * 40)

        # 1. Find experts for a project
        print("\n1. Finding Experts for Projects")
        projects = self.client.search_objects("project")

        for proj in projects.data[:2]:  # Limit to first 2 projects
            proj_name = proj["properties"]["name"]
            proj_id = proj["pkValue"]

            # Get required skills for this project
            required_skills = self.client.traverse("project", proj_id, "requires_skill")

            print(f"\n{proj_name} needs experts for:")

            for skill in required_skills.data:
                skill_name = skill["properties"]["name"]
                required_level = (
                    self.client.get_link("requires_skill", proj_id, skill["pkValue"])
                    .get("linkProperties", {})
                    .get("required_level", 0)
                )

                # Find employees with this skill at required level or higher
                skilled_employees = self.client.traverse(
                    "skill", skill["pkValue"], "has_skill", direction="reverse"
                )

                experts = []
                for emp in skilled_employees.data:
                    emp_skill_link = self.client.get_link(
                        "has_skill", emp["pkValue"], skill["pkValue"]
                    )
                    proficiency = emp_skill_link.get("linkProperties", {}).get("proficiency", 0)

                    if proficiency >= required_level:
                        experts.append(f"{emp['properties']['name']} (Level: {proficiency})")

                print(
                    f"   - {skill_name} (Required: {required_level}): {', '.join(experts) if experts else 'No experts found'}"
                )

        # 2. Find skill gaps in teams
        print("\n2. Finding Skill Gaps in Teams")
        active_projects = self.client.search_objects(
            "project", where=[{"property": "status", "op": "eq", "value": "active"}]
        )

        for proj in active_projects.data:
            proj_name = proj["properties"]["name"]
            proj_id = proj["pkValue"]

            # Get team members
            team_members = self.client.traverse("project", proj_id, "works_on", direction="reverse")

            # Get all skills the team has
            team_skills = set()
            for member in team_members.data:
                member_skills = self.client.traverse("employee", member["pkValue"], "has_skill")
                for skill in member_skills.data:
                    team_skills.add(skill["properties"]["name"])

            # Get required skills
            required_skills = self.client.traverse("project", proj_id, "requires_skill")
            required_skill_names = {skill["properties"]["name"] for skill in required_skills.data}

            # Find gaps
            skill_gaps = required_skill_names - team_skills

            print(f"\n{proj_name}:")
            print(f"   Team skills: {', '.join(team_skills) if team_skills else 'None'}")
            print(
                f"   Required: {', '.join(required_skill_names) if required_skill_names else 'None'}"
            )
            print(f"   Skill gaps: {', '.join(skill_gaps) if skill_gaps else 'None! 🎉'}")

    def graph_analytics(self):
        """Demonstrate graph analytics."""
        print("\n📊 Graph Analytics")
        print("=" * 40)

        # 1. Department collaboration network
        print("\n1. Department Collaboration Analysis")

        # Get all employees and their projects
        all_employees = self.client.search_objects("employee")
        dept_collaboration = {}

        for emp in all_employees.data:
            emp_dept = emp["properties"]["department"]
            emp_id = emp["pkValue"]

            # Get projects this employee works on
            emp_projects = self.client.traverse("employee", emp_id, "works_on")

            for proj in emp_projects.data:
                proj_id = proj["pkValue"]

                # Get colleagues on the same project
                colleagues = self.client.traverse(
                    "project", proj_id, "works_on", direction="reverse"
                )

                for colleague in colleagues.data:
                    if colleague["pkValue"] != emp_id:  # Exclude self
                        colleague_dept = colleague["properties"]["department"]

                        if colleague_dept != emp_dept:  # Cross-department collaboration
                            key = tuple(sorted([emp_dept, colleague_dept]))
                            dept_collaboration[key] = dept_collaboration.get(key, 0) + 1

        print("Cross-department collaborations:")
        for (dept1, dept2), count in sorted(
            dept_collaboration.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"   {dept1} ↔ {dept2}: {count} shared projects")

        # 2. Skill popularity analysis
        print("\n2. Skill Popularity Analysis")

        all_skills = self.client.search_objects("skill")
        skill_stats = []

        for skill in all_skills.data:
            skill_name = skill["properties"]["name"]
            skill_id = skill["pkValue"]

            # Count employees with this skill
            skilled_employees = self.client.traverse(
                "skill", skill_id, "has_skill", direction="reverse"
            )

            # Count projects requiring this skill
            requiring_projects = self.client.traverse(
                "skill", skill_id, "requires_skill", direction="reverse"
            )

            # Calculate average proficiency
            total_proficiency = 0
            for emp in skilled_employees.data:
                link = self.client.get_link("has_skill", emp["pkValue"], skill_id)
                total_proficiency += link.get("linkProperties", {}).get("proficiency", 0)

            avg_proficiency = (
                total_proficiency / len(skilled_employees.data) if skilled_employees.data else 0
            )

            skill_stats.append(
                {
                    "name": skill_name,
                    "employees": len(skilled_employees.data),
                    "projects": len(requiring_projects.data),
                    "avg_proficiency": round(avg_proficiency, 1),
                }
            )

        # Sort by employee count
        skill_stats.sort(key=lambda x: x["employees"], reverse=True)

        print("Skill popularity (by number of employees):")
        for stat in skill_stats:
            print(
                f"   {stat['name']}: {stat['employees']} employees, {stat['projects']} projects, avg proficiency: {stat['avg_proficiency']}"
            )

        # 3. Project complexity analysis
        print("\n3. Project Complexity Analysis")

        all_projects = self.client.search_objects("project")
        project_complexity = []

        for proj in all_projects.data:
            proj_name = proj["properties"]["name"]
            proj_id = proj["pkValue"]

            # Count team members
            team_size = len(
                self.client.traverse("project", proj_id, "works_on", direction="reverse").data
            )

            # Count required skills
            skill_count = len(self.client.traverse("project", proj_id, "requires_skill").data)

            # Calculate complexity score
            complexity_score = team_size * skill_count

            project_complexity.append(
                {
                    "name": proj_name,
                    "team_size": team_size,
                    "skills": skill_count,
                    "complexity": complexity_score,
                }
            )

        # Sort by complexity
        project_complexity.sort(key=lambda x: x["complexity"], reverse=True)

        print("Projects by complexity:")
        for proj in project_complexity:
            print(
                f"   {proj['name']}: Team={proj['team_size']}, Skills={proj['skills']}, Complexity={proj['complexity']}"
            )


def main():
    """Run all graph traversal examples."""
    print("🚀 Ontologia Graph Traversal Examples")
    print("=" * 50)

    try:
        examples = GraphTraversalExamples(BASE_URL)

        # Setup sample data
        examples.setup_sample_data()

        # Run examples
        examples.basic_traversal()
        examples.multi_hop_traversal()
        examples.complex_queries()
        examples.graph_analytics()

        print("\n🎉 All graph traversal examples completed!")
        print("\n💡 Key takeaways:")
        print("   - Graph traversals enable complex relationship queries")
        print("   - Multi-hop traversals reveal indirect connections")
        print("   - Graph analytics provide insights into network structure")
        print("   - KùzuDB enables high-performance graph operations")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
