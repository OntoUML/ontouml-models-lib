from enum import Enum

class OntologyDevelopmentContext(Enum):
    CLASSROOM = "Classroom"
    INDUSTRY = "Industry"
    RESEARCH = "Research"

class OntologyRepresentationStyle(Enum):
    ONTOUMLSTYLE = "OntoumlStyle"
    UFOSTYLE = "UfoStyle"

class OntologyPurpose(Enum):
    CONCEPTUALCLARIFICATION = "ConceptualClarification"
    DATAPUBLICATION = "DataPublication"
    DECISIONSUPPORTSYSTEM = "DecisionSupportSystem"
    EXAMPLE = "Example"
    INFORMATIONRETRIEVAL = "InformationRetrieval"
    INTEROPERABILITY = "Interoperability"
    LANGUAGEENGINEERING = "LanguageEngineering"
    LEARNING = "Learning"
    ONTOLOGICALANALYSIS = "OntologicalAnalysis"
    SOFTWAREENGINEERING = "SoftwareEngineering"

class OntologyType(Enum):
    CORE = "Core"
    DOMAIN = "Domain"
    APPLICATION = "Application"
