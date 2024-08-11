"""
This module defines enumerations used in the OntoUML/UFO Catalog.

These enumerations classify and filter ontology models based on their development context, representation style,
purpose, and type. The enumerations align with the metadata schema specification used in the catalog.

Enumerations:
-------------
- `OntologyDevelopmentContext`: Represents the contexts in which ontologies are developed.
- `OntologyRepresentationStyle`: Represents the styles of ontology representation.
- `OntologyPurpose`: Represents the purposes for which ontologies are created.
- `OntologyType`: Represents the types of ontologies based on their scope and application.
"""


from enum import Enum


class OntologyDevelopmentContext(Enum):
    """
    Represents the different contexts in which ontologies are developed.

    :cvar CLASSROOM: Indicates that the ontology was developed within an educational setting, such as a classroom.
    :cvar INDUSTRY: Indicates that the ontology was developed for or within an industrial or corporate context.
    :cvar RESEARCH: Indicates that the ontology was developed as part of a research project, often associated with
                    academic publications.

    These contexts categorize ontologies based on their origin, whether they are created in educational, industrial,
    or research environments.
    """
    CLASSROOM = "Classroom"
    INDUSTRY = "Industry"
    RESEARCH = "Research"



class OntologyRepresentationStyle(Enum):
    """
    Represents the styles of ontology representation.

    :cvar ONTOUML_STYLE: Characterizes a model that contains at least one class, relation, or property using a valid
                         OntoUML stereotype.
    :cvar UFO_STYLE: Characterizes a model that contains at least one class or relation from UFO (Unified Foundational
                     Ontology) without an OntoUML stereotype.

    These representation styles classify ontologies based on whether they adhere to OntoUML stereotypes or use
    foundational ontology elements from UFO.
    """
    ONTOUML_STYLE = "OntoumlStyle"
    UFO_STYLE = "UfoStyle"


class OntologyPurpose(Enum):
    """
    Represents the purposes for which ontologies are created.

    :cvar CONCEPTUAL_CLARIFICATION: Created to clarify and untangle complex notions and relations through ontological
                                    analysis.
    :cvar DATA_PUBLICATION: Created to support data publication, such as generating an OWL vocabulary to publish data
                            as linked open data.
    :cvar DECISION_SUPPORT_SYSTEM: Created during the development of a decision support system.
    :cvar EXAMPLE: Created to demonstrate OntoUML's application, support an experiment, or exemplify model reuse in
                   specific scenarios.
    :cvar INFORMATION_RETRIEVAL: Created to support the design of an information retrieval system.
    :cvar INTEROPERABILITY: Created to support data integration, vocabulary alignment, or interoperability between
                            software systems.
    :cvar LANGUAGE_ENGINEERING: Created for the design of a domain-specific modeling language.
    :cvar LEARNING: Created by authors to learn UFO and OntoUML, often as part of a course assignment.
    :cvar ONTOLOGIC_ANALYSIS: Created as part of a broader ontological analysis.
    :cvar SOFTWARE_ENGINEERING: Created during the development of an information system, such as generating a
                                relational database schema.

    These purposes categorize ontologies based on their intended use, from data publication to software engineering
    and conceptual analysis.
    """
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
    """
    Represents the types of ontologies based on their scope and application.

    :cvar CORE: An ontology that grasps central concepts and relations of a given domain, often integrating several
                domain ontologies and being applicable in multiple scenarios.
    :cvar DOMAIN: An ontology that describes how a community conceptualizes a phenomenon of interest, typically
                  narrower in scope than a core ontology.
    :cvar APPLICATION: An ontology that specializes a domain ontology for a particular application, representing a model
                       of a domain according to a specific viewpoint.

    These types classify ontologies based on their scope, from core ontologies applicable in multiple domains to
    specialized application ontologies.
    """
    CORE = "Core"
    DOMAIN = "Domain"
    APPLICATION = "Application"
