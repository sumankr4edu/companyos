import random
from datetime import datetime, timedelta

from graph.client import graph_client


class NovaTechGenerator:
    """
    Deterministic demo-company graph generator.

    Generates:
    - 1 company
    - 100+ people
    - 20 teams
    - 30 projects
    - 50 systems
    - 100 documents
    - 100 incidents
    - 200 decisions
    - extensive relationships
    """

    def __init__(self, graph_name: str = "novatech"):
        self.graph_name = graph_name
        self.graph = graph_client.get_graph(graph_name)

        random.seed(42)

        self.first_names = [
            "Alice", "Raj", "Maya", "Arjun", "Priya",
            "Rahul", "Neha", "Vikram", "Ananya", "Rohan",
            "Karan", "Sneha", "Aditya", "Pooja", "Amit",
            "Kavya", "Nikhil", "Ishita", "Varun", "Meera",
        ]

        self.last_names = [
            "Chen", "Patel", "Singh", "Sharma", "Kumar",
            "Gupta", "Verma", "Reddy", "Joshi", "Mehta",
            "Iyer", "Nair", "Das", "Kapoor", "Malhotra",
        ]

        self.team_names = [
            "Platform Engineering",
            "Payments Engineering",
            "Checkout Engineering",
            "Infrastructure",
            "Cloud Engineering",
            "Security Engineering",
            "Data Engineering",
            "Machine Learning",
            "Developer Experience",
            "SRE",
            "Mobile Engineering",
            "Web Engineering",
            "Product Engineering",
            "Architecture",
            "Quality Engineering",
            "Observability",
            "Customer Experience",
            "Internal Tools",
            "Release Engineering",
            "Technical Operations",
        ]

        self.service_names = [
            "Checkout Service",
            "Payment Service",
            "Order Service",
            "User Service",
            "Inventory Service",
            "Notification Service",
            "Fraud Detection Service",
            "API Gateway",
            "Authentication Service",
            "Recommendation Service",
            "Search Service",
            "Catalog Service",
            "Pricing Service",
            "Shipping Service",
            "Analytics Service",
            "Reporting Service",
            "Subscription Service",
            "Billing Service",
            "Refund Service",
            "Ledger Service",
            "Wallet Service",
            "Settlement Service",
            "Merchant Service",
            "Partner Service",
            "Webhook Service",
            "Identity Service",
            "Feature Flag Service",
            "Configuration Service",
            "Audit Service",
            "Document Service",
            "Media Service",
            "Experiment Service",
            "Risk Service",
            "Compliance Service",
            "Data Pipeline",
            "Event Service",
            "Message Service",
            "Search Indexer",
            "Recommendation Engine",
            "AI Assistant",
            "Customer Support Service",
            "Incident Service",
            "Deployment Service",
            "Monitoring Service",
            "Metrics Service",
            "Tracing Service",
            "Secrets Service",
            "Access Service",
            "Reporting API",
            "Partner API",
        ]

        self.project_names = [
            "Payment Service Migration",
            "Checkout Reliability",
            "Cloud Modernization",
            "Zero Downtime Deployment",
            "Fraud Platform",
            "Customer Identity",
            "Observability Upgrade",
            "Developer Portal",
            "Data Platform",
            "AI Recommendation Engine",
            "Mobile Checkout",
            "Global Payments",
            "Merchant Platform",
            "Subscription Platform",
            "Order Platform",
            "Search Modernization",
            "API Gateway Migration",
            "Security Hardening",
            "Event Streaming",
            "Analytics Platform",
            "Feature Flag Rollout",
            "Infrastructure as Code",
            "Disaster Recovery",
            "Database Modernization",
            "Service Mesh",
            "Cost Optimization",
            "Performance Engineering",
            "Compliance Automation",
            "Internal Developer Platform",
            "Unified Customer Profile",
        ]

    def _escape(self, value: str) -> str:
        return (
            str(value)
            .replace("\\", "\\\\")
            .replace("'", "\\'")
        )

    def _run(self, query: str):
        return self.graph.query(query)

    def _merge_company(self):
        self._run(
            """
            MERGE (c:Company {name: 'NovaTech'})
            SET c.id = 'COMPANY-NOVATECH',
                c.industry = 'Technology',
                c.description = 'NovaTech technology company demo graph',
                c.source_type = 'seed',
                c.confidence = 1.0
            """
        )

    def _create_teams(self):
        for index, team in enumerate(self.team_names, start=1):
            team_id = f"TEAM-{index:03d}"

            query = f"""
            MERGE (t:Team {{id: '{team_id}'}})
            SET t.name = '{self._escape(team)}',
                t.source_type = 'seed',
                t.confidence = 1.0
            WITH t
            MATCH (c:Company {{name: 'NovaTech'}})
            MERGE (c)-[:HAS_TEAM]->(t)
            """

            self._run(query)

    def _create_people(self, count: int = 120):
        people = []

        for index in range(1, count + 1):
            first = self.first_names[(index - 1) % len(self.first_names)]
            last = self.last_names[(index * 3) % len(self.last_names)]

            name = f"{first} {last}"
            person_id = f"PERSON-{index:03d}"

            if index == 1:
                name = "Alice Chen"
            elif index == 2:
                name = "Raj Patel"
            elif index == 3:
                name = "Maya Singh"

            role = random.choice(
                [
                    "Software Engineer",
                    "Senior Software Engineer",
                    "Staff Software Engineer",
                    "Backend Engineer",
                    "Frontend Engineer",
                    "Platform Engineer",
                    "SRE",
                    "Engineering Manager",
                    "Technical Lead",
                    "Principal Engineer",
                    "Data Engineer",
                    "ML Engineer",
                ]
            )

            people.append(
                {
                    "id": person_id,
                    "name": name,
                    "role": role,
                }
            )

            query = f"""
            MERGE (p:Person {{id: '{person_id}'}})
            SET p.name = '{self._escape(name)}',
                p.role = '{self._escape(role)}',
                p.email = '{person_id.lower()}@novatech.example',
                p.source_type = 'seed',
                p.confidence = 1.0
            """

            self._run(query)

            team_index = ((index - 1) % len(self.team_names)) + 1

            self._run(
                f"""
                MATCH (p:Person {{id: '{person_id}'}})
                MATCH (t:Team {{id: 'TEAM-{team_index:03d}'}})
                MERGE (p)-[:MEMBER_OF]->(t)
                """
            )

        return people

    def _create_projects(self, people):
        for index, project_name in enumerate(
            self.project_names,
            start=1,
        ):
            project_id = f"PROJECT-{index:03d}"

            self._run(
                f"""
                MERGE (p:Project {{id: '{project_id}'}})
                SET p.name = '{self._escape(project_name)}',
                    p.status = '{random.choice(["ACTIVE", "COMPLETED", "PLANNED"])}',
                    p.source_type = 'seed',
                    p.confidence = 1.0
                """
            )

            # Connect project to 3–6 people.
            members = random.sample(
                people,
                random.randint(3, 6),
            )

            for person in members:
                self._run(
                    f"""
                    MATCH (p:Person {{id: '{person["id"]}'}})
                    MATCH (project:Project {{id: '{project_id}'}})
                    MERGE (p)-[:WORKED_ON]->(project)
                    """
                )

    def _create_services(self):
        services = []

        for index, service_name in enumerate(
            self.service_names,
            start=1,
        ):
            service_id = f"SERVICE-{index:03d}"

            status = random.choice(
                [
                    "HEALTHY",
                    "HEALTHY",
                    "HEALTHY",
                    "WARNING",
                    "DEGRADED",
                ]
            )

            services.append(
                {
                    "id": service_id,
                    "name": service_name,
                }
            )

            self._run(
                f"""
                MERGE (s:Service {{id: '{service_id}'}})
                SET s.name = '{self._escape(service_name)}',
                    s.status = '{status}',
                    s.source_type = 'seed',
                    s.confidence = 1.0
                """
            )

        return services

    def _create_service_dependencies(self, services):
        for service in services:
            candidates = [
                s for s in services
                if s["id"] != service["id"]
            ]

            dependencies = random.sample(
                candidates,
                random.randint(1, 4),
            )

            for dependency in dependencies:
                self._run(
                    f"""
                    MATCH (a:Service {{id: '{service["id"]}'}})
                    MATCH (b:Service {{id: '{dependency["id"]}'}})
                    MERGE (a)-[:DEPENDS_ON]->(b)
                    """
                )

    def _create_documents(self, count: int = 100):
        document_types = [
            "Architecture Document",
            "Runbook",
            "Design Document",
            "Technical Specification",
            "Incident Report",
            "Engineering Guide",
            "API Documentation",
            "Operations Guide",
        ]

        for index in range(1, count + 1):
            document_id = f"DOC-{index:03d}"

            title = (
                f"{random.choice(document_types)} "
                f"{index}"
            )

            self._run(
                f"""
                MERGE (d:Document {{id: '{document_id}'}})
                SET d.name = '{self._escape(title)}',
                    d.title = '{self._escape(title)}',
                    d.source_type = 'seed',
                    d.source_url = 'https://docs.novatech.example/{document_id}',
                    d.document_id = '{document_id}',
                    d.author = 'NovaTech Engineering',
                    d.created_at = '{datetime.utcnow().isoformat()}',
                    d.updated_at = '{datetime.utcnow().isoformat()}',
                    d.confidence = 1.0
                """
            )

    def _create_incidents(self, services, people, count: int = 100):
        incident_titles = [
            "Checkout failures increased",
            "Payment timeout spike",
            "API latency increased",
            "Database connection pool exhausted",
            "Deployment rollback required",
            "Elevated 5xx responses",
            "Webhook delivery failures",
            "Authentication failures",
            "Inventory synchronization delay",
            "Fraud service degradation",
        ]

        for index in range(1, count + 1):
            incident_id = f"INCIDENT-{index:03d}"

            title = random.choice(incident_titles)

            severity = random.choice(
                ["SEV-1", "SEV-2", "SEV-3", "SEV-4"]
            )

            status = random.choice(
                ["OPEN", "INVESTIGATING", "RESOLVED"]
            )

            service = random.choice(services)
            person = random.choice(people)

            self._run(
                f"""
                MERGE (i:Incident {{id: '{incident_id}'}})
                SET i.name = '{self._escape(title)} #{index}',
                    i.title = '{self._escape(title)}',
                    i.severity = '{severity}',
                    i.status = '{status}',
                    i.source_type = 'seed',
                    i.created_at = '{datetime.utcnow().isoformat()}',
                    i.updated_at = '{datetime.utcnow().isoformat()}',
                    i.confidence = 1.0
                WITH i
                MATCH (s:Service {{id: '{service["id"]}'}})
                MERGE (i)-[:AFFECTS]->(s)
                WITH i
                MATCH (p:Person {{id: '{person["id"]}'}})
                MERGE (i)-[:INVOLVES]->(p)
                """
            )

    def _create_decisions(self, people, projects, count: int = 200):
        decision_titles = [
            "Move payment processing to dedicated Payment Service",
            "Adopt event-driven architecture",
            "Migrate database infrastructure",
            "Introduce service ownership model",
            "Adopt centralized observability",
            "Move authentication to Identity Service",
            "Introduce feature flags",
            "Adopt zero-downtime deployments",
            "Standardize REST APIs",
            "Introduce distributed tracing",
        ]

        for index in range(1, count + 1):
            decision_id = f"DECISION-{index:03d}"

            title = random.choice(decision_titles)
            maker = random.choice(people)
            project = random.choice(projects)

            self._run(
                f"""
                MERGE (d:Decision {{id: '{decision_id}'}})
                SET d.name = '{self._escape(title)} #{index}',
                    d.title = '{self._escape(title)}',
                    d.status = 'APPROVED',
                    d.source_type = 'seed',
                    d.created_at = '{datetime.utcnow().isoformat()}',
                    d.updated_at = '{datetime.utcnow().isoformat()}',
                    d.confidence = 1.0
                WITH d
                MATCH (p:Person {{id: '{maker["id"]}'}})
                MERGE (d)-[:MADE_BY]->(p)
                WITH d
                MATCH (project:Project {{id: '{project["id"]}'}})
                MERGE (d)-[:IMPLEMENTED_BY]->(project)
                """
            )

    def _create_special_demo_path(self):
        """
        Ensures the hero demo path always exists.
        """

        self._run(
            """
            MATCH (checkout:Service {name: 'Checkout Service'})
            MATCH (payment:Service {name: 'Payment Service'})
            MATCH (incident:Incident)
            WHERE incident.title = 'Checkout failures increased'
            MATCH (migration:Project {name: 'Payment Service Migration'})
            MATCH (decision:Decision)
            WHERE decision.title = 'Move payment processing to dedicated Payment Service'
            MATCH (alice:Person {name: 'Alice Chen'})
            MATCH (maya:Person {name: 'Maya Singh'})

            MERGE (checkout)-[:DEPENDS_ON]->(payment)
            MERGE (incident)-[:AFFECTS]->(checkout)
            MERGE (incident)-[:INVOLVES]->(payment)
            MERGE (alice)-[:WORKED_ON]->(migration)
            MERGE (decision)-[:MADE_BY]->(alice)
            MERGE (decision)-[:IMPLEMENTED_BY]->(migration)
            MERGE (maya)-[:OWNS]->(payment)
            """
        )

    def _create_owner_relationships(self, people, services):
        for service in services:
            owner = random.choice(people)

            self._run(
                f"""
                MATCH (p:Person {{id: '{owner["id"]}'}})
                MATCH (s:Service {{id: '{service["id"]}'}})
                MERGE (p)-[:OWNS]->(s)
                """
            )

        # Explicit hero owner.
        self._run(
            """
            MATCH (maya:Person {name: 'Maya Singh'})
            MATCH (payment:Service {name: 'Payment Service'})
            MERGE (maya)-[:OWNS]->(payment)
            """
        )

    def generate(self):
        print("🚀 Starting NovaTech graph generation...")

        self._merge_company()

        print("👥 Creating teams...")
        self._create_teams()

        print("👤 Creating people...")
        people = self._create_people(120)

        print("📦 Creating projects...")
        self._create_projects(people)

        projects = [
            {
                "id": f"PROJECT-{index:03d}",
                "name": name,
            }
            for index, name in enumerate(
                self.project_names,
                start=1,
            )
        ]

        print("⚙️ Creating services...")
        services = self._create_services()

        print("🔗 Creating service dependencies...")
        self._create_service_dependencies(services)

        print("📚 Creating documents...")
        self._create_documents(100)

        print("🚨 Creating incidents...")
        self._create_incidents(
            services,
            people,
            100,
        )

        print("🧠 Creating decisions...")
        self._create_decisions(
            people,
            projects,
            200,
        )

        print("👑 Creating ownership relationships...")
        self._create_owner_relationships(
            people,
            services,
        )

        print("🎯 Creating hero demo path...")
        self._create_special_demo_path()

        print("✅ NovaTech graph generation complete.")


if __name__ == "__main__":
    NovaTechGenerator().generate()