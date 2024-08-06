from enum import Enum


class OntologyDevelopmentContext(Enum):
    CLASSROOM = "Classroom"
    INDUSTRY = "Industry"
    RESEARCH = "Research"


class OntologyRepresentationStyle(Enum):
    ONTOUML_STYLE = "OntoumlStyle"
    UFO_STYLE = "UfoStyle"


class OntologyPurpose(Enum):
    CONCEPTUAL_CLARIFICATION = "ConceptualClarification"
    DATA_PUBLICATION = "DataPublication"
    DECISION_SUPPORT_SYSTEM = "DecisionSupportSystem"
    EXAMPLE = "Example"
    INFORMATION_RETRIEVAL = "InformationRetrieval"
    INTEROPERABILITY = "Interoperability"
    LANGUAGE_ENGINEERING = "LanguageEngineering"
    LEARNING = "Learning"
    ONTOLOGIC_ALANALYSIS = "OntologicalAnalysis"
    SOFTWARE_ENGINEERING = "SoftwareEngineering"


class OntologyType(Enum):
    CORE = "Core"
    DOMAIN = "Domain"
    APPLICATION = "Application"
