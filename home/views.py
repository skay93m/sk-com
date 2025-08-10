from django.shortcuts import render
from datetime import datetime

def home(request):
    return render(request, 'index.html', {
        'title': 'Home',
        'header': 'Welcome!',
        'statement1': 'Pharmacist → Aspiring Barrister | Tech Enthusiast | Lifelong Learner', # who am I
        'statement2': (
            "My professional journey began in the field of pharmacy, where I developed a strong foundation in healthcare, patient advocacy, and scientific rigor. Driven by a passion for justice and a desire to make a broader impact, I transitioned towards law, aspiring to become a barrister. This shift has allowed me to combine my analytical skills and ethical commitment from pharmacy with the critical thinking and advocacy required in legal practice. Along the way, I discovered a deep interest in technology, recognizing its transformative potential in both healthcare and law. I have actively pursued opportunities to expand my technical skills, engaging with projects that bridge the gap between these disciplines. Lifelong learning is at the core of my journey, motivating me to continuously seek new knowledge and adapt to evolving challenges. My diverse background enables me to approach problems from multiple perspectives, fostering innovative solutions and meaningful contributions. Whether working on legal cases, healthcare initiatives, or tech-driven projects, I am committed to making a positive difference and inspiring others to embrace interdisciplinary growth."
        ), # what I do
        'cta_button': 'Explore my projects' # call to action
    })