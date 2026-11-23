BIO = {
    'tagline': (
        'Pharmacist · Digital Medicines & Clinical Systems · '
        'EPMA, Epic & Medicines Optimisation · MSc Mental Health, Ethics & Law'
    ),
    'paragraphs': [
        (
            'I am a pharmacist who prefers lasting fixes to quick patches. '
            'Whether a prescribing workflow breaks in software or a statutory rule '
            'clashes with ward reality, I want to repair the underlying design so '
            'the problem stays solved. Lately that focus narrows to one question: '
            'whether mental health tribunals should have jurisdiction to review '
            'compulsory treatment decisions. This site collects my working notes '
            'along the way.'
        ),
    ],
}


def bio(request):
    return {'bio': BIO}
