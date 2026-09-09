"""Management command to seed the database with sample articles
for local testing."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from news.models import Article, Publisher

User = get_user_model()

SAMPLE_JOURNALISTS = [
    {"username": "grace_holloway", "email": "grace@example.com"},
    {"username": "daniel_reyes", "email": "daniel@example.com"},
]

SAMPLE_PUBLISHER = {"name": "Oxford Chronicle"}

SAMPLE_ARTICLES = [
    {
        "title": "City Council Approves New Bike Lane Network",
        "content": (
            "The city council voted 7-2 on Tuesday to approve a new "
            "network of protected bike lanes connecting the downtown core "
            "to three residential districts. Construction is expected to "
            "begin next spring and take roughly eighteen months to complete."
        ),
        "author": "grace_holloway",
        "publisher": "Oxford Chronicle",
    },
    {
        "title": "Local University Opens New Research Lab",
        "content": (
            "Oxford Tech University unveiled its new Applied Robotics Lab "
            "this week, a facility funded jointly by the university and three "
            "private tech firms."
        ),
        "author": "grace_holloway",
        "publisher": "Oxford Chronicle",
    },
    {
        "title": "Weekend Farmers Market Sees Record Turnout",
        "content": (
            "More than four thousand visitors passed through the Saturday "
            "farmers market this weekend, according to organizers, marking "
            "the highest attendance since the market relaunched two years ago."
        ),
        "author": "daniel_reyes",
        "publisher": None,
    },
    {
        "title": "Independent Bookstore Celebrates Twenty Years",
        "content": (
            "Foxglove Books, one of the last independent bookstores in the "
            "city center, marked its twentieth anniversary this month with "
            "a weekend of author readings and discounts."
        ),
        "author": "daniel_reyes",
        "publisher": None,
    },
    {
        "title": "New Bus Route Connects Suburbs to Downtown",
        "content": (
            "Transit authorities launched a new express bus route this week "
            "linking the northern suburbs directly to downtown, cutting the "
            " average commute by roughly twenty minutes."
        ),
        "author": "grace_holloway",
        "publisher": "Oxford Chronicle",
    },
]


class Command(BaseCommand):
    help = (
        "Seed the database with sample journalists, a publisher, "
        "and approved articles."
    )

    def handle(self, *args, **options):
        publisher, _ = Publisher.objects.get_or_create(name=SAMPLE_PUBLISHER["name"])

        journalists = {}
        for data in SAMPLE_JOURNALISTS:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={"email": data["email"], "role": User.Role.JOURNALIST},
            )
            if created:
                user.set_password("sample1234")
                user.save()
            journalists[data["username"]] = user
            publisher.journalists.add(user)

        created_count = 0
        for data in SAMPLE_ARTICLES:
            _, created = Article.objects.get_or_create(
                title=data["title"],
                defaults={
                    "content": data["content"],
                    "author": journalists[data["author"]],
                    "publisher": publisher if data["publisher"] else None,
                    "approved": True,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created_count} new article(s)."))
