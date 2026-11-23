BIO = {
    'tagline': (
        'Pharmacist · Digital Medicines & Clinical Systems · '
        'EPMA, Epic & Medicines Optimisation · MSc Mental Health, Ethics & Law'
    ),
    'paragraphs': [
        (
            'Eight years of clinical pharmacy across community, acute hospital, and '
            'mental health settings taught me one lesson that rarely appears in policy '
            'papers: healthcare design often diverges from what clinicians face on the '
            'ground. I study that gap across EPMA, Epic, and electronic health records '
            'to spot system-related safety risks, improve structured prescribing data, '
            'and strengthen medicines optimisation.'
        ),
        (
            'My background deliberately crosses disciplines. I extracted clinical '
            'insights from electronic health records at South London and Maudsley NHS '
            'Trust, coded adverse events across clinical trials at Femtogenix to spot '
            'toxicity patterns, and gathered cross-agency evidence for patients at '
            'Rethink. Legal training through the GDL, an MSc in Mental Health, Ethics '
            "and Law at King's College London, and programming self-taught during my "
            'MPharm research run alongside that clinical work.'
        ),
        (
            'Right now I investigate psychiatric prescribing, evidence heterogeneity, '
            'and healthcare law: specifically whether the Mental Health Act 1983 '
            'accounts for the limits of population-level evidence when applied to '
            'individual patients. Open to conversations on healthcare policy, '
            'research collaboration, and analytical roles across health and the '
            'public sector.'
        ),
    ],
}


def bio(request):
    return {'bio': BIO}
