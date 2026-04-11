from __future__ import annotations

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.entities import Question
from app.models.entities import TaxonomyVersion


def main() -> None:
    with SessionLocal() as db:
        existing = db.execute(
            select(TaxonomyVersion).where(
                TaxonomyVersion.code == "mindtrace_mvp_v2_draft_38",
            ),
        ).scalar_one_or_none()

        if existing is not None:
            print("Seed already exists.")
            return

        active_taxonomies = db.execute(
            select(TaxonomyVersion).where(
                TaxonomyVersion.status == "active",
            ),
        ).scalars().all()

        for active_taxonomy in active_taxonomies:
            active_taxonomy.status = "archived"

        taxonomy = TaxonomyVersion(
            code="mindtrace_mvp_v2_draft_38",
            version_label="v2-draft-38",
            status="active",
            title="MindTrace MVP Taxonomy Draft 38",
            description=(
                "Draft question set with up to 38 questions for MVP "
                "validation."
            ),
            schema_json={},
            rules_json={},
        )
        db.add(taxonomy)
        db.flush()

        questions = [
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_001",
                order_no=1,
                title="Что для вас по-настоящему важно в жизни?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_002",
                order_no=2,
                title="Что сейчас больше всего занимает ваши мысли?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_003",
                order_no=3,
                title="Какие задачи вы сейчас откладываете и почему?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_004",
                order_no=4,
                title=(
                    "Что в вашей текущей жизни работает хорошо, а что "
                    "требует изменений?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_005",
                order_no=5,
                title=(
                    "По каким признакам вы понимаете, что движетесь в "
                    "правильном направлении?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_006",
                order_no=6,
                title="Что сейчас сильнее всего забирает вашу энергию?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_007",
                order_no=7,
                title=(
                    "Какие события прошлого сильнее всего повлияли на ваш "
                    "образ мыслей?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_008",
                order_no=8,
                title="Какие решения из прошлого вы считаете удачными и почему?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_009",
                order_no=9,
                title="Какие ошибки прошлого вы до сих пор вспоминаете чаще всего?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_010",
                order_no=10,
                title=(
                    "Какие убеждения вы вынесли из семьи, детства или "
                    "раннего опыта?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_011",
                order_no=11,
                title=(
                    "Что из прошлого опыта помогает вам сегодня лучше "
                    "справляться с жизнью?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_012",
                order_no=12,
                title="Какие повторяющиеся сценарии вы замечаете в своей жизни?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_013",
                order_no=13,
                title="Каким вы хотите видеть свою жизнь через 3 года?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_014",
                order_no=14,
                title="О чем вы мечтаете, но пока не приблизились к этому?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_015",
                order_no=15,
                title=(
                    "Какие цели для вас сейчас действительно важны, а не "
                    "просто желательны?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_016",
                order_no=16,
                title=(
                    "Что вы готовы делать ради будущего, а что постоянно "
                    "откладываете?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_017",
                order_no=17,
                title="Какие риски будущего беспокоят вас сильнее всего?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_018",
                order_no=18,
                title=(
                    "Как вы понимаете, что выбранный вами путь ведет к "
                    "желаемому будущему?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_019",
                order_no=19,
                title="Какие люди сильнее всего влияют на ваши решения?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_020",
                order_no=20,
                title="Что для вас значит доверие в отношениях?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_021",
                order_no=21,
                title="В каких ситуациях вам сложнее всего договариваться с людьми?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_022",
                order_no=22,
                title=(
                    "Как вы обычно реагируете на критику, замечания или "
                    "несогласие?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_023",
                order_no=23,
                title=(
                    "Что вы чаще даете людям: поддержку, контроль, "
                    "дистанцию или требования?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_024",
                order_no=24,
                title=(
                    "Какие отношения в вашей жизни сейчас требуют "
                    "наибольшего внимания?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_025",
                order_no=25,
                title=(
                    "Какой результат в работе или проектах для вас "
                    "сейчас самый важный?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_026",
                order_no=26,
                title="Как вы обычно превращаете идею в конкретный план действий?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_027",
                order_no=27,
                title="Что чаще всего мешает вам доводить начатое до результата?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_028",
                order_no=28,
                title="Как вы понимаете, что проект действительно движется успешно?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_029",
                order_no=29,
                title=(
                    "Какие ресурсы вы умеете использовать хорошо, а "
                    "каких вам обычно не хватает?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_030",
                order_no=30,
                title="Как вы принимаете решения о деньгах, вложениях или рисках?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_031",
                order_no=31,
                title=(
                    "Если бы у вас был один главный проект на ближайший "
                    "год, каким бы он был?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_032",
                order_no=32,
                title="В каких ситуациях вам приходят самые нестандартные идеи?",
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_033",
                order_no=33,
                title=(
                    "Как вы понимаете, что неожиданная возможность "
                    "действительно стоит внимания?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_034",
                order_no=34,
                title=(
                    "Бывает ли, что вы чувствуете правильное решение "
                    "раньше, чем можете его логически объяснить?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_035",
                order_no=35,
                title=(
                    "Как вы относитесь к случайностям, совпадениям и "
                    "неожиданным поворотам событий?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_036",
                order_no=36,
                title=(
                    "Что для вас важнее в неопределенности: контроль, "
                    "гибкость или поиск новой возможности?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_037",
                order_no=37,
                title=(
                    "Когда в вашей жизни происходили резкие качественные "
                    "скачки и что к ним привело?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
            Question(
                taxonomy_version_id=taxonomy.id,
                code="q_038",
                order_no=38,
                title=(
                    "Что помогает вам замечать возможности там, где "
                    "другие видят только проблемы?"
                ),
                description=None,
                question_type="text",
                is_required=True,
                is_active=True,
                ui_config={},
                validation_rules={},
            ),
        ]

        db.add_all(questions)
        db.commit()

    print("Seed inserted successfully.")


if __name__ == "__main__":
    main()
