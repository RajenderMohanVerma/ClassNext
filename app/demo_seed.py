"""Demo accounts and starter content for ClassNext.

Seeds the one-click demo logins offered on the sign-in page:

* Teacher (the real teacher account): ``teacher@classnext.demo``
* Student demo account:               ``student@classnext.demo``

Also seeds a small amount of starter content (two classes with subjects,
chapters and published lessons, plus a welcome announcement) the first time
it runs, so both dashboards have something real to show. Every step is
get-or-create by unique key, so running it repeatedly — e.g. on every
Vercel cold start — is safe and never duplicates or overwrites data.
"""

from datetime import datetime, timezone

from app.extensions import db
from app.models.announcement import Announcement
from app.models.catalog import Chapter, SchoolClass
from app.models.content import Content
from app.models.enums import ACCOUNT_ACTIVE, CONTENT_STATUS_PUBLISHED
from app.models.subject import Subject
from app.models.user import User

TEACHER_EMAIL = 'teacher@classnext.demo'
TEACHER_PASSWORD = 'Teacher@123'
TEACHER_NAME = 'Er. Amit Sir'

STUDENT_EMAIL = 'student@classnext.demo'
STUDENT_PASSWORD = 'Student@123'
STUDENT_NAME = 'Demo Student'


def _now():
    return datetime.now(timezone.utc)


def _get_or_create_user(email, name, role, password):
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(
            name=name,
            email=email,
            role=role,
            account_status=ACCOUNT_ACTIVE,
            is_email_verified=True,
            email_verified_at=_now(),
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
    return user


def _get_or_create_class(teacher, name, slug, description, order):
    school_class = SchoolClass.query.filter_by(slug=slug).first()
    if school_class is None:
        school_class = SchoolClass(
            name=name,
            slug=slug,
            description=description,
            display_order=order,
            is_enabled=True,
            status='active',
            created_by=teacher.id,
        )
        db.session.add(school_class)
        db.session.flush()
    return school_class


def _get_or_create_subject(teacher, school_class, name, slug, icon, description, order):
    subject = Subject.query.filter_by(slug=slug).first()
    if subject is None:
        subject = Subject(
            name=name,
            slug=slug,
            description=description,
            icon=icon,
            class_id=school_class.id,
            status=CONTENT_STATUS_PUBLISHED,
            display_order=order,
            is_enabled=True,
            created_by=teacher.id,
        )
        db.session.add(subject)
        db.session.flush()
    return subject


def _get_or_create_chapter(teacher, subject, school_class, title, slug, description, order):
    chapter = Chapter.query.filter_by(slug=slug).first()
    if chapter is None:
        chapter = Chapter(
            subject_id=subject.id,
            class_id=school_class.id,
            title=title,
            slug=slug,
            description=description,
            display_order=order,
            status=CONTENT_STATUS_PUBLISHED,
            created_by=teacher.id,
        )
        db.session.add(chapter)
        db.session.flush()
    return chapter


def _get_or_create_content(teacher, subject, school_class, chapter, **fields):
    slug = fields.pop('slug')
    content = Content.query.filter_by(slug=slug).first()
    if content is None:
        content = Content(
            slug=slug,
            subject_id=subject.id,
            class_id=school_class.id,
            chapter_id=chapter.id if chapter else None,
            created_by=teacher.id,
            status=CONTENT_STATUS_PUBLISHED,
            published_at=_now(),
            **fields,
        )
        db.session.add(content)
        db.session.flush()
    return content


def seed_demo_data():
    """Create the demo accounts and starter content if they are missing."""
    teacher = _get_or_create_user(TEACHER_EMAIL, TEACHER_NAME, 'teacher', TEACHER_PASSWORD)
    student = _get_or_create_user(STUDENT_EMAIL, STUDENT_NAME, 'student', STUDENT_PASSWORD)

    class10 = _get_or_create_class(
        teacher, 'Class 10', 'class-10',
        'Board-year foundation: Mathematics and Science, chapter by chapter.', 1,
    )
    class12 = _get_or_create_class(
        teacher, 'Class 12', 'class-12',
        'Board + competitive preparation: Physics and Mathematics.', 2,
    )

    if student.class_id is None:
        student.class_id = class10.id

    maths10 = _get_or_create_subject(
        teacher, class10, 'Mathematics', 'class-10-mathematics', 'bi-calculator',
        'Algebra, geometry and trigonometry — explained step by step.', 1,
    )
    science10 = _get_or_create_subject(
        teacher, class10, 'Science', 'class-10-science', 'bi-lightbulb',
        'Physics, chemistry and biology concepts made simple.', 2,
    )
    physics12 = _get_or_create_subject(
        teacher, class12, 'Physics', 'class-12-physics', 'bi-lightning-charge',
        'Mechanics, optics and modern physics for boards and beyond.', 1,
    )

    quad = _get_or_create_chapter(
        teacher, maths10, class10, 'Quadratic Equations', 'class-10-maths-quadratic-equations',
        'Solving quadratics by factorisation, completing the square and the formula.', 1,
    )
    light = _get_or_create_chapter(
        teacher, science10, class10, 'Light — Reflection and Refraction', 'class-10-science-light',
        'Mirrors, lenses and the laws that govern them.', 1,
    )
    electro = _get_or_create_chapter(
        teacher, physics12, class12, 'Electrostatics', 'class-12-physics-electrostatics',
        'Charges, fields and potential — the foundation of electromagnetism.', 1,
    )

    _get_or_create_content(
        teacher, maths10, class10, quad,
        slug='quadratic-equations-introduction-notes',
        title='Quadratic Equations — Introduction & Standard Form',
        content_type='notes',
        topic='Quadratic Equations',
        access_level='public',
        is_featured=True,
        description='What makes an equation quadratic, the standard form ax² + bx + c = 0, and how to check whether an equation is quadratic.',
        body_html=(
            '<p>A <strong>quadratic equation</strong> in the variable x is an equation of the form '
            '<strong>ax² + bx + c = 0</strong>, where a, b and c are real numbers and a ≠ 0.</p>'
            '<p>Quick check: the highest power of x must be exactly 2, and the coefficient of x² '
            'must not be zero.</p>'
            '<p><em>Example:</em> 2x² + 5x − 3 = 0 is quadratic (a = 2, b = 5, c = −3). '
            'x² + 1/x = 5 is <strong>not</strong> quadratic until it is rearranged.</p>'
        ),
    )
    _get_or_create_content(
        teacher, maths10, class10, quad,
        slug='quadratic-equations-factorisation-video',
        title='Quadratic Equations — Complete Chapter Video Lesson',
        content_type='video_lesson',
        topic='Quadratic Equations',
        access_level='logged_in',
        description='The complete chapter in one lesson: standard form, factorisation, the quadratic formula and the nature of roots.',
        video_url='https://www.youtube.com/watch?v=150TM0Fbc3k',
    )
    _get_or_create_content(
        teacher, science10, class10, light,
        slug='light-mirror-formula-notes',
        title='Mirror Formula & Magnification — Quick Notes',
        content_type='notes',
        topic='Light — Reflection and Refraction',
        access_level='public',
        description='The mirror formula 1/v + 1/u = 1/f, magnification m = −v/u, and the sign convention you must follow in every numerical.',
        body_html=(
            '<p><strong>Mirror formula:</strong> 1/v + 1/u = 1/f, where u = object distance, '
            'v = image distance and f = focal length.</p>'
            '<p><strong>Magnification:</strong> m = h′/h = −v/u. A negative m means the image is '
            'inverted; |m| &gt; 1 means it is enlarged.</p>'
            '<p>Remember the sign convention: distances measured against the direction of '
            'incident light are negative.</p>'
        ),
    )
    _get_or_create_content(
        teacher, physics12, class12, electro,
        slug='electrostatics-coulombs-law-notes',
        title="Coulomb's Law — Notes with Solved Examples",
        content_type='notes',
        topic='Electrostatics',
        access_level='logged_in',
        description="Coulomb's law, the principle of superposition, and a solved numerical in board style.",
        body_html=(
            '<p><strong>Coulomb\'s law:</strong> the force between two point charges is '
            'F = (1/4πε₀) · q₁q₂/r², directed along the line joining them.</p>'
            '<p>Like charges repel, unlike charges attract, and forces add vectorially '
            '(principle of superposition).</p>'
            '<p><em>Solved example:</em> two charges of 2 µC and 3 µC placed 10 cm apart in air '
            'experience F = 9×10⁹ × (2×10⁻⁶ × 3×10⁻⁶) / (0.1)² = 5.4 N.</p>'
        ),
    )

    announcement = Announcement.query.filter_by(title='Welcome to ClassNext!').first()
    if announcement is None:
        announcement = Announcement(
            title='Welcome to ClassNext!',
            body=(
                'Welcome to your learning space. New video lessons and notes are added chapter '
                'by chapter — start with your class, pick a subject, and learn at your own pace. '
                'Learn • Practice • Achieve.'
            ),
            created_by=teacher.id,
        )
        announcement.publish()
        db.session.add(announcement)

    db.session.commit()
    return {'teacher': teacher, 'student': student}
