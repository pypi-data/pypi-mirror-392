import random
import string
from abc import ABC, abstractmethod
from datafakegenerator.dataset_manager import DatasetManager


class BaseProvider(ABC):
    def __init__(self, *, blank_percentage: float = 0.0, datasets: list[str] | None = None, **kwargs):
        self.blank_percentage = float(blank_percentage or 0.0)
        self.datasets = datasets or []
        self.data = None
        self.format = {
            'company': ("{{last_name}} {{company_suffix}}", "{{last_name}}-{{last_name}}", "{{last_name}}, {{last_name}} and {{last_name}}",),
            'username':  ("{{first_name}}.{{last_name}}", "{{last_name}}.{{first_name}}", "{{first_name}}_{{last_name}}",
                          "{{first_name}}-{{last_name}}", "{{first_name}}{{last_name}}", "{{first_name}}.{{last_name}}@",
                          "{{first_name}}.{{last_name}}##", "{{first_name}}_{{last_name}}@", "{{first_name}}_{{last_name}}_##",
                          "{{first_name}}##",  "{{last_name}}##",  "@{{first_name}}_{{last_name}}",  "{{first_name}}_@{{last_name}}",
                          "{{first_name}}##@{{last_name}}",  "{{first_name}}_{{last_name}}_@", "{{first_name}}-{{last_name}}##",
                          "{{first_name}}.{{last_name}}_@", "{{first_name}}##.{{last_name}}", "{{last_name}}_{{first_name}}##"),
            'email': "{{user_name}}@{{domain_name}}",
            'plate_number': ("#^^####", "##^^###", "### ^^^", "####", "^^^####", "### ^^^", "###^^^", "#^^^###",
                             "###-^^^", "^^^-###", "###-^^^", "######", "^^-####", "^^^ ^##", "### ^^^", "^## #^^",
                             "### #^^", "^^^####", "^^ ####", "^^^ ###", "H^^ ###", "Z^^ ###", "K^^ ###", "L^^ ###",
                             "M^^ ###", "^ ######", "#^ #####", "#^ ^####", "#^ ^^^###", "#^ ####^", "##^ ####",
                             "^^ #####", "^^# ####", "###^", "###^^", "###^^^", "^^^ ###", "### ^^^", "### ^^^",
                             "### ^^^", "#### ^^", "#^^####", "#^^^ ##", "#^^ ###", "### ^^#", "##^ ^##", "### ^^^",
                             "#^^ ^##", "###-^^^", "^^^ ###", "^^# ^#^", "#-#####^", "##-####^", "^^^ ###", "#-^####",
                             "##-^###", "##-^^##", "##^-###", "### ####", "^##-^^^", "###-^^^", "^^^-###", "^^^-####",
                             "###-^^^^", "### ^^^", "^^^ ###", "^^^ ####", "^^^-###", "### ^^^", "^^^ ###", "^^^ ####",
                             "^^^-###", "###-###", "### #^^", "#^^ ###", "#^^ ^##", "##^ ###", "##^ ^##", "##^ ^^#",
                             "^##-##^", "^^^-####", "^## #^^", "^^^ ###", "##^^#", "#^^##", "###^#", "#^###", "^^^ ###",
                             "^^^-####", "^^^####", "###-^^^", "#^^ ###", "^^^ ###", "^^^-####", "###-^^^", "#-#####",
                             "#-####^", "##-#####", "^^^####")
        }
        self.basic = {
            'frequency': self.get_data_from_json('basic', 'frequency'),
            'nato_phonetic': self.get_data_from_json('basic', 'nato_phonetic'),
            'emoji': self.get_data_from_json('emoji', 'emoji'),
            'priority_levels': self.get_data_from_json('basic', 'priority_levels'),
            'season':  self.get_data_from_json('basic', 'season'),
            'sentiment': self.get_data_from_json('basic', 'sentiment'),
            'weather_condition': self.get_data_from_json('basic', 'weather_condition'),
            'weight_units': self.get_data_from_json('basic', 'weight_units'),
            "height_units": self.get_data_from_json('basic', 'height_units'),
            'day_of_week': self.get_data_from_json('basic', 'day_of_week'),
            'duration_units': self.get_data_from_json('basic', 'duration_units'),
            'metric_prefixes': self.get_data_from_json('basic', 'metric_prefixes'),
            'imperial_units': self.get_data_from_json('basic', 'imperial_units'),
            'month': self.get_data_from_json('basic', 'month'),
            'paper_size': self.get_data_from_json('basic', 'paper_size'),
            'punctuation_marks': self.get_data_from_json('basic', 'punctuation_marks'),
        }
        self.person = {
            'first_name': {
                'female': self.get_data_from_json('names', 'first_name_female'),
                'male':  self.get_data_from_json('names', 'first_name_male')
            },
            'last_name': self.get_data_from_json('names', 'last_name'),
            'suffix':   ("Jr.", "Sr.", "II", "III", "IV", "V"),
            'title': ("Mr.", "Mrs.", "Ms.", "Miss", "Mx.", "Dr.", "Prof.", "Rev.", "Fr.", "Sir", "Madam", "Hon.", "Capt.", "Col.", "Maj.", "Lt.", "Sgt.", "Judge", "Pres.", "Gov.", "Amb.", "Engr.", "Atty.")
        }

        self.construction = {
            "heavy_equipment": self.get_data_from_json('construction', 'heavy_equipment'),
            "materials":  self.get_data_from_json('construction', 'materials'),
            "roles": self.get_data_from_json('construction', 'roles'),
            "subcontracts": self.get_data_from_json('construction', 'subcontracts'),
            'trades': self.get_data_from_json('construction', 'trades'),
            "building_type": self.get_data_from_json('construction', 'building_type'),
            "material_type": self.get_data_from_json('construction', 'material_type'),
            "tool_type": self.get_data_from_json('construction', 'tool_type'),
        }

        self.departments = {
            'corporate':  self.get_data_from_json('misc', 'corporate'),
            'retail': self.get_data_from_json('misc', 'retail'),
        }

        self.file = {
            "image":  self.get_data_from_json('file', 'image'),
            "audio": self.get_data_from_json('file', 'audio'),
            "video": self.get_data_from_json('file', 'video'),
            "text": self.get_data_from_json('file', 'text'),
            "office": self.get_data_from_json('file', 'office'),
            "archive": self.get_data_from_json('file', 'archive'),
            "executable": self.get_data_from_json('file', 'executable'),
            "data": self.get_data_from_json('file', 'data'),
            "code": self.get_data_from_json('file', 'code'),
            "font": self.get_data_from_json('file', 'font'),
            "system": self.get_data_from_json('file', 'system'),
            "design": self.get_data_from_json('file', 'design'),
            "backup": self.get_data_from_json('file', 'backup'),
        }

        self.it = {
            'domains': self.get_data_from_json('it', 'domains'),
            'mime_types': {
                "application": ("application/atom+xml", "application/ecmascript", "application/EDI-X12", "application/EDIFACT", "application/json", "application/javascript",
                                "application/octet-stream", "application/ogg", "application/pdf", "application/postscript", "application/rdf+xml", "application/rss+xml",
                                "application/soap+xml", "application/font-woff", "application/xhtml+xml", "application/xml-dtd", "application/xop+xml", "application/zip", "application/gzip"),
                "audio": ("audio/basic", "audio/L24", "audio/mp4", "audio/mpeg", "audio/ogg", "audio/vorbis", "audio/vnd.rn-realaudio", "audio/vnd.wave", "audio/webm"),
                "image": ("image/gif", "image/jpeg", "image/pjpeg", "image/png", "image/svg+xml", "image/tiff", "image/vnd.microsoft.icon"),
                "message": ("message/http", "message/imdn+xml", "message/partial", "message/rfc822"),
                "model": ("model/example", "model/iges", "model/mesh", "model/vrml", "model/x3d+binary", "model/x3d+vrml", "model/x3d+xml"),
                "multipart": ("multipart/mixed", "multipart/alternative", "multipart/related", "multipart/form-data", "multipart/signed", "multipart/encrypted"),
                "text": ("text/cmd", "text/css", "text/csv", "text/html", "text/javascript", "text/plain", "text/vcard", "text/xml"),
                "video": ("video/mpeg", "video/mp4", "video/ogg", "video/quicktime", "video/webm", "video/x-matroska", "video/x-ms-wmv", "video/x-flv"),
            },
            'user_agents': self.get_data_from_json('it', 'user_agents'),
            'tlds': (".com", ".org", ".net", ".io", ".co", ".edu", ".gov", ".mil", ".us", ".uk", ".ca", ".au", ".de", ".fr", ".jp", ".sg", ".ph", ".in", ".cn", ".br",
                     ".za", ".es", ".it", ".nl", ".se", ".no", ".ch", ".biz", ".info", ".xyz", ".online", ".site", ".tech", ".store", ".ai", ".app", ".dev", ".cloud", ".me", ".tv"),
            'prefix': ("sk-", "api_", "key-", "ghp_", "tok_", "auth_"),
            'browsers': (("Google Chrome", "130.0.6723.69"),
                         ("Mozilla Firefox", "132.0"),
                         ("Microsoft Edge", "130.0.2849.56"),
                         ("Safari", "18.0"),
                         ("Opera", "105.0.4985.64"),
                         ("Brave", "1.73.113"),
                         ("Vivaldi", "6.7.3329.25"),
                         ("Samsung Internet", "25.0.1.3"),
                         ("UC Browser", "15.1.0.1225"),
                         ("DuckDuckGo Browser", "1.100.2"),
                         ("Tor Browser", "13.0.4"),
                         ("QQ Browser", "15.2.0.0"),
                         ("Yandex Browser", "24.9.1.822"),
                         ("Puffin Browser", "9.10.2.51548"),
                         ("Maxthon", "7.1.8.9000")),
            'cloud_provider': self.get_data_from_json('it', 'cloud_provider'),
            'database_type': self.get_data_from_json('it', 'database_type'),
            'cloud_storage_service': self.get_data_from_json('it', 'cloud_storage_service'),
            'docker_images': self.get_data_from_json('it', 'docker_images'),
            'error_messages': self.get_data_from_json('it', 'error_messages'),
            'file_size_units': ("B", "KB", "MB", "GB", "TB"),
            'font_family': self.get_data_from_json('it', 'font_family'),
            'http_method': ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"),
            'http_standard_code': self.get_data_from_json('it', 'http_standard_code'),
            'iot_device_type': self.get_data_from_json('it', 'iot_device_type'),
            'operating_system': self.get_data_from_json('it', 'operating_system'),
            'port_number': self.get_data_from_json('it', 'port_number'),
            'programming_language': self.get_data_from_json('it', 'programming_language'),
            'security_question': self.get_data_from_json('it', 'security_question'),
            "wifi_ssid": self.get_data_from_json('it', 'wifi_ssid'),
            "app_store_category": self.get_data_from_json('it', 'app_store_category'),
            "cookie_name": self.get_data_from_json('it', 'cookie_name'),
            'css_color': self.get_data_from_json('it', 'css_color'),
            'data_centers': self.get_data_from_json('it', 'data_centers'),
            'dns_record_type': self.get_data_from_json('it', 'dns_record_type'),
            'document_type': self.get_data_from_json('it', 'document_type'),
            'electrical_component': self.get_data_from_json('it', 'electrical_component'),
            'encryption_algorithm': self.get_data_from_json('it', 'encryption_algorithm'),
            'form_factor': self.get_data_from_json('it', 'form_factor'),
            'framework': self.get_data_from_json('it', 'framework'),
            'hardware':  self.get_data_from_json('it', 'hardware'),
            'incident_type': self.get_data_from_json('it', 'incident_type'),
            'keyboard_layout': self.get_data_from_json('it', 'keyboard_layout'),
            'laptop_brand':  self.get_data_from_json('it', 'laptop_brand'),
            'license_type': self.get_data_from_json('it', 'license_type'),
            'memory_size':  self.get_data_from_json('it', 'memory_size'),
            'microservice_name':  self.get_data_from_json('it', 'microservice_name'),
            'network_protocol': self.get_data_from_json('it', 'network_protocol'),
            'notification_type': self.get_data_from_json('it', 'notification_type'),
            'package_manager': self.get_data_from_json('it', 'package_manager'),
            'password_strength': self.get_data_from_json('it', 'password_strength'),
            'permission_level': self.get_data_from_json('it', 'permission_level'),
            'power_source': self.get_data_from_json('it', 'power_source'),
            'printer_type': self.get_data_from_json('it', 'printer_type'),
            'protocol_version': self.get_data_from_json('it', 'protocol_version'),
            'screen_resolution': self.get_data_from_json('it', 'screen_resolution'),
            "screen_size": self.get_data_from_json('it', 'screen_size'),
            "social_media_platform": self.get_data_from_json('it', 'social_media_platform'),
            "software_license": self.get_data_from_json('it', 'software_license'),
            "storage_type": self.get_data_from_json('it', 'storage_type'),
            "subject_line": self.get_data_from_json('it', 'subject_line'),
            "technology_stack": self.get_data_from_json('it', 'technology_stack'),
            "ticket_priority": self.get_data_from_json('it', 'ticket_priority'),
            "uptime_percentage": self.get_data_from_json('it', 'uptime_percentage'),
            "api_endpoint_path": self.get_data_from_json('it', 'api_endpoint_path'),
            "log_level": self.get_data_from_json('it', 'log_level'),
            "server_name": self.get_data_from_json('it', 'server_name'),
            "sensor_type":  self.get_data_from_json('it', 'sensor_type'),
            "device_location":  self.get_data_from_json('it', 'device_location'),
            "power_state":  self.get_data_from_json('it', 'power_state'),
            "smart_device_brand": self.get_data_from_json('it', 'smart_device_brand'),
            "smart_device_type":  self.get_data_from_json('it', 'smart_device_type'),
            "automation_trigger":  self.get_data_from_json('it', 'automation_trigger'),
            "automation_action":  self.get_data_from_json('it', 'automation_action'),
            "energy_mode":  self.get_data_from_json('it', 'energy_mode'),
            "feature_usage_event":  self.get_data_from_json('it', 'feature_usage_event'),
            "subscription_renewal_status": self.get_data_from_json('it', 'subscription_renewal_status'),
            "engagement_level": self.get_data_from_json('it', 'engagement_level'),
        }

        self.personal = {
            'race': self.get_data_from_json('personal', 'race'),
            'gender': {
                'facebook': self.get_data_from_json('personal', 'gender_facebook'),
                'main': ('Male', 'Female', 'Non-binary', 'Genderqueer', 'Genderfluid', 'Bigender', 'Agender'),
                'abbrev': ('M', 'F'),
                'binary': ('Male', 'Female')
            },
            'job':  self.get_data_from_json('misc', 'job'),
            'shirt_sizes': ("XS", "S", "M", "L", "XL", "XXL", "XXXL"),
            'buzzword': self.get_data_from_json('personal', 'buzzword'),
            'nationality': self.get_data_from_json('personal', 'nationality'),
            'quote': self.get_data_from_json('quote', 'quotes'),
            "business_type": self.get_data_from_json('personal', 'business_type'),
            "degree": self.get_data_from_json('personal', 'degree'),
            "education_level": self.get_data_from_json('personal', 'education_level'),
            "employment_status": self.get_data_from_json('personal', 'employment_status'),
            "hobby":  self.get_data_from_json('personal', 'hobby'),
            "industry": self.get_data_from_json('personal', 'industry'),
            "marital_status": self.get_data_from_json('personal', 'marital_status'),
            "military_rank": self.get_data_from_json('personal', 'military_rank'),
            "mood":  self.get_data_from_json('personal', 'mood'),
            "pronoun": self.get_data_from_json('personal', 'pronoun'),
            "religion": self.get_data_from_json('personal', 'religion'),
            "team_name": self.get_data_from_json('personal', 'team_name'),
            "zodiac_sign": self.get_data_from_json('personal', 'zodiac_sign'),
            "age_group": self.get_data_from_json('personal', 'age_group'),
            "conference_name": self.get_data_from_json('personal', 'conference_name'),
            "contract_type":  self.get_data_from_json('personal', 'contract_type'),
            "event_type":  self.get_data_from_json('personal', 'event_type'),
            "hair_color":  self.get_data_from_json('personal', 'hair_color'),
            "income_level":  self.get_data_from_json('personal', 'income_level'),
            "interview_stage": self.get_data_from_json('personal', 'interview_stage'),
            "legal_entity": self.get_data_from_json('personal', 'legal_entity'),
            "life_stage": self.get_data_from_json('personal', 'life_stage'),
            "occupation": self.get_data_from_json('misc', 'job'),
            "organization_type": self.get_data_from_json('personal', 'organization_type'),
            "performance_rating":  self.get_data_from_json('personal', 'performance_rating'),
            "pet_type": self.get_data_from_json('personal', 'pet_type'),
            "political_party": self.get_data_from_json('personal', 'political_party'),
            "project_status":  self.get_data_from_json('personal', 'project_status'),
            "reaction": self.get_data_from_json('personal', 'reaction'),
            "relationship_type": self.get_data_from_json('personal', 'relationship_type'),
            "role": self.get_data_from_json('personal', 'role'),
            "daily_habit": self.get_data_from_json('personal', 'daily_habit'),
            "personality_trait":  self.get_data_from_json('personal', 'personality_trait'),
        }

        self.commerce = {
            "product": {
                "category": self.get_data_from_json('commerce', 'category'),
                "description": self.get_data_from_json('commerce', 'description'),
                "grocery": self.get_data_from_json('commerce', 'grocery'),
                'name': self.get_data_from_json('commerce', 'name'),
                'subcategory': self.get_data_from_json('commerce', 'subcategory'),
            },
            'stock': {
                'industries': self.get_data_from_json('commerce', 'stock_industries'),
                'market': self.get_data_from_json('commerce', 'stock_market')
            },
            'order_status': self.get_data_from_json('commerce', 'order_status'),
            'payment_method': self.get_data_from_json('commerce', 'payment_method'),
            'restaurant_type': self.get_data_from_json('commerce', 'restaurant_type'),
            'review_text': self.get_data_from_json('commerce', 'review_text'),
            'shipping_method': self.get_data_from_json('commerce', 'shipping_method'),
            'subscription_plan': self.get_data_from_json('commerce', 'subscription_plan'),
            'coffee_type': self.get_data_from_json('commerce', 'coffee_type'),
            'delivery_status': self.get_data_from_json('commerce', 'delivery_status'),
            'fabric_type': self.get_data_from_json('commerce', 'fabric_type'),
            'furniture_type': self.get_data_from_json('commerce', 'furniture_type'),
            'gem_stone': self.get_data_from_json('commerce', 'gem_stone'),
            'ingredient': self.get_data_from_json('commerce', 'ingredient'),
            'inventory_status': self.get_data_from_json('commerce', 'inventory_status'),
            'loyalty_tier': self.get_data_from_json('commerce', 'loyalty_tier'),
            'meal_type': self.get_data_from_json('commerce', 'meal_type'),
            'membership_level': self.get_data_from_json('commerce', 'membership_level'),
            'office_supply': self.get_data_from_json('commerce', 'office_supply'),
            'payment_status': self.get_data_from_json('commerce', 'payment_status'),
            'postal_service': self.get_data_from_json('commerce', 'postal_service'),
            'recipe_name': self.get_data_from_json('commerce', 'recipe_name'),
            'sales_channel': self.get_data_from_json('commerce', 'sales_channel'),
            'warranty_period': self.get_data_from_json('commerce', 'warranty_period'),
            'water_type': self.get_data_from_json('commerce', 'water_type'),
            'return_reason': self.get_data_from_json('commerce', 'return_reason'),
            'bundle_type': self.get_data_from_json('commerce', 'bundle_type'),
            "price_sensitivity_level": self.get_data_from_json('commerce', 'price_sensitivity_level'),
            "freight_mode": self.get_data_from_json('commerce', 'freight_mode'),
            "recommendation_slot_position":  self.get_data_from_json('commerce', 'recommendation_slot_position'),
        }

        self.naughty_string = self.get_data_from_json(
            'advanced', 'naughty_string')

        self.street = {
            'suffix': (
                "Alley", "Avenue", "Bridge", "Brook", "Boulevard", "Bypass", "Circle",
                "Court", "Drive", "Expressway", "Freeway", "Highway", "Lane",
                "Parkway", "Place", "Plaza", "Road", "Square", "Street", "Terrace",
                "Trail", "Way", "Walk", "Loop", "Crescent", "Grove", "Heights"
            ),
            'street_formats': ("{{first_name}} {{street_suffix}}", "{{last_name}} {{street_suffix}}",),
            'building_number_formats': ("#####", "####", "###"),
            'address_formats': ("{{street_number}} {{street_name}}",)
        }

        self.health = {
            "blood_type": self.get_data_from_json('health', 'blood_type'),
            "disease_name": self.get_data_from_json('health', 'disease_name'),
            "medication_dosage": self.get_data_from_json('health', 'medication_dosage'),
            "vitamin": self.get_data_from_json('health', 'vitamin'),
            "allergy": self.get_data_from_json('health', 'allergy'),
            "body_part": self.get_data_from_json('health', 'body_part'),
            "chromosome": self.get_data_from_json('health', 'chromosome'),
            "dietary_restriction": self.get_data_from_json('health', 'dietary_restriction'),
            "disability_type": self.get_data_from_json('health', 'disability_type'),
            "emergency_type": self.get_data_from_json('health', 'emergency_type'),
            "exercise_type": self.get_data_from_json('health', 'exercise_type'),
            "health_insurance_plan": self.get_data_from_json('health', 'health_insurance_plan'),
            "hormone":  self.get_data_from_json('health', 'hormone'),
            "hospital_department": self.get_data_from_json('health', 'hospital_department'),
            "lab_test": self.get_data_from_json('health', 'lab_test'),
            "macro_nutrient": self.get_data_from_json('health', 'macro_nutrient'),
            "medical_specialty": self.get_data_from_json('health', 'medical_specialty'),
            "mental_health_condition": self.get_data_from_json('health', 'mental_health_condition'),
            "nutrient": self.get_data_from_json('health', 'nutrient'),
            "organ":  self.get_data_from_json('health', 'organ'),
            "pharmacy_name": self.get_data_from_json('health', 'pharmacy_name'),
            "symptom": self.get_data_from_json('health', 'symptom'),
            "workout_duration": ("15 minutes", "30 minutes", "45 minutes", "90 minutes", "1 hour", "2 hour", "3 Hour"),
            "vaccination_type": self.get_data_from_json('health', 'vaccination_type'),
            "diet_type": self.get_data_from_json('health', 'diet_type'),
            "blood_pressure_category": self.get_data_from_json('health', 'blood_pressure_category'),
            "allergy_flag": self.get_data_from_json('health', 'allergy_flag'),
            "appointment_status": self.get_data_from_json('health', 'appointment_status'),
            "lab_test_type": self.get_data_from_json('health', 'lab_test_type'),
            "triage_level": self.get_data_from_json('health', 'triage_level'),
        }

        self.finance = {
            "loan_type": self.get_data_from_json('finance', 'loan_type'),
            "asset_type": self.get_data_from_json('finance', 'asset_type'),
            "expense_category": self.get_data_from_json('finance', 'expense_category'),
            "grant_type": self.get_data_from_json('finance', 'grant_type'),
            "insurance_type": self.get_data_from_json('finance', 'insurance_type'),
            "investment_strategy": self.get_data_from_json('finance', 'investment_strategy'),
            "payment_term": self.get_data_from_json('finance', 'payment_term'),
            "risk_level": self.get_data_from_json('finance', 'risk_level'),
            "tax_type": self.get_data_from_json('finance', 'tax_type'),
            "transaction_type": self.get_data_from_json('finance', 'transaction_type'),
            "spending_behavior": self.get_data_from_json('finance', 'spending_behavior'),
            "investment_persona": self.get_data_from_json('finance', 'investment_persona'),
            "transaction_pattern": self.get_data_from_json('finance', 'transaction_pattern'),
            "financial_goal": self.get_data_from_json('finance', 'financial_goal'),
            "account_type": self.get_data_from_json('finance', 'account_type'),
            "transfer_channel": self.get_data_from_json('finance', 'transfer_channel'),
            "aml_risk_category": self.get_data_from_json('finance', 'aml_risk_category'),
            "spending_category": self.get_data_from_json('finance', 'spending_category'),
            "savings_goal": self.get_data_from_json('finance', 'savings_goal'),
            "credit_score_band": self.get_data_from_json('finance', 'credit_score_band'),
            "kyc_status": self.get_data_from_json('finance', 'kyc_status'),
            "wealth_segment": self.get_data_from_json('finance', 'wealth_segment'),
        }

        self.cryptocurrency = {
            "wallet": self.get_data_from_json('crypto', 'wallet'),
        }

        self.nature = {
            "planet": self.get_data_from_json('nature', 'planet'),
            "biome": self.get_data_from_json('nature', 'biome'),
            "bird_species": self.get_data_from_json('nature', 'bird_species'),
            "constellation":  self.get_data_from_json('nature', 'constellation'),
            "dog_breed":  self.get_data_from_json('nature', 'dog_breed'),
            "ecosystem":  self.get_data_from_json('nature', 'ecosystem'),
            "element_state": self.get_data_from_json('nature', 'element_state'),
            "energy_source":  self.get_data_from_json('nature', 'energy_source'),
            "environmental_issue":  self.get_data_from_json('nature', 'environmental_issue'),
            "fish_species": self.get_data_from_json('nature', 'fish_species'),
            "flower_type":  self.get_data_from_json('nature', 'flower_type'),
            "insect_species": self.get_data_from_json('nature', 'insect_species'),
            "moon_phase":  self.get_data_from_json('nature', 'moon_phase'),
            "ocean": self.get_data_from_json('nature', 'ocean'),
            "particle":  self.get_data_from_json('nature', 'particle'),
            "precipitation_type":  self.get_data_from_json('nature', 'precipitation_type'),
            "satellite": self.get_data_from_json('nature', 'satellite'),
            "species":  self.get_data_from_json('nature', 'species'),
            "tree_species": self.get_data_from_json('nature', 'tree_species'),
            "wind_direction": self.get_data_from_json('nature', 'wind_direction'),
            "animal_habitat": self.get_data_from_json('nature', 'animal_habitat'),
            "geological_formation": self.get_data_from_json('nature', 'geological_formation'),
            "climate_zone": self.get_data_from_json('nature', 'climate_zone'),
            "natural_resource":  self.get_data_from_json('nature', 'natural_resource'),
            "vegetation_type": self.get_data_from_json('nature', 'vegetation_type'),
            'hazard_risk_zone': self.get_data_from_json('nature', 'hazard_risk_zone'),
            'air_quality_category': self.get_data_from_json('nature', 'air_quality_category'),
        }

        self.travel = {
            "flight_status": self.get_data_from_json('travel', 'flight_status'),
            "room_type": self.get_data_from_json('travel', 'room_type'),
            "amenity": self.get_data_from_json('travel', 'amenity'),
            "bed_size": self.get_data_from_json('travel', 'bed_size'),
            "parking_type": self.get_data_from_json('travel', 'parking_type'),
            "ticket_type": self.get_data_from_json('travel', 'ticket_type'),
            "transport_mode": self.get_data_from_json('travel', 'transport_mode'),
        }
        self.location = {
            "timezone_abbreviation": self.get_data_from_json('location', 'timezone_abbreviation'),
            "compass_direction": self.get_data_from_json('location', 'compass_direction'),
            "continent": self.get_data_from_json('location', 'continent'),
            "facility_type": self.get_data_from_json('location', 'facility_type'),
            "federal_holiday": self.get_data_from_json('location', 'federal_holiday'),
            "floor_number": self.get_data_from_json('location', 'floor_number'),
            "holiday": self.get_data_from_json('location', 'holiday'),
            "home_type": self.get_data_from_json('location', 'home_type'),
            "property_type": self.get_data_from_json('location', 'property_type'),
            "road_type": self.get_data_from_json('location', 'road_type'),
            "venue_type": self.get_data_from_json('location', 'venue_type'),
            "geo_zone": self.get_data_from_json('location', 'venue_type'),
            "street_type": self.get_data_from_json('location', 'street_type'),
            "traffic_flow_level": self.get_data_from_json('location', 'traffic_flow_level'),
            "urban_land_use": self.get_data_from_json('location', 'urban_land_use'),
            "public_service_request_type": self.get_data_from_json('location', 'public_service_request_type'),
        }
        self.car = {
            "vehicle_type":  self.get_data_from_json('car', 'vehicle_type'),
            "engine_type": self.get_data_from_json('car', 'engine_type'),
            "fuel_type": self.get_data_from_json('car', 'fuel_type'),
            "gas_type": self.get_data_from_json('car', 'gas_type'),
            "transmission_type": self.get_data_from_json('car', 'transmission_type'),
        }
        self.products = {
            "podcast_name": self.get_data_from_json('products', 'podcast_name'),
            "streaming_service": self.get_data_from_json('products', 'streaming_service'),
            "award_name": self.get_data_from_json('products', 'award_name'),
            "broadcast_network": self.get_data_from_json('products', 'broadcast_network'),
            "content_rating": self.get_data_from_json('products', 'content_rating'),
            "guitar_type": self.get_data_from_json('products', 'guitar_type'),
            "magazine_title": self.get_data_from_json('products', 'magazine_title'),
            "media_format": self.get_data_from_json('products', 'media_format'),
            "musical_genre": self.get_data_from_json('products', 'musical_genre'),
            "musical_instrument": self.get_data_from_json('products', 'musical_instrument'),
            "news_category": self.get_data_from_json('products', 'news_category'),
            "parental_rating": self.get_data_from_json('products', 'parental_rating'),
            "record_label": self.get_data_from_json('products', 'record_label'),
            "sound_effect": self.get_data_from_json('products', 'sound_effect'),
            "supernatural_creature": self.get_data_from_json('products', 'supernatural_creature'),
            "video_format": self.get_data_from_json('products', 'video_format'),
            "video_quality": self.get_data_from_json('products', 'video_quality'),
            "stock_reorder_flag": self.get_data_from_json('products', 'stock_reorder_flag'),
            "shelf_location": self.get_data_from_json('products', 'shelf_location'),
            "product_grade": self.get_data_from_json('products', 'product_grade'),
            "demand_forecast": self.get_data_from_json('products', 'demand_forecast'),
            "supplier_contract": self.get_data_from_json('products', 'supplier_contract'),
        }
        self.education = {
            "academic_subject": self.get_data_from_json('education', 'academic_subject'),
            "attendance_status": self.get_data_from_json('education', 'attendance_status'),
            "certification": self.get_data_from_json('education', 'certification'),
            "college_major": self.get_data_from_json('education', 'college_major'),
            "elearning_platform": self.get_data_from_json('education', 'e_learning_platform'),
            "qualification": self.get_data_from_json('education', 'qualification'),
            "school_type": self.get_data_from_json('education', 'school_type'),
            "semester": self.get_data_from_json('education', 'semester')
        }
        self.political = {
            'election_type': self.get_data_from_json('political', 'election_Type'),
            "political_ideology": self.get_data_from_json('political', 'political_ideology'),
            "political_party": self.get_data_from_json('political', 'political_party'),
            "party_affiliation_strength": self.get_data_from_json('political', 'party_affiliation_strength'),
            "government_branch": self.get_data_from_json('political', 'government_branch'),
            "head_of_state": self.get_data_from_json('political', 'head_of_state'),
            "head_of_government": self.get_data_from_json('political', 'head_of_government'),
            "cabinet_position": self.get_data_from_json('political', 'cabinet_position'),
            "voter_eligibility": self.get_data_from_json('political', 'voter_eligibility'),
            "campaign_funding_source": self.get_data_from_json('political', 'campaign_funding_source'),
            "lobbying_influence_level": self.get_data_from_json('political', 'lobbying_influence_level'),
            "policy_domain": self.get_data_from_json('political', 'policy_domain'),
            "diplomatic_relationship": self.get_data_from_json('political', 'diplomatic_relationship'),
            "treaty_type": self.get_data_from_json('political', 'treaty_type'),
            "sanction_type": self.get_data_from_json('political', 'sanction_type'),
            "border_control_status": self.get_data_from_json('political', 'border_control_status'),
            "military_alliance": self.get_data_from_json('political', 'military_alliance'),
            "geopolitical_region": self.get_data_from_json('political', 'geopolitical_region'),
        }

        self.gaming = {
            "badge": self.get_data_from_json('gaming', 'badge'),
            "avatar_class": self.get_data_from_json('gaming', 'avatar_class'),
            "skill_level": self.get_data_from_json('gaming', 'skill_level'),
            "match_result": self.get_data_from_json('gaming', 'match_result'),
            "player_role": self.get_data_from_json('gaming', 'player_role'),
            "guild_name": self.get_data_from_json('gaming', 'guild_name'),
            "achievement_title": self.get_data_from_json('gaming', 'achievement_title'),
            "session_outcome": self.get_data_from_json('gaming', 'session_outcome'),
        }
        self.sports = {
            'olympic': self.get_data_from_json('sports', 'olympic'),
            "equipment_type": self.get_data_from_json('sports', 'equipment_type'),
            "league": self.get_data_from_json('sports', 'league'),
            "stadium_name": self.get_data_from_json('sports', 'stadium_name'),
        }

        self.marketing = {
            'campaign_name': self.get_data_from_json('marketing', 'campaign_name'),
            "recommendation_reason": self.get_data_from_json('marketing', 'recommendation_reason'),
            "next_best_action":  self.get_data_from_json('marketing', 'next_best_action'),
            "user_preference_tag": self.get_data_from_json('marketing', 'user_preference_tag'),
            "promotion_type":  self.get_data_from_json('marketing', 'promotion_type'),
            "customer_segment":  self.get_data_from_json('marketing', 'customer_segment'),
            "channel_source":  self.get_data_from_json('marketing', 'channel_source'),
            "conversion_status": self.get_data_from_json('marketing', 'conversion_status'),
            "churn_risk":  self.get_data_from_json('marketing', 'churn_risk'),
            "preferred_communication_channel": self.get_data_from_json('marketing', 'preferred_communication_channel'),
            "recent_search_term":  self.get_data_from_json('marketing', 'recent_search_term'),
            "cart_abandonment_status":  self.get_data_from_json('marketing', 'cart_abandonment_status'),
            "cross_sell_opportunity": self.get_data_from_json('marketing', 'cross_sell_opportunity'),
            "upsell_opportunity": self.get_data_from_json('marketing', 'upsell_opportunity'),
            "sms_response_status": self.get_data_from_json('marketing', 'sms_response_status'),
            "coupon_usage_status": self.get_data_from_json('marketing', 'coupon_usage_status'),
            "referral_source":  self.get_data_from_json('marketing', 'referral_source'),
            "influencer_attribution": self.get_data_from_json('marketing', 'influencer_attribution'),
            "preferred_product_category":  self.get_data_from_json('marketing', 'preferred_product_category'),
            "seasonal_interest":  self.get_data_from_json('marketing', 'seasonal_interest'),
            "price_sensitivity":  self.get_data_from_json('marketing', 'price_sensitivity'),
            "customer_mood_intent": self.get_data_from_json('marketing', 'customer_mood_intent'),
        }
        self.legal = {
            'crime': self.get_data_from_json('legal', 'crime'),
            "law_type": self.get_data_from_json('legal', 'law_type'),
            "court_level": self.get_data_from_json('legal', 'court_level'),
            "legislation_status": self.get_data_from_json('legal', 'legislation_status'),
            "legal_jurisdiction": self.get_data_from_json('legal', 'legal_jurisdiction'),
            "evidence_type": self.get_data_from_json('legal', 'evidence_type'),
            "legal_representation": self.get_data_from_json('legal', 'legal_representation'),
            "verdict": self.get_data_from_json('legal', 'verdict'),
            "penalty_type": self.get_data_from_json('legal', 'penalty_type'),
            "appeal_status": self.get_data_from_json('legal', 'appeal_status'),
            "contract_type": self.get_data_from_json('legal', 'contract_type'),
            "notary_status": self.get_data_from_json('legal', 'notary_status'),
            "legal_compliance_status": self.get_data_from_json('legal', 'legal_compliance_status'),
            "regulatory_agency": self.get_data_from_json('legal', 'regulatory_agency'),
            "legal_filing_type": self.get_data_from_json('legal', 'legal_filing_type'),
            "legal_fee_category": self.get_data_from_json('legal', 'legal_fee_category'),
            "bail_status": self.get_data_from_json('legal', 'bail_status'),
        }

        self.communication = {
            'latency_range': {
                "2G": (150, 1000),
                "2G EDGE": (200, 800),
                "3G": (100, 500),
                "3G HSPA": (80, 400),
                "4G LTE": (20, 100),
                "4G LTE-A": (15, 80),
                "5G": (5, 50),
                "5G NSA": (5, 40),
                "5G SA": (3, 20),
                "Wi-Fi 2.4GHz": (2, 60),
                "Wi-Fi 5GHz": (1, 30),
                "Wi-Fi 6": (1, 15),
                "Satellite": (500, 1500),
                "Satellite LEO": (50, 100),
                "DSL": (10, 100),
                "Fiber": (1, 20),
            },
            "bluetooth_version": self.get_data_from_json('communication', 'bluetooth_version'),
            "upload_speed": self.get_data_from_json('communication', 'upload_speed'),
            "download_speed": self.get_data_from_json('communication', 'download_speed'),
            "sim_card_type": self.get_data_from_json('communication', 'sim_card_type'),
            "mobile_carrier": self.get_data_from_json('communication', 'mobile_carrier'),
            "data_plan": self.get_data_from_json('communication', 'data_plan'),
            "wifi_standard": self.get_data_from_json('communication', 'wifi_standard'),
            "wifi_band": self.get_data_from_json('communication', 'wifi_band'),
            "nfc_support": self.get_data_from_json('communication', 'nfc_support'),
            "hotspot_capability":  self.get_data_from_json('communication', 'hotspot_capability'),
            "roaming_status": self.get_data_from_json('communication', 'roaming_status'),
            "carrier_lock_status": self.get_data_from_json('communication', 'carrier_lock_status'),
            "volte_support": self.get_data_from_json('communication', 'volte_support'),
            "wifi_calling_support": self.get_data_from_json('communication', 'wifi_calling_support'),
            "dual_sim_capability": self.get_data_from_json('communication', 'dual_sim_capability'),
            "apn_settings": self.get_data_from_json('communication', 'apn_settings'),
            "call_quality_rating": self.get_data_from_json('communication', 'call_quality_rating'),
        }

        self.ai = {
            "model_type": self.get_data_from_json('ai', 'model_type'),
            "inference_result": self.get_data_from_json('ai', 'inference_result'),
            "model_deployment_env": self.get_data_from_json('ai', 'model_deployment_env'),
            "model_task": self.get_data_from_json('ai', 'model_task'),
            "model_input_format": self.get_data_from_json('ai', 'model_input_format'),
            "model_output_format": self.get_data_from_json('ai', 'model_output_format'),
            "compute_precision": self.get_data_from_json('ai', 'compute_precision'),
            "model_framework": self.get_data_from_json('ai', 'model_framework'),
            "model_owner": self.get_data_from_json('ai', 'model_owner'),
            "retraining_frequency": self.get_data_from_json('ai', 'retraining_frequency'),
            "concept_drift_status": self.get_data_from_json('ai', 'concept_drift_status'),
            "model_explainability_method": self.get_data_from_json('ai', 'model_explainability_method'),
            "model_training_dataset": self.get_data_from_json('ai', 'model_training_dataset'),
            "model_lifecycle_stage": self.get_data_from_json('ai', 'model_lifecycle_stage'),
        }

    @abstractmethod
    def generate_non_blank(self, row_data: dict | None = None):
        raise NotImplementedError

    def import_datasets(self):
        return {name: DatasetManager.load(name) for name in self.datasets}

    def get_dataset_lookup(self, dataset, key_col):
        datasets = self.import_datasets()
        rows = datasets[dataset]

        return {row[key_col]: row for row in rows if row.get(key_col)}

    def get_row_data_from_datasets(self, dataset, columns):
        if self.data is None:
            datasets = self.import_datasets()
            self.data = tuple({d.get(columns)
                               for d in datasets[dataset] if d.get(columns)})
        return random.choice(self.data)

    def get_data_from_json(self, file_name, dataset):
        data = DatasetManager.load(file_name)
        return tuple(data[dataset])

    def sublify_char(self, symbol: str) -> str:
        if symbol == "#":
            return random.choice(string.digits)
        elif symbol == "@":
            return random.choice(string.ascii_lowercase)
        elif symbol == "^":
            return random.choice(string.ascii_uppercase)
        elif symbol == "*":
            return random.choice(string.ascii_letters + string.digits)
        elif symbol == "$":
            return random.choice(string.ascii_lowercase + string.digits)
        elif symbol == "%":
            return random.choice(string.ascii_uppercase + string.digits)
        else:
            return symbol

    def generate_username(self, row_data: dict | None = None):
        name_mix_gender = self.person['first_name']['female'] + \
            self.person['first_name']['male']
        pattern = random.choice(self.format['username'])

        first_name = None
        last_name = None

        if row_data:
            first_name = row_data.get('first_name')
            last_name = row_data.get('last_name')

        if not first_name:
            first_name = random.choice(name_mix_gender)
        if not last_name:
            last_name = random.choice(self.person['last_name'])

        username = (
            pattern
            .replace("{{first_name}}", first_name)
            .replace("{{last_name}}", last_name)
        )

        return "".join(self.sublify_char(c) for c in username).lower()

    def random_base58(self, length):
        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        return ''.join(random.choice(alphabet) for _ in range(length))

    def encode_base32(self, data: bytes) -> str:
        alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
        num = int.from_bytes(data, "big")
        chars = []
        for _ in range((len(data) * 8 + 4) // 5):
            num, rem = divmod(num, 32)
            chars.append(alphabet[rem])
        return ''.join(reversed(chars))

    def generate_number(self, min: float = 0.0, max: float = 1000):
        return random.uniform(min, max)

    def get_random_data_by_list(self, d):
        return random.choice(d)
