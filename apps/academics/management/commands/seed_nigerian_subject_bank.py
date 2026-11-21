from django.core.management.base import BaseCommand
from apps.academics.models import MasterSubjectBank, LevelGroupCategory, Department, LevelGroup, Subject

class Command(BaseCommand):
    help = 'Seeds the comprehensive Nigerian National Subject Bank (NERDC, WAEC, NECO)'

    def handle(self, *args, **options):
        self.stdout.write("Populating Nigerian National Subject Bank...")

        SUBJECTS = [
            # ---------------- EARLY YEARS ----------------
            {
                "name": "Number Work", "code": "EY-NUM", "cat": LevelGroupCategory.EARLY_YEARS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Foundational numeracy and counting skills"
            },
            {
                "name": "Letter Work & Phonics", "code": "EY-LET", "cat": LevelGroupCategory.EARLY_YEARS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Alphabet recognition, letter sounds, and early vocabulary"
            },
            {
                "name": "Rhymes & Songs", "code": "EY-RHY", "cat": LevelGroupCategory.EARLY_YEARS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Auditory memory, rhythm, and expressive singing"
            },
            {
                "name": "Health Habits", "code": "EY-HLT", "cat": LevelGroupCategory.EARLY_YEARS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Personal hygiene, handwashing, and cleanliness"
            },
            {
                "name": "Social Habits", "code": "EY-SOC", "cat": LevelGroupCategory.EARLY_YEARS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Manners, peer interaction, and emotional development"
            },
            {
                "name": "Colouring & Drawing", "code": "EY-ART", "cat": LevelGroupCategory.EARLY_YEARS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Fine motor development, pencil control, and creativity"
            },
            {
                "name": "Writing & Pre-Writing", "code": "EY-WRT", "cat": LevelGroupCategory.EARLY_YEARS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Tracing, pencil grip, strokes, and letter formation"
            },
            {
                "name": "Practical Life Skills", "code": "EY-PRC", "cat": LevelGroupCategory.EARLY_YEARS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Self-reliance, buttoning, packing, and orderly habits"
            },
            {
                "name": "Basic Science / Nature Study", "code": "EY-SCI", "cat": LevelGroupCategory.EARLY_YEARS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Plants, animals, weather, and five senses exploration"
            },
            {
                "name": "Christian Religious Knowledge", "code": "EY-CRK", "cat": LevelGroupCategory.EARLY_YEARS,
                "dept": Department.NONE, "is_core": False, "trade": False, "desc": "Bible stories and foundational moral values"
            },
            {
                "name": "Islamic Religious Knowledge", "code": "EY-IRK", "cat": LevelGroupCategory.EARLY_YEARS,
                "dept": Department.NONE, "is_core": False, "trade": False, "desc": "Quranic verses, Dua, and foundational moral values"
            },

            # ---------------- PRIMARY (NERDC CURRICULUM) ----------------
            {
                "name": "English Language", "code": "PR-ENG", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Grammar, comprehension, composition, and spelling"
            },
            {
                "name": "Mathematics", "code": "PR-MTH", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Arithmetic, algebra basics, geometry, and word problems"
            },
            {
                "name": "Basic Science and Technology", "code": "PR-BST", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Integrated science, physical world, and technology concepts"
            },
            {
                "name": "Social Studies", "code": "PR-SOS", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Community, culture, environment, and national institutions"
            },
            {
                "name": "Civic Education", "code": "PR-CIV", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Rights, national symbols, duties, and responsible citizenship"
            },
            {
                "name": "Verbal Reasoning", "code": "PR-VRB", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Vocabulary aptitude, analogies, and critical thinking"
            },
            {
                "name": "Quantitative Reasoning", "code": "PR-QNT", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Numerical patterns, logical problem solving, and math aptitude"
            },
            {
                "name": "Computer Studies / Digital Literacy", "code": "PR-CMP", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Computer hardware, internet safety, and typing skills"
            },
            {
                "name": "Agricultural Science", "code": "PR-AGR", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Farming practices, soil, crops, and farm animals"
            },
            {
                "name": "Home Economics", "code": "PR-HEC", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Food nutrition, clothing, sewing, and home management"
            },
            {
                "name": "Cultural and Creative Arts (CCA)", "code": "PR-CCA", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Music, drama, drawing, painting, and craftwork"
            },
            {
                "name": "Physical and Health Education (PHE)", "code": "PR-PHE", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Athletics, games, body wellness, and first aid"
            },
            {
                "name": "Handwriting & Penmanship", "code": "PR-HWT", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Cursive writing neatness and presentation skills"
            },
            {
                "name": "Christian Religious Studies (CRS)", "code": "PR-CRS", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": False, "trade": False, "desc": "Old/New Testament teachings and character formation"
            },
            {
                "name": "Islamic Religious Studies (IRS)", "code": "PR-IRS", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": False, "trade": False, "desc": "Islamic history, Hadith, and moral instruction"
            },
            {
                "name": "Yoruba Language", "code": "PR-YOR", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": False, "trade": False, "desc": "Yoruba grammar, reading, and cultural heritage"
            },
            {
                "name": "Hausa Language", "code": "PR-HAU", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": False, "trade": False, "desc": "Hausa grammar, reading, and cultural heritage"
            },
            {
                "name": "Igbo Language", "code": "PR-IGB", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": False, "trade": False, "desc": "Igbo grammar, reading, and cultural heritage"
            },
            {
                "name": "French Language", "code": "PR-FRN", "cat": LevelGroupCategory.PRIMARY,
                "dept": Department.NONE, "is_core": False, "trade": False, "desc": "Introductory French communication and vocabulary"
            },

            # ---------------- JUNIOR SECONDARY (JSS / BECE REVISED CURRICULUM) ----------------
            {
                "name": "English Studies", "code": "JS-ENG", "cat": LevelGroupCategory.JSS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Grammar, summary writing, oral English, and literature"
            },
            {
                "name": "Mathematics", "code": "JS-MTH", "cat": LevelGroupCategory.JSS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "General math, statistics, trigonometry, and algebra"
            },
            {
                "name": "Intermediate Science", "code": "JS-ISC", "cat": LevelGroupCategory.JSS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Integrated intermediate science and technology curriculum"
            },
            {
                "name": "Digital Technology", "code": "JS-DTE", "cat": LevelGroupCategory.JSS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Digital literacy, computing, and technology application"
            },
            {
                "name": "Pre-Vocational Studies (PVS)", "code": "JS-PVS", "cat": LevelGroupCategory.JSS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Integrated pre-vocational education (Agricultural Science & Home Economics)"
            },
            {
                "name": "Social Studies", "code": "JS-SOS", "cat": LevelGroupCategory.JSS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Contemporary Nigerian society, family life, and globe"
            },
            {
                "name": "Civic Education", "code": "JS-CIV", "cat": LevelGroupCategory.JSS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Constitution, democracy, rule of law, and anti-corruption"
            },
            {
                "name": "Business Studies", "code": "JS-BUS", "cat": LevelGroupCategory.JSS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Commerce basics, book-keeping, office practice, and keyboarding"
            },
            {
                "name": "Cultural and Creative Arts", "code": "JS-CCA", "cat": LevelGroupCategory.JSS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Visual arts, performing arts, and Nigerian crafts"
            },
            {
                "name": "Physical and Health Education", "code": "JS-PHE", "cat": LevelGroupCategory.JSS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Sports physiology, track & field, and personal health"
            },
            {
                "name": "Christian Religious Studies", "code": "JS-CRS", "cat": LevelGroupCategory.JSS,
                "dept": Department.NONE, "is_core": False, "trade": False, "desc": "Biblical literature, apostles, and moral guidance"
            },
            {
                "name": "Islamic Religious Studies", "code": "JS-IRS", "cat": LevelGroupCategory.JSS,
                "dept": Department.NONE, "is_core": False, "trade": False, "desc": "Fiqh, Sirah, Tawhid, and ethical Islamic living"
            },
            {
                "name": "French Language", "code": "JS-FRN", "cat": LevelGroupCategory.JSS,
                "dept": Department.NONE, "is_core": False, "trade": False, "desc": "Conversational French and francophone culture"
            },
            {
                "name": "Nigerian Language (Yoruba/Hausa/Igbo)", "code": "JS-NIG", "cat": LevelGroupCategory.JSS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Indigenous language comprehension and literature"
            },

            # ---------------- SENIOR SECONDARY: CORE (WAEC COMPULSORY) ----------------
            {
                "name": "English Language", "code": "SS-ENG", "cat": LevelGroupCategory.SS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Compulsory WAEC English Language"
            },
            {
                "name": "General Mathematics", "code": "SS-MTH", "cat": LevelGroupCategory.SS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Compulsory WAEC General Mathematics"
            },
            {
                "name": "Civic Education", "code": "SS-CIV", "cat": LevelGroupCategory.SS,
                "dept": Department.NONE, "is_core": True, "trade": False, "desc": "Compulsory WAEC Civic Education"
            },

            # ---------------- SENIOR SECONDARY: TRADE / ENTREPRENEURSHIP ----------------
            {
                "name": "Data Processing", "code": "SS-TRD-DAT", "cat": LevelGroupCategory.SS,
                "dept": Department.NONE, "is_core": False, "trade": True, "desc": "WAEC Trade: Database, spreadsheets, and data analytics"
            },
            {
                "name": "Catering Craft Practice", "code": "SS-TRD-CAT", "cat": LevelGroupCategory.SS,
                "dept": Department.NONE, "is_core": False, "trade": True, "desc": "WAEC Trade: Food production, culinary arts, and hospitality"
            },
            {
                "name": "Garment Making", "code": "SS-TRD-GAR", "cat": LevelGroupCategory.SS,
                "dept": Department.NONE, "is_core": False, "trade": True, "desc": "WAEC Trade: Pattern cutting, fashion design, and tailoring"
            },
            {
                "name": "Animal Husbandry", "code": "SS-TRD-ANH", "cat": LevelGroupCategory.SS,
                "dept": Department.NONE, "is_core": False, "trade": True, "desc": "WAEC Trade: Poultry, cattle, rabbit, and livestock farming"
            },
            {
                "name": "Fisheries", "code": "SS-TRD-FSH", "cat": LevelGroupCategory.SS,
                "dept": Department.NONE, "is_core": False, "trade": True, "desc": "WAEC Trade: Aquaculture, fish breeding, and pond management"
            },
            {
                "name": "Marketing", "code": "SS-TRD-MKT", "cat": LevelGroupCategory.SS,
                "dept": Department.NONE, "is_core": False, "trade": True, "desc": "WAEC Trade: Product marketing, pricing, and retail salesmanship"
            },
            {
                "name": "Electrical Installation & Maintenance Work", "code": "SS-TRD-ELC", "cat": LevelGroupCategory.SS,
                "dept": Department.NONE, "is_core": False, "trade": True, "desc": "WAEC Trade: Domestic wiring, testing, and electrical appliances"
            },

            # ---------------- SENIOR SECONDARY: SCIENCE DEPARTMENT ----------------
            {
                "name": "Physics", "code": "SS-PHY", "cat": LevelGroupCategory.SS,
                "dept": Department.SCIENCE, "is_core": True, "trade": False, "desc": "Mechanics, waves, electricity, optics, and modern physics"
            },
            {
                "name": "Chemistry", "code": "SS-CHM", "cat": LevelGroupCategory.SS,
                "dept": Department.SCIENCE, "is_core": True, "trade": False, "desc": "Physical, inorganic, organic, and analytical chemistry"
            },
            {
                "name": "Biology", "code": "SS-BIO", "cat": LevelGroupCategory.SS,
                "dept": Department.SCIENCE, "is_core": True, "trade": False, "desc": "Plant/animal physiology, ecology, genetics, and health"
            },
            {
                "name": "Further Mathematics", "code": "SS-FMTH", "cat": LevelGroupCategory.SS,
                "dept": Department.SCIENCE, "is_core": False, "trade": False, "desc": "Calculus, vectors, matrices, mechanics, and advanced math"
            },
            {
                "name": "Agricultural Science", "code": "SS-AGR", "cat": LevelGroupCategory.SS,
                "dept": Department.SCIENCE, "is_core": False, "trade": False, "desc": "Agronomy, animal nutrition, farm engineering, and economics"
            },
            {
                "name": "Technical Drawing", "code": "SS-TDR", "cat": LevelGroupCategory.SS,
                "dept": Department.SCIENCE, "is_core": False, "trade": False, "desc": "Orthographic projections, isometric drawing, and drafting"
            },
            {
                "name": "Geography", "code": "SS-GEO", "cat": LevelGroupCategory.SS,
                "dept": Department.SCIENCE, "is_core": False, "trade": False, "desc": "Physical geography, map reading, and economic geography"
            },
            {
                "name": "Computer Studies", "code": "SS-CMP", "cat": LevelGroupCategory.SS,
                "dept": Department.SCIENCE, "is_core": False, "trade": False, "desc": "Algorithms, programming logic, networks, and hardware"
            },

            # ---------------- SENIOR SECONDARY: ARTS / HUMANITIES ----------------
            {
                "name": "Literature-in-English", "code": "SS-LIT", "cat": LevelGroupCategory.SS,
                "dept": Department.ARTS, "is_core": True, "trade": False, "desc": "African and Non-African prose, drama, and poetry"
            },
            {
                "name": "Government", "code": "SS-GOV", "cat": LevelGroupCategory.SS,
                "dept": Department.ARTS, "is_core": True, "trade": False, "desc": "Political systems, Nigerian constitutional history, and diplomacy"
            },
            {
                "name": "Christian Religious Studies (CRS)", "code": "SS-CRS", "cat": LevelGroupCategory.SS,
                "dept": Department.ARTS, "is_core": False, "trade": False, "desc": "Gospel synopsis, epistles, and contemporary Christian ethics"
            },
            {
                "name": "Islamic Religious Studies (IRS)", "code": "SS-IRS", "cat": LevelGroupCategory.SS,
                "dept": Department.ARTS, "is_core": False, "trade": False, "desc": "Quranic exegesis, Hadith sciences, and Islamic jurisprudence"
            },
            {
                "name": "History", "code": "SS-HIS", "cat": LevelGroupCategory.SS,
                "dept": Department.ARTS, "is_core": False, "trade": False, "desc": "Pre-colonial Nigerian kingdoms, colonial rule, and world history"
            },
            {
                "name": "Visual Art", "code": "SS-ART", "cat": LevelGroupCategory.SS,
                "dept": Department.ARTS, "is_core": False, "trade": False, "desc": "Painting, sculpture, textile design, and art history"
            },
            {
                "name": "Music", "code": "SS-MUS", "cat": LevelGroupCategory.SS,
                "dept": Department.ARTS, "is_core": False, "trade": False, "desc": "Music theory, harmony, orchestration, and African traditional music"
            },
            {
                "name": "French Language", "code": "SS-FRN", "cat": LevelGroupCategory.SS,
                "dept": Department.ARTS, "is_core": False, "trade": False, "desc": "Advanced written/oral French and literature"
            },
            {
                "name": "Yoruba Language", "code": "SS-YOR", "cat": LevelGroupCategory.SS,
                "dept": Department.ARTS, "is_core": False, "trade": False, "desc": "Yoruba grammar, oral literature (Ewi), and culture"
            },
            {
                "name": "Hausa Language", "code": "SS-HAU", "cat": LevelGroupCategory.SS,
                "dept": Department.ARTS, "is_core": False, "trade": False, "desc": "Hausa grammar, literature, and cultural heritage"
            },
            {
                "name": "Igbo Language", "code": "SS-IGB", "cat": LevelGroupCategory.SS,
                "dept": Department.ARTS, "is_core": False, "trade": False, "desc": "Igbo grammar, literature, and cultural heritage"
            },

            # ---------------- SENIOR SECONDARY: COMMERCIAL / BUSINESS ----------------
            {
                "name": "Financial Accounting", "code": "SS-ACC", "cat": LevelGroupCategory.SS,
                "dept": Department.COMMERCIAL, "is_core": True, "trade": False, "desc": "Double entry, balance sheets, ledger accounts, and audit"
            },
            {
                "name": "Commerce", "code": "SS-COM", "cat": LevelGroupCategory.SS,
                "dept": Department.COMMERCIAL, "is_core": True, "trade": False, "desc": "Trade, banking, insurance, transportation, and warehousing"
            },
            {
                "name": "Economics", "code": "SS-ECO", "cat": LevelGroupCategory.SS,
                "dept": Department.COMMERCIAL, "is_core": True, "trade": False, "desc": "Micro/macro-economics, public finance, inflation, and development"
            },
            {
                "name": "Book Keeping", "code": "SS-BKP", "cat": LevelGroupCategory.SS,
                "dept": Department.COMMERCIAL, "is_core": False, "trade": False, "desc": "Cash books, receipts, petty cash, and commercial records"
            },
            {
                "name": "Office Practice", "code": "SS-OFP", "cat": LevelGroupCategory.SS,
                "dept": Department.COMMERCIAL, "is_core": False, "trade": False, "desc": "Filing, business correspondence, secretarial duties, and meetings"
            },
            {
                "name": "Insurance", "code": "SS-INS", "cat": LevelGroupCategory.SS,
                "dept": Department.COMMERCIAL, "is_core": False, "trade": False, "desc": "Risk management, life/general policies, and indemnities"
            },
            {
                "name": "Store Management", "code": "SS-STM", "cat": LevelGroupCategory.SS,
                "dept": Department.COMMERCIAL, "is_core": False, "trade": False, "desc": "Inventory control, procurement, stock valuation, and logistics"
            },
        ]

        created_count = 0
        updated_count = 0

        for item in SUBJECTS:
            obj, created = MasterSubjectBank.objects.update_or_create(
                code=item["code"],
                defaults={
                    "name": item["name"],
                    "level_category": item["cat"],
                    "department": item["dept"],
                    "is_core": item["is_core"],
                    "is_trade_subject": item["trade"],
                    "description": item["desc"]
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded {created_count} new subjects (updated {updated_count}) into Master Subject Bank!"
        ))
