from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from portfolio.models import WorkingIdentity, IdentityFeed


class Command(BaseCommand):
    help = 'Populate WorkingIdentity and IdentityFeed models with initial data'

    def handle(self, *args, **options):
        # Create WorkingIdentities
        pharmacy, _ = WorkingIdentity.objects.get_or_create(
            identity='pharmacy',
            defaults={
                'description': 'Foundation identity',
                'experiment_plan': 'Aim: Validate clinical pharmacy skills while exploring alternatives.\n\nHypothesis: 6 years of pharmacy + data analysis provide foundation for other identities.\n\nMethods: Transition to locum model. Build pharmacy informatics portfolio demonstrating technical capabilities for healthcare technology roles.'
            }
        )

        law, _ = WorkingIdentity.objects.get_or_create(
            identity='law',
            defaults={
                'description': 'Testing through observation',
                'experiment_plan': 'Aim: Test whether legal work resonates beyond academic interest.\n\nHypothesis: GDL completion + court observations will reveal if law aligns with temperament.\n\nMethods: Monthly court observations. Considering bar professional course. Document patterns and reflections.'
            }
        )

        cybersecurity, _ = WorkingIdentity.objects.get_or_create(
            identity='cybersecurity',
            defaults={
                'description': 'Active testing in progress',
                'experiment_plan': 'Aim: Build detection and incident response capabilities through hands-on SOC lab.\n\nHypothesis: Pattern recognition from pharmacy (clinical data analysis) transfers to security detection rules.\n\nMethods: Home SOC lab (ELK + Cowrie honeypot). Document detection rules and attack patterns. CompTIA Network+ by end 2026. Open source contributions in security tools.'
            }
        )

        actuary, _ = WorkingIdentity.objects.get_or_create(
            identity='actuary',
            defaults={
                'description': 'Study phase',
                'experiment_plan': 'Aim: Test whether quantitative risk modelling aligns with strengths.\n\nHypothesis: Financial modeling experience + actuarial training reveal aptitude and interest.\n\nMethods: CS1 exam April 2026. Mini project: pharmacy data analysis using actuarial frameworks. Target GAD Graduate Trainee Sept 2027.'
            }
        )

        self.stdout.write(self.style.SUCCESS('Created WorkingIdentities'))

        # Create IdentityFeed entries for Pharmacy
        IdentityFeed.objects.get_or_create(
            working_identity=pharmacy,
            date=timezone.make_aware(datetime(2025, 11, 15)),
            defaults={
                'status': 'Transitioning to locum pharmacy model post-Boots. Building resilience for flexible working and portfolio development.',
                'next_action': 'Register with locum agencies. Establish locum schedule for January 2026 onwards.',
                'notes': 'Blog post: Why I chose locum pharmacy and what flexibility enables.'
            }
        )

        IdentityFeed.objects.get_or_create(
            working_identity=pharmacy,
            date=timezone.make_aware(datetime(2025, 12, 1)),
            defaults={
                'status': 'Pharmacy informatics portfolio development. Demonstrating technical capabilities: data extraction, analysis, dashboard design from Boots systems.',
                'next_action': 'Complete first informatics project documenting workflow and insights.',
                'notes': 'Blog post: From clinical pharmacist to healthcare informatics—the bridge.'
            }
        )

        # Create IdentityFeed entries for Law
        IdentityFeed.objects.get_or_create(
            working_identity=law,
            date=timezone.make_aware(datetime(2023, 11, 30)),
            defaults={
                'status': 'Graduate Diploma in Law completed. Seven core subjects: constitutional, criminal, civil, commercial, property, trusts, EU law.',
                'next_action': 'Plan court observations. Research bar professional course requirements.',
                'notes': 'Foundation knowledge established. Testing through observation and potential Bar route.'
            }
        )

        IdentityFeed.objects.get_or_create(
            working_identity=law,
            date=timezone.make_aware(datetime(2025, 12, 3)),
            defaults={
                'status': 'Monthly court observations planned to begin January 2026. Testing whether legal practice resonates beyond academic interest.',
                'next_action': 'Schedule first court visit. Document observations and reflections on legal practice.',
                'notes': 'Blog series planned: Observations from the courtroom.'
            }
        )

        IdentityFeed.objects.get_or_create(
            working_identity=law,
            date=timezone.make_aware(datetime(2025, 12, 10)),
            defaults={
                'status': 'Evaluating bar professional course as next step. Considering whether to pursue solicitor or barrister route.',
                'next_action': 'Research bar course providers and funding options. Clarify timeline post-grievance settlement.',
                'notes': 'Decision point: proceed to bar qualification or continue with court observations only?'
            }
        )

        # Create IdentityFeed entries for Cybersecurity
        IdentityFeed.objects.get_or_create(
            working_identity=cybersecurity,
            date=timezone.make_aware(datetime(2025, 11, 15)),
            defaults={
                'status': 'AZ-900 (Azure) and SC-900 (Security) certifications completed. Foundation cloud and security knowledge validated.',
                'next_action': 'Begin CompTIA Network+ study. Start home SOC lab setup.',
                'notes': ''
            }
        )

        IdentityFeed.objects.get_or_create(
            working_identity=cybersecurity,
            date=timezone.make_aware(datetime(2025, 11, 27)),
            defaults={
                'status': 'Home SOC lab setup initiated. Architecture: Mac-based ELK (Elasticsearch, Logstash, Kibana) + Cowrie SSH honeypot. Documenting detection rules for real attack patterns.',
                'next_action': 'Complete ELK + Cowrie Docker setup. Build first detection rule. Document architecture on portfolio subdomain.',
                'notes': 'Blog: Building a home SOC lab from scratch. Documenting pattern recognition in security detection.'
            }
        )

        IdentityFeed.objects.get_or_create(
            working_identity=cybersecurity,
            date=timezone.make_aware(datetime(2026, 4, 1)),
            defaults={
                'status': 'CompTIA Network+ exam study phase begins April 2026. Targeting completion by end 2026.',
                'next_action': 'Enroll in Network+ study materials. Schedule exam.',
                'notes': 'Timeline: Study during summer 2026 alongside locum pharmacy work.'
            }
        )

        # Create IdentityFeed entries for Actuary
        IdentityFeed.objects.get_or_create(
            working_identity=actuary,
            date=timezone.make_aware(datetime(2025, 11, 20)),
            defaults={
                'status': 'CS1 actuarial exam preparation underway. Target: April 2026 examination.',
                'next_action': 'Complete CS1 study materials. Take mock exams monthly.',
                'notes': 'Financial modeling experience (CFI FMVA) supports quantitative foundation.'
            }
        )

        IdentityFeed.objects.get_or_create(
            working_identity=actuary,
            date=timezone.make_aware(datetime(2025, 12, 15)),
            defaults={
                'status': 'Planning mini project: pharmacy data analysis using actuarial frameworks. Extracting prescription patterns from Boots data.',
                'next_action': 'Define scope: analyze medication adherence patterns, cost-benefit analysis, risk stratification.',
                'notes': 'Blog: Bridging pharmacy and actuarial science—quantifying healthcare risk.'
            }
        )

        IdentityFeed.objects.get_or_create(
            working_identity=actuary,
            date=timezone.make_aware(datetime(2026, 9, 1)),
            defaults={
                'status': 'Target: GAD Graduate Trainee Actuary role application (September 2027 start). CS1 completion prerequisite.',
                'next_action': 'Achieve CS1 pass. Explore other actuarial exams (CS2). Apply to GAD trainee programmes.',
                'notes': 'Timeline: 2027 onwards pending CS1 success and career clarity.'
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully populated WorkingIdentity and IdentityFeed'))

'''
Run it:
python manage.py populate_identities
'''