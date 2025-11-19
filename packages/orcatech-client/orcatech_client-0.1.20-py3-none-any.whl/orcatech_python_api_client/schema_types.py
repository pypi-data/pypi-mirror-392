from orcatech_python_api_client.config import APIID

# from custom_types.types import Duration
from .schemas import SSOProtocol, GraphRelationship
from typing import List, Dict, Literal, Optional, TypedDict, Union
from dataclasses import dataclass
from datetime import datetime


class Duration(TypedDict):
    months: int
    days: int
    milliseconds: int


"""An Authentication Provider Record from the public endpoint"""


@dataclass
class AuthenticationProviderRecord:

    # The id of the provider record

    id: Optional[APIID]

    # The name of the provider

    name: str

    # The supported authentication protocol

    protocol: SSOProtocol  # type: ignore


"""The status of the SSO session as a record"""


@dataclass
class IdentificationCheckRecord:

    # The number of seconds until the session expires

    maxAge: int

    # If true, indicates that the user needs to setup MFA

    requiresMultiFacterAuth: bool

    # If true, indicates that the user needs to supply a new password

    requiresNewPassword: bool

    # The AuthenticationProviderRecord ID for the Password Authentication Provider

    passwordProviderID: APIID


"""The methods that can be used by the identified user to satisfy the MFA requirement"""


@dataclass
class MFACheckRecord:

    # True is the user has MFA setup with WebAuthN, false otherwise

    hasRegisteredWebAuthn: bool

    # Map of pin code mediums to their enabled value

    canSendPin: Dict[str, bool]

    # True is the user has already satisfied the MFA requirement

    authenticated: bool


# A data structure contain the type and version information for a data schema
# @version 0.0.1


SchemaRecord = {
    # The name of the schema
    "name": str,
    # The major version
    "major": int,
    # The major version
    "minor": int,
    # The release version
    "release": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Vendor specific testing data
# @version 0.0.1

# Set of available observation data schemas in the API
ObservationDataSchemaType = Literal[
    "com.orcatech.alert.incident",
    "com.orcatech.event",
    "com.orcatech.measure.access.period",
    "com.orcatech.measure.access.request",
    "com.orcatech.measure.activity.physical.period",
    "com.orcatech.measure.application.user.period",
    "com.orcatech.measure.battery",
    "com.orcatech.measure.bed.activity",
    "com.orcatech.measure.bed.awake.period",
    "com.orcatech.measure.bed.exit.period",
    "com.orcatech.measure.body.weight",
    "com.orcatech.measure.checkin",
    "com.orcatech.measure.contact",
    "com.orcatech.measure.coordinate",
    "com.orcatech.measure.heart.rate",
    "com.orcatech.measure.heart.rate.period",
    "com.orcatech.measure.heart.rate.variability.period",
    "com.orcatech.measure.heart.rate.variability.rmssd",
    "com.orcatech.measure.pillbox.state",
    "com.orcatech.measure.presence",
    "com.orcatech.measure.respiration.rate",
    "com.orcatech.measure.respiration.rate.period",
    "com.orcatech.measure.sleep.movement.fast",
    "com.orcatech.measure.sleep.movement.fast.period",
    "com.orcatech.measure.sleep.movement.period",
    "com.orcatech.measure.sleep.period",
    "com.orcatech.measure.sleep.score.period",
    "com.orcatech.measure.sleep.state.period",
    "com.orcatech.measure.step.period",
    "com.orcatech.measure.swim.period",
    "com.orcatech.measure.trip",
    "com.orcatech.measure.vehicle.event",
    "com.orcatech.measure.vehicle.mil",
    "com.orcatech.measure.vehicle.state",
    "com.orcatech.measure.web.search",
    "com.orcatech.report.life.event",
    "com.orcatech.survey.event",
    "com.orcatech.survey.event.error",
    "com.orcatech.survey.form",
    "com.orcatech.survey.input",
    "com.orcatech.survey.response",
    "com.orcatech.test.neuropsych.imagerecog",
    "com.orcatech.test.neuropsych.stroop",
    "com.orcatech.test.neuropsych.trails",
]
# Microservices that are performed on sensor as data comes in.
# @version 0.0.1


MicroserviceRecord = {
    # The name of the microservice
    "name": str,
    # Version number of microservice
    "version": str,
    # Description of what the microservice does and what information it changes.
    "description": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A change history of the observation.
# @version 0.0.1


MicroserviceChangeRecord = {
    # The time at which the change was made by the microservice
    "stamp": datetime,
    # The microservice that made the change
    "microservice": MicroserviceRecord,
    # True if the change is a creation
    "created": bool,
    # True if the change is an update
    "updated": bool,
    # True if the change is a deletion
    "deleted": bool,
    # Map of meta fields that were changed with the key being the field name and the value being the previous value of the field in json
    "metaFields": Dict[str, str],
    # Map of meta fields that were changed with the key being the field name and the value being the previous value of the field in json
    "dataFields": Dict[str, str],
    # Lookup id number for user
    "userID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

ObservationGenericRecord = {
    # This is not an identifier from a database but a concatenated list of fields that uniquely identify the data
    "uuid": str,
    # The timestamp at which the observation takes place. Most databases only support millisecond precisions, see Cassandra, so use the common denominator.
    "stamp": datetime,
    # The partition bucket that the observation is stored in
    "bucket": str,
    # The schema and version of the data field
    "dataSchema": SchemaRecord,
    # The schema and version of the meta field
    "metaSchema": SchemaRecord,
    # The schema and version of the changes field items
    "changesSchema": SchemaRecord,
    # The time series data in generic specific format
    "data": ObservationDataSchemaType,
    # The time series meta data about the generic specific format
    "meta": ObservationDataSchemaType,
    # List of changes made to the observation.
    "changes": [MicroserviceChangeRecord],
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id number for study
    "studyID": APIID,
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id number for home
    "homeID": APIID,
    # Lookup id number for item
    "itemID": APIID,
    # Lookup id number for hubItem
    "hubItemID": APIID,
    # Lookup id number for user
    "userID": APIID,
    # Lookup id number for survey
    "surveyID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The type of alert
# @version 0.0.1


AlertIncidentRecord = {
    # The source of the alert
    "source": ObservationGenericRecord,
    # A unique key for the alert to allow it to be automatically resolved
    "key": str,
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for status
    "statusID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# how a user/role wants to be notified for an alert
# @version 0.0.1


AlertNotificationGroupRecord = {
    # The  unique identifier
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for roles
    "roleIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for users
    "userIDs": [APIID],
    # Lookup id number for notificationType
    "notificationTypeID": APIID,
    # Lookup id number for alertType
    "alertTypeID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A record of notifications issued
# @version 0.0.1


AlertNotificationSentRecord = {
    # The alert incident that triggered that notification
    "alertIncident": AlertIncidentRecord,
    # Lookup id numbers for users
    "userIDs": [APIID],
    # Lookup id number for type
    "typeID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Type definition of an alert notification
# @version 0.0.1


AlertNotificationTypeRecord = {
    # The unique identifier
    "id": APIID,
    # A short descriptive name for the type. eg 'email', 'sms', 'im'
    "name": str,
    # Detailed information about the notification type
    "description": str,
    # Notifications with this type
    "notifications": [AlertNotificationSentRecord],
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # user text to publish with alert
    "userText": str,
    # email address or phone # (sms)
    "destinationAddress": str,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for groups
    "groupIDs": [APIID],
    # Lookup id number for credentials
    "credentialsID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The state of a given alert
# @version 0.0.1


AlertStatusRecord = {
    # The  unique identifier
    "id": APIID,
    # A short name for the alert state type
    "name": str,
    # A longer description of the alert state type
    "description": str,
    #
    "alertIncidents": [AlertIncidentRecord],
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The type of alert
# @version 0.0.1


AlertTypeRecord = {
    # The  unique identifier
    "id": APIID,
    # A short name for the alert type
    "name": str,
    # A longer description of the alert type
    "description": str,
    #
    "alertIncidents": [AlertIncidentRecord],
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for notificationGroups
    "notificationGroupIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# A pair of two sensors that compose a segment within a sensor line
# @version 0.0.1


AlgorithmsLineCalibrationSegmentRecord = {
    # Order number for the current sensor pair. I.e. 0 is the first pair, 1 is the second pair, etc
    "order": int,
    # A unique id representing the item (i.e. first sensor in the pair) in the  database
    "firstSensor": int,
    # A unique id representing the item (i.e. second sensor in the pair) in the  database
    "secondSensor": int,
    # Distance between the two sensors measured in centimeters
    "distance": int,
    # True if the distance is null and was assumed to be 2 feet, false if the distance was measured and entered
    "assumed": bool,
    # Average time differential (in seconds) between the firings of the firstSensor and the secondSensor
    "deltaX": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Parameters used to create the model used for determining which walking speeds are valid (i.e. the walks used to calculate the calibration parameters deltaX and C)
# @version 0.0.1


AlgorithmsLineCalibrationParametersRecord = {
    # Only take walks with residuals less than this cutoff (which is unitless)
    "residualCutoff": int,
    # Number of nearest neighbor residuals used when calculating the standard deviations
    "nearestNeighbor": int,
    # Fraction of nearest neighbor residuals to trim when calculating the standard deviations
    "nearestNeighborTrim": int,
    # Minimum walking speed (in cm/s) allowed when creating the model (below this people start shuffling)
    "modelSpeedMin": int,
    # Maximum walking speed (in cm/s) allowed when creating the model
    "modelSpeedMax": int,
    # Minimum number of walking speed estimates needed to create a model
    "minFitPoints": int,
    # Number of restarts used when finding the optimized model parameters
    "numberModelStarts": int,
    # Multiple (unitless) of standard deviation allowed for residual error
    "k": int,
    # Maximum number of candidate walks used for generating the model to determine which candidates are valid walks.  If set to '0', all possible candidate walks were used.
    "maxModelWalks": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Calibration parameters (i.e. deltax and C) for each sensor line
# @version 0.0.1


AlgorithmsLineCalibrationRecord = {
    # A unique id representing the home in the  database
    "homeID": int,
    # Numerically sequenced firings through the sensor line (i.e. 1234 or 4321)
    "type": int,
    # Indicates the direction of the pass where 0 is 'forward' and 1 is 'backward' so that 1234 would be 'forward'.
    "direction": int,
    # Series of com.orcatech.sensor.line.segment objects that contain the deltaX calibration parameter
    "segments": [AlgorithmsLineCalibrationSegmentRecord],
    # Calibration parameter (in cm/s) that is the speed a person would have to walk in order for the sensors to register time differences equal to the average time differences calculated from the traning data set
    "c": int,
    # Number of days that the walks were taken from to calculate the calibration parameters deltaX and C
    "numberDays": int,
    # Number of walks used to calculate the calibration parameters deltaX and C
    "numberWalks": int,
    # Number of walks used to create the model used for determining which walking speeds are valid (i.e. the walks used to calculate the calibration parameters deltaX and C)
    "numberSpeeds": int,
    # Type of threshold used for generating the calibration parameters deltaX and C (0 -> DAYS |1-> NUMBER OF CANDIDATE WALKS)
    "thresholdType": int,
    # Threshold for the number of walks used or the number of days that the walks were taken from to calculate the calibration parameters deltaX and C
    "threshold": int,
    # Multiplicative factor used in walking speed calculation empirically determined using data from a GAIT mat
    "rho": int,
    # Set of parameters used to create the model used for determining which walking speeds are valid (i.e. the walks used to calculate the calibration parameters deltaX and C)
    "parameters": AlgorithmsLineCalibrationParametersRecord,
    # Lookup id number for line
    "lineID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


# Room transitions derived from sequential sensor fires from different rooms. The transition algorithm does not check that the rooms are adjacent.
# @version 0.0.1


AlgorithmsTransitionsRecord = {
    # Home ID of the event
    "homeID": int,
    # Unix timestamp of the event in seconds
    "stamp": datetime,
    # Sensor Placement area ID of the itemStart sensor
    "areaStart": int,
    # Sensor Placement area ID of the itemEnd sensor
    "areaEnd": int,
    # Inventory item ID of transition start sensor
    "itemStart": int,
    # Inventory item ID of transition end sensor
    "itemEnd": int,
    # Inventory model ID of transition of the itemStart sensor
    "itemModelStart": int,
    # Inventory model ID of transition of the itemEnd sensor
    "itemModelEnd": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Sequential sensor firings of a com.orcatech.sensor.line.segment
# @version 0.0.1


AlgorithmsWalkSegmentRecord = {
    # Order number for the current sensor pair
    "order": int,
    # A unique id representing the item (i.e. first sensor in the pair) in the  Inventory database
    "firstSensor": int,
    # A unique id representing the item (i.e. second sensor in the pair) in the  Inventory database
    "secondSensor": int,
    # Time differential between the firings of each sensor in seconds
    "duration": int,
    # True if the distance is null and was assumed to be 2 feet, false if the distance was measured and entere
    "assumed": bool,
    # Distance between the sensors in centimeters
    "distance": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Sequential sensor line firings which represent a candidate for a walk
# @version 0.0.1


AlgorithmsWalkCandidateRecord = {
    # Numerically sequenced firings through the sensor line (i.e. 1234 or 4321)
    "type": int,
    # A unix timestamp in seconds indicating the time at which the pass occurred
    "stamp": datetime,
    # Indicates the direction of the pass where 0 is 'forward' and 1 is 'backward' so that 1234 would be 'forward'.
    "direction": int,
    # Series of com.orcatech.sensor.line.segment firings that compose the walk candidate
    "segments": [AlgorithmsWalkSegmentRecord],
    # How long it took for the subject to walk through the walkCandidate.type in seconds
    "duration": int,
    # Distance between the first and last sensor of the walkCandidate.type in centimeters
    "distance": int,
    # Speed at which the subject walked through the walkCandidate.type in cm/s
    "speed": int,
    # Lookup id number for line
    "lineID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Calibration parameters (i.e. deltaX and C) used to calculate walkingSpeed.speed and metadata about the estimation of the calibration parameters
# @version 0.0.1


AlgorithmsWalkingSpeedCalibrationRecord = {
    # Calibration parameter (in cm/s) that is the speed a person would have to walk in order for the sensors to register time differences equal to the average time differences calculated from the traning data set
    "c": int,
    # Number of days that the walks were taken from to calculate the calibration parameters deltaX and C
    "numberDays": int,
    # Number of walks used to calculate the calibration parameters deltaX and C
    "numberWalks": int,
    # Type of threshold used for generating the calibration parameters deltaX and C (0 -> DAYS |1-> NUMBER OF CANDIDATE WALKS)
    "thresholdType": int,
    # Threshold for the number of walks used or the number of days that the walks were taken from to calculate the calibration parameters deltaX and C
    "threshold": int,
    # Series of com.orcatech.sensor.line.segment objects that contain the deltaX calibration parameter
    "segments": [AlgorithmsLineCalibrationSegmentRecord],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Parameters used calculate walkingSpeed.speed and to create the model used for determining which walkingSpeed.speed are valid
# @version 0.0.1


AlgorithmsWalkingSpeedParametersRecord = {
    # Only take walks with residuals less than this cutoff (which is unitless)
    "residualCutoff": int,
    # Number of nearest neighbor residuals used when calculating the standard deviations
    "nearestNeighbor": int,
    # Fraction of nearest neighbor residuals to trim when calculating the standard deviations
    "nearestNeighborTrim": int,
    # Minimum walking speed (in cm/s) allowed when creating the model (below this people start shuffling)
    "modelSpeedMin": int,
    # Maximum walking speed (in cm/s) allowed when creating the model
    "modelSpeedMax": int,
    # Minimum number of walking speed estimates needed to create a model
    "minFitPoints": int,
    # Number of restarts used when finding the optimized model parameters
    "numberModelStarts": int,
    # Multiple (unitless) of standard deviations allowed for residual error
    "k": int,
    # Multiplicative factor used in walking speed calculation empirically determined using data from a GAIT mat
    "rho": int,
    # Number of walks used to create the model used for determining which walking speeds are valid
    "numberSpeeds": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Estimated walking speeds calculated from the walking speed algorithm
# @version 0.0.1


AlgorithmsWalkingSpeedRecord = {
    # A unique id representing the home in the  database
    "homeID": int,
    # A unique id from the  database representing the area in which the sensor line is monitoring
    "areaID": int,
    # Numerically sequenced firings through the sensor line (i.e. 1234 or 4321)
    "type": int,
    # Indicates the direction of the pass where 0 is 'forward' and 1 is 'backward' so that 1234 would be 'forward'.
    "direction": int,
    # A unix timestamp in seconds indicating the time at which the walkingSpeed.speed pass occurred
    "stamp": int,
    # Speed at which the subject walked through the walkingSpeed.type in cm/s
    "speed": int,
    # Calibration parameters (i.e. deltaX and C) used to calculate walkingSpeed.speed and metadata about the estimation of the calibration parameters
    "calibration": AlgorithmsWalkingSpeedCalibrationRecord,
    # Parameters used calculate walkingSpeed.speed and to create the model used for determining which walkingSpeed.speed are valid
    "parameters": AlgorithmsWalkingSpeedParametersRecord,
    # Series of com.orcatech.sensor.line.segment firings that compose the walk candidate
    "segments": AlgorithmsWalkSegmentRecord,
    # Lookup id number for line
    "lineID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


# A generic animal to be tracked.
# @version 0.0.1


AnimalRecord = {
    # The unique identifier
    "id": APIID,
    # A short descriptive name of the animal
    "name": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # Lookup id numbers for homes
    "homeIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A tag used to categorize a set of animals
# @version 0.0.1


AnimalTagRecord = {
    # The unique identifier
    "id": APIID,
    # A unique name for the tag
    "name": str,
    # A longer description of the tag
    "description": str,
    # A hexidecimal representation of a color for this tag
    "color": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for animals
    "animalIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A type of animal that can be tracked.
# @version 0.0.1


AnimalTypeRecord = {
    # A short descriptive name of the animal type
    "name": str,
    # The unique identifier
    "id": APIID,
    # A description of the animal type
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for animals
    "animalIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An web application within the  system.
# @version 0.0.1


AppRecord = {
    # The URI to the application
    "host": str,
    # The  unique identifier
    "id": APIID,
    # A short descriptive name of the application
    "name": str,
    # A full description of the application and what it does.
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for roles
    "roleIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A generic area such as a living room, bedroom, bathroom, toilet, top drawer, etc
# @version 0.0.1


AreaRecord = {
    # Unique identifier for the area.
    "id": APIID,
    # Descriptive name of the area
    "name": str,
    # Extended description of area
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # Lookup id numbers for adjacentAreas
    "adjacentAreaIDs": [APIID],
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for line
    "lineID": APIID,
    # Lookup id number for dwelling
    "dwellingID": APIID,
    # Lookup id numbers for items
    "itemIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A category of area such a chair, toilet, bed, room, etc
# @version 0.0.1


AreaCategoryRecord = {
    # Descriptive name of the area category
    "name": str,
    # Unique identifier for the area category.
    "id": APIID,
    # Extended description of area category
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for types
    "typeIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A tag used to categorize a set of area
# @version 0.0.1


AreaTagRecord = {
    # A unique name for the tag
    "name": str,
    # The unique identifier
    "id": APIID,
    # A longer description of the tag
    "description": str,
    # A hexidecimal representation of a color for this tag
    "color": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for areas
    "areaIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A type of area such a chair, toilet, bed, room, etc
# @version 0.0.1


AreaTypeRecord = {
    # Descriptive name of the area type
    "name": str,
    # Unique identifier for the area type.
    "id": APIID,
    # Extended description of area type
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id number for category
    "categoryID": APIID,
    # Lookup id numbers for areas
    "areaIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Location as an address
# @version 0.0.1


AutomaticAddressRecord = {
    # Name of the location
    "name": str,
    # Nickname of the location
    "displayName": str,
    # Street number of the location
    "streetName": str,
    # Street number of the location
    "streetNumber": str,
    # Long name of city
    "city": str,
    # Abbreviated name of state
    "state": str,
    # Abbreviated name of country
    "country": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Credentials for accessing automatic data
# @version 0.0.1


AutomaticCredentialsRecord = {
    # Access token
    "token": str,
    # Refresh token for generating a new access token
    "refresh": str,
    # Estimated time when the token will expire
    "expiration": datetime,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Location as a set of geocoordinates
# @version 0.0.1


AutomaticLocationRecord = {
    # Latitude coordinate of the location
    "lat": int,
    # Longitude coordinate of the location
    "lng": int,
    # Accuracy of the location in meters
    "accuracy": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Vehicle malfunction indicator light
# @version 0.0.1


AutomaticVehicleMilRecord = {
    # Malfunction indicator lamp code [scope:vehicle:profile]
    "code": str,
    # Indicates if the light is on [scope:vehicle:profile]
    "on": bool,
    # Time of the event [scope:vehicle:profile]
    "createdAt": datetime,
    #  Human readable description of the mil [scope:vehicle:profile]
    "description": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Information about the vehicle the sensor is plugged into
# @version 0.0.1


AutomaticVehicleRecord = {
    # Unique identifier for the vehicle given by Automatic
    "id": APIID,
    # Vehicle Identification number
    "vin": str,
    # CreatedAt [scope:public scope:vehicle:profile]
    "createdAt": datetime,
    # UpdatedAt [scope:public scope:vehicle:profile]
    "updatedAt": datetime,
    # Make (Honda, Chevy, etc.,)
    "make": str,
    # Model (Civic, F150, etc.,)
    "model": str,
    # Submodel (EX, Deluxe, etc.,)
    "submodel": str,
    # Year [scope:public, scope:vehicle:profile]
    "year": int,
    # Nickname given by the user
    "displayName": str,
    # Detected battery voltage
    "batteryVoltage": int,
    # Fuel level percent is not available on all cars
    "fuelLevelPercent": int,
    # Currently active malfunction indicator lights
    "activeDTCs": [AutomaticVehicleMilRecord],
    # username each vehicle is connected to.
    "userAccount": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# A vehicle event measured by the automatic sensor
# @version 0.0.1


AutomaticVehicleEventRecord = {
    # The type of event that occured
    "type": str,
    # Latitude coordinate of the location
    "lat": int,
    # Longitude coordinate of the location
    "lng": int,
    # The g force felt during the event
    "gForce": int,
    # The time in which the event occured
    "createdAt": datetime,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Trip A trip is created when a vehicle is understood to have one full cycle of ignition:on to ignition:off. In some vehicles, these signals must be inferred. Trips are the most commonly used objects in the API. They contain a wealth of metadata about a vehicle's usage history and a user's behavior. At present, one write is possible: adding a tag to a trip. The mobile apps have a feature that allows combining of trips that happened within 15 minutes of each other. This merge is applied on the apps' frontend only and does not affect the REST objects, which would show the multiple 'segments' as distinct and unrelated entities. Trips must have a minimum distance of 10 meters or they will be discarded as invalid. In the United States, fuel price is retrieved automatically based on location at the time of fillup. If a car does not report its fuel level, then each trip's cost will be estimated using prevailing local prices. Outside the United States, our fuel costing will currently provide unreliable results. This will be improved in the future. For the time being, it is recommended to use fuel volume as the reliable metric instead.
# @version 0.0.1


AutomaticTripRecord = {
    # Unique identifier for the trip given by Automatic
    "id": APIID,
    # Vehicle used on trip
    "vehicle": AutomaticVehicleRecord,
    # Started At [scope:trip] in UTC
    "startedAt": datetime,
    # Ended At [scope:trip] in UTC
    "endedAt": datetime,
    # Distance of the trip in meters
    "distance": int,
    # Duration of the trip in seconds
    "duration": int,
    # Starting location of the trip
    "startLoc": AutomaticLocationRecord,
    # Ending location of the trip
    "endLoc": AutomaticLocationRecord,
    # Starting address of the trip
    "startAddr": AutomaticAddressRecord,
    # Ending address of the trip
    "endAddr": AutomaticAddressRecord,
    # Encoded path data of the trip
    "path": str,
    # Fuel cost in dollars
    "fuelCost": int,
    # Amount of fuel used in meters cubed
    "fuelVol": int,
    # Fuel efficiency in km per liter
    "avgKMpL": int,
    # Fuel efficiency in km per liter according to the EPA
    "avgFromEPAKMpL": int,
    # Driving score for events
    "scoreEvents": int,
    # Driving score for speeding
    "scoreSpeeding": int,
    # Number of hard brakes
    "hardBrakes": int,
    #  Number of hard accelerations
    "hardAccels": int,
    # Duration of trip spend over 70 mph in seconds
    "durOver70": int,
    # Duration of trip spend over 75 mph in seconds
    "durOver75": int,
    # Duration of trip spend over 80 mph in seconds
    "durOver80": int,
    # Duration of trip spent idling in seconds
    "idlingTime": int,
    # Vehicle events that occured during trip
    "vehicleEvents": [AutomaticVehicleEventRecord],
    # Timezone at the start of the trip
    "timezoneStart": str,
    # Timezone at the end of the trip
    "timezoneEnd": str,
    # Fraction of time spent in the city
    "cityFraction": int,
    # Fraction of time spent on the highway
    "highwayFraction": int,
    # Fraction of time spent driving at night
    "nightDrivingFraction": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Tag used for grouping of trips
# @version 0.0.1


AutomaticTripTagRecord = {
    # [scope: trip]
    "tag": str,
    # Date when the trip was tagged [scope:trip]
    "createdAt": datetime,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# User is the object representing an Automatic account holder. In practice this represents an owner or driver of a vehicle. A user may have many vehicles (and a vehicle may have many users).
# @version 0.0.1


AutomaticUserRecord = {
    # User URI
    "url": str,
    # Unique identifier for the user given by Automatic
    "id": APIID,
    # [scope:public scope:user:profile]
    "userName": str,
    # User's first name [scope:public scope:user:profile]
    "firstName": str,
    # User's last name [scope:public scope:user:profile]
    "lastName": str,
    # User's email address [scope:public scope:user:profile]
    "email": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Additional information about the user / phone
# @version 0.0.1


AutomaticUserMetadataRecord = {
    # User metadata URI
    "url": str,
    # User URI
    "userURL": str,
    # The firmware version of ???
    "firmwareVersion": str,
    # The Automatic App version on the phone used for setup
    "appVersion": str,
    # The OS version of the phone used for setup
    "osVersion": str,
    # Device type of ???
    "deviceType": str,
    # The platform of the phone used for setup
    "phonePlatform": str,
    # Latest app version installed [scope:user:profile]
    "isLastestAppVersion": bool,
    # True if the user an Automatic staff user [scope:user:profile]
    "isStaff": bool,
    # List of clients that this user has authorized through OAuth [scope:user:profile]
    "authenticatedClients": [str],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Information about the vehicle the sensor is plugged into
# @version 0.0.1


AutomaticUserProfileRecord = {
    # User profile URI
    "url": str,
    # User URI
    "userURL": str,
    # The date the user was created
    "dateJoined": datetime,
    # Tagged locations (i.e. home/work)
    "taggedLocations": [AutomaticAddressRecord],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


# Credentials for encrypting and decrypting data sent by Beiwe clients
# @version 0.0.1


BeiweCredentialRecord = {
    # A public client key for encrypting data
    "publicKey": str,
    # A private client key for decrypting data
    "privateKey": str,
    # The  unique identifier
    "id": APIID,
    # A password used for registering the user on a device
    "temporaryPassword": str,
    # A password used for authenticating the user on a device
    "password": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id number for study
    "studyID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Accelerometer data collected by the Beiwe app for android and ios devices
# @version 0.0.1


BeiweDeviceAccelerometerRecord = {
    # The time of the observation
    "stamp": datetime,
    # The device reported accuracy
    "accuracy": str,
    # The acceleration in the X direction
    "x": int,
    # The acceleration in the Y direction
    "y": int,
    # The acceleration in the Z direction
    "z": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The observed app usage of a device with the Beiwe app installed for Android devices
# @version 0.0.1


BeiweDeviceAppUsageRecord = {
    # The time of the observation
    "stamp": datetime,
    # The label of the app
    "appLabel": str,
    # The package name of the app
    "appPackageName": str,
    # The last time the app was used
    "lastTimeUsed": datetime,
    # The last time the app was visible in the UI
    "lastTimeVisible": datetime,
    # The total time the app was in the foreground in milliseconds
    "totalTimeInForeground": str,
    # The total time the app was visible in the UI in milliseconds
    "totalTimeVisible": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Bluetooth device observation collected by the Beiwe app for android devices
# @version 0.0.1


BeiweDeviceBluetoothRecord = {
    # The time of the observation
    "stamp": datetime,
    # The bluetooth address detected
    "macaddressHash": str,
    # The reported signal strength
    "rssi": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A call made or received by a device collected with the Beiwe app installed
# @version 0.0.1


BeiweDeviceCallRecord = {
    # The time of the observation
    "stamp": datetime,
    # A hashed phone number that was called from the device or called into the device
    "phoneNumberHash": str,
    # The type of the phone call
    "type": str,
    # The duration of the phone call
    "duration": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# GPS coordinates observed by a device observation with the Beiwe app installed
# @version 0.0.1


BeiweDeviceGpsRecord = {
    # The time of the observation
    "stamp": datetime,
    # TODO
    "latitude": int,
    # TODO
    "longitude": int,
    # TODO
    "altitude": int,
    # TODO
    "accuracy": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Gyroscope data collected by the Beiwe app for android and ios devices
# @version 0.0.1


BeiweDeviceGyroscopeRecord = {
    # The time of the observation
    "stamp": datetime,
    # TODO
    "x": int,
    # TODO
    "y": int,
    # TODO
    "z": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A log made by an android device collected with the Beiwe app installed
# @version 0.0.1


BeiweDeviceLogAndroidRecord = {
    # The time of the observation
    "stamp": datetime,
    # TODO
    "event": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A log made by an android device collected with the Beiwe app installed
# @version 0.0.1


BeiweDeviceLogIosRecord = {
    # The time of the observation
    "stamp": datetime,
    # TODO
    "launchID": str,
    # TODO
    "memory": int,
    # TODO
    "battery": int,
    # TODO
    "event": str,
    # TODO
    "message": str,
    # TODO
    "d1": str,
    # TODO
    "d2": str,
    # TODO
    "d3": str,
    # TODO
    "d4": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Magnetometer data collected by the Beiwe app for android and ios devices
# @version 0.0.1


BeiweDeviceMagnetometerRecord = {
    # The time of the observation
    "stamp": datetime,
    # TODO
    "x": int,
    # TODO
    "y": int,
    # TODO
    "z": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Motion data collected by the Beiwe app for iOS devices
# @version 0.0.1


BeiweDeviceMotionRecord = {
    # The time of the observation
    "stamp": datetime,
    # TODO
    "magneticFieldAccuracy": str,
    # TODO
    "magneticFieldX": int,
    # TODO
    "magneticFieldY": int,
    # TODO
    "magneticFieldZ": int,
    # TODO
    "userAccelerationX": int,
    # TODO
    "userAccelerationY": int,
    # TODO
    "userAccelerationZ": int,
    # TODO
    "gravityX": int,
    # TODO
    "gravityY": int,
    # TODO
    "gravityZ": int,
    # TODO
    "rotationRateX": int,
    # TODO
    "rotationRateY": int,
    # TODO
    "rotationRateZ": int,
    # TODO
    "roll": int,
    # TODO
    "pitch": int,
    # TODO
    "yaw": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The observed power state of a device with the Beiwe app installed
# @version 0.0.1


BeiweDevicePowerRecord = {
    # The time of the observation
    "stamp": datetime,
    # A description state of the power supply
    "state": str,
    # The observed power level of the device
    "level": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Proximity observed by a device collected with the Beiwe app installed
# @version 0.0.1


BeiweDeviceProximityRecord = {
    # The time of the observation
    "stamp": datetime,
    # TODO
    "event": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A reachability status observed by a device collected with the Beiwe app installed
# @version 0.0.1


BeiweDeviceReachabilityRecord = {
    # The time of the observation
    "stamp": datetime,
    # TODO
    "event": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The actual state of the settings on the device for the OMAR app
# @version 0.0.1


BeiweDeviceSettingRecord = {
    # TODO: from Beiwe docs
    "aboutPageText": str,
    # TODO: from Beiwe docs
    "callClinicianButtonText": str,
    # TODO: from Beiwe docs
    "consentFormText": str,
    # TODO: from Beiwe docs
    "surveySubmitSuccessToastText": str,
    # The orcatech unique identifier for the setting
    "id": APIID,
    # TODO: from Beiwe docs
    "allowUploadOverCellularData": bool,
    # in seconds
    "accelerometerOffDurationSeconds": int,
    # in seconds
    "checkAppUsageFrequencySeconds": int,
    # in seconds
    "checkForNewSettingsFrequencySeconds": int,
    # in seconds
    "accelerometerOnDurationSeconds": int,
    # in seconds
    "bluetoothOnDurationSeconds": int,
    # in seconds
    "bluetoothTotalDurationSeconds": int,
    # in seconds
    "bluetoothGlobalOffsetSeconds": int,
    # in seconds
    "checkForNewSurveysFrequencySeconds": int,
    # in seconds
    "createNewDataFilesFrequencySeconds": int,
    # in seconds
    "gpsOffDurationSeconds": int,
    # in seconds
    "gpsOnDurationSeconds": int,
    # in seconds
    "secondsBeforeAutoLogout": int,
    # in seconds
    "uploadDataDilesFrequencySeconds": int,
    # in seconds
    "voiceRecordingMaxTimeLengthSeconds": int,
    # in seconds
    "wifiLogFrequencySeconds": int,
    # in seconds
    "gyroOffDurationSeconds": int,
    # in seconds
    "gyroOnDurationSeconds": int,
    # in seconds
    "magnetometerOffDurationSeconds": int,
    # in seconds
    "magnetometerOnDurationSeconds": int,
    # in seconds
    "devicemotionOffDurationSeconds": int,
    # in seconds
    "devicemotionOnDurationSeconds": int,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for device
    "deviceID": APIID,
    # Lookup id number for accelerometer
    "accelerometerID": APIID,
    # Lookup id number for gps
    "gpsID": APIID,
    # Lookup id number for calls
    "callsID": APIID,
    # Lookup id number for texts
    "textsID": APIID,
    # Lookup id number for wifi
    "wifiID": APIID,
    # Lookup id number for bluetooth
    "bluetoothID": APIID,
    # Lookup id number for powerState
    "powerStateID": APIID,
    # Lookup id number for proximity
    "proximityID": APIID,
    # Lookup id number for gyro
    "gyroID": APIID,
    # Lookup id number for magnetometer
    "magnetometerID": APIID,
    # Lookup id number for deviceMotion
    "deviceMotionID": APIID,
    # Lookup id number for reachability
    "reachabilityID": APIID,
    # Lookup id numbers for consentSections
    "consentSectionIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Text used for consenting subjects
# @version 0.0.1


BeiweDeviceSettingConsentSectionRecord = {
    # The orcatech unique identifier for the settings section
    "id": APIID,
    # TODO: from Beiwe docs
    "text": str,
    # TODO: from Beiwe docs
    "more": str,
    # The type of consent being given
    "type": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for requiredConsents
    "requiredConsentIDs": [APIID],
    # Lookup id number for setting
    "settingID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Text used for consenting subjects
# @version 0.0.1


BeiweDeviceSettingConsentSectionRequiredRecord = {
    # The orcatech unique identifier for the settings section
    "id": APIID,
    # TODO: from Beiwe docs
    "text": str,
    # TODO: from Beiwe docs
    "more": str,
    # The type of consent being given
    "type": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for consents
    "consentsID": APIID,
    # Lookup id number for setting
    "settingID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id number for study
    "studyID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The required state of the OMAR app settings for a study or organization
# @version 0.0.1


BeiweDeviceSettingRequiredRecord = {
    # TODO: from Beiwe docs
    "aboutPageText": str,
    # TODO: from Beiwe docs
    "callClinicianButtonText": str,
    # TODO: from Beiwe docs
    "consentFormText": str,
    # TODO: from Beiwe docs
    "surveySubmitSuccessToastText": str,
    # The orcatech unique identifier for the setting
    "id": APIID,
    # The state of the settings
    "accelerometer": bool,
    # The state of the settings
    "gps": bool,
    # The state of the settings
    "calls": bool,
    # The state of the settings
    "texts": bool,
    # The state of the settings
    "wifi": bool,
    # The state of the settings
    "bluetooth": bool,
    # The state of the settings
    "powerState": bool,
    # The state of the settings
    "proximity": bool,
    # The state of the settings
    "gyro": bool,
    # The state of the settings
    "magnetometer": bool,
    # The state of the settings
    "devicemotion": bool,
    # The state of the settings
    "reachability": bool,
    # TODO: from Beiwe docs
    "allowUploadOverCellularData": bool,
    # in seconds
    "accelerometerOffDurationSeconds": int,
    # in seconds
    "checkAppUsageFrequencySeconds": int,
    # in seconds
    "accelerometerOnDurationSeconds": int,
    # in seconds
    "bluetoothOnDurationSeconds": int,
    # in seconds
    "bluetoothTotalDurationSeconds": int,
    # in seconds
    "bluetoothGlobalOffsetSeconds": int,
    # in seconds
    "checkForNewSurveysFrequencySeconds": int,
    # in seconds
    "checkForNewSettingsFrequencySeconds": int,
    # in seconds
    "createNewDataFilesFrequencySeconds": int,
    # in seconds
    "gpsOffDurationSeconds": int,
    # in seconds
    "gpsOnDurationSeconds": int,
    # in seconds
    "secondsBeforeAutoLogout": int,
    # in seconds
    "uploadDataFilesFrequencySeconds": int,
    # in seconds
    "voiceRecordingMaxTimeLengthSeconds": int,
    # in seconds
    "wifiLogFrequencySeconds": int,
    # in seconds
    "gyroOffDurationSeconds": int,
    # in seconds
    "gyroOnDurationSeconds": int,
    # in seconds
    "magnetometerOffDurationSeconds": int,
    # in seconds
    "magnetometerOnDurationSeconds": int,
    # in seconds
    "devicemotionOffDurationSeconds": int,
    # in seconds
    "devicemotionOnDurationSeconds": int,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for consentSections
    "consentSectionIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id number for study
    "studyID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A sms made by a device collected with the Beiwe app installed
# @version 0.0.1


BeiweDeviceSmsRecord = {
    # The time of the observation
    "stamp": datetime,
    # TODO
    "phoneNumberHash": str,
    # TODO
    "direction": str,
    # TODO
    "length": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A wifi access point observed by a device collected with the Beiwe app installed
# @version 0.0.1


BeiweDeviceWifiRecord = {
    # The time of the observation
    "stamp": datetime,
    # TODO
    "accessPointMACHash": str,
    # TODO
    "accessPointSSIDHash": str,
    # TODO
    "frequency": int,
    # TODO
    "rssi": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A state of the beiwe setting. i.e. requested, denied, enabled, or disabled.
# @version 0.0.1


BeiweSettingStateRecord = {
    # The unique identifier
    "id": APIID,
    # A short descriptive name for the setting state
    "name": str,
    # The long description of the setting state
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for accelerometerSettings
    "accelerometerSettingIDs": [APIID],
    # Lookup id numbers for gpsSettings
    "gpsSettingIDs": [APIID],
    # Lookup id numbers for callsSettings
    "callsSettingIDs": [APIID],
    # Lookup id numbers for textsSettings
    "textsSettingIDs": [APIID],
    # Lookup id numbers for wifiSettings
    "wifiSettingIDs": [APIID],
    # Lookup id numbers for bluetoothSettings
    "bluetoothSettingIDs": [APIID],
    # Lookup id numbers for powerStateSettings
    "powerStateSettingIDs": [APIID],
    # Lookup id numbers for proximitySettings
    "proximitySettingIDs": [APIID],
    # Lookup id numbers for gyroSettings
    "gyroSettingIDs": [APIID],
    # Lookup id numbers for magnetometerSettings
    "magnetometerSettingIDs": [APIID],
    # Lookup id numbers for deviceMotionSettings
    "deviceMotionSettingIDs": [APIID],
    # Lookup id numbers for reachabilitySettings
    "reachabilitySettingIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A 2d geological coordinate
# @version 0.0.1


CoordinateRecord = {
    # The latitude coordinate of the location.
    "lat": int,
    # The longitude coordinate of the location.
    "lng": int,
    # Optional accuracy of the location in meters
    "accuracy": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The type of device event
# @version 0.0.1


DeviceEventTypeRecord = {
    # The  unique identifier
    "id": APIID,
    # A short name for the event type
    "name": str,
    # A longer description of the event type
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An input event.
# @version 0.0.1


# DeviceInputEventRecord = {
#     # An input identifier
#     "id": APIID,
#     # The time in which the input happened
#     "stamp": datetime,
#     # If true, indicates that the record is frozen
#     "isFrozen": bool,
# }


class DeviceInputEventRecord(TypedDict):
    # An input identifier
    id: APIID
    # The time in which the input happened
    stamp: datetime
    # If true, indicates that the record is frozen
    isFrozen: bool


# The input events captured while a subject is using a device.
# @version 0.0.1


# DeviceInputRecord = {
#     # Timestamp of when the input was made.
#     "stamp": datetime,
#     # Indicates mouse on or off an image. Null indicates on hover event.
#     "imageHover": bool,
#     # Numeric code of key pressed.
#     "keyCode": int,
#     # Idicates key pressed or released. Null indicates no key pressed.
#     "keyDown": bool,
#     # List of all keys pressed.
#     "keysDown": [DeviceInputEventRecord],
#     # Character of key pressed.
#     "keyText": str,
#     # Mouse button pressed.
#     "mouseButton": int,
#     # Indicates mouse button pressed or released. Null indicates no button pressed.
#     "mouseButtonDown": bool,
#     # List of all mouse buttons pressed.
#     "mouseButtonsDown": [DeviceInputEventRecord],
#     # Mouse pointer horizontal position.
#     "mouseX": int,
#     # Mouse pointer vertical position.
#     "mouseY": int,
#     # Indicates scrolled down or up. Null indicates no scroll occurred.
#     "scrollDown": bool,
#     # Distance in pixels scrolled.
#     "scrollLength": int,
#     # Class name of active textbox.
#     "textBox": str,
#     # Indicates textbox focused or unfocused. Null indicates no focus occurred.
#     "textBoxActive": bool,
#     # List of touch events (expect to always be null as browsers have touch mimic mouse)
#     "touches": [DeviceInputEventRecord],
#     # Touch type id.
#     "touchType": int,
#     # Touch horizontal position.
#     "touchX": int,
#     # Touch vertical position.
#     "touchY": int,
#     # If true, indicates that the record is frozen
#     "isFrozen": bool,
# }


class DeviceInputRecord(TypedDict):
    # Timestamp of when the input was made.
    stamp: datetime
    # Indicates mouse on or off an image. Null indicates on hover event.
    imageHover: bool
    # Numeric code of key pressed.
    keyCode: int
    # Idicates key pressed or released. Null indicates no key pressed.
    keyDown: bool
    # List of all keys pressed.
    keysDown: List[DeviceInputEventRecord]
    # Character of key pressed.
    keyText: str
    # Mouse button pressed.
    mouseButton: int
    # Indicates mouse button pressed or released. Null indicates no button pressed.
    mouseButtonDown: bool
    # List of all mouse buttons pressed.
    mouseButtonsDown: List[DeviceInputEventRecord]
    # Mouse pointer horizontal position.
    mouseX: int
    # Mouse pointer vertical position.
    mouseY: int
    # Indicates scrolled down or up. Null indicates no scroll occurred.
    scrollDown: bool
    # Distance in pixels scrolled.
    scrollLength: int
    # Class name of active textbox.
    textBox: str
    # Indicates textbox focused or unfocused. Null indicates no focus occurred.
    textBoxActive: bool
    # List of touch events (expect to always be null as browsers have touch mimic mouse)
    touches: List[DeviceInputEventRecord]
    # Touch type id.
    touchType: int
    # Touch horizontal position.
    touchX: int
    # Touch vertical position.
    touchY: int
    # If true indicates that the record is frozen
    isFrozen: bool


# Periods spent out of the bed
# @version 0.0.1


EmfitBedexitRecord = {
    # Start time of out of bed period
    "start": datetime,
    # End time of out of bed period
    "end": datetime,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# No description. Series of calculations?
# @version 0.0.1


EmfitCalcRecord = {
    # Start time of out of bed period
    "stamp": datetime,
    # beats per minute
    "hr": int,
    # breaths per minute
    "rr": int,
    # unitless
    "activity": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Events are reported by an emfit device every 30s
# @version 0.0.1


EmfitEventRecord = {
    # Time of measurement
    "stamp": datetime,
    # Emfit device's serial number
    "device": str,
    # Event ID defined by Emfit
    "id": APIID,
    # Event description inferred using Emfit documentation
    "description": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Heart rate variability information for Evening and Morning. There are two version of the data. BasedFirstLast90: based on first and last 90 mins of 3 min RMSSD datapoints, and also whole night RMSSD graph which included the integratingRecovery field. BasedWholeNight: ased on linear fit of whole night RMSSD datapoints
# @version 0.0.1


EmfitHrvRecord = {
    # evening value of RMSSD, average values within first 90 minutes of bed presence
    "start": int,
    # morning value of RMSSD, average values within last 90 minutes of bed presence
    "end": int,
    # endRMSSD-startRMSSD
    "totalRecovery": int,
    # endRMSSD/startRMSSD
    "recoveryRatio": int,
    # totalRecovery/duration of sleep (in hours)
    "recoveryRate": int,
    # area under curve formed by all night 3 min RMSSD dots only present in BasedFirstLast90
    "integratingRecovery": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Heart rate variability information for Evening and Morning based on linear fit of whole night RMSSD datapoints
# @version 0.0.1


EmfitHrvLinearRecord = {
    # evening value of RMSSD, start point of linear fit line
    "start": int,
    # morning value of RMSSD , end point of linear fit line
    "end": int,
    # endRMSSD-startRMSSD
    "totalRecovery": int,
    # endRMSSD/startRMSSD
    "recoveryRatio": int,
    # totalRecovery/duration of sleep (in hours)
    "recoveryRate": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Heart rate variability root mean square of successive differences
# @version 0.0.1


EmfitHrvrmssdRecord = {
    # Time of measurement
    "stamp": datetime,
    # The low frequency measured in the window
    "lowFrequency": int,
    # The high frequence measured in the window
    "highFrequency": int,
    # root mean square of successive differences
    "rmssd": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Heart Rate Variability is calculated every 3 minutes per device. If these fields are omitted then they are equal to NULL, which usually indicates absence or not enough signal quality(movement artefact or else) data for HRV calculation for the period
# @version 0.0.1


EmfitLiveHRVRecord = {
    # Time of measurement
    "stamp": datetime,
    # Emfit device's serial number
    "device": str,
    # Root Mean Square of Successive Differences
    "RMSSD": int,
    # Total power in .04 to .4 Hz area
    "TP": int,
    # Low Frequency area (normalized), 0.04 to 0.15 Hz
    "LFN": int,
    # High Frequency area (normalized), 0.15 to 0.4 Hz
    "HFN": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Information routinely requested from a local emfit bed mat
# @version 0.0.1


EmfitPollRecord = {
    # Time of measurement
    "stamp": datetime,
    # Device serial number, unique identifier
    "serialNumber": str,
    # Whether or not subject is presently in bed
    "present": bool,
    # Emfit's calculated heart rate at time of poll
    "heartrate": int,
    # Emfit's calculated heart rate at time of poll
    "respiratoryRate": int,
    # Emfit's unitless measurement of activity at time of poll
    "activityLevel": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Heart rate variability root mean square of successive differences
# @version 0.0.1


EmfitSleepRecord = {
    # Time of measurement
    "stamp": datetime,
    # One of the SleepClass constants (1:Deep, 2:Light, 3:REM, 4:Awake)
    "classID": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Sleep Summary data is POST--ed by webhook in JSON format to consumers once the user bed presence period is ended. Approximate delay between actual bed exit that starts period data processing, to the delivery of the Sleep Summary data, is at about 5--20 minutes.Note that if user return to bed within following 20 minutes after bed exit and the Night/Day setting is not used, after the next bed exit the same data is send again from the whole sleep period. You need to have means to delete doubled data. Sleep summary data is associated with a particular device. It contains information about device, presence period and all calculated dataof the period.
# @version 0.0.1


EmfitSummaryRecord = {
    # Presence period unique identifier
    "id": APIID,
    # Device serial number, unique identifier
    "device": str,
    # Unique identifier of the user who is linked to the account
    "userID": int,
    # Start time of presence period
    "from": datetime,
    # End time of presence period
    "to": datetime,
    # Duration of the period in seconds
    "duration": int,
    # user time offset to GMT time, minutes
    "fromGMTOffset": int,
    # total duration of presence period, seconds
    "durationInBed": int,
    # sum of time at awake state during sleep period, seconds
    "durationAwake": int,
    # total time at sleep during sleep period, seconds
    "durationInSleep": int,
    # total time spent at REM sleep during presence period, seconds
    "durationInREM": int,
    # total time spent at LIGHT sleep during presence period, seconds
    "durationInLight": int,
    # total time spent at DEEP sleep during presence period, seconds
    "durationInDeep": int,
    # time from presence period start to fall asleep
    "durationSleepOnset": int,
    # total duration of time spent out of the bed during presence period
    "durationBedExit": int,
    # number of awakenings
    "awakenings": int,
    # number of bed exits
    "bedExitCount": int,
    # total number of tossnturns
    "tossNTurnCount": int,
    # whole night (presence period) average of heart rate, beats per minute
    "avgHR": int,
    # lowest 3 min average heart rate (same as resting HR) from whole night, beats per minute
    "minHR": int,
    # highest3 min average heart rate from whole night, beats per minute
    "maxHR": int,
    # morning value of HRV, RMSSD
    "hrvScore": int,
    # low frequency part of HRV spectral distribution.  NOTE: hrv_lf + hrv_hf = 100
    "hrvLF": int,
    # high frequency part of HRV spectral distribution
    "hrvHF": int,
    # HRV data for whole night, at 3 min intervals [TIMESTAMP, RMSSD, LF, HF]
    "hrvRMSSDData": [EmfitHrvrmssdRecord],
    # evening value of RMSSD
    "hrvRMSSDEvening": int,
    # morning value of RMSSD
    "hrvRMSSDMorning": int,
    # whole night (presence period) average of respiration rate, breaths per minute
    "avgRR": int,
    # minimum 3 min average respiration rate from whole night, breaths per minute
    "minRR": int,
    # maximum 3 min average respiration rate from whole night, breaths per minute
    "maxRR": int,
    # whole night average of physical activity, unitless
    "avgActivity": int,
    # fast movements count(over 10 sec periods).
    "fmCount": int,
    # Heart rate variability information for Evening and Morning based on linear fit of whole night RMSSD data points
    "linearHrvData": EmfitHrvLinearRecord,
    # Heart rate variability information for Evening and Morning based on first and last 90 mins of 3 min RMSSD data points, and also whole night RMSSD graph
    "hrvData": EmfitHrvRecord,
    # timestamps of fast movement occurrences
    "fmData": [datetime],
    # no description
    "calcData": [EmfitCalcRecord],
    # no description
    "sleepData": [EmfitSleepRecord],
    # Periods out of the bed
    "bedExitData": [EmfitBedexitRecord],
    # occurrence times of toss and turns (bigger movements)
    "tossNTurnData": [datetime],
    # no description
    "checked": int,
    # compound index of sleep quality (0-100). Constitutes from amount of sleep, deep and rem and awakenings
    "sleepScore": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Body of the request that is POST--ed by Emfit's API in JSON format after a mat recognizes a sleep period
# @version 0.0.2


EmfitSummaryStringRecord = {
    # Body of the request represented as a string
    "body": str,
    # Unix timestamp divided by approximate number of seconds in a month (2500000)
    "unixMonth": int,
    # Timestamp for when emfit's API sent the sleep summary
    "received": datetime,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Heart Rate, Respiration Rate and movement Activity level. If Heart Rate, Respiration Rate fields are omitted then they are equal to NULL. In such case Activity value is 0 - it means that device is turned on,but nobody is in the bed.Thedefault behavior of the webhook is to POSTonly one record per device per 30 seconds.But there is an option to includeall past 30 seconds window of data(15 data points). Activity values arebetween 0 - 32767
# @version 0.0.1


EmfitVitalsRecord = {
    # Time of measurement
    "stamp": datetime,
    # Emfit device's serial number
    "device": str,
    # Measured heart rate
    "heartRate": int,
    # Respiration rate
    "respirationRate": int,
    # Activity level defined by Emfit (range 0 - 32767). If 0, thedevice is on but nobody is in bed
    "activity": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The occurrence of an event
# @version 0.0.1


EventRecord = {
    # The schema of the event source
    "sourceSchema": SchemaRecord,
    # The source of the event. This can be sensors for reading, microservices for errors, etc
    "source": any,
    # Lookup id number for type
    "typeID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The type of event
# @version 0.0.1


EventChangeFieldRecord = {
    # The name of the record field that changed
    "field": str,
    # The previous value of the field as a string
    "previous": str,
    # The next value of the field as a string
    "next": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The type of event
# @version 0.0.1


EventTypeRecord = {
    # The  unique identifier
    "id": APIID,
    # A short name for the event type
    "name": str,
    # A longer description of the event type
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Fibaro sensor events collected over a z-wave network
# @version 0.0.1


FibaroEventRecord = {
    # A timestamp indicating the time at which the event occurred
    "stamp": datetime,
    # The unique mac address of the fibaro sensor which triggered the event
    "macaddress": str,
    # Whether or not the fibaro sensor detected presence
    "presenceDetected": bool,
    # Whether or not the fibaro sensor detected an open door
    "open": bool,
    # Whether or not the fibaro sensor detected current
    "current": bool,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A history of associations between records
# @version 0.0.1


HistoryAssociationRecord = {
    # The schema name of the first record
    "firstSchema": str,
    # The association field of the first record
    "firstField": str,
    # The unique identifier for the first schema
    "firstID": int,
    # The schema name of the second record
    "secondSchema": str,
    # The association field of the second record
    "secondField": str,
    # The unique identifier for the second schema
    "secondID": int,
    # The unique identifier
    "id": APIID,
    # When the two records were first associated
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the two records were disassociated
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A history of record field values
# @version 0.0.1


HistoryFieldRecord = {
    # The schema name of the record
    "recordSchema": str,
    # The name of the record field that changed
    "recordField": str,
    # The unique identifier of the schema
    "recordID": int,
    # The previous value of the field
    "previousValue": Union[str, datetime, int],
    # The current value of the field
    "nextValue": Union[str, datetime, int],
    # The unique identifier
    "id": APIID,
    # When the two records were first associated
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the two records were disassociated
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The home is a collection of common objects that reside in a dwelling.
# @version 0.0.1


HomeRecord = {
    # The unique identifier
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for users
    "userIDs": [APIID],
    # Lookup id numbers for subjects
    "subjectIDs": [APIID],
    # Lookup id numbers for people
    "personIDs": [APIID],
    # Lookup id numbers for animals
    "animalIDs": [APIID],
    # Lookup id numbers for issues
    "issueIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for tasks
    "taskIDs": [APIID],
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # Lookup id number for dwelling
    "dwellingID": APIID,
    # Lookup id numbers for identifiers
    "identifierIDs": [APIID],
    # Lookup id numbers for attributes
    "attributeIDs": [APIID],
    # Lookup id numbers for items
    "itemIDs": [APIID],
    # Lookup id number for phone
    "phoneID": APIID,
    # Lookup id numbers for sensorLines
    "sensorLineIDs": [APIID],
    # Lookup id numbers for integrationCredentials
    "integrationCredentialIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The value portion of a key value pair belonging to an home
# @version 0.0.1


HomeAttributeRecord = {
    # The local unique identifier
    "id": APIID,
    # The attribute string
    "value": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for home
    "homeID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A type of home attribute for the home. This will act as the key in the key value pair
# @version 0.0.1


HomeAttributeTypeRecord = {
    # A short unique name to categorize the identifiers
    "name": str,
    # The local unique identifier
    "id": APIID,
    # A description of the external database
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for attributes
    "attributeIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An external identifier for the study to map the it's data to an external database
# @version 0.0.1


HomeIdentifierRecord = {
    # The identification string
    "value": str,
    # The unique identifier
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for home
    "homeID": APIID,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A type of external identifier for the home to map the their data to an external database
# @version 0.0.1


HomeIdentifierTypeRecord = {
    # A short unique name to categorize the identifiers
    "name": str,
    # The  unique identifier
    "id": APIID,
    # A description of the external database
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for identifiers
    "identifierIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A tag used to categorize a set of homes
# @version 0.0.1


HomeTagRecord = {
    # The unique identifier
    "id": APIID,
    # A unique name for the tag
    "name": str,
    # A longer description of the tag
    "description": str,
    # A hexidecimal representation of a color for this tag
    "color": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for homes
    "homeIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Credentials and connection parameters for 3rd party application integrations
# @version 0.0.1


IntegrationRecord = {
    # A descriptive name of the integration
    "name": str,
    # The unique identifier
    "id": APIID,
    # Details about the integration
    "description": str,
    # The namespace to use when interacting with the integration
    "namespace": str,
    # If set to true, the management console will make use of the integration.
    "enabled": bool,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id number for study
    "studyID": APIID,
    # Lookup id numbers for credentials
    "credentialIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A set of credentials used for authenticating with an integration
# @version 0.0.1


IntegrationCredentialRecord = {
    # The database unique identifier
    "id": APIID,
    # The hostname at which the api can be reached.
    "host": str,
    # The port number at which the api can be reached.
    "port": int,
    # The unique identifier for identifying the client to the provider
    "clientID": str,
    #
    "url": str,
    #
    "channel": str,
    # The token used to make queries
    "accessToken": str,
    # The token used to create new access tokens
    "refreshToken": str,
    # address for reply-to in email (user@someplace.com)
    "fromAddress": str,
    # The username that is used to authenticate with the integration.
    "username": str,
    # The password that is used to authenticate with the integration.
    "password": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for states
    "stateIDs": [APIID],
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id number for home
    "homeID": APIID,
    # Lookup id number for integration
    "integrationID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id number for study
    "studyID": APIID,
    # Lookup id number for notificationType
    "notificationTypeID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The pulling status for a particular API client.
# @version 0.0.1


IntegrationCredentialStateRecord = {
    # The database unique identifier
    "id": APIID,
    # The schema name of the of the queried record as a string
    "recordSchema": str,
    # The timestamp of the last interaction
    "last": datetime,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for credential
    "credentialID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id number for study
    "studyID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A tracked piece of equipment such as sensors, computers, etc
# @version 0.0.1


InventoryItemRecord = {
    # A unique serialnumber for the item model
    "serialNumber": str,
    # A mac address for the item model
    "macaddress": str,
    # The  unique identifier
    "id": APIID,
    # A unique name for the item
    "name": str,
    # Time when the item's battery was changed.
    "batteryChanged": datetime,
    # The item was not working correctly and data generated from the item should be ignored
    "inactive": datetime,
    # True if the item is connected, false otherwise. This can refer to the connectivity of the device or the physical status
    "isConnected": bool,
    # The last recorded timestamp at which the device checked in
    "lastTransmission": datetime,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for model
    "modelID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for issues
    "issueIDs": [APIID],
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # Lookup id number for beiweDeviceSetting
    "beiweDeviceSettingID": APIID,
    # Lookup id number for area
    "areaID": APIID,
    # Lookup id number for firstLineSegment
    "firstLineSegmentID": APIID,
    # Lookup id number for secondLineSegment
    "secondLineSegmentID": APIID,
    # Lookup id number for state
    "stateID": APIID,
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id number for home
    "homeID": APIID,
    # Lookup id numbers for users
    "userIDs": [APIID],
    # Lookup id numbers for identifiers
    "identifierIDs": [APIID],
    # Lookup id numbers for attributes
    "attributeIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The value portion of a key value pair belonging to an inventory item
# @version 0.0.1


InventoryItemAttributeRecord = {
    # The local unique identifier
    "id": APIID,
    # The attribute string
    "value": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for item
    "itemID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A type of item attribute for the item. This will act as the key in the key value pair
# @version 0.0.1


InventoryItemAttributeTypeRecord = {
    # The local unique identifier
    "id": APIID,
    # A short unique name to categorize the identifiers
    "name": str,
    # A description of the external database
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for attributes
    "attributeIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An external identifier for the item to map the their data to an external database
# @version 0.0.1


InventoryItemIdentifierRecord = {
    # The identification string
    "value": str,
    # The local unique identifier
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for item
    "itemID": APIID,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A type of external identifier for the item to map the their data to an external database
# @version 0.0.1


InventoryItemIdentifierTypeRecord = {
    # The local unique identifier
    "id": APIID,
    # A short unique name to categorize the identifiers
    "name": str,
    # A description of the external database
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for identifiers
    "identifierIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A state of the item in the inventory. i.e. working vs. not working.
# @version 0.0.1


InventoryItemStateRecord = {
    # The unique identifier
    "id": APIID,
    # A short descriptive name for the study state
    "name": str,
    # The long description of the study state
    "description": str,
    # True if this state indicates that the item is not possessed, false otherwise.
    "notPossessed": bool,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for items
    "itemIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The status of the inventory item
# @version 0.0.1


InventoryItemStatusRecord = {
    # True if this inventory item is currently connected
    "connected": bool,
    # The current reported firmware version
    "firmware": str,
    # The current reported battery level
    "batteryLevel": int,
    # List of active alerts
    "alerts": [AlertIncidentRecord],
    # A map where the key is the data schema and the value is the time of the last data point
    "lastDataPoint": Dict[str, datetime],
    # A map where the key is the data schema and the value is the total number of data points
    "totalDataPoints": Dict[str, int],
    # Lookup id number for item
    "itemID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# User account credentials for an inventory item
# @version 0.0.1


InventoryItemUserRecord = {
    #  unique identifier
    "id": APIID,
    # The login username
    "username": str,
    # The login password
    "password": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for item
    "itemID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Information shared across items that share the same hardware
# @version 0.0.1


InventoryModelRecord = {
    # The  unique identifier
    "id": APIID,
    # A vendor unique name for the model
    "name": str,
    # True is the model has batteries, false otherwise
    "hasBatteries": bool,
    # True is the model is a hub for collecting sensor data, false otherwise
    "isHub": bool,
    # True is the model has batteries, false otherwise
    "estimatedBatteryLife": Duration,
    # duration before sensor is considered 'non-reporting'
    "ttl": Duration,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id number for vendor
    "vendorID": APIID,
    # Lookup id numbers for items
    "itemIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A tag used to categorize the inventory records
# @version 0.0.1


InventoryTagRecord = {
    # The unique identifier
    "id": APIID,
    # A unique name for the tag
    "name": str,
    # A longer description of the tag
    "description": str,
    # A hexidecimal representation of a color for this tag
    "color": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for items
    "itemIDs": [APIID],
    # Lookup id numbers for models
    "modelIDs": [APIID],
    # Lookup id numbers for vendors
    "vendorIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id number for software
    "softwareID": APIID,
    # Lookup id number for user
    "userID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A user account managed on a set of devices
# @version 0.0.1


InventoryUserRecord = {
    # The unique identifier
    "id": APIID,
    # The name of the managed account
    "name": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id number for study
    "studyID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A company that makes equipment purchased by
# @version 0.0.1


InventoryVendorRecord = {
    # The unique identifier
    "id": APIID,
    # A unique name for the vendor
    "name": str,
    # A description of the vendor including any links to their website
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for models
    "modelIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An internal review board document for the study
# @version 0.0.1


IrbDocumentRecord = {
    # The unique identifier
    "id": APIID,
    # The identification string
    "identifier": str,
    # Link to the irb web page
    "link": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for state
    "stateID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An internal review board state
# @version 0.0.1


IrbStateRecord = {
    # The unique identifier
    "id": APIID,
    # The identification string
    "name": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for documents
    "documentIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An issue that needs to be resolved. Work resolving the issue is tracked through comments and assignments.
# @version 0.0.1


IssueRecord = {
    # The  unique identifier
    "id": APIID,
    # A short name describing the issue.
    "name": str,
    # A description of the issue.
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for tracking
    "trackingIDs": [APIID],
    # Lookup id numbers for assignedTo
    "assignedToIDs": [APIID],
    # Lookup id numbers for homes
    "homeIDs": [APIID],
    # Lookup id numbers for subjects
    "subjectIDs": [APIID],
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for items
    "itemIDs": [APIID],
    # Lookup id numbers for tasks
    "taskIDs": [APIID],
    # Lookup id numbers for hemispheres
    "hemisphereIDs": [APIID],
    # Lookup id numbers for hemisphereCassettes
    "hemisphereCassetteIDs": [APIID],
    # Lookup id numbers for hemisphereSlides
    "hemisphereSlideIDs": [APIID],
    # Lookup id numbers for hemisphereSlices
    "hemisphereSliceIDs": [APIID],
    # Lookup id numbers for comments
    "commentIDs": [APIID],
    # Lookup id number for state
    "stateID": APIID,
    # Lookup id number for source
    "sourceID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A comment about the issue indicating an update in status.
# @version 0.0.1


IssueCommentRecord = {
    # The  unique identifier
    "id": APIID,
    # The content of the comment.
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for issue
    "issueID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# What, who or how the issue what identified.
# @version 0.0.1


IssueSourceRecord = {
    # The  unique identifier
    "id": APIID,
    # A short name for the source
    "name": str,
    # The long description of the what the source means.
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for issues
    "issueIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The status of an issue. i.e. open, pending, fixed, etc.
# @version 0.0.1


IssueStateRecord = {
    # The  unique identifier
    "id": APIID,
    # A short description name of the state
    "name": str,
    # True if this state is a resolution of the issue.
    "resolution": bool,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for issues
    "issueIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A tag used to categorize a set of issues
# @version 0.0.1


IssueTagRecord = {
    # The unique identifier
    "id": APIID,
    # A unique name for the tag
    "name": str,
    # A longer description of the tag
    "description": str,
    # A hexidecimal representation of a color for this tag
    "color": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for issues
    "issueIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A home containing an individual who participates in an  affiliated study. The home should represent a real physical location and not an abstract space
# @version 0.0.1


LocationRecord = {
    # The street number and street name of the location
    "address": str,
    # The  unique identifier
    "id": APIID,
    # The name of the location if any. This is most useful for larger facilities such as apartments and condos
    "name": str,
    # The latitude coordinate of the location.
    "lat": int,
    # The longitude coordinate of the location.
    "lng": int,
    # The timezone of the location in the form `America/Los_Angeles`
    "timezone": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id numbers for dwellings
    "dwellingIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A physical location or space for living.
# @version 0.0.1


LocationDwellingRecord = {
    # If the location is an apartment or condo, this is the building number. For single family homes this should be null.
    "apt": str,
    # The  unique identifier
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for location
    "locationID": APIID,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for areas
    "areaIDs": [APIID],
    # Lookup id number for home
    "homeID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The type of location. i.e. apartments, single family housing, townhomes, etc
# @version 0.0.1


LocationTypeRecord = {
    # The  unique identifier
    "id": APIID,
    # A short name for the location type
    "name": str,
    # A longer description of the location type
    "description": str,
    # True if the location contains multiple dwellings at a single address, false otherwise
    "hasMultipleDwellings": bool,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for locations
    "locationIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An  application log line.
# @version 0.0.1


LogRecord = {
    # The application which created this log
    "application": str,
    # A unix timestamp indicating the time at which the log was created by the application
    "stamp": datetime,
    # The name of the host in which the application is running on
    "hostname": str,
    # The importance level of the log 1=Error,2=Warn,3=Info,...9=Test
    "level": int,
    # The namespace of the application. i.e. test, beta, production, etc...
    "namespace": str,
    # A set of key value pairs indicating the state of the application as well as any messages
    "values": Dict[str, str],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Audit log for when user's login to the system
# @version 0.0.1


MeasureAccessPeriodRecord = {
    # The identifier of the user who logged in
    "user": any,
    # The schema of the user who logged in
    "userSchema": SchemaRecord,
    # When the login finished
    "stop": datetime,
    # The
    "ipAddress": str,
    # The operating system name of the device used to administer the test
    "operatingSystemFamily": str,
    # The operating system version of the device used to administer the test
    "operatingSystemVersion": str,
    # The device family of the device used to administer the test
    "deviceFamily": str,
    # The device model of the device used to administer the test
    "deviceModel": str,
    # The device brand of the device used to administer the test
    "deviceBrand": str,
    # The raw user agent string if it was administered over a web browser
    "userAgent": str,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Audit log for when user's login to the system
# @version 0.0.1


MeasureAccessRequestRecord = {
    # The identifier of the user who logged in
    "user": any,
    # The schema of the user who logged in
    "userSchema": SchemaRecord,
    # The http method from the request
    "method": str,
    # The uri of the request
    "uri": str,
    # The
    "status": int,
    # The average duration of the request
    "duration": Duration,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The observed period of physical activity
# @version 0.0.1


MeasureActivityPhysicalPeriodRecord = {
    # The length of time of this epoch in which the measurements were taken
    "duration": Duration,
    # The name of the activity, possible values as walking, running and sitting
    "name": str,
    # The number of stories the user has ascended
    "ascent": int,
    # How many levels the user has descended, assuming this is in stories of a building
    "descent": int,
    # How far the user has traveled
    "distance": int,
    # The total number of calories burned included both active and passive periods
    "calories": int,
    # The calories burned while being active
    "caloriesEarned": int,
    # The metabolic calories used (even by resting) during this period
    "metabolicCalories": int,
    # The metabolic calories earned during this period
    "metabolicCaloriesEarned": int,
    # If the user is walking (WalkStateNotWalking(1)->false, WalkStateWalking(2)->true)
    "walkState": int,
    # If the user is running (RunStateNotRunning(1)->false, RunStateRunning(2)->true)
    "runState": int,
    # The sleeping state of the user (SleepStateWake(0)->Wake, SleepStateLight(1)->Light, SleepStateDeep(2)->Deep, SleepStateREM(3)->REM) for this period
    "sleepState": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# generic application use schema that includes meta
# @version 0.0.1


MeasureApplicationUserPeriodRecord = {
    # The timestamp in which the session ended.  The timestamp is recorded and stored as the local time (i.e. time zone) to which the the user's workstation is set. If the session is current than this value is null.
    "duration": datetime,
    # The name of the application being used. The value is null if unable to detect the application.
    "applicationName": str,
    # The name of the application executable being used. The value is null if unable to detect the application.
    "applicationExecutable": str,
    # The name of the application executable filename being used. The value is null if unable to detect the application.
    "applicationExecutableFileName": str,
    # The name of the application document being used. The value is null if unable to detect the document.
    "document": str,
    # The title of the website being accessed. The value is null if unable to detect the website title.
    "site": str,
    # The name of the domain being accessed. The value is null if unable to detect the website.
    "domain": str,
    # The URL of the website being used. The value is null if unable to detect the website.
    "url": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An event indicating the battery level of a sensor
# @version 0.0.1


MeasureBatteryRecord = {
    # The battery level as a percentage from 0-100
    "level": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Detected activity on the bed
# @version 0.0.1


MeasureBedActivityRecord = {
    # Activity level defined by Emfit (range 0 - 32767). If 0, thedevice is on but nobody is in bed
    "level": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A period of being awake while in bed
# @version 0.0.1


MeasureBedAwakePeriodRecord = {
    # Duration of the period
    "duration": Duration,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Period out of bed during a sleeping period
# @version 0.0.1


MeasureBedExitPeriodRecord = {
    # Duration of the period
    "duration": Duration,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A measurement of weight
# @version 0.0.1


MeasureBodyWeightRecord = {
    # A descriptive name of what was weighed. Possible values are 'total', 'bone', 'water', 'muscle', 'fat
    "name": str,
    # The weight measured in grams
    "weight": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A heartbeat indicating that the sensor is connected and working
# @version 0.0.1


MeasureCheckinRecord = {
    # The expected interval between heartbeats
    "interval": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An event indicating an opened or closed state of an area monitored by a sensor
# @version 0.0.1


MeasureContactRecord = {
    # False if the sensor is not in contact, true if it is in contact
    "contact": bool,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An observed location as a set of geocoordinates
# @version 0.0.1


MeasureCoordinateRecord = {
    # The coordinate measurement information
    "coordinate": CoordinateRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Information about a particular vehicle
# @version 0.0.1


VehicleRecord = {
    # Unique identifier for the vehicle given by the database
    "id": APIID,
    # Vehicle Identification number
    "vin": str,
    # Make (Honda, Chevy, etc.,)
    "make": str,
    # Model (Civic, F150, etc.,)
    "model": str,
    # Submodel (EX, Deluxe, etc.,)
    "submodel": str,
    # Year made
    "year": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A device event
# @version 0.0.1


MeasureDeviceEventRecord = {
    # When the event occurred
    "stamp": datetime,
    # vehicle info
    "vehicle": VehicleRecord,
    # coordinates of the location
    "location": CoordinateRecord,
    # Lookup id number for device
    "deviceID": APIID,
    # Lookup id number for type
    "typeID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# document what it does here
# @version 0.0.1


MeasureHeartRateRecord = {
    # The length of time of this epoch in which the measurements were taken
    "duration": Duration,
    # Measured heart rate
    "rate": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# document what it does here
# @version 0.0.1


MeasureHeartRatePeriodRecord = {
    # Duration of the period
    "duration": Duration,
    # whole night (presence period) average of heart rate, beats per minute
    "average": int,
    # lowest 3 min average heart rate (same as resting HR) from whole night, beats per minute
    "minumum": int,
    # highest 3 min average heart rate from whole night, beats per minute
    "maximum": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# document what it does here
# @version 0.0.1


MeasureHeartRateVariabilityPeriodRecord = {
    # Duration of the period
    "duration": Duration,
    # morning value of HRV, RMSSD
    "score": int,
    # low frequency part of HRV spectral distribution.  NOTE: hrv_lf + hrv_hf = 100
    "lowFrequencyPart": int,
    # high frequency part of HRV spectral distribution
    "highFrequencyPart": int,
    # evening value of RMSSD
    "RMSSDEvening": int,
    # morning value of RMSSD
    "RMSSDMorning": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Heart rate variability root mean square of successive differences
# @version 0.0.1


MeasureHeartRateVariabilityRmssdRecord = {
    # The low frequency measured in the window
    "lowFrequency": int,
    # The high frequency measured in the window
    "highFrequency": int,
    # root mean square of successive differences
    "rmssd": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The state of the doors on a pillbox
# @version 0.0.1


MeasurePillboxStateRecord = {
    # Indicates the order of records as they are generated in case the timekeeping on the device is not correct
    "recordNumber": int,
    # A bitmask describing the state of all the doors. A binary representation describes the doors as either open (1) or closed (0) where the first bit in big endian representation represents Saturday and the seventh bit represents Sunday. BoxState is a uint16 and therefore can represent a 2-row pillbox where the 8th bit represents Saturday and the 14th bit represents Sunday in the second row.
    "state": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An event indicating presence or no presence within an area monitored by a sensor
# @version 0.0.1


MeasurePresenceRecord = {
    # True if the sensor detected presence, false if the sensor is no longer detecting a presence
    "present": bool,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# document what it does here
# @version 0.0.1


MeasureRespirationRateRecord = {
    # The rate of respiration
    "rate": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# document what it does here
# @version 0.0.1


MeasureRespirationRatePeriodRecord = {
    # Duration of the period
    "duration": Duration,
    # whole night (presence period) average of respiration rate, breaths per minute
    "average": int,
    # minimum 3 min average respiration rate from whole night, breaths per minute
    "minimum": int,
    # maximum 3 min average respiration rate from whole night, breaths per minute
    "maximum": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Fast movement that occurred while sleeping
# @version 0.0.1


MeasureSleepMovementFastRecord = {
    # If true, indicates that the record is frozen
    "isFrozen": bool
}

# Summary information about fast movements that occurred during a sleep period
# @version 0.0.1


MeasureSleepMovementFastPeriodRecord = {
    # Duration of the period
    "duration": Duration,
    # fast movements count(over 10 sec periods).
    "count": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Information about a period of restlessness while sleeping
# @version 0.0.1


MeasureSleepMovementPeriodRecord = {
    # Duration of the period
    "duration": Duration,
    # total number of tossnturns
    "count": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# document what it does here
# @version 0.0.1


MeasureSleepPeriodRecord = {
    # Duration of the period
    "duration": Duration,
    # total duration of presence period
    "inBed": Duration,
    # sum of time at awake state during sleep period
    "wakeAfterSleepOnSet": Duration,
    # total time at sleep during sleep period
    "totalSleepTime": Duration,
    # total time spent at REM sleep during presence period
    "rem": Duration,
    # total time spent at LIGHT sleep during presence period
    "light": Duration,
    # total time spent at DEEP sleep during presence period
    "deep": Duration,
    # time from presence period start to fall asleep
    "sleepOnSetLatency": Duration,
    # total duration of time spent out of the bed during presence period
    "outOfBed": Duration,
    # number of bed exits
    "bedExitCount": int,
    # number of awakenings
    "awakeningCount": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A scored period of sleep
# @version 0.0.1


MeasureSleepScorePeriodRecord = {
    # Duration of the period
    "duration": Duration,
    # compound index of sleep quality (0-100). Constitutes from amount of sleep, deep and rem and awakenings
    "score": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The observed sleep state during a period of time
# @version 0.0.1


MeasureSleepStatePeriodRecord = {
    # The length of time of this epoch in which the measurements were taken
    "duration": Duration,
    # The sleeping state of the user (0->Wake, 1->Light, 2->Deep, 3->REM) for this period
    "state": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Steps observed during a period of time
# @version 0.0.1


MeasureStepPeriodRecord = {
    # The length of time of this epoch in which the measurements were taken
    "duration": Duration,
    # The number of steps made by the user during this period
    "steps": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The observed period of swimming
# @version 0.0.1


MeasureSwimPeriodRecord = {
    # The length of time of this epoch in which the measurements were taken
    "duration": Duration,
    # The number of laps that the user has gone during this period
    "laps": int,
    # The number of strokes recorded during this period
    "strokes": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A sensed vehicular trip
# @version 0.0.1


MeasureTripRecord = {
    # Duration of the trip
    "duration": Duration,
    # Vehicle used to make the trip
    "vehicle": VehicleRecord,
    # Distance of the trip in meters
    "distance": int,
    # Starting location of the trip
    "startLoc": CoordinateRecord,
    # Ending location of the trip
    "endLoc": CoordinateRecord,
    # Encoded path data of the trip
    "path": str,
    # Fuel cost in dollars
    "fuelCost": int,
    # Amount of fuel used in meters cubed
    "fuelVol": int,
    # Fuel efficiency in km per liter
    "avgKMpL": int,
    # Fuel efficiency in km per liter according to the EPA
    "avgFromEPAKMpL": int,
    # Driving score for events
    "scoreEvents": int,
    # Driving score for speeding
    "scoreSpeeding": int,
    # Number of hard brakes
    "hardBrakes": int,
    #  Number of hard accelerations
    "hardAccels": int,
    # Duration of trip spend over 70 mph
    "durOver70": Duration,
    # Duration of trip spend over 75 mph
    "durOver75": Duration,
    # Duration of trip spend over 80 mph
    "durOver80": Duration,
    # Duration of trip spent idling
    "idlingTime": Duration,
    # Timezone at the start of the trip
    "timezoneStart": str,
    # Timezone at the end of the trip
    "timezoneEnd": str,
    # Fraction of time spent in the city
    "cityFraction": int,
    # Fraction of time spent on the highway
    "highwayFraction": int,
    # Fraction of time spent driving at night
    "nightDrivingFraction": int,
    # The total number of trip points (uniformly sampled by time) on city roads. Total Points = ('pointsCityCount' + 'pointsHWYCount')
    "pointsCityCount": int,
    # The total number of trip points (uniformly sampled by time) on highways. Total Points = ('pointsCityCount' + 'pointsHWYCount')
    "pointsHWYCount": int,
    # The number of minor speeding events for city points in the trip
    "speedingCityMinorCount": int,
    # The number of major speeding events for city points in the trip
    "speedingCityMajorCount": int,
    # The number of minor speeding events for highway points in the trip
    "speedingHighwayMinorCount": int,
    # The number of major speeding events for highwayz points in the trip
    "speedingHighwayMajorCount": int,
    # The highest speed recorded during the trip - meters/sec
    "speedTop": int,
    # Price per gallon
    "fuelPPG": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A trip event
# @version 0.0.1


MeasureTripEventRecord = {
    # When the event occurred
    "stamp": datetime,
    # vehicle info
    "vehicle": VehicleRecord,
    # The current battery level of the vehicle
    "batteryLevel": int,
    # Distance of the trip in meters
    "distance": int,
    # Starting location of the trip
    "startLoc": CoordinateRecord,
    # Ending location of the trip
    "endLoc": CoordinateRecord,
    # Fuel cost in dollars
    "fuelCost": int,
    # Number of hard brakes
    "hardBrakes": int,
    #  Number of hard accelerations
    "hardAccels": int,
    # Duration of trip spent idling
    "idlingTime": Duration,
    # The total number of trip points (uniformly sampled by time) on city roads. Total Points = ('pointsCityCount' + 'pointsHWYCount')
    "pointsCityCount": int,
    # The total number of trip points (uniformly sampled by time) on highways. Total Points = ('pointsCityCount' + 'pointsHWYCount')
    "pointsHWYCount": int,
    # The number of minor speeding events for city points in the trip
    "speedingCityMinorCount": int,
    # The number of major speeding events for city points in the trip
    "speedingCityMajorCount": int,
    # The number of minor speeding events for highway points in the trip
    "speedingHighwayMinorCount": int,
    # The number of major speeding events for highwayz points in the trip
    "speedingHighwayMajorCount": int,
    # The highest speed recorded during the trip - meters/sec
    "speedTop": int,
    # Acceleration at event time
    "acceleration": int,
    # The quality of the GPS when the measurement was taken
    "gpsQuality": int,
    # The date and time at which the gps was recorded.
    "gpsStamp": datetime,
    # compass heading
    "heading": int,
    # Rotations per minute of the vehicle at this point
    "rpm": int,
    # velocity at event time
    "speed": int,
    # where the event occurred
    "location": CoordinateRecord,
    # The value of the tag
    "tag": str,
    # Lookup id number for type
    "typeID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A vehicle event measured by a sensor in the car
# @version 0.0.1


MeasureVehicleEventRecord = {
    # The vehicle this measure was take on
    "vehicle": VehicleRecord,
    # coordinates of the location
    "location": CoordinateRecord,
    # The g force felt during the event
    "gForce": int,
    # Acceleration at event time
    "acceleration": int,
    # The quality of the GPS when the measurement was taken
    "gpsQuality": int,
    # The date and time at which the gps was recorded.
    "gpsStamp": datetime,
    # compass heading
    "heading": int,
    # Rotations per minute of the vehicle at this point
    "rpm": int,
    # velocity at event time
    "speed": int,
    # Lookup id number for type
    "typeID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Vehicle malfunction indicator light
# @version 0.0.1


MeasureVehicleMilRecord = {
    # Malfunction indicator lamp code [scope:vehicle:profile]
    "code": str,
    # Indicates if the light is on [scope:vehicle:profile]
    "on": bool,
    #  Human readable description of the mil [scope:vehicle:profile]
    "description": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Information about a particular vehicle
# @version 0.0.1


MeasureVehicleStateRecord = {
    # The vehicle this measure was take on
    "vehicle": VehicleRecord,
    # Detected battery voltage on the vehicle
    "batteryVoltage": int,
    # Fuel level percent of the vehicle
    "fuelLevelPercent": int,
    # Currently active malfunction indicator lights on the vehicle
    "activeDTCs": [MeasureVehicleMilRecord],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A web search instance
# @version 0.0.1


MeasureWebSearchRecord = {
    # The search terms entered. The value is null if unable to detect the website.
    "terms": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A medication
# @version 0.0.1


MedicationRecord = {
    # The  unique identifier
    "id": APIID,
    # The medication name
    "name": str,
    # A description of the phone, i.e. only call after 5pm and before 9pm
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# medtracker device built and designed by Jon Hunt circa 2007
# @version 0.0.1


MedtrackerDeviceRecord = {
    # The macaddress of the device
    "macaddress": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Status report from the ORCATECH Medtracker
# @version 0.0.1


MedtrackerStatusRecord = {
    # The ORCATECH medtracker device that collected the data
    "device": MedtrackerDeviceRecord,
    # The number of seconds spent on battery power. This counter is reset when the battery dies or is removed and the device is unplugged.
    "batterySeconds": int,
    # ￼The number of door events that have been recorded. This counter is reset when the battery dies or is removed and the device is unplugged.
    "doors": int,
    # ￼The firmware on the device.
    "firmware": str,
    # When the device is unplugged, it will only power its bluetooth radio during panic periods. This is a unix timestamp in seconds indicating the end of the next panic period.
    "nextPanicEnd": datetime,
    # When the device is unplugged, it will only power its bluetooth radio during panic periods. This is a unix timestamp in seconds indicating the beginning of the next panic period.
    "nextPanicStart": datetime,
    # This a string representing the source of power. It will be either 'battery_power' or 'external_power'.
    "power": str,
    # The current time of the device as a unix timestamp in seconds.
    "deviceTime": datetime,
    # The current time of the system which collected the status as a unix timestamp in seconds.
    "systemTime": datetime,
    # The voltage being read from the external power source.
    "volts": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The state of the ORCATECH Medtracker's doors at a given point in time
# @version 0.0.1


MedtrackerReportStateRecord = {
    # The state of each door on the seven day pill box where '-' indicates closed and 'u' indicates open. There should be 7 characteracters in the string but data can be corrupted resulting in strings less than 7 characters long.
    "doors": str,
    # The device time as a unix timestamp in seconds in which the door states where recorded.
    "time": datetime,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Door state history report from the ORCATECH Medtracker
# @version 0.0.1


MedtrackerReportRecord = {
    # The ORCATECH medtracker device that collected the data.
    "status": MedtrackerStatusRecord,
    # The number of recorded states. This should be the length of the state array.
    "size": int,
    # The current time of the device as a unix timestamp in seconds.
    "deviceTime": datetime,
    # The current time of the system which collected the report as a unix timestamp in seconds.
    "systemTime": datetime,
    # The door state history of the medtracker.
    "states": [MedtrackerReportStateRecord],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# User credential for multi-facter authentication generated by WebAuthN
# @version 0.0.1

MfaWebauthnCredentialRecord = {
    # The base64 URL encoding of the public key portion of a Relying Party-specific credential key pair, generated by an authenticator and returned to a Relying Party at registration time (see also public key credential). The private key portion of the credential key pair is known as the credential private key. Note that in the case of self attestation, the credential key pair is also used as the attestation key pair.
    "publicKey": str,
    # The  unique identifier
    "id": APIID,
    # The base64 URL encoding of a probabilistically-unique byte sequence identifying a public key credential source and its authentication assertions.
    "credentialID": str,
    # The attestation format used (if any) by the authenticator when creating the credential. A value of none indicates that the server did not care about attestation. A value of indirect means that the server allowed for anonymized attestation data. direct means that the server wished to receive the attestation data from the authenticator.
    "attestationType": str,
    # The AAGUID of the authenticator. An AAGUID is defined as an array containing the globally unique identifier of the authenticator model being sought.
    "authenticatorAAGUID": str,
    # Upon a new login operation, the Relying Party compares the stored signature counter value with the new signCount value returned in the assertion’s authenticator data. If this new signCount value is less than or equal to the stored value, a cloned authenticator may exist, or the authenticator may be malfunctioning.
    "authenticatorSignCount": int,
    # This is a signal that the authenticator may be cloned, i.e. at least two copies of the credential private key may exist and are being used in parallel. Relying Parties should incorporate this information into their risk scoring. Whether the Relying Party updates the stored signature counter value in this case, or not, or fails the authentication ceremony or not, is Relying Party-specific.
    "authenticatorCloneWarning": bool,
    # Either platform or cross platform. See: https://w3c.github.io/webauthn/#sctn-authenticator-attachment-modality
    "authenticationAttachment": str,
    # The operating system name as determined by the user agent string when registering
    "operatingSystemFamily": str,
    # The operating system version as determined by the user agent string when registering
    "operatingSystemVersion": str,
    # The device family as determined by the user agent string when registering
    "deviceFamily": str,
    # The device model as determined by the user agent string when registering
    "deviceModel": str,
    # The device brand as determined by the user agent string when registering
    "deviceBrand": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for user
    "userID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


# A change history of the observation.
# @version 0.0.1


MicroserviceChangeRecord = {
    # The time at which the change was made by the microservice
    "stamp": datetime,
    # The microservice that made the change
    "microservice": MicroserviceRecord,
    # True if the change is a creation
    "created": bool,
    # True if the change is an update
    "updated": bool,
    # True if the change is a deletion
    "deleted": bool,
    # Map of meta fields that were changed with the key being the field name and the value being the previous value of the field in json
    "metaFields": Dict[str, str],
    # Map of meta fields that were changed with the key being the field name and the value being the previous value of the field in json
    "dataFields": Dict[str, str],
    # Lookup id number for user
    "userID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The migration state of a platform component
# @version 0.0.1


MigrationStateRecord = {
    # The  unique identifier
    "id": APIID,
    # The current version of the data
    "version": str,
    # The current version of the code
    "nextVersion": str,
    # A description of the current status
    "status": str,
    # The platform component type
    "type": str,
    # The platform component sub type
    "subType": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A milestone to track achievement
# @version 0.0.1

MilestoneRecord = {
    # The unique identifier
    "id": APIID,
    # The date at which the milestone is to be met
    "stop": datetime,
    # The desired number to reach for this milestone to be completed
    "desired": int,
    # The actual number achieved for this milestone
    "actual": int,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for state
    "stateID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id number for study
    "studyID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The state of a milestone.
# @version 0.0.1


MilestoneStateRecord = {
    # A short descriptive name of the animal type
    "name": str,
    # The unique identifier
    "id": APIID,
    # A description of the animal type
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for milestones
    "milestoneIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A type of milestone.
# @version 0.0.1


MilestoneTypeRecord = {
    # A short descriptive name of the animal type
    "name": str,
    # The unique identifier
    "id": APIID,
    # A description of the animal type
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for milestones
    "milestoneIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A one time token used to prevent replay attacks
# @version 0.0.1


NonceRecord = {
    # A base64 representation of the nonce value
    "base64": str,
    # The unique identifier
    "id": APIID,
    # The time at which this nonce was generated
    "stamp": datetime,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# NYCE sensor events collected over a zigbee network. See http://nycesensors.com
# @version 0.0.1


NyceEventRecord = {
    # A timestamp indicating the time at which the event occurred
    "stamp": datetime,
    # The unique mac address of the nyce sensor which triggered the event
    "macaddress": str,
    # A bitmask representing the event that occurred as well as the state of the device. See http://www.zigbee.org/zigbee-for-developers/applicationstandards/zigbeehomeautomation/
    "event": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Contextual information about an alert event
# @version 0.0.1


ObservationGenericEventAlertMetaRecord = {
    # The item was not working correctly and data generated from the item should be ignored
    "itemInactive": bool,
    # Null if the microservice hasn't populated value, empty string if no applicable or could not be determined
    "firmware": str,
    # doc
    "batteryLevel": int,
    # Lookup id number for item
    "itemID": APIID,
    # Lookup id number for hubItem
    "hubItemID": APIID,
    # Lookup id numbers for itemTags
    "itemTagIDs": [APIID],
    # Lookup id number for itemState
    "itemStateID": APIID,
    # Lookup id number for home
    "homeID": APIID,
    # Lookup id number for homeDwelling
    "homeDwellingID": APIID,
    # Lookup id numbers for homeSubjects
    "homeSubjectIDs": [APIID],
    # Lookup id numbers for homeResidents
    "homeResidentIDs": [APIID],
    # Lookup id numbers for homeAnimals
    "homeAnimalIDs": [APIID],
    # Lookup id numbers for homeTags
    "homeTagIDs": [APIID],
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id numbers for subjectTags
    "subjectTagIDs": [APIID],
    # Lookup id numbers for subjectHomes
    "subjectHomeIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id number for area
    "areaID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Contextual information about an status event
# @version 0.0.1


ObservationGenericEventStatusMetaRecord = {
    # The item was not working correctly and data generated from the item should be ignored
    "itemInactive": bool,
    # Null if the microservice hasn't populated value, empty string if no applicable or could not be determined
    "firmware": str,
    # doc
    "batteryLevel": int,
    # Lookup id number for item
    "itemID": APIID,
    # Lookup id number for hubItem
    "hubItemID": APIID,
    # Lookup id numbers for itemTags
    "itemTagIDs": [APIID],
    # Lookup id number for itemState
    "itemStateID": APIID,
    # Lookup id number for home
    "homeID": APIID,
    # Lookup id number for homeDwelling
    "homeDwellingID": APIID,
    # Lookup id numbers for homeSubjects
    "homeSubjectIDs": [APIID],
    # Lookup id numbers for homeResidents
    "homeResidentIDs": [APIID],
    # Lookup id numbers for homeAnimals
    "homeAnimalIDs": [APIID],
    # Lookup id numbers for homeTags
    "homeTagIDs": [APIID],
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id numbers for subjectTags
    "subjectTagIDs": [APIID],
    # Lookup id numbers for subjectHomes
    "subjectHomeIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id number for area
    "areaID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An meta data about platform storage events
# @version 0.0.1


ObservationGenericEventStorageMetaRecord = {
    # A timestamp indicating when the event was marked as having occurred on. This is different from the observation stamp in that the observation stamp is when the event was generated
    "occurredOn": datetime,
    # The schema of the record field
    "recordSchema": SchemaRecord,
    # The record that was changed
    "record": any,
    # The schema of the related field
    "relatedSchema": SchemaRecord,
    # The related record that was changed
    "related": [any],
    # The field name of the record that contained the relationship to the related record
    "recordField": str,
    # The field name of the related record that contained the relationship to the record
    "relatedField": str,
    # If this was type `update` then this array will contain the fields that changed
    "changedFields": [EventChangeFieldRecord],
    # Lookup id number for user
    "userID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Contextual information about a sensor measurement
# @version 0.0.1


ObservationGenericMeasureMetaRecord = {
    # The item was not working correctly and data generated from the item should be ignored
    "itemInactive": bool,
    # Null if the microservice hasn't populated value, empty string if no applicable or could not be determined
    "firmware": str,
    # doc
    "batteryLevel": int,
    # UUID from vendor data that this generic data is derived from
    "vendorUUID": str,
    # vendor data schema that this generic data is derived from
    "vendorDataSchema": SchemaRecord,
    # Lookup id number for item
    "itemID": APIID,
    # Lookup id number for hubItem
    "hubItemID": APIID,
    # Lookup id numbers for itemTags
    "itemTagIDs": [APIID],
    # Lookup id number for itemState
    "itemStateID": APIID,
    # Lookup id number for home
    "homeID": APIID,
    # Lookup id number for homeDwelling
    "homeDwellingID": APIID,
    # Lookup id numbers for homeSubjects
    "homeSubjectIDs": [APIID],
    # Lookup id numbers for homeResidents
    "homeResidentIDs": [APIID],
    # Lookup id numbers for homeAnimals
    "homeAnimalIDs": [APIID],
    # Lookup id numbers for homeTags
    "homeTagIDs": [APIID],
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id numbers for subjectTags
    "subjectTagIDs": [APIID],
    # Lookup id numbers for subjectHomes
    "subjectHomeIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id number for area
    "areaID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Contextual information about an administered test
# @version 0.0.1


ObservationGenericReportMetaRecord = {
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id numbers for subjectTags
    "subjectTagIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Display information about a survey administered by Qualtrics
# @version 0.0.1


SurveyQuestionChoiceRecord_old = {
    # TODO
    "recode": str,
    # TODO
    "description": str,
    # TODO
    "text": str,
    # TODO
    "imageDescription": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


class SurveyQuestionChoiceRecord(TypedDict):
    # TODO
    recode: str
    # TODO
    description: str
    # TODO
    text: str
    # TODO
    imageDescription: str
    # If true, indicates that the record is frozen
    isFrozen: bool


# Display information about a survey administered by Qualtrics
# @version 0.0.1


SurveyQuestionRecord_old = {
    # The type of question.
    "type": str,
    # The text displayed to the user
    "text": str,
    # The question label
    "label": str,
    # The question key
    "name": str,
    # The possible choices for a question
    "choices": Dict[str, SurveyQuestionChoiceRecord],
    # The possible follow up questions for a question
    "subQuestions": Dict[str, SurveyQuestionChoiceRecord],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


class SurveyQuestionRecord(TypedDict):
    # The type of question.
    type: str
    # The text displayed to the user
    text: str
    # The question label
    label: str
    # The question key
    name: str
    # The possible choices for a question
    choices: Dict[str, SurveyQuestionChoiceRecord]
    # The possible follow up questions for a question
    subQuestions: Dict[str, SurveyQuestionChoiceRecord]
    # If true indicates that the record is frozen
    isFrozen: bool


# Display information about a survey
# @version 0.0.1


SurveyFormRecord = {
    # The timestamp in which the survey was created
    "createdAt": datetime,
    # The questions object contains information about the questions that make up your survey keyed by their identifier
    "questions": Dict[str, SurveyQuestionRecord],
    # The flow array represents the order of items that make up the survey.
    "flow": [str],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Contextual information about an administered survey
# @version 0.0.1


ObservationGenericSurveyMetaRecord = {
    # An identifier used to link life events generated from the original healthforms (2007 to ~2014)
    "healthFormID": int,
    # The structure of the survey given
    "form": SurveyFormRecord,
    # The medium in which the survey was given. i.e. web browser, app, paper
    "medium": str,
    # The name of the person who assisted in completing the survey.
    "assistedBy": str,
    # The operating system name of the device used to administer the survey
    "operatingSystemFamily": str,
    # The operating system version of the device used to administer the survey
    "operatingSystemVersion": str,
    # The device family of the device used to administer the survey
    "deviceFamily": str,
    # The device model of the device used to administer the survey
    "deviceModel": str,
    # The device brand of the device used to administer the survey
    "deviceBrand": str,
    # The raw user agent string if it was administered over a web browser
    "userAgent": str,
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id numbers for subjectTags
    "subjectTagIDs": [APIID],
    # Lookup id number for user
    "userID": APIID,
    # Lookup id numbers for userTags
    "userTagIDs": [APIID],
    # Lookup id number for survey
    "surveyID": APIID,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Contextual information about an administered test
# @version 0.0.1


ObservationGenericTestMetaRecord = {
    # The version of the test administered
    "version": str,
    # The medium in which the test was given. i.e. web browser, app, paper
    "medium": str,
    # The userid of the person who administered the test.
    "administeredBy": int,
    # The operating system name of the device used to administer the test
    "operatingSystemFamily": str,
    # The operating system version of the device used to administer the test
    "operatingSystemVersion": str,
    # The device family of the device used to administer the test
    "deviceFamily": str,
    # The device model of the device used to administer the test
    "deviceModel": str,
    # The device brand of the device used to administer the test
    "deviceBrand": str,
    # The raw user agent string if it was administered over a web browser
    "userAgent": str,
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id numbers for subjectTags
    "subjectTagIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Vendor specific testing data
# @version 0.0.1


ObservationVendorRecord = {
    # This is not an identifier from a database but a concatenated list of fields that uniquely identify the data
    "uuid": str,
    # The timestamp at which the survey takes place
    "stamp": datetime,
    # The partition bucket that the measure is stored in
    "bucket": str,
    # The schema of the measurement details
    "dataSchema": SchemaRecord,
    # The time series data in vendor specific format
    "data": any,
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id number for study
    "studyID": APIID,
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id number for home
    "homeID": APIID,
    # Lookup id number for item
    "itemID": APIID,
    # Lookup id number for hubItem
    "hubItemID": APIID,
    # Lookup id number for user
    "userID": APIID,
    # Lookup id number for survey
    "surveyID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An is a managing group which maintains it's own roles and users.
# @version 0.0.1


OrganizationRecord = {
    # A short descriptive name for the organization
    "name": str,
    # The  unique identifier
    "id": APIID,
    # The long description of the organization
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # When the record was updated
    "updatedAt": datetime,
    # When the record was deleted
    "deletedAt": datetime,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for plugins
    "pluginIDs": [APIID],
    # Lookup id numbers for roles
    "roleIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An external identifier for the organization to map the it's data to an external database
# @version 0.0.1


OrganizationIdentifierRecord = {
    # The identification string
    "value": str,
    # The unique identifier
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A type of external identifier for the organization to map the it's data to an external database
# @version 0.0.1


OrganizationIdentifierTypeRecord = {
    # A short unique name to categorize the identifiers
    "name": str,
    # The unique identifier
    "id": APIID,
    # A description of the external database
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for identifiers
    "identifierIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The status of the organization
# @version 0.0.1


OrganizationStatusRecord = {
    # The number of connected hubs belonging to the organization
    "connectedHubs": int,
    # The number of connected hubs belonging to the organization that are also assigned
    "connectedAssignedHubs": int,
    # A map where the key is the firmware version and the value is the number of items with that version
    "firmware": Dict[str, int],
    # A map where the key is the alert type id and the value is the number of active alerts with that type
    "alerts": Dict[str, int],
    # The number of active alerts for the organization
    "alertCount": int,
    # A map where the key is the data schema and the value is the time of the last data point
    "lastDataPoint": Dict[str, datetime],
    # A map where the key is the data schema and the value is the total number of data points
    "totalDataPoints": Dict[str, int],
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The allele of the APOE gene. This will be one of E2, E3, E4.
# @version 0.0.1


PathologyApoeAlleleRecord = {
    # This will be one of E2, E3, E4.
    "name": str,
    # The unique identifier for the record
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for summaries
    "summaryIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Autopsy results of the hemisphere
# @version 0.0.1


PathologyAutopsyRecord = {
    # Tissue ID
    "bfo": int,
    # The unique identifier for the record
    "id": APIID,
    # TODO
    "hospitalReportNumber": int,
    # TODO
    "frozenTissue": int,
    # TODO
    "deathStamp": datetime,
    # TODO
    "ageAtDeath": int,
    # TODO
    "postmortemInterval": int,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for caseType
    "caseTypeID": APIID,
    # Lookup id number for gender
    "genderID": APIID,
    # Lookup id number for autopsyHemisphere
    "autopsyHemisphereID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id number for clinicalSummary
    "clinicalSummaryID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Stain used on a piece of tissue
# @version 0.0.1


PathologyAutopsyCaseTypeRecord = {
    # Key to stain or protocol
    "name": str,
    # The unique identifier for the record
    "id": APIID,
    # A description of the stain.
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for autopsies
    "autopsyIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Autopsy results of the hemisphere
# @version 0.0.1


PathologyAutopsyHemisphereRecord = {
    # Tissue ID
    "bfo": int,
    # The unique identifier for the record
    "id": APIID,
    # TODO
    "atherosclerosis": int,
    # TODO
    "neuriticPlaqueScore": int,
    # TODO
    "difusePlaqueScore": int,
    # TODO
    "braakStage": int,
    # TODO
    "midbrainLewyBodies": int,
    # TODO
    "limbicLewyBodies": int,
    # TODO
    "neocorticalLewyBodies": int,
    # TODO
    "arteriolosclerosis": int,
    # TODO
    "neocorticalMicrovascularLesions": int,
    # TODO
    "deepMicrovascularLesions": int,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for diagnoses
    "diagnosisIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for hemisphere
    "hemisphereID": APIID,
    # Lookup id number for autopsy
    "autopsyID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Summary clinical information generated from 4D
# @version 0.0.1


PathologyClinicalSummaryRecord = {
    # The unique identifier for the tissue sample. TODO: is this correct? or is the uid for the hemi?
    "bfo": int,
    # Unique identifier for the subject from the 4D database
    "adc": int,
    # The unique identifier for the record
    "id": APIID,
    # The recorded age at death.
    "ageAtDeath": int,
    # The recorded age of onset of dementia.
    "ageAtOnset": int,
    # How many years of schooling the subject had
    "yearsSchool": int,
    # Do postmortem pathology diagnosis findings support clinical diagnosis
    "diagnosisSupported": bool,
    # The recorded age at most recent clinical visit and diagnosis.
    "diagnosisAge": int,
    # The number of clinical visits
    "visitCount": int,
    # The most recent result of the mini-mental state exam
    "mmse": int,
    # The age at which the last mini-mental state exam was done
    "mmseAge": int,
    # The number of mini-mental state exams the subject has taken
    "mmseCount": int,
    # The most recent result of the Montreal Cognitive Assessment
    "moca": int,
    # The age at which the last Montreal Cognitive Assessment was done
    "mocaAge": int,
    # The number of Montreal Cognitive Assessments the subject has taken
    "mocaCount": int,
    # The most recent result of the Clinical Dementia Rating
    "cdr": int,
    # The age at which the last Clinical Dementia Rating was done
    "cdrAge": int,
    # The number of Clinical Dementia Ratings the subject has been given
    "cdrCount": int,
    # The number of nueropsych evaluations given to the subject
    "neuropsychEvals": int,
    # The number of nueropsych exams given to the subject
    "neuropsychExams": int,
    # TODO: ?
    "htn": bool,
    # TODO: ?
    "mi": bool,
    # TODO: ?
    "cad": bool,
    # TODO: ?
    "afib": bool,
    # TODO: ?
    "stroke": bool,
    # TODO: ?
    "tia": bool,
    # TODO: ?
    "hypercholesterolemia": bool,
    # TODO: ?
    "diabetes": bool,
    # TODO: ?
    "smoking": bool,
    # The number of in vivo scans taken at the AIRC with a 3T machine
    "scanCountAIRC3T": int,
    # The number of in vivo scans taken at the Hospital with a 3T machine
    "scanCountHospital3T": int,
    # The number of in vivo scans taken on a non 3T machine
    "scanCountNon3T": int,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for diagnosisClinical
    "diagnosisClinicalIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for diagnosisAtLastVisit
    "diagnosisAtLastVisitID": APIID,
    # Lookup id number for apoeAllele1
    "apoeAllele1ID": APIID,
    # Lookup id number for apoeAllele2
    "apoeAllele2ID": APIID,
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id number for hemisphere
    "hemisphereID": APIID,
    # Lookup id number for autopsy
    "autopsyID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Stain used on a piece of tissue
# @version 0.0.1


PathologyDiagnosisAutopsyHemisphereRecord = {
    # Abbreviation of the name
    "abbreviation": str,
    # The full name of the diagnosis
    "name": str,
    # The unique identifier for the record
    "id": APIID,
    # A description of the diagnosis.
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for autopsyHemispheres
    "autopsyHemisphereIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A clinical pathology diagnosis type
# @version 0.0.1


PathologyDiagnosisTypeClinicalRecord = {
    # The name of the diagnosis
    "name": str,
    # The unique identifier for the record
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for summaries
    "summaryIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A pathology diagnosis type given during an in person visit
# @version 0.0.1


PathologyDiagnosisTypeVisitRecord = {
    # The name of the diagnosis
    "name": str,
    # The unique identifier for the record
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for summaries
    "summaryIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Cassette level data
# @version 0.0.1


PathologyHemisphereRecord = {
    # Tissue ID
    "bfo": int,
    # The unique identifier for the record
    "id": APIID,
    # If true, the hemisphere has been sliced, false otherwise.
    "sliced": bool,
    # Optional notes
    "notes": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for issues
    "issueIDs": [APIID],
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id numbers for scans
    "scanIDs": [APIID],
    # Lookup id numbers for slices
    "sliceIDs": [APIID],
    # Lookup id numbers for masks
    "maskIDs": [APIID],
    # Lookup id number for montage
    "montageID": APIID,
    # Lookup id number for autopsyHemisphere
    "autopsyHemisphereID": APIID,
    # Lookup id number for clinicalSummary
    "clinicalSummaryID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Cassette level data
# @version 0.0.1


PathologyHemisphereCassetteRecord = {
    # Tissue ID
    "bfo": int,
    # Cassette ID (A-M or 1 to 20)
    "cassetteLabel": str,
    # The unique identifier for the record
    "id": APIID,
    # Perivascular WMH in cassette_data
    "perivascularWMH": bool,
    # Deep WMH in cassette
    "deepWMH": bool,
    # WM PVS in cassette
    "perivascularWM": bool,
    # Basal ganglia perivascular in cassette
    "perivascularBasal": bool,
    # Small vessel infarct in cassette
    "smallVesselInfarct": bool,
    # If true, the cassette has been cut into slides, false otherwise
    "slidesCut": bool,
    # Optional notes
    "notes": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for issues
    "issueIDs": [APIID],
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for processing
    "processingID": APIID,
    # Lookup id number for registration
    "registrationID": APIID,
    # Lookup id number for regionMapImage
    "regionMapImageID": APIID,
    # Lookup id numbers for regionImages
    "regionImageIDs": [APIID],
    # Lookup id numbers for registeredImages
    "registeredImageIDs": [APIID],
    # Lookup id numbers for referenceImages
    "referenceImageIDs": [APIID],
    # Lookup id number for slice
    "sliceID": APIID,
    # Lookup id numbers for slides
    "slideIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Cassette level data
# @version 0.0.1


PathologyHemisphereSliceRecord = {
    # Tissue ID
    "bfo": int,
    # The unique identifier for the record
    "id": APIID,
    # If true, the slice has been cassetted, false otherwise
    "cassetted": bool,
    # TODO: ?
    "acSlice": int,
    # Optional notes
    "notes": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for issues
    "issueIDs": [APIID],
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for hemisphere
    "hemisphereID": APIID,
    # Lookup id numbers for cassettes
    "cassetteIDs": [APIID],
    # Lookup id numbers for scans
    "scanIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Slides level data
# @version 0.0.1


PathologyHemisphereSlideRecord = {
    # Tissue ID
    "bfo": int,
    # Cassette ID (A-M or 1 to 20)
    "cassetteLabel": str,
    # Cassette ID (A-M or 1 to 20)
    "slideKey": str,
    # The unique identifier for the record
    "id": APIID,
    # The timestamp at which the slide was stained
    "stainedOn": datetime,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for issues
    "issueIDs": [APIID],
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for stain
    "stainID": APIID,
    # Lookup id number for cassette
    "cassetteID": APIID,
    # Lookup id number for processing
    "processingID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Information about a hemisphere cassette image.
# @version 0.0.1


PathologyImageHemisphereCassetteRecord = {
    # The path to the image file
    "path": str,
    # The unique identifier for the record
    "id": APIID,
    # The unique identifier for the tissue sample. Links the mask to the correct hemisphere.
    "bfo": int,
    # Cassette ID (A-M or 1 to 20)
    "cassetteLabel": str,
    # The path to a thumbnail of the montage file
    "pathThumb": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for cassette
    "cassetteID": APIID,
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Information about a hemisphere cassette image.
# @version 0.0.1


PathologyImageHemisphereCassetteMapRegionRecord = {
    # The path to the image file
    "path": str,
    # The unique identifier for the record
    "id": APIID,
    # The unique identifier for the tissue sample. Links the mask to the correct hemisphere.
    "bfo": int,
    # Cassette ID (A-M or 1 to 20)
    "cassetteLabel": str,
    # The path to a thumbnail of the montage file
    "pathThumb": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for cassette
    "cassetteID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Information about a hemisphere cassette image with a stain.
# @version 0.0.1


PathologyImageHemisphereCassetteStainRecord = {
    # The path to the image file
    "path": str,
    # The unique identifier for the record
    "id": APIID,
    # The unique identifier for the tissue sample. Links the mask to the correct hemisphere.
    "bfo": int,
    # Cassette ID (A-M or 1 to 20)
    "cassetteLabel": str,
    # The path to a thumbnail of the montage file
    "pathThumb": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for cassette
    "cassetteID": APIID,
    # Lookup id number for stain
    "stainID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Information about a region of interest within the hemisphere cassette image that has been stained.
# @version 0.0.1


PathologyImageHemisphereCassetteStainRegionRecord = {
    # The path to the image file
    "path": str,
    # The unique identifier for the record
    "id": APIID,
    # The unique identifier for the tissue sample. Links the mask to the correct hemisphere.
    "bfo": int,
    # Cassette ID (A-M or 1 to 20)
    "cassetteLabel": str,
    # The path to a thumbnail of the montage file
    "pathThumb": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for cassette
    "cassetteID": APIID,
    # Lookup id number for stain
    "stainID": APIID,
    # Lookup id number for region
    "regionID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A region of interest
# @version 0.0.1


PathologyImageHemisphereCassetteTypeRecord = {
    # Key to stain or protocol
    "name": str,
    # The unique identifier for the record
    "id": APIID,
    # A description of the stain.
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for images
    "imageIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Masking information about the hemisphere's white matter, gray matter and white matter hyper intensity
# @version 0.0.1


PathologyMaskHemisphereRecord = {
    # The unique identifier for the tissue sample. Links the mask to the correct hemisphere
    "bfo": int,
    # The unique identifier for the record
    "id": APIID,
    # The white matter filename. A null value indicates that the file does not exist
    "pathWhiteMatter": str,
    # The grey hatter filename. A null value indicates that the file does not exist
    "pathGrayMatter": str,
    # The white matter hyper intensity filename. A null value indicates that the file does not exist
    "pathWhiteMatterHyperIntensity": str,
    # True indicates that all slice steps are completed
    "completed": bool,
    # Optional notes about the mask
    "notes": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for hemisphere
    "hemisphereID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A region of interest
# @version 0.0.1


PathologyRegionRecord = {
    # Key to stain or protocol
    "name": str,
    # The unique identifier for the record
    "id": APIID,
    # A description of the stain.
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for images
    "imageIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# T2-IHC Registration
# @version 0.0.1


PathologyRegistrationHemisphereCassetteRecord = {
    # The unique identifier for tissue samples
    "bfo": int,
    # The unique identifier for cassette samples
    "cassetteLabel": str,
    # The unique identifier for the record
    "id": APIID,
    # Directory holding the registration files
    "path": str,
    # Flag indicating all slice-hemisphere registration steps are complete
    "completed": bool,
    # Optional notes
    "notes": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for files
    "fileIDs": [APIID],
    # Lookup id number for cassette
    "cassetteID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# T2-IHC Registration File
# @version 0.0.1


PathologyRegistrationHemisphereCassetteFileRecord = {
    # Path to the cassette registration file
    "path": str,
    # The unique identifier for the record
    "id": APIID,
    # The unique identifier for tissue samples
    "bfo": int,
    # The unique identifier for cassette samples
    "cassetteLabel": str,
    # Optional notes
    "notes": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for registrationCassette
    "registrationCassetteID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Hemisphere information processed by Core #1
# @version 0.0.1


PathologyRegistrationHemisphereSliceRecord = {
    # The unique identifier for tissue samples
    "bfo": int,
    # The unique identifier for the record
    "id": APIID,
    # Directory holding the registration files
    "path": str,
    # Name of registered hemi file
    "pathHemisphere": str,
    # Name of final slices file
    "pathSlices": str,
    # Name of registered WM mask file
    "pathWhiteMatterMask": str,
    # Name of registered GM mask file
    "pathGrayMatterMask": str,
    # Name of registered WMH mask file
    "pathWhiteMatterHyperIntensityMask": str,
    # Flag indicating all slice-hemisphere registration steps are complete
    "completed": bool,
    # Optional notes
    "notes": str,
    # Location of log file
    "pathLog": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for scanHemisphere
    "scanHemisphereID": APIID,
    # Lookup id number for scanSlice
    "scanSliceID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Information about a scan of the brain hemisphere
# @version 0.0.1


PathologyScanHemisphereRecord = {
    # File name of the hemisphere DICOM scans
    "path": str,
    # The unique identifier for the record
    "id": APIID,
    # The unique identifier for the tissue sample. TODO: is this correct? or is the uid for the hemi?
    "bfo": int,
    # The timestamp of hemisphere DICOM scan
    "stamp": datetime,
    # The hemisphere scan has been completed. TODO: what does this really mean?
    "completed": bool,
    # Optional notes about the scan
    "notes": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for processing
    "processingID": APIID,
    # Lookup id number for registration
    "registrationID": APIID,
    # Lookup id number for hemisphere
    "hemisphereID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Information about a scan of the brain hemisphere
# @version 0.0.1


PathologyScanHemisphereSliceRecord = {
    # The unique identifier for the tissue sample. TODO: is this correct? or is the uid for the hemi?
    "bfo": int,
    # File name of the hemisphere DICOM scans
    "path": str,
    # The unique identifier for the record
    "id": APIID,
    # The timestamp of hemisphere DICOM scan
    "stamp": datetime,
    # The first slab in the scan
    "slabStartID": int,
    # The last slab in the scan
    "slabStopID": int,
    # The hemisphere scan has been completed. TODO: what does this really mean?
    "completed": bool,
    # Optional notes about the scan
    "notes": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for processing
    "processingID": APIID,
    # Lookup id number for registration
    "registrationID": APIID,
    # Lookup id number for slice
    "sliceID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Hemisphere information processed by Core #1
# @version 0.0.1


PathologyScanProcessingHemisphereRecord = {
    # The unique identifier for tissue samples
    "bfo": int,
    # Full path of the T2 file
    "pathT2": str,
    # The unique identifier for the record
    "id": APIID,
    # Path to processing files
    "path": str,
    # All slice preprocessing steps are completed
    "completed": bool,
    # Optional preprocessing notes about the hemisphere scan
    "notes": str,
    # Version describing preprocessing that was done on the scan
    "version": int,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for scanHemisphere
    "scanHemisphereID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Cassette processing information
# @version 0.0.1


PathologyScanProcessingHemisphereCassetteRecord = {
    # The unique identifier for the record
    "id": APIID,
    # The unique identifier for tissue samples
    "bfo": int,
    # The unique identifier for cassette samples
    "cassetteLabel": str,
    # All cassette preprocessing steps are completed
    "completed": bool,
    # Path to the trichrome file for the cassette
    "trichromePath": str,
    # Path to the helfb file for the cassette
    "helfbPath": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for cassette
    "cassetteID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Hemisphere information processed by Core #1
# @version 0.0.1


PathologyScanProcessingHemisphereSliceRecord = {
    # The unique identifier for tissue samples
    "bfo": int,
    # Full path of the T2 file
    "pathT2": str,
    # The unique identifier for the record
    "id": APIID,
    # Directory of preprocessed NIFTI files
    "path": str,
    # All slice preprocessing steps are completed
    "completed": bool,
    # Optional preprocessing notes about the hemisphere scan
    "notes": str,
    # Version describing preprocessing that was done on the scan
    "version": int,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for scanSlice
    "scanSliceID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Hemisphere information processed by Core #1
# @version 0.0.1


PathologyScanProcessingHemisphereSlideRecord = {
    # The unique identifier for tissue samples
    "bfo": int,
    # The unique identifier for cassette samples
    "cassetteLabel": str,
    # The unique identifier for stain samples
    "slideKey": str,
    # Path to the processing files directory
    "path": str,
    # The unique identifier for the record
    "id": APIID,
    # Path to CZI file
    "pathCZI": str,
    # Path to down sampled PNG file
    "pathPNG": str,
    # Path to archived PNG file
    "pathArchive": str,
    # All slice processing steps are completed
    "completed": bool,
    # Optional preprocessing notes about the hemisphere scan
    "notes": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for slide
    "slideID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Information about hemisphere montage images. If all paths are null then the BFO exists in the montage directory but none of the filenames match the expected values.
# @version 0.0.1


PathologyScanProcessingMontageRecord = {
    # The unique identifier for the tissue sample. Links the mask to the correct hemisphere.
    "bfo": int,
    # The unique identifier for the record
    "id": APIID,
    # The path to the montage file
    "path": str,
    # The path to a thumbnail of the montage file
    "pathThumb": str,
    # The path to the montage file with ROIs marked
    "pathROI": str,
    # The path to a thumbnail of the montage file
    "pathROIThumb": str,
    # The path to the montage file with ROIs marked on box
    "pathBox": str,
    # True if the montage with ROIs has been reviewed, false otherwise
    "reviewed": bool,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for hemisphere
    "hemisphereID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Stain used on a piece of tissue
# @version 0.0.1


PathologyStainRecord = {
    # Key to stain or protocol
    "name": str,
    # The unique identifier for the record
    "id": APIID,
    # A description of the stain.
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for slides
    "slideIDs": [APIID],
    # Lookup id numbers for regionImages
    "regionImageIDs": [APIID],
    # Lookup id numbers for cassetteImages
    "cassetteImageIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A tag used to categorize a set of pathology tissues
# @version 0.0.1


PathologyTagRecord = {
    # The unique identifier
    "id": APIID,
    # A unique name for the tag
    "name": str,
    # A longer description of the tag
    "description": str,
    # A hexidecimal representation of a color for this tag
    "color": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for hemispheres
    "hemisphereIDs": [APIID],
    # Lookup id numbers for hemisphereSlices
    "hemisphereSliceIDs": [APIID],
    # Lookup id numbers for hemisphereCassettes
    "hemisphereCassetteIDs": [APIID],
    # Lookup id numbers for hemisphereSlides
    "hemisphereSlideIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An endpoint permission
# @version 0.0.1


PermissionRecord = {
    # A short descriptive name of the permission
    "name": str,
    # The unique identifier
    "id": APIID,
    # The long description of the permission
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for roles
    "roleIDs": [APIID],
    # Lookup id number for endpoint
    "endpointID": APIID,
    # Lookup id number for action
    "actionID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An api action
# @version 0.0.1


PermissionActionRecord = {
    # A short descriptive name of the permission action
    "name": str,
    # The unique identifier
    "id": APIID,
    # The long description of the permission action
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for permissions
    "permissionIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An api endpoint
# @version 0.0.1


PermissionEndpointRecord = {
    # The name of the record schema being served by the endpoint
    "recordSchema": str,
    # The unique identifier
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for plugins
    "pluginIDs": [APIID],
    # Lookup id numbers for permissions
    "permissionIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# This schema is differs from a subject in that this individual is not enrolled as part of the study but whose presence should be known about
# @version 0.0.1


PersonRecord = {
    # The unique identifier
    "id": APIID,
    # An identifying name of the resident
    "name": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for homes
    "homeIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # Lookup id numbers for comments
    "commentIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A note or comment about the subject
# @version 0.0.1


PersonCommentRecord = {
    # The  unique identifier
    "id": APIID,
    # The timestamp when the comment was made
    "stamp": datetime,
    # The content of the comment
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for person
    "personID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A phone number
# @version 0.0.1


PhoneRecord = {
    # The  unique identifier
    "id": APIID,
    # The phone number
    "number": str,
    # A description of the phone, i.e. only call after 5pm and before 9pm
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id number for home
    "homeID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A type of phone number
# @version 0.0.1


PhoneTypeRecord = {
    # A descriptive name for the type
    "name": str,
    # The  unique identifier
    "id": APIID,
    # A short description of the type
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for phones
    "phoneIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A feature set of the system. When associated with a particular study or organization, the feature set endpoints will be available
# @version 0.0.1


PluginRecord = {
    # A descriptive name of the integration
    "name": str,
    # The unique identifier
    "id": APIID,
    # True if the plugin is enabled by the instance for organizations to use, false otherwise
    "enabled": bool,
    # Details about the integration
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for endpoints
    "endpointIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Coordinate location and associated image
# @version 0.0.1


TestNeuropsychImagerecogCoordRecord = {
    # The row number of the image.
    "row": int,
    # The column number of the image.
    "col": int,
    # An optional image associated with this coordinate. This will be the image file name or an empty string.
    "img": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# The context and coordinate information about a user's selection
# @version 0.0.1


TestNeuropsychImagerecogSelectionRecord = {
    # A timestamp representing time of selection.
    "stamp": datetime,
    # The coordinate picked by the user.
    "pickedCoord": TestNeuropsychImagerecogCoordRecord,
    # The coordinate of the displayed image.
    "correctCoord": TestNeuropsychImagerecogCoordRecord,
    # True if the user selected the correct answer, false otherwise.
    "correct": bool,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Captured events and timing for an Image Recognition test administered via a web browser
# @version 0.0.1


TestNeuropsychImagerecogRecord = {
    # A timestamp representing when the display component was mounted.
    "displayStart": datetime,
    # A timestamp representing when the display component was unmounted.
    "displayStop": datetime,
    # A timestamp representing when the question component was mounted.
    "questionStart": datetime,
    # A timestamp representing when the question component was unmounted.
    "questionStop": datetime,
    # The coordinate of the displayed image.
    "displayedCoord": TestNeuropsychImagerecogCoordRecord,
    # The coordinate selected by the user.
    "selectedCoord": TestNeuropsychImagerecogCoordRecord,
    # True if the user selected the correct answer, false is they did not and null if a selection has not been made.
    "correct": bool,
    # A array of coordinates outlining the grid shown to the user
    "grid": [TestNeuropsychImagerecogCoordRecord],
    # An array of coordinate selections made by the user. The last element of the array will be the user's final selection. If the array is empty, then no selection was made.
    "selections": [TestNeuropsychImagerecogSelectionRecord],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Captured events and timing for an Image Recognition test administered via a Qualtrics survey
# @version 0.0.1


QualtricsImagerecogRecord = {
    # The Qualtrics survey url. This should have the Qualtrics survey and recipient id
    "url": str,
    # Data captured by the image recogition task.
    "task": TestNeuropsychImagerecogRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Information about a question choice.
# @version 0.0.1


QualtricsQuestionChoiceRecord_old = {
    # No description provided
    "recodeValue": str,
    # No description provided
    "variableName": str,
    # No description provided
    "text": str,
    # No description provided
    "exclusive": bool,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


class QualtricsQuestionChoiceRecord(TypedDict):
    # No description provided
    recodeValue: str
    # No description provided
    variableName: str
    # No description provided
    text: str
    # No description provided
    exclusive: bool
    # If true indicates that the record is frozen
    isFrozen: bool


# The input events captured while the subject was taking a survey.
# @version 0.0.1

QualtricsQuestionRecord_old = {
    # The Qualtrics question id
    "id": APIID,
    # The question text
    "text": str,
    # The question type code
    "type": str,
    # List of choices where the key is the choice id and the value is information about the choice
    "choices": Dict[str, QualtricsQuestionChoiceRecord],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


class QualtricsQuestionRecord(TypedDict):
    # The Qualtrics question id
    id: APIID
    # The question text
    text: str
    # The question type code
    type: str
    # List of choices where the key is the choice id and the value is information about the choice
    choices: Dict[str, QualtricsQuestionChoiceRecord]
    # If true, indicates that the record is frozen
    isFrozen: bool


# The input events captured while the subject was taking a survey.
# @version 0.0.1


QualtricsInputRecord = {
    # The Qualtrics survey url. This should have the Qualtrics survey and recipient id embeded in it
    "url": str,
    # The Qualtrics question info as pulled from their JS engine
    "questionInfo": Dict[str, QualtricsQuestionRecord],
    # An input event that happened during the survey.
    "deviceInput": DeviceInputRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# A selection event with context relative the Stroop test being administered
# @version 0.0.1


TestNeuropsychStroopSelectionRecord = {
    # The type of the selection. Possible values as `Success` for matching colors and `Error` for selecting dissimiliar colors.
    "type": str,
    # A timestamp indicating the time at which the event took place.
    "stamp": datetime,
    # The array index of this element in the order of elements to be shown to the user
    "index": int,
    # The text being shown to the user
    "word": str,
    # The color of the text being shown to the user
    "color": str,
    # A timestamp indicating when the colored word was first shown to the user
    "start": datetime,
    # The text color of the button selected by the user
    "selectedColor": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Captured events and timing for a Stroop test administered via a web browser
# @version 0.0.1


TestNeuropsychStroopRecord = {
    # A timestamp indicating the time at which the task began. The task is shown and events are recorded at this time.
    "start": datetime,
    # A timestamp indicating the time at which the task ended such that the user could no longer create additional events.
    "stop": datetime,
    # How long the user has to do the test in seconds
    "timeLimit": int,
    # If false, the user went through all possible combos, true otherwise.
    "timeLimitReached": bool,
    # A series of captured selections that occurred during the test. These include correct and incorrect clicks.
    "events": [TestNeuropsychStroopSelectionRecord],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Captured events and timing for an Stroop test administered via a Qualtrics survey
# @version 0.0.1


QualtricsStroopRecord = {
    # The Qualtrics survey url. This should have the Qualtrics survey and recipient id
    "url": str,
    # Data captured by the Stroop task.
    "task": TestNeuropsychStroopRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Display information about a survey administered by Qualtrics
# @version 0.0.1


QualtricsSurveyExpirationRecord = {
    # TODO
    "startDate": datetime,
    # TODO
    "endDate": datetime,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Display information about a survey administered by Qualtrics
# @version 0.0.1


QualtricsSurveyQuestionTypeRecord_old = {
    # TODO
    "type": str,
    # TODO
    "selector": str,
    # TODO
    "subSelector": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


class QualtricsSurveyQuestionTypeRecord(TypedDict):
    # TODO
    type: str
    # TODO
    selector: str
    # TODO
    subSelector: str
    # If true, indicates that the record is frozen
    isFrozen: bool


# Display information about a survey administered by Qualtrics
# @version 0.0.1


class QualtricsSurveyQuestionChoiceRecord(TypedDict):
    # TODO
    recode: str
    # TODO
    description: str
    # TODO
    choiceText: str
    # TODO
    imageDescription: str
    # TODO
    analyze: bool
    # The name for the choice variable
    variableName: str
    # If true, indicates that the record is frozen
    isFrozen: bool


QualtricsSurveyQuestionChoiceRecord_old = {
    # TODO
    "recode": str,
    # TODO
    "description": str,
    # TODO
    "choiceText": str,
    # TODO
    "imageDescription": str,
    # TODO
    "analyze": bool,
    # The name for the choice variable
    "variableName": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Display information about a survey administered by Qualtrics
# @version 0.0.1


QualtricsSurveyQuestionValidationRecord_old = {
    # TODO
    "doesForceResponse": bool,
    # TODO
    "doesRequestResponse": bool,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


class QualtricsSurveyQuestionValidationRecord(TypedDict):
    # TODO
    doesForceResponse: bool
    # TODO
    doesRequestResponse: bool
    # If true, indicates that the record is frozen
    isFrozen: bool


# Display information about a survey administered by Qualtrics
# @version 0.0.1


QualtricsSurveyQuestionRecord_old = {
    # The type of question.
    "questionType": QualtricsSurveyQuestionTypeRecord,
    # The text displayed to the user
    "questionText": str,
    # The question label
    "questionLabel": str,
    # The question key
    "questionName": str,
    # The possible choices for a question
    "choices": Dict[str, QualtricsSurveyQuestionChoiceRecord],
    # The possible follow up questions for a question
    "subQuestions": Dict[str, QualtricsSurveyQuestionChoiceRecord],
    # Any validation to be applied to the response before progressing
    "validation": QualtricsSurveyQuestionValidationRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


class QualtricsSurveyQuestionRecord(TypedDict):
    # The type of question.
    questionType: QualtricsSurveyQuestionTypeRecord
    # The text displayed to the user
    questionText: str
    # The question label
    questionLabel: str
    # The question key
    questionName: str
    # The possible choices for a question
    choices: Dict[str, QualtricsSurveyQuestionChoiceRecord]
    # The possible follow up questions for a question
    subQuestions: Dict[str, QualtricsSurveyQuestionChoiceRecord]
    # Any validation to be applied to the response before progressing
    validation: QualtricsSurveyQuestionValidationRecord
    # If true indicates that the record is frozen
    isFrozen: bool


# Display information about a survey administered by Qualtrics
# @version 0.0.1


QualtricsSurveyColumnRecord = {
    # TODO
    "question": str,
    # TODO
    "subQuestion": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


class QualtricsSurveyColumnRecord(TypedDict):
    # TODO
    question: str
    # TODO
    subQuestion: str
    # If true, indicates that the record is frozen
    isFrozen: bool


# Display information about a survey administered by Qualtrics
# @version 0.0.1


QualtricsSurveyBlockElementRecord_old = {
    # TODO
    "type": str,
    # TODO
    "questionID": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


class QualtricsSurveyBlockElementRecord(TypedDict):
    # TODO
    type: str
    # TODO
    questionID: str
    # If true, indicates that the record is frozen
    isFrozen: bool


# Display information about a survey administered by Qualtrics
# @version 0.0.1

QualtricsSurveyBlockRecord_old = {
    # TODO
    "description": str,
    # TODO
    "elements": [QualtricsSurveyBlockElementRecord],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


class QualtricsSurveyBlockRecord(TypedDict):
    # TODO
    description: str
    # TODO
    elements: List[QualtricsSurveyBlockElementRecord]
    # If true, indicates that the record is frozen
    isFrozen: bool


# Display information about a survey administered by Qualtrics
# @version 0.0.1


QualtricsSurveyFlowRecord = {
    # TODO
    "id": APIID,
    # TODO
    "type": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Display information about a survey administered by Qualtrics
# @version 0.0.1


QualtricsSurveyLoopQuestionMetaRecord_old = {
    # TODO
    "questionID": str,
    # TODO
    "questionType": str,
    # TODO
    "loopOn": [Dict[str, str]],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


class QualtricsSurveyLoopQuestionMetaRecord(TypedDict):
    # TODO
    questionID: str
    # TODO
    questionType: str
    # TODO
    loopOn: List[Dict[str, str]]
    # If true, indicates that the record is frozen
    isFrozen: bool


# Display information about a survey administered by Qualtrics
# @version 0.0.1


QualtricsSurveyLoopRecord_old = {
    # Type of loop either 'Question' or 'Static.'
    "loopType": str,
    # Contains an object that references the question defined by the loop.
    "loopQuestionMeta": QualtricsSurveyLoopQuestionMetaRecord,
    # Indicates how the loop is randomized (if enabled in the survey design).
    "randomizationMeta": Dict[str, str],
    # Is an object with members such as field1, field2, etc. Each value associated with a field contains and array of the values that appear in that field.
    "columnNames": Dict[str, List[str]],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


class QualtricsSurveyLoopRecord(TypedDict):
    # Type of loop either 'Question' or 'Static.'
    loopType: str
    # Contains an object that references the question defined by the loop.
    loopQuestionMeta: QualtricsSurveyLoopQuestionMetaRecord
    # Indicates how the loop is randomized (if enabled in the survey design).
    randomizationMeta: Dict[str, str]
    # Is an object with members such as field1, field2, etc. Each value associated with a field contains and array of the values that appear in that field.
    columnNames: Dict[str, List[str]]
    # If true, indicates that the record is frozen
    isFrozen: bool


# Display information about a survey administered by Qualtrics
# @version 0.0.1

QualtricsSurveyRecord = {
    # The name of the survey. It is also the same as the project name.
    "name": str,
    # The user ID of the owner of the survey.
    "ownerID": str,
    # The date and time (UTC time zone) the survey was last modified.
    "lastModifiedDate": datetime,
    # The time in which the survey was created as a string.
    "creationDate": datetime,
    # Indicates whether the survey is currently active.
    "isActive": bool,
    # Contains two members, endDate and startDate that express the date range during which the survey is valid.
    "expiration": QualtricsSurveyExpirationRecord,
    # The questions object contains information about the questions that make up your survey. Each member in the questions object is the question ID, and its value is an object that defines the question. For example, in the following Multiple Choice snippet, the question ID is QID1, which is a multiple-choice question. Each choice is a member (1, 2, and 3) that contains an object with members that describe that choice. Other question types have different objects that describe the question.
    "questions": Dict[str, QualtricsSurveyQuestionRecord],
    # The exportColumnMap is useful for mapping the names you've given to your questions with the internal identifiers (question IDs) that Qualtrics uses to identify your questions. When tabulating responses to your survey, this information is particularly useful.
    "exportColumnMap": Dict[str, QualtricsSurveyColumnRecord],
    # The blocks object's members are block IDs, such as 'BL_1234567890' and inside each block is an object.
    "blocks": Dict[str, QualtricsSurveyBlockRecord],
    # The flow array represents the order of items that make up the survey. Each object in the flow array contains a type member that identifies the block. There are sometimes type members in the object that indicate the type of block in the flow
    "flow": [QualtricsSurveyFlowRecord],
    # Each object in embeddedData contains two members, name and defaultValue.
    "embeddedData": [Dict[str, str]],
    # The comments map contains members for each question ID that has comments (or notes). Each question has a commentList array of one object per comment.
    "comments": Dict[str, str],
    # The loopAndMerge object contains block IDs as members and objects as values. The possible loop types for loop and merge are static and question. If the loop is static it will always loop the same regardless of previous answers selected. If the loop type is question, then there will be a criterion in the loopOn array member which will say what you are looping on ('UnselectedChoices', 'SelectedChoices', etc.). The loopQuestionMeta also provides the questionId and questionType of the question that is being used to loop on. If 'Randomize loop order' is enabled the randomizationMeta will contain information about how many loops the question will go through.
    "loopAndMerge": Dict[str, QualtricsSurveyLoopRecord],
    # Contains three members, auditable, deleted, and generated which contain counts of responses
    "responseCounts": Dict[str, int],
    # Lookup id number for survey
    "surveyID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


# Captured events, questions and answers from the a survey administered by Qualtrics
# @version 0.0.1


QualtricsSurveyResponseRecord = {
    # The Qualtrics response ID.
    "responseID": str,
    # The time at which the first response was started
    "start": datetime,
    # The response values input by the recipient
    "values": Dict[str, str],
    # The question labels for the questions there are responses for
    "labels": Dict[str, str],
    # The possible values displayed to the user
    "displayedValues": Dict[str, List[str]],
    # TODO
    "displayedFields": [str],
    # Lookup id number for survey
    "surveyID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# A token displayed on the Trails Making test. This is a outlined circle with text displayed in the center of the circle.
# @version 0.0.1


TestNeuropsychTrailsTokenRecord = {
    # The text display in the center of the token
    "text": str,
    # The center of the token in the X direction in pixels relative to the dimensions of the task container
    "x": int,
    # The center of the token in the X direction in pixels relative to the dimensions of the task container
    "y": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# A selection event with context relative the trails making test being administered
# @version 0.0.1


TestNeuropsychTrailsSelectionRecord = {
    # A timestamp indicating the time at which the event took place.
    "stamp": datetime,
    # The type of event that occured. Valid string values are `Success` for a correct selection, `Error` for an incorrect selection and `Miss` for clicking on the test but not any circle tokens
    "type": str,
    # The current correct token to be selected by the user
    "correctToken": TestNeuropsychTrailsTokenRecord,
    # The actual token selected by the user
    "selectedToken": TestNeuropsychTrailsTokenRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Captured events and timing for a Trail Making test administered via a web browser
# @version 0.0.1


TestNeuropsychTrailsRecord = {
    # A timestamp indicating the time at which the task began. The task is shown and events are recorded at this time.
    "start": datetime,
    # A timestamp indicating the time at which the task ended such that the user could no longer create additional events.
    "stop": datetime,
    # The type of Trails Making test administered. The format is A or B concatinated with the number of circles
    "part": str,
    # A series of captured selections that occured during the test. These include correct, incorrect and missed clicks.
    "events": [TestNeuropsychTrailsSelectionRecord],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Captured events and timing for a Trails Making test administered via a Qualtrics survey
# @version 0.0.1


QualtricsTrailsRecord = {
    # The Qualtrics survey url. This should have the Qualtrics survey and recipient id
    "url": str,
    # Data captured by the Trails Making task.
    "task": TestNeuropsychTrailsRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A reported life event change that could a meaningful impact on collected data samples
# @version 0.0.1


ReportLifeEventRecord = {
    # When life event when into effect
    "start": datetime,
    # When life event is no longer applicable. If this is null, then the stop date is unknown
    "stop": datetime,
    # The reported text about the event
    "description": str,
    # Notes added to the event for further explanation
    "notes": str,
    # Reasoning attributes to the event
    "reason": str,
    # True if the participant was called to verify the report, false otherwise
    "called": bool,
    # True if the life event has been redacted, false otherwise
    "redacted": bool,
    # True if the reported life event has been verified as true, false if the report has been verified as false, null if verification process has not happened
    "accepted": bool,
    # When the record was verified. Null if the verification process has not happened
    "verifiedOn": datetime,
    # Lookup id number for medication
    "medicationID": APIID,
    # Lookup id number for source
    "sourceID": APIID,
    # Lookup id number for primaryCategory
    "primaryCategoryID": APIID,
    # Lookup id number for secondaryCategory
    "secondaryCategoryID": APIID,
    # Lookup id number for verifiedBy
    "verifiedByID": APIID,
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An role within a scope of the system. This is essentially a set of permissions
# @version 0.0.1


RoleRecord = {
    # A short descriptive name of the role
    "name": str,
    # The unique identifier
    "id": APIID,
    # The long description of the role
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for permissions
    "permissionIDs": [APIID],
    # Lookup id numbers for users
    "userIDs": [APIID],
    # Lookup id numbers for apps
    "appIDs": [APIID],
    # Lookup id numbers for notificationGroups
    "notificationGroupIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id number for study
    "studyID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


# An alert indicating a problem with a sensor
# @version 0.0.1


SensorAlertRecord = {
    # A unix timestamp indicating the time at which the alert occurred
    "stamp": datetime,
    # A unique id from the  database representing the item/sensor
    "itemID": int,
    # A unique id from the  database representing the type of alert which occured
    "alertID": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Unique sensor line information
# @version 0.0.1


SensorLineRecord = {
    # The unique identifier
    "id": APIID,
    # A descriptive name for the line
    "name": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for home
    "homeID": APIID,
    # Lookup id number for area
    "areaID": APIID,
    # Lookup id numbers for segments
    "segmentIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A pair of two sensors that compose a segment within a sensor line
# @version 0.0.1


SensorLineSegmentRecord = {
    # The unique identifier
    "id": APIID,
    # Order number for the current sensor pair. I.e. 0 is the first pair, 1 is the second pair, etc
    "order": int,
    # Distance between the two sensors measured in centimeters
    "distance": int,
    # True if the distance is null and was assumed to be 2 feet, false if the distance was measured and entered
    "assumed": bool,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for first
    "firstID": APIID,
    # Lookup id number for second
    "secondID": APIID,
    # Lookup id number for line
    "lineID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A type of sensor line
# @version 0.0.1


SensorLineTypeRecord = {
    # The  unique identifier
    "id": APIID,
    # A descriptive name for the type
    "name": str,
    # A short description of the type
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for lines
    "lineIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Audio recording for SHARP
# @version 0.0.1


SharpAudioRecord = {
    # The unique identifier
    "id": APIID,
    # The macaddress of the device where the audio recording was created
    "macaddress": str,
    #
    "walk": str,
    #
    "file": str,
    #
    "duration": str,
    #
    "stamp": datetime,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for subjects
    "subjectIDs": [APIID],
    # Lookup id number for inventoryItem
    "inventoryItemID": APIID,
    # Lookup id number for path
    "pathID": APIID,
    # Lookup id number for marker
    "markerID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Coordinates for SHARP
# @version 0.0.1


SharpCoordinateRecord = {
    # The  unique identifier
    "id": APIID,
    # The macaddress of the device where the event was created
    "macaddress": str,
    #
    "walk": str,
    #
    "lat": str,
    #
    "lng": str,
    #
    "stamp": datetime,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id number for inventoryItem
    "inventoryItemID": APIID,
    # Lookup id number for path
    "pathID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Events for SHARP
# @version 0.0.1


SharpEventRecord = {
    # The  unique identifier
    "id": APIID,
    # The macaddress of the device where the event was created
    "macaddress": str,
    #
    "walk": str,
    #
    "type": str,
    #
    "stamp": datetime,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id number for inventoryItem
    "inventoryItemID": APIID,
    # Lookup id number for path
    "pathID": APIID,
    # Lookup id number for marker
    "markerID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Tokens for subject 3rd party data retrieval
# @version 0.0.1


SharpParticipantTokenRecord = {
    # The unique identifier for this record
    "id": APIID,
    # The access token to supply with all request
    "access": str,
    # A refresh token to generate new access tokens
    "refresh": str,
    # The time at which this token is no longer valid
    "expires": datetime,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for subject
    "subjectID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Path for SHARP
# @version 0.0.1


SharpPathRecord = {
    #
    "directions": str,
    # The unique identifier
    "id": APIID,
    #
    "name": str,
    #
    "distance": str,
    #
    "address": str,
    #
    "built": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for markers
    "markerIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Path marker for SHARP
# @version 0.0.1


SharpPathMarkerRecord = {
    # The  unique identifier
    "id": APIID,
    #
    "lat": str,
    #
    "lng": str,
    #
    "address": str,
    #
    "city": str,
    #
    "state": str,
    #
    "walkOrder": str,
    #
    "name": str,
    #
    "visible": str,
    #
    "kind": str,
    #
    "actualLocation": str,
    #
    "type": str,
    #
    "image": str,
    #
    "prompts": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for path
    "pathID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Software available to the organization and can be installed
# @version 0.0.1


SoftwareRecord = {
    # The unique identifier
    "id": APIID,
    # A unique name for the tag
    "name": str,
    # A longer description of the tag
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for aptPackage
    "aptPackageID": APIID,
    # Lookup id number for inventoryTag
    "inventoryTagID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An apt package repository
# @version 0.0.1


SoftwareAptRecord = {
    # The unique identifier
    "id": APIID,
    # The package name
    "package": str,
    # The package version
    "version": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for repo
    "repoID": APIID,
    # Lookup id number for software
    "softwareID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Software installed using an apt repo
# @version 0.0.1


SoftwareAptRepoRecord = {
    # The unique identifier
    "id": APIID,
    # The url to the repository, i.e. http://api.repo.org/somesubdirectory
    "location": str,
    # The location of the public key for the repository
    "keySource": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for software
    "softwareIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Account identifiers provided by the OAuth2 provider
# @version 0.0.1


SsoAccountRecord = {
    # The user name registered with the provider
    "name": str,
    # The email associated with the OAuth2 provider's authenticated account.
    "email": str,
    # The  unique identifier
    "id": APIID,
    # The provider's user identifier for the authenticated user
    "providerUserID": str,
    # The password used by the password provider for authentication
    "password": str,
    # The number of failed login attempts
    "loginAttempts": int,
    # If true the account is locked against logins
    "locked": bool,
    # The URL to the user's profile picture
    "picture": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for user
    "userID": APIID,
    # Lookup id number for provider
    "providerID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# OAuth2 Providers scopes to be requested during authentication
# @version 0.0.1


SsoOauth2ScopeRecord = {
    # The endpoint as specified by the provider
    "endPoint": str,
    # The unique identifier
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for provider
    "providerID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Tokens used for access to authenticated endpoints protects by OAuth2
# @version 0.0.1


SsoOauth2TokenRecord = {
    # The  unique identifier
    "id": APIID,
    # The access token to supply with all request
    "access": str,
    # A refresh token to generate new access tokens
    "refresh": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for provider
    "providerID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Application credentials to an sso identity provider
# @version 0.0.1


SsoProviderRecord = {
    # The name of the sso identity provider
    "name": str,
    # The unique identifier
    "id": APIID,
    # The name of the handshake protocol. Supported values are OAuth2 and SAML2
    "protocol": str,
    # The token Auth2.0 endpoint supported by the provider
    "tokenURL": str,
    # The auth Auth2.0 endpoint supported by the provider
    "authURL": str,
    # The application's OAuth2 client ID
    "clientID": str,
    # The application's OAuth2 client secret
    "clientSecret": str,
    # The identity provider sso url for SAML2
    "ssoURL": str,
    # The identity provider issuer for SAML2
    "issuer": str,
    # The identity provider certificate for SAML2
    "certificate": str,
    # If true, a multi-facter authentication with will implemented on top of this providers login. Otherwise, it is assumed that the provider requires multi-facter authentication internally.
    "requiresMultiFacterAuth": bool,
    # If the provider can be used for authentication
    "enabled": bool,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for scopes
    "scopeIDs": [APIID],
    # Lookup id numbers for tokens
    "tokenIDs": [APIID],
    # Lookup id numbers for accounts
    "accountIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An  study is an research study consisting of a subset of subjects who and agreed to participant.
# @version 0.0.1


StudyRecord = {
    # The  unique identifier
    "id": APIID,
    # A short descriptive name for the study
    "name": str,
    # The long description of the study
    "description": str,
    # The scheduled start date of the study
    "start": datetime,
    # The scheduled end date of the study
    "stop": datetime,
    # When the record was created
    "createdAt": datetime,
    # When the record was updated
    "updatedAt": datetime,
    # When the record was deleted
    "deletedAt": datetime,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for plugins
    "pluginIDs": [APIID],
    # Lookup id numbers for roles
    "roleIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Subject study enrollment information.
# @version 0.0.1


StudyEnrollmentRecord = {
    # The unique identifier
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for subjects
    "subjectIDs": [APIID],
    # Lookup id number for state
    "stateID": APIID,
    # Lookup id number for study
    "studyID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A study enrollment state for a subject. The state should indicate where the subject is in the enrollment process.
# @version 0.0.1


StudyEnrollmentStateRecord = {
    # The unique identifier
    "id": APIID,
    # A short descriptive name for the study state
    "name": str,
    # The long description of the study state
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for enrollments
    "enrollmentIDs": [APIID],
    # Lookup id numbers for taskTypes
    "taskTypeIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An external identifier for the study to map the it's data to an external database
# @version 0.0.1


StudyIdentifierRecord = {
    # The identification string
    "value": str,
    # The unique identifier
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for study
    "studyID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A type of external identifier for the study to map the it's data to an external database
# @version 0.0.1


StudyIdentifierTypeRecord = {
    # The unique identifier
    "id": APIID,
    # A short unique name to categorize the identifiers
    "name": str,
    # A description of the external database
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for identifiers
    "identifierIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The status of the study
# @version 0.0.1


StudyStatusRecord = {
    # The number of connected hubs belonging to the organization
    "connectedHubs": int,
    # The number of connected hubs belonging to the organization that are also assigned
    "connectedAssignedHubs": int,
    # A map where the key is the firmware version and the value is the number of items with that version
    "firmware": Dict[str, int],
    # A map where the key is the alert type id and the value is the number of active alerts with that type
    "alerts": Dict[str, int],
    # The number of active alerts for the organization
    "alertCount": int,
    # A map where the key is the data schema and the value is the time of the last data point
    "lastDataPoint": Dict[str, datetime],
    # A map where the key is the data schema and the value is the total number of data points
    "totalDataPoints": Dict[str, int],
    # Lookup id number for study
    "studyID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A subject who participates in an  affiliated study
# @version 0.0.1


SubjectRecord = {
    # The email address of the subject. Information regarding the study will be sent to this address.
    "email": str,
    # The  unique identifier
    "id": APIID,
    # The subject's full name
    "name": str,
    # The subject's date of birth
    "dob": datetime,
    # The subject's date of death
    "dod": datetime,
    # A URI to download the subject's picture
    "picture": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for users
    "userIDs": [APIID],
    # Lookup id numbers for homes
    "homeIDs": [APIID],
    # Lookup id numbers for issues
    "issueIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for tasks
    "taskIDs": [APIID],
    # Lookup id numbers for studiesEnrollment
    "studiesEnrollmentIDs": [APIID],
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # Lookup id number for gender
    "genderID": APIID,
    # Lookup id number for race
    "raceID": APIID,
    # Lookup id number for ethnicity
    "ethnicityID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id numbers for phones
    "phoneIDs": [APIID],
    # Lookup id numbers for comments
    "commentIDs": [APIID],
    # Lookup id numbers for contacts
    "contactIDs": [APIID],
    # Lookup id numbers for items
    "itemIDs": [APIID],
    # Lookup id numbers for identifiers
    "identifierIDs": [APIID],
    # Lookup id numbers for attributes
    "attributeIDs": [APIID],
    # Lookup id number for clinicalSummary
    "clinicalSummaryID": APIID,
    # Lookup id number for hemisphere
    "hemisphereID": APIID,
    # Lookup id numbers for beiweCredentials
    "beiweCredentialIDs": [APIID],
    # Lookup id numbers for worktimeUsers
    "worktimeUserIDs": [APIID],
    # Lookup id number for sharpParticipantToken
    "sharpParticipantTokenID": APIID,
    # Lookup id numbers for integrationCredentials
    "integrationCredentialIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The value portion of a key value pair belonging to an subject
# @version 0.0.1


SubjectAttributeRecord = {
    # The local unique identifier
    "id": APIID,
    # The attribute string
    "value": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A type of subject attribute for the subject. This will act as the key in the key value pair
# @version 0.0.1


SubjectAttributeTypeRecord = {
    # A short unique name to categorize the identifiers
    "name": str,
    # The local unique identifier
    "id": APIID,
    # A description of the external database
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for attributes
    "attributeIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A note or comment about the subject
# @version 0.0.1


SubjectCommentRecord = {
    # The content of the comment
    "description": str,
    # The  unique identifier
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A contact with the subject. This can be a phone call, in person visit, etc.
# @version 0.0.1


SubjectContactRecord = {
    # The content of the comment
    "description": str,
    # The  unique identifier
    "id": APIID,
    # The timestamp when the contact started
    "start": datetime,
    # The timestamp when the contact ended
    "stop": datetime,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for reason
    "reasonID": APIID,
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A reason for which the contact was made.
# @version 0.0.1


SubjectContactReasonRecord = {
    # The  unique identifier
    "id": APIID,
    # A descriptive name for the type of contact
    "name": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for contacts
    "contactIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A type on contact such as phone call, in person visit, etc.
# @version 0.0.1


SubjectContactTypeRecord = {
    # The  unique identifier
    "id": APIID,
    # A descriptive name for the type of contact
    "name": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for contacts
    "contactIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The ethnicity the subject identifies with
# @version 0.0.1


SubjectEthnicityRecord = {
    # The unique identifier
    "id": APIID,
    # The name of the race
    "name": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for subjects
    "subjectIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A type of gender
# @version 0.0.1


SubjectGenderRecord = {
    # The  unique identifier
    "id": APIID,
    # A short descriptive name for the gender
    "name": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for subjects
    "subjectIDs": [APIID],
    # Lookup id numbers for autopsies
    "autopsyIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An external identifier for the subject to map the their data to an external database
# @version 0.0.1


SubjectIdentifierRecord = {
    # The identification string
    "value": str,
    # The  unique identifier
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A type of external identifier for the subject to map the their data to an external database
# @version 0.0.1


SubjectIdentifierTypeRecord = {
    # A short unique name to categorize the identifiers
    "name": str,
    # The  unique identifier
    "id": APIID,
    # A description of the external database
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for identifiers
    "identifierIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The primary category of the the life event
# @version 0.0.1


SubjectLifeEventCategoryPrimaryRecord = {
    # The name of the code
    "code": str,
    # The unique identifier
    "id": APIID,
    # The name of the code
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for secondary
    "secondaryIDs": [APIID],
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The secondary category of the life event
# @version 0.0.1


SubjectLifeEventCategorySecondaryRecord = {
    # The name of the code
    "code": str,
    # The unique identifier
    "id": APIID,
    # The name of the code
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for primary
    "primaryID": APIID,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The source that generated the life event
# @version 0.0.1


SubjectLifeEventSourceRecord = {
    # The name of the code
    "name": str,
    # The unique identifier
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A tag used to categorize a set of life events
# @version 0.0.1


SubjectLifeEventTagRecord = {
    # A unique name for the tag
    "name": str,
    # The unique identifier
    "id": APIID,
    # A longer description of the tag
    "description": str,
    # A hexidecimal representation of a color for this tag
    "color": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for primary
    "primaryID": APIID,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The race the subject identifies with
# @version 0.0.1


SubjectRaceRecord = {
    # The unique identifier
    "id": APIID,
    # The name of the race
    "name": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for subjects
    "subjectIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A tag used to categorize a set of subjects or people
# @version 0.0.1


SubjectTagRecord = {
    # The unique identifier
    "id": APIID,
    # A unique name for the tag
    "name": str,
    # A longer description of the tag
    "description": str,
    # A hexidecimal representation of a color for this tag
    "color": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for subjects
    "subjectIDs": [APIID],
    # Lookup id numbers for people
    "personIDs": [APIID],
    # Lookup id numbers for distributions
    "distributionIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A survey that has been or can be administered to a set of subjects
# @version 0.0.1


SurveyRecord = {
    # The unique identifier
    "id": APIID,
    # A descriptive name of the survey
    "name": str,
    # Details about the survey
    "description": str,
    # A unique identifier of the survey given by the survey software.
    "surveyID": str,
    # The time at which an attempt was made to query the survey api for new responses.
    "lastTry": datetime,
    # The time at which the survey api was last queried successfully for new responses.
    "lastUpdated": datetime,
    # The timestamp of the last pulled survey response.
    "lastResponse": datetime,
    # A token pointing to the next set of responses to be pulled.
    "continuationToken": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id number for study
    "studyID": APIID,
    # Lookup id numbers for distributions
    "distributionIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A distribution of the survey to a particular group of subjects
# @version 0.0.1


SurveyDistributionRecord = {
    # The text to appear in the email to the participant
    "message": str,
    # The unique identifier
    "id": APIID,
    # When to send the survey for the first time.
    "start": datetime,
    # Should the survey be sent on a reoccurring interval.
    "repeat": bool,
    # How ofter to resend the survey. This is only used when the repeat field is set to true.
    "every": Duration,
    # When the survey is next scheduled for distribution
    "scheduledFor": datetime,
    # The from email address
    "fromEmail": str,
    # The name to appear next to the from email address
    "fromName": str,
    # The subject line of the email
    "subject": str,
    # The email reply to address
    "replyToEmail": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for survey
    "surveyID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A reported life event change that could a meaningful impact on collected data samples
# @version 0.0.1


SurveyEventRecord = {
    # When life event when into effect
    "start": datetime,
    # When life event is no longer applicable. If this is null, then the stop date is unknown
    "stop": datetime,
    # The relevant text entered into the survey about the event
    "description": str,
    # Answers to other questions that give more detail about the event
    "extras": Dict[str, str],
    # The time at which the record was generated
    "createdAt": datetime,
    # Lookup id number for primaryCategory
    "primaryCategoryID": APIID,
    # Lookup id number for secondaryCategory
    "secondaryCategoryID": APIID,
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The primary category of the generated the survey event
# @version 0.0.1


SurveyEventCategoryPrimaryRecord = {
    # The name of the code
    "code": str,
    # The unique identifier
    "id": APIID,
    # The name of the code
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for secondary
    "secondaryIDs": [APIID],
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The secondary category of the generated the survey event
# @version 0.0.1


SurveyEventCategorySecondaryRecord = {
    # The name of the code
    "code": str,
    # The unique identifier
    "id": APIID,
    # The name of the code
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for primary
    "primaryID": APIID,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A reported life event change that could a meaningful impact on collected data samples
# @version 0.0.1


SurveyEventErrorRecord_old = {
    # A description of the error
    "description": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


class SurveyEventErrorRecord(TypedDict):
    # A description of the error
    description: str
    # If true, indicates that the record is frozen
    isFrozen: bool


# A tag applied to the survey event to group them together
# @version 0.0.1


class SurveyEventTagRecord(TypedDict):
    # The name of the code
    name: str
    # The unique identifier
    id: APIID
    # A description of the code
    description: str
    # When the record was created
    createdAt: datetime
    # The com.orcatech.user.id for the user who created the record
    createdBy: int
    # When the record was updated
    updatedAt: datetime
    # The com.orcatech.user.id for the user who updated the record
    updatedBy: int
    # When the record was deleted
    deletedAt: datetime
    # The com.orcatech.user.id for the user who deleted the record
    deletedBy: int
    # Lookup id number for primary
    primaryID: APIID
    # Lookup id numbers for organizations
    organizationIDs: List[APIID]
    # Lookup id numbers for studies
    studyIDs: List[APIID]
    # If true indicates that the record is frozen
    isFrozen: bool


# SurveyEventTagRecord_old = {
#     # The name of the code
#     "name": str,
#     # The unique identifier
#     "id": APIID,
#     # A description of the code
#     "description": str,
#     # When the record was created
#     "createdAt": datetime,
#     # The com.orcatech.user.id for the user who created the record
#     "createdBy": int,
#     # When the record was updated
#     "updatedAt": datetime,
#     # The com.orcatech.user.id for the user who updated the record
#     "updatedBy": int,
#     # When the record was deleted
#     "deletedAt": datetime,
#     # The com.orcatech.user.id for the user who deleted the record
#     "deletedBy": int,
#     # Lookup id number for primary
#     "primaryID": APIID,
#     # Lookup id numbers for organizations
#     "organizationIDs": [APIID],
#     # Lookup id numbers for studies
#     "studyIDs": [APIID],
#     # If true, indicates that the record is frozen
#     "isFrozen": bool,
# }


# Information about a specific survey question. The metrics will be additive if the respondent is viewing the page multiple times, either through the use of a back button or by exiting and reopening the survey. For example, let’s say a respondent submits a page after 20 seconds, goes back to that page using the back button, and then submits the page again after 30 seconds. Their recorded Page Submit time will be 50 seconds.
# @version 0.0.1


class SurveyResponseQuestionMetricClickRecord(TypedDict):
    # How long the page was visible before the respondent clicks the first time.
    first: Duration
    # How long the page was visible before the respondent clicks the last time (not including clicking the Next button).
    last: Duration
    # How many total times the respondent clicks on the page.
    count: int
    # If true, indicates that the record is frozen
    isFrozen: bool


# SurveyResponseQuestionMetricClickRecord_old = {
#     # How long the page was visible before the respondent clicks the first time.
#     "first": Duration,
#     # How long the page was visible before the respondent clicks the last time (not including clicking the Next button).
#     "last": Duration,
#     # How many total times the respondent clicks on the page.
#     "count": int,
#     # If true, indicates that the record is frozen
#     "isFrozen": bool,
# }

# Captured device input that happened during a survey
# @version 0.0.1

# SurveyInputRecord = {
#     # User input captured by the device.
#     "deviceInput": DeviceInputRecord,
#     # If true, indicates that the record is frozen
#     "isFrozen": bool,
# }


class SurveyInputRecord(TypedDict):
    # User input captured by the device.
    deviceInput: DeviceInputRecord
    # If true, indicates that the record is frozen
    isFrozen: bool


# Information about a specific survey question. The metrics will be additive if the respondent is viewing the page multiple times, either through the use of a back button or by exiting and reopening the survey. For example, let’s say a respondent submits a page after 20 seconds, goes back to that page using the back button, and then submits the page again after 30 seconds. Their recorded Page Submit time will be 50 seconds.
# @version 0.0.1

# SurveyResponseQuestionMetricRecord_old = {
#     # How long before the respondent clicks the Next button (i.e., the total amount of time the respondent spends on the page).
#     "duration": Duration,
#     # Metrics collected about the clicking events on the page
#     "clicks": SurveyResponseQuestionMetricClickRecord,
#     # If true, indicates that the record is frozen
#     "isFrozen": bool,
# }


class SurveyResponseQuestionMetricRecord(TypedDict):
    # How long before the respondent clicks the Next button (i.e., the total amount of time the respondent spends on the page).
    duration: Duration
    # Metrics collected about the clicking events on the page
    clicks: SurveyResponseQuestionMetricClickRecord  # type: ignore
    # If true, indicates that the record is frozen
    isFrozen: bool


# Information about a specific survey question. The metrics will be additive if the respondent is viewing the page multiple times, either through the use of a back button or by exiting and reopening the survey. For example, let’s say a respondent submits a page after 20 seconds, goes back to that page using the back button, and then submits the page again after 30 seconds. Their recorded Page Submit time will be 50 seconds.
# @version 0.0.1


class SurveyResponseQuestionRecord(TypedDict):
    # The question posed to the user
    prompt: str
    # The possible values displayed to the user.
    displayed: List[str]
    # Labels attached to the question
    labels: str
    # The selected display values. For single choice, the array will be of length 1.
    selected: List[str]
    # Additional text given by the respondent
    text: str
    # Metrics collected on this page.
    metrics: SurveyResponseQuestionMetricRecord
    # If true, indicates that the record is frozen
    isFrozen: bool


SurveyResponseQuestionRecord_old = {
    # The question posed to the user
    "prompt": str,
    # The possible values displayed to the user.
    "displayed": [str],
    # Labels attached to the question
    "labels": str,
    # The selected display values. For single choice, the array will be of length 1.
    "selected": [str],
    # Additional text given by the respondent
    "text": str,
    # Metrics collected on this page.
    "metrics": SurveyResponseQuestionMetricRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


# Captured questions and answers from an administered survey
# @version 0.0.1


SurveyResponseRecord = {
    # The unique identifier for the response.
    "responseID": str,
    # The timestamp in which the survey was started
    "start": datetime,
    # The timestamp in which the survey was finished
    "stop": datetime,
    # The type of measurement observed
    "finished": bool,
    # The fields (questions) displayed to the user
    "displayedFields": [str],
    # The answers to questions displayed to the user. The key is the field listed in displayedFields.
    "questions": Dict[str, SurveyResponseQuestionRecord],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


# A task to be done or has been done for a project/study
# @version 0.0.1


TaskRecord = {
    # The unique identifier
    "id": APIID,
    # The name of the individual task
    "name": str,
    # When the task was scheduled to happen
    "scheduledFor": datetime,
    # When the task was actually completed
    "completedAt": datetime,
    # When the task was marked as missed
    "missedAt": datetime,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for users
    "userIDs": [APIID],
    # Lookup id numbers for homes
    "homeIDs": [APIID],
    # Lookup id numbers for subjects
    "subjectIDs": [APIID],
    # Lookup id numbers for issues
    "issueIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # Lookup id number for completedBy
    "completedByID": APIID,
    # Lookup id number for missedBy
    "missedByID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A task to be done or has been done for a study
# @version 0.0.1


TaskTypeRecord = {
    # The unique identifier
    "id": APIID,
    # A short descriptive name for the task type
    "name": str,
    # The long description of the task type
    "description": str,
    # If true than the task is rescheduled at an interval specified by repeatInterval
    "repeating": bool,
    # How long between repeating tasks
    "repeatInterval": Duration,
    # How long after the trigger will the task it be considered due
    "daysTillDue": Duration,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for triggeredTasks
    "triggeredTaskIDs": [APIID],
    # Lookup id number for enrollmentTrigger
    "enrollmentTriggerID": APIID,
    # Lookup id number for taskTrigger
    "taskTriggerID": APIID,
    # Lookup id numbers for tasks
    "taskIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


# Coordinate location and associated image
# @version 0.0.1


TestNeuropsychImagerecogCoordRecord = {
    # The row number of the image.
    "row": int,
    # The column number of the image.
    "col": int,
    # An optional image associated with this coordinate. This will be the image file name or an empty string.
    "img": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


# Thunderboard snapshot encapsulates readings from the various sensors on a thunderboard, see https://www.silabs.com/products/development-tools/thunderboard/thunderboard-iot-kit-platform
# @version 0.0.1


ThunderboardSnapshotRecord = {
    # The mac address of the device that collected the data
    "macaddress": str,
    # The time at which the thunderboard device was polled
    "timestamp": datetime,
    # The temperature measured by the thunderboard in degrees Celcius
    "temperature": int,
    # The humidity measured by the thunderboard in Relative Humidity (RH). See https://en.wikipedia.org/wiki/Relative_humidity
    "humidity": int,
    # The UV Index measured by the thunderboard. See https://en.wikipedia.org/wiki/Ultraviolet_index
    "uvIndex": int,
    # The atmospheric pressure measured by the thunderboard in millibars
    "pressure": int,
    # Ambient light measured by the thunderboard in Lux
    "ambientLight": int,
    # The sound level measured by the thunderboard in dB
    "sound": int,
    # The amount of carbon dioxide in the air measured by the thunderboard in parts per million
    "carbonDioxide": int,
    # Total Volatile Organic Compounds in the air measured by the thunderboard measured in parts per billion. See https://en.wikipedia.org/wiki/Volatile_organic_compound
    "totalVOC": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An timeline event outlining what happened, who did it and to who.
# @version 0.0.1


TimelineRecord = {
    # The type of object that the timeline belongs to
    "objectType": str,
    # The id of the object that the timeline belongs to
    "objectID": int,
    # A unix timestamp indicating the time at which the timeline event was created
    "stamp": datetime,
    # The id of the user who created the timeline event
    "userID": int,
    # The type of timeline event (enumeration)
    "type": int,
    # A descriptive comment about what happened
    "comment": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# TimerCap device which is either iSorts or iCaps, see https://timercap.com
# @version 0.0.1


TimercapDeviceRecord = {
    # The macaddress of the device
    "macaddress": str,
    # The 'capnumber' which is printed on the device
    "number": int,
    # ￼The number of rows for this device. iCaps have 0 and iSorts can have several
    "rows": int,
    # The type of TimerCap device. This will be either 'iCap' or 'iSort'
    "type": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# TimerCap close records collected from either iSorts or iCaps, see https://timercap.com
# @version 0.0.1


TimercapCloseEventRecordRecord = {
    # The TimerCap device that collected the data
    "device": TimercapDeviceRecord,
    # This is written LAST_RECORD_NUMBER in a range from 1- 65535. The LAST_RECORD_NUMBER is set to ZERO when the firmware is burned, and then it increments at each CLOSE, and is then recorded in this record.
    "recordNumber": int,
    # The day of the week of the door which triggered the event. See https://golang.org/pkg/time/#Weekday
    "weekDay": int,
    # The time at which the door was either closed or opened with resolution only in seconds.
    "timestamp": datetime,
    # Whether or not the event was created when a door was opened.
    "doorOpen": bool,
    # A bitmask describing the state of all the doors. A binary representation describes the doors as either open (1) or closed (0) where the first bit in big endian representation represents Saturday and the seventh bit represents Sunday. BoxState is a uint16 and therefore can represent a 2-row pillbox where the 8th bit represents Saturday and the 14th bit represents Sunday in the second row.
    "boxState": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


# A set of timestamps describing the status of a timercap device data sync
# @version 0.0.1


TimercapHeartbeatRecord = {
    # A unix timestamp indicating the time at which the heartbeat occurred
    "stamp": datetime,
    # The macaddress of the timercap device
    "macaddress": str,
    # The unique identifier assigned by Timercap for the device type
    "type": str,
    # The time of the last sync attempt
    "attempted": datetime,
    # The time of the last successful sync attempt
    "synced": datetime,
    # The time of the last data point pulled from the pillbox
    "pulled": datetime,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The type of trip event
# @version 0.0.1


TripEventTypeRecord = {
    # The  unique identifier
    "id": APIID,
    # A short name for the event type
    "name": str,
    # A longer description of the event type
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An  user who has access to the data streams. This can be researchers, study admins, etc
# @version 0.0.1


UserRecord = {
    # The linux user name to add to hub computers for remote connection
    "username": str,
    # The primary email associated with the user.
    "email": str,
    # Notifications sent
    "notificationSent": [AlertNotificationSentRecord],
    # The  unique identifier
    "id": APIID,
    # The name that will be displayed in UIs for this user.
    "name": str,
    # The user's phone number used for sending multi factor authentication one time codes
    "phone": str,
    # A unique string given to the user to use along with their id as way to identify themselves for token generation
    "secret": str,
    # A one time password sent to the user as part of multifacter authentication
    "oneTimePassword": str,
    # The time at which the one time password will be considered as expired and no longer valid
    "oneTimePasswordExpiration": datetime,
    # If this user is on a trial. Trial versions will be restricted in what they can do.
    "trial": bool,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for subjects
    "subjectIDs": [APIID],
    # Lookup id numbers for homes
    "homeIDs": [APIID],
    # Lookup id numbers for issues
    "issueIDs": [APIID],
    # Lookup id numbers for issuesAssigned
    "issuesAssignedIDs": [APIID],
    # Lookup id numbers for tags
    "tagIDs": [APIID],
    # Lookup id numbers for roles
    "roleIDs": [APIID],
    # Lookup id numbers for tasks
    "taskIDs": [APIID],
    # Lookup id numbers for notificationGroups
    "notificationGroupIDs": [APIID],
    # Lookup id numbers for accounts
    "accountIDs": [APIID],
    # Lookup id numbers for webAuthCredentials
    "webAuthCredentialIDs": [APIID],
    # Lookup id numbers for inventoryTags
    "inventoryTagIDs": [APIID],
    # Lookup id numbers for identifiers
    "identifierIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An external identifier for the user to map the it's data to an external database
# @version 0.0.1


UserIdentifierRecord = {
    # The identification string
    "value": str,
    # The unique identifier
    "id": APIID,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id number for type
    "typeID": APIID,
    # Lookup id number for user
    "userID": APIID,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A type of external identifier for the user to map the it's data to an external database
# @version 0.0.1


UserIdentifierTypeRecord = {
    # A short unique name to categorize the identifiers
    "name": str,
    # The unique identifier
    "id": APIID,
    # A description of the external database
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for identifiers
    "identifierIDs": [APIID],
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A tag used to categorize a set of users
# @version 0.0.1


UserTagRecord = {
    # The unique identifier
    "id": APIID,
    # A unique name for the tag
    "name": str,
    # A longer description of the tag
    "description": str,
    # A hexidecimal representation of a color for this tag
    "color": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for users
    "userIDs": [APIID],
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A short lived token used to identify the user
# @version 0.0.1


UserTokenRecord = {
    # The unique identifier for the token
    "uuid": str,
    # A unique descriptive name for the token given by the user
    "name": str,
    # The access token
    "access": str,
    # When the record is to expire
    "expiration": datetime,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


# The type of vehicle event
# @version 0.0.1


VehicleEventTypeRecord = {
    # The  unique identifier
    "id": APIID,
    # A short name for the event type
    "name": str,
    # A longer description of the event type
    "description": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An set of basic metrics measured by a withings scale
# @version 0.0.1


WithingsBodyRecord = {
    # A unix timestamp indicating the time at which the measurement was taken
    "stamp": datetime,
    # The withings user account id associated with the collected metrics
    "withingsId": int,
    # The macaddress of the withings scale
    "macaddress": str,
    # The withings model id for the device checking in
    "model": int,
    # The current battery level as a percentage
    "batteryLevel": int,
    # The weight measured in grams
    "weight": int,
    # The fat weight measured in grams
    "fatMass": int,
    # The water weight measured in grams
    "waterMass": int,
    # The bone weight measured in grams
    "boneMass": int,
    # The muscle weight measured in grams
    "muscleMass": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Nokia device information, see https://health.nokia.com
# @version 0.0.1


WithingsDeviceRecord = {
    # The true macaddress of the device. This may not always be the broadcasted mac address of the device
    "macaddress": str,
    # The broadcasted name of the device
    "name": str,
    # The current signal strength of the device
    "rssi": int,
    # The unique identifier assigned by Withings for the device type
    "type": int,
    # The current battery level of the device
    "battery": int,
    # The version of the firmware currently on the device
    "firmware": int,
    # The unique identifier assigned to the device's model
    "model": int,
    # The unique identifier assigned to the mannufacturer who made the device
    "manufacturer": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Information about the last checkin from the scale
# @version 0.0.1


WithingsDeviceCheckinRecord = {
    # A unix timestamp indicating the time at which the checkin occurred
    "stamp": datetime,
    # The macaddress of the withings device
    "macaddress": str,
    # The withings model id for the device checking in
    "model": int,
    # The current battery level as a percentage
    "batteryLevel": int,
    # The current firmware of the device
    "firmware": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# A set of timestamps describing the status of a withings device data sync
# @version 0.0.1


WithingsDeviceHeartbeatRecord = {
    # A unix timestamp indicating the time at which the heartbeat occurred
    "stamp": datetime,
    # The macaddress of the withings device
    "macaddress": str,
    # The unique identifier assigned by Withings for the device type
    "type": int,
    # The time of the last sync attempt
    "attempted": datetime,
    # The time of the last successful sync attempt
    "synced": datetime,
    # The time of the last data point pulled from the watch
    "pulled": datetime,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# An set of heart metrics measured by a withings scale
# @version 0.0.1


WithingsHeartRecord = {
    # A unix timestamp indicating the time at which the measurement was taken
    "stamp": datetime,
    # The withings user account id associated with the collected metrics
    "withingsId": int,
    # The macaddress of the withings scale
    "macaddress": str,
    # The withings model id for the device checking in
    "model": int,
    # The measured heart rate using electrical pulses send through the foot
    "heartRate": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# intraday high frequency activity measures
# @version 0.0.1


WithingsHighfreqActivityRecord = {
    # A unix timestamp indicating the time at which the measurement was taken
    "stamp": datetime,
    # Withings deviceid
    "deviceId": str,
    # Withings modelid
    "modelId": int,
    # The length of time of this epoch in which the measurements were taken
    "duration": Duration,
    # step count
    "steps": int,
    # floors climbed
    "elevation": int,
    # kCal estimated
    "calories": int,
    # distance (meters)
    "distance": int,
    # swim strokes
    "strokes": int,
    # pool laps
    "poolLap": int,
    # heart rate
    "heartRate": int,
    # SpO2 measurement automatically tracked by a device tracker
    "spo2Auto": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Nokia account user information, see https://health.nokia.com
# @version 0.0.1


WithingsUserRecord = {
    # The first name of the user
    "first": str,
    # The last name of the user
    "last": str,
    # The gender of the user (0 -> female, 1 -> male)
    "gender": int,
    # The birthday of the user as a unix timestamp
    "birthday": int,
    # The height of the user in centimeters
    "height": int,
    # The weight of the user in grams
    "weight": int,
    # The unique identifier assigned to the user by Withings
    "withingsId": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Nokia high frequency activity information, see https://health.nokia.com
# @version 0.0.1


WithingsVasistasRecord = {
    # The Withings device that collection the data
    "device": WithingsDeviceRecord,
    # The Withings user associated with the data
    "user": WithingsUserRecord,
    # The number of stories the user has ascended
    "ascent": int,
    # The total number of calories burned included both active and passive periods
    "calories": int,
    # The calories burned while being active
    "caloriesEarned": int,
    # How many levels the user has descended, assumming this is in stories of a building
    "descent": int,
    # How far the user has traveled using step counts
    "distance": int,
    # The length of time of this epoch in which the measurements were taken
    "duration": int,
    # The metabolic calories used (even by resting) during this period
    "metabolicCalories": int,
    # The metabolic calories earned during this period
    "metabolicCaloriesEarned": int,
    # The running state of the user (1->Not running, 2->running)
    "runState": int,
    # The sleeping state of the user (0->Wake, 1->Light, 2->Deep, 3->REM) for this period
    "sleepState": int,
    # The starting timestamp of this period as a unix timestamp
    "stamp": datetime,
    # The number of steps made by the user during this period
    "steps": int,
    # The number of laps that the user has gone during this period
    "swimLaps": int,
    # If the user is walking (1->false, 2->true)
    "walkState": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Individual computer use sessions tracked using the WorkTime software. See https://www.worktime.com/
# @version 0.0.1


WorktimeSessionRecord = {
    # Unique indentifier for the session instance
    "id": APIID,
    # The ip address of the WorkTime Server
    "hostIP": str,
    # The unique identifier for the user name. This is not unique to the user using the workstation but the name itself.
    "userID": int,
    # The unique identifier for the workstation name. Workstations with the same name with share the same id value.
    "workstationID": int,
    # The date in which the session started
    "date": datetime,
    # The timestamp in which the session started.  The timestamp is recorded and stored as the local time (i.e. time zone) to which the the user's workstation is set.
    "begin": datetime,
    # The timestamp in which the session ended.  The timestamp is recorded and stored as the local time (i.e. time zone) to which the the user's workstation is set. If the session is current than this value is null.
    "end": datetime,
    # The id of the application being used. The value is null if unable to detect the application.
    "appID": int,
    # The name of the application being used. The value is null if unable to detect the application.
    "appName": str,
    # The name of the application executable being used. The value is null if unable to detect the application.
    "appEXE": str,
    # The name of the application executable filename being used. The value is null if unable to detect the application.
    "appEXEFileName": str,
    # The id of the application document being used. The value is null if unable to detect the document.
    "docID": int,
    # The name of the application document being used. The value is null if unable to detect the document.
    "docName": str,
    # The id of the website being accessed. The value is null if unable to detect the website title.
    "siteID": int,
    # The title of the website being accessed. The value is null if unable to detect the website title.
    "siteName": str,
    # The id of the domain being accessed. The value is null if unable to detect the website.
    "domainID": int,
    # The name of the domain being accessed. The value is null if unable to detect the website.
    "domainName": str,
    # The id of the website URL being accessed. The value is null if unable to detect the website.
    "urlID": int,
    # The URL of the website being used. The value is null if unable to detect the website.
    "urlName": str,
    # The id of the search terms being used. The value is null if unable to detect the website.
    "searchID": int,
    # The search terms entered. The value is null if unable to detect the website.
    "searchName": str,
    # The worktime version
    "worktime": int,
    # Unknown
    "timeIndicator": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Individual computer users tracking by the WorkTime software. See https://www.worktime.com/
# @version 0.0.1


WorktimeUserRecord = {
    # The unique identifier for the user name. This is not unique to the user using the workstation but the name itself.
    "userID": int,
    # The unique identifier for the workstation name. Workstations with the same name with share the same id value.
    "workstationID": int,
    # The ip address of the WorkTime Server
    "hostIP": str,
    # Unique indentifier for the workstation/account combination
    "id": APIID,
    # The workstation user account name owned by the subject.
    "userName": str,
    # The computer name of the workstation used by the subject.
    "workstationName": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id number for subject
    "subjectID": APIID,
    # Lookup id number for organization
    "organizationID": APIID,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Zigbee device
# @version 0.0.1


ZigbeeDeviceRecord = {
    #
    "EUI": str,
    # The ZCLVersion attribute represents a published set of foundation items (in Chapter 2), such as global commands and functional descriptions
    "ZCLVersion": int,
    # The ApplicationVersion attribute is 8 bits in length and specifies the version number of the application software contained in the device. The usage of this attribute is manufacturer dependent.
    "applicationVersion": int,
    # The StackVersion attribute is 8 bits in length and specifies the version number of the implementation of the ZigBee stack contained in the device. The usage of this attribute is manufacturer dependent.
    "stackVersion": int,
    # The HWVersion attribute is 8 bits in length and specifies the version number of the hardware of the device. The usage of this attribute is manufacturer dependent.
    "hwVersion": int,
    # The ManufacturerName attribute is a maximum of 32 bytes in length and specifies the name of the manufacturer as a ZigBee character string.
    "manufacturerName": str,
    # The ModelIdentifier attribute is a maximum of 32 bytes in length and specifies the model number (or other identifier) assigned by the manufacturer as a ZigBee character string.
    "modelIdentifier": str,
    # The DateCode attribute is a ZigBee character string with a maximum length of 16 bytes. The first 8 char- acters specify the date of manufacturer of the device in international date notation according to ISO 8601, i.e., YYYYMMDD, e.g., 20060814. The final 8 characters MAY include country, factory, line, shift or other related information at the option of the manufacturer. The format of this information is manufacturer dependent.
    "dateCode": str,
    # The PowerSource attribute is 8 bits in length and specifies the source(s) of power available to the device. Bits b0–b6 of this attribute represent the primary power source of the device and bit b7 indicates whether the device has a secondary power source in the form of a battery backup. Bits b0–b6 of this attribute SHALL be set to one of the non-reserved values listed in Table 3-8. Bit b7 of this attribute SHALL be set to 1 if the device has a secondary power source in the form of a battery backup. Otherwise, bit b7 SHALL be set to 0.
    "powerSource": int,
    # The LocationDescription attribute is a maximum of 16 bytes in length and describes the physical location of the device as a ZigBee character string. This location description MAY be added into the device during commissioning.
    "locationDescription": str,
    # The PhysicalEnvironment attribute is 8 bits in length and specifies the type of physical environment in which the device will operate. This attribute SHALL be set to one of the non-reserved values listed in Table 3-9. All values are valid for endpoints supporting all profiles except when noted.
    "physicalEnvironment": int,
    # The DeviceEnabled attribute is a Boolean and specifies whether the device is enabled or disabled.  'Disabled' means that the device does not send or respond to application level commands, other than com- mands to read or write attributes. Values of attributes which depend on the operation of the application MAY be invalid, and any functionality triggered by writing to such attributes MAY be disabled. ZigBee networking functionality remains operational. If implemented, the identify cluster cannot be disabled, i.e., it remains functional regardless of this setting.
    "deviceEnabled": bool,
    # The AlarmMask attribute is 8 bits in length and specifies which of a number of general alarms MAY be generated, as listed in Table 3-11. A ‘1’ in each bit position enables the associated alarm. These alarms are provided as basic alarms that a device MAY use even if no other clusters with alarms are present on the device.
    "alarmMask": int,
    # The DisableLocalConfig attribute allows a number of local device configuration functions to be disabled. The intention of this attribute is to allow disabling of any local configuration user interface, for example to prevent reset or binding buttons being activated by non-authorized persons in a public building. Bit 0 of the DisableLocalConfig attribute disables any factory reset button (or equivalent) on the device. Bit 1 disables any device configuration button(s) (or equivalent)—for example, a bind button.
    "disableLocalConfig": int,
    # The SWBuildID attribute represents a detailed, manufacturer-specific reference to the version of the software.
    "softwareBuildID": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Zigbee zone status events
# @version 0.0.1


ZigbeeZoneStatusRecord = {
    # A timestamp indicating the time at which the event occurred
    "stamp": datetime,
    #
    "zigbeePANMember": ZigbeeDeviceRecord,
    #
    "zigbeeCoordinator": ZigbeeDeviceRecord,
    #
    "systemAlarm": bool,
    #
    "indicationFire": bool,
    #
    "indicationWaterOverflow": bool,
    #
    "indicationCO": bool,
    #
    "indicationCooking": bool,
    #
    "indicationIntrusion": bool,
    #
    "indicationPresence": bool,
    #
    "indicationFall": bool,
    #
    "indicationMovement": bool,
    #
    "indicationVibration": bool,
    #
    "indicationEmergency": bool,
    #
    "indicationGlassBreaking": bool,
    #
    "openPortal1": bool,
    #
    "openPortal2": bool,
    #
    "panic": bool,
    #
    "emergency": bool,
    #
    "alarm1": bool,
    #
    "alarm2": bool,
    #
    "lowBattery": bool,
    #
    "tampered": bool,
    #
    "supervisionReports": bool,
    #
    "restoreReports": bool,
    #
    "trouble": bool,
    #
    "acFault": bool,
    #
    "testMode": bool,
    #
    "batteryDefective": bool,
    # A bitmask representing the event that occurred as well as the state of the device. See http://www.zigbee.org/zigbee-for-developers/applicationstandards/zigbeehomeautomation/
    "bitmask": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Address details for a Zubie point.
# @version 0.0.1


ZubieAddressRecord = {
    # The street portion of the address
    "street": str,
    # The city portion of the address
    "city": str,
    # The state portion of the address
    "state": str,
    # The zipcode portion of the address
    "zipcode": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Information about the Zubie OBD sensor.
# @version 0.0.1


ZubieDeviceRecord = {
    # The database unique identifier
    "id": APIID,
    # The Zubie unique identifier
    "key": str,
    # The serial number printed on the back of the sensor
    "serial": str,
    # The status of the device, either pending or installed.
    "status": str,
    # Boolean indicating if device is currently considered connected to a vehicle.
    "isConnected": bool,
    # Timestamp of when device reported current disconnection, or null if device is still connected.
    "disconnected": datetime,
    # Timestamp of when server last received data from device.
    "lastTransmission": datetime,
    # The key identifying the associated vehicle.
    "vehicleKey": str,
    # When the record was created
    "createdAt": datetime,
    # The com.orcatech.user.id for the user who created the record
    "createdBy": int,
    # When the record was updated
    "updatedAt": datetime,
    # The com.orcatech.user.id for the user who updated the record
    "updatedBy": int,
    # When the record was deleted
    "deletedAt": datetime,
    # The com.orcatech.user.id for the user who deleted the record
    "deletedBy": int,
    # Lookup id numbers for studies
    "studyIDs": [APIID],
    # Lookup id numbers for organizations
    "organizationIDs": [APIID],
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Location coordinates
# @version 0.0.1


ZubiePointRecord = {
    # Latitude of the location
    "latitude": int,
    # Longitude of the location
    "longitude": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Contextual data about the vehicle used in the event
# @version 0.0.1


ZubieEventVehicleRecord = {
    # Zubie unique identifier.
    "key": str,
    # Vehicle nickname
    "nickname": str,
    # vehicle identifier information about make, model, etc
    "vin": str,
    # The current battery level of the vehicle
    "batteryLevel": int,
    # Vehicle location information
    "point": ZubiePointRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Contextual data about device events
# @version 0.0.1


ZubieEventDeviceRecord = {
    # Zubie unique identifier for the device
    "key": str,
    # Serial number of the device
    "serial": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Contextual data about devices when they transition between vehicles
# @version 0.0.1


ZubieEventContextDeviceClaimRecord = {
    # The date and time at which the event was recorded.
    "stamp": datetime,
    # Zubie's unique identifier for the event
    "event": str,
    # Zubie unique identifier for the claim
    "claimKey": str,
    # State and identification information about the vehicle
    "vehicle": ZubieEventVehicleRecord,
    # Identification information about the device
    "device": ZubieEventDeviceRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Contextual data about device events
# @version 0.0.1


ZubieEventContextDeviceRecord = {
    # The date and time at which the event was recorded.
    "stamp": datetime,
    # Zubie's unique identifier for the event
    "event": str,
    # State and identification information about the vehicle
    "vehicle": ZubieEventVehicleRecord,
    # Identification information about the device
    "device": ZubieEventDeviceRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Contextual data about vehicle location
# @version 0.0.1


ZubieEventContextVehicleLocationRecord = {
    # The date and time at which the event was recorded.
    "stamp": datetime,
    # Zubie's unique identifier for the event
    "event": str,
    # State and identification information about the vehicle
    "vehicle": ZubieEventVehicleRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Current state and identification information about a place
# @version 0.0.1


ZubieEventPlaceRecord = {
    # Zubie unique identifier.
    "key": str,
    # The name of the place
    "name": str,
    # Zubie's unique identifier for the event
    "address": str,
    # The radius of the place around the coordinates
    "radius": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Contextual data at a location
# @version 0.0.1


ZubieEventPointRecord = {
    # Zubie unique identifier.
    "key": str,
    # The date and time at which the reading was recorded.
    "stamp": datetime,
    # How fast the vehicle was moving at this point
    "acceleration": int,
    # The quality of the GPS when the measurement was taken
    "gpsQuality": int,
    # The date and time at which the gps was recorded.
    "gpsStamp": datetime,
    # Not documented by Zubie
    "heading": int,
    # Rotations per minute of the vehicle at this point
    "rpm": int,
    # Not documented by Zubie
    "speed": int,
    # Not documented by Zubie
    "speedBySecond": [int],
    # Vehicle location information
    "point": ZubiePointRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Contextual data about the vehicle at a particular location
# @version 0.0.1


ZubieEventContextVehicleGeofenceRecord = {
    # The date and time at which the event was recorded.
    "stamp": datetime,
    # Zubie's unique identifier for the event
    "event": str,
    # State and identification information about the vehicle
    "vehicle": ZubieEventVehicleRecord,
    # State and identification information about the place
    "place": ZubieEventPlaceRecord,
    # State and location information at this point
    "point": ZubieEventPointRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Current state and identification information about a trip
# @version 0.0.1


ZubieEventTripRecord = {
    # Zubie unique identifier.
    "key": str,
    # The distance travelled during the trip
    "distance": int,
    # State and location information about the point where the trip ended
    "startPoint": ZubiePointRecord,
    # State and location information about the point where the trip ended
    "endPoint": ZubiePointRecord,
    # Not documented by Zubie
    "fuelCost": int,
    # Not documented by Zubie
    "fuelCostCurrencyCode": str,
    # The number of times during the trip that a hard-brake event was detected
    "hardBrakes": int,
    # The number of times during the trip that a hard-acceleration event was detected
    "hardAccelerations": int,
    # Time spent in idle during the trip
    "idle": Duration,
    # The total number of trip points on city roads.
    "pointsCityCount": int,
    # The total number of trip points on highways.
    "pointsHWYCount": int,
    # The number of minor speeding events for city points in the trip
    "speedingCityMinorCount": int,
    # The number of major speeding events for city points in the trip
    "speedingCityMajorCount": int,
    # The number of minor speeding events for highway points in the trip
    "speedingHighwayMinorCount": int,
    # The number of major speeding events for highway points in the trip
    "speedingHighwayMajorCount": int,
    # The highest speed recorded during the trip
    "speedTop": int,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Contextual data about trip events
# @version 0.0.1


ZubieEventContextTripRecord = {
    # The date and time at which the event was recorded.
    "stamp": datetime,
    # Zubie's unique identifier for the event
    "event": str,
    # State and identification information about the vehicle
    "vehicle": ZubieEventVehicleRecord,
    # Information about the trip the vehicle was one when this event occured
    "trip": ZubieEventTripRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Contextual data about trip tagging events
# @version 0.0.1


ZubieEventContextTripTaggedRecord = {
    # The date and time at which the event was recorded.
    "stamp": datetime,
    # Zubie's unique identifier for the event
    "event": str,
    # Information about the trip the vehicle was one when this event occured
    "trip": ZubieEventTripRecord,
    # The value of the tag
    "tag": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Contextual data about vehicle alert events during a trip
# @version 0.0.1


ZubieEventContextTripAlertRecord = {
    # The date and time at which the event was recorded.
    "stamp": datetime,
    # Zubie's unique identifier for the event
    "event": str,
    # State and identification information about the vehicle
    "vehicle": ZubieEventVehicleRecord,
    # Information about the trip the vehicle was one when this event occured
    "trip": ZubieEventTripRecord,
    # State and location information at this point
    "point": ZubieEventPointRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
# Vehicle and device events
# @version 0.0.1
ZubieEventRecord = {
    # The date and time at which the event was recorded.
    "stamp": datetime,
    # Zubie's unique identifier for the event
    "key": str,
    # The serial number of the Zubie device that generated this event or this event is related to
    "deviceSerial": str,
    # The Zubie vehicle identifier of the Zubie vehicle that generated this event or this event is related to
    "vehicleKey": str,
    # Unique internal event identifier.
    "kind": str,
    # Additional contextual data about events relating to devices, null if event does not relate to a device.
    "contextDevice": ZubieEventContextDeviceRecord,
    # Additional contextual data about events relating to device claims, null if event does not relate to a device claim.
    "contextDeviceClaim": ZubieEventContextDeviceClaimRecord,
    # Additional contextual data about events relating to vehicle locations, null if event does not relate to a vehicle location.
    "contextVehicleLocation": ZubieEventContextVehicleLocationRecord,
    # Additional contextual data about events relating to vehicle geofencing, null if event does not relate to the vehicle's geofencing.
    "contextVehicleGeofence": ZubieEventContextVehicleGeofenceRecord,
    # Additional contextual data about events relating to trips, null if event does not relate to a trip.
    "contextTrip": ZubieEventContextTripRecord,
    # Additional contextual data about events relating to tagging trips, null if event does not relate to a tagged trip.
    "contextTripTagged": ZubieEventContextTripTaggedRecord,
    # Additional contextual data about events relating to trip alerts, null if event does not relate to a trip alert.
    "contextTripAlert": ZubieEventContextTripAlertRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


#
# @version 0.0.1


ZubieTagRecord = {
    # Unique identifier for the trip given by Zubie
    "key": str,
    # The name of the tag
    "name": str,
    # The color of the tag
    "color": str,
    # Type of tag. Must be Car, Trip or User.
    "type": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# The coordinates of a trip with relevant vehicle state information
# @version 0.0.1


ZubieTripBoundRecord = {
    # The coordinates of the bound
    "point": ZubiePointRecord,
    # The time at which this reading was taken
    "stamp": datetime,
    # The vehicle odometer at the point. Only set when true odometer reading is provided, else null.
    "odometer": int,
    # The vehicle's reported fuel level at the point.
    "fuelLevel": int,
    # The place identifier that corresponds to the trip point’s geographic location; will be null if the point has no corresponding place.
    "placeKey": str,
    # The address that corresponds to the trip point’s geographic location; will be null if the point has no corresponding address.
    "address": ZubieAddressRecord,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}
#
# @version 0.0.1


ZubieTripRecord = {
    # Unique identifier for the trip given by Zubie
    "key": str,
    # Zubie vehicle identifier
    "vehicleKey": str,
    # Zubie device identifier
    "deviceKey": str,
    # Zubie device serial number
    "deviceSerial": str,
    # Zubie user identifier
    "userKey": str,
    # Zubie account identifier
    "accountKey": str,
    # Where the trip started
    "startPoint": ZubieTripBoundRecord,
    # Where the trip ended
    "endPoint": ZubieTripBoundRecord,
    # The duration of the trip
    "duration": Duration,
    # Time spent in idle during the trip
    "idle": Duration,
    # Distance traveled in distanceUM
    "distanceOBD": int,
    # The trip distance, in decimal format, as calculated by summing the geographical distance between all the GPS points recorded during the trip. The obd_distance value is usually more accurate than the gps_distance value, but obd_distance is not always available. You should prefer the obd_distance value if it’s available, and fall back to the gps_distance value if necessary.
    "distanceGPS": int,
    # Unit of measure for obd_distance and gps_distance. mi or km.
    "distanceUM": str,
    # The highest speed recorded during the trip
    "speedTop": int,
    # Unit of measure for top_speed. mph or km/h
    "speedUM": str,
    # The number of times during the trip that a hard-brake event was detected
    "hardBrakes": int,
    # The number of times during the trip that a hard-acceleration event was detected
    "hardAccelerations": int,
    # The total number of trip points (uniformly sampled by time) on city roads. Total Points = ('pointsCityCount' + 'pointsHWYCount').
    "pointsCityCount": int,
    # The total number of trip points (uniformly sampled by time) on highways. Total Points = ('pointsCityCount' + 'pointsHWYCount').
    "pointsHWYCount": int,
    # The number of minor speeding events for city points in the trip
    "speedingCityMinorCount": int,
    # The number of major speeding events for city points in the trip
    "speedingCityMajorCount": int,
    # The number of minor speeding events for highway points in the trip
    "speedingHighwayMinorCount": int,
    # The number of major speeding events for highway points in the trip
    "speedingHighwayMajorCount": int,
    # A list of tags associated with this trip
    "tags": [ZubieTagRecord],
    # A string containing an encoded path of the trip’s gps points. See Google documentation. May be null in some cases if a preview path is not available (e.g. trip is too long, older trips)
    "path": str,
    # Estimated cost of fuel used
    "fuelCost": str,
    # Localized symbol to display for currency
    "fuelCostCurrencyCode": str,
    # Localized symbol to display for currency
    "fuelCostCurrencySymbol": str,
    # Price per gallon
    "fuelPPG": str,
    # Type of fuel used. regular, premium, diesel
    "fuelType": str,
    # Amount of fuel consumed on this trip (if reported by device)
    "fuelConsumed": int,
    # Unit of measure for fuel_consumed. gal or L
    "fuelConsumedUM": str,
    # How many segments make up this trip. Regular trips will be 1, merged trips more.
    "tripSegments": int,
    # A url from which to get a static image of the trip.
    "staticMapURL": str,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


# Vehicle state information collected at a certain time point
# @version 0.0.1


ZubieTripPointRecord = {
    # A list of events detected at this trip point. Can be any of hard-brake, rapid-accel, over-speed, geofence-enter, geofence-exit, speeding-minor, speeding-major.
    "events": [str],
    # The vehicle speed reported by engine
    "speed": int,
    # The vehicle speed based on GPS
    "speedGPS": int,
    # The difference of vehicle speed from the road’s speed limit, or null if not available. Units in the same measure as speed.
    "speedLimitDelta": int,
    # The vehicle acceleration recorded at the trip point. A positive value indicates acceleration; a negative value indicates deceleration
    "acceleration": int,
    # Unit of measure for acceleration. mph/s (Miles per hour per second) or m/s/s (Meters per second per second)
    "accelerationUM": str,
    # The vehicle heading recorded at the trip point; an integer.
    "heading": int,
    # The vehicle engine’s rotations-per-minute
    "rpm": int,
    # The date and time the trip point was recorded by the OBD device.
    "stamp": datetime,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}

# Location details recorded by the vehicle
# @version 0.0.1


ZubieVehicleTripPointRecord = {
    # The address closest to this point
    "address": ZubieAddressRecord,
    # The key referencing the related zubie place
    "placeKey": str,
    # Latitude and longitude coordinates
    "point": ZubiePointRecord,
    # The timestamp at which this measurement was taken
    "stamp": datetime,
    # If true, indicates that the record is frozen
    "isFrozen": bool,
}


# A map of schema to record types
RecordSchema = {
    "com.orcatech.alert.incident": {
        "record": AlertIncidentRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.alert.notification.group": {
        "record": AlertNotificationGroupRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "roleIDs": "com.orcatech.role",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
            "userIDs": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.role": "roleIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy" "userIDs",
        },
    },
    "com.orcatech.alert.notification.sent": {
        "record": AlertNotificationSentRecord,
        "fieldsWithRelationships": {
            "userIDs": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.user": "userIDs",
        },
    },
    "com.orcatech.alert.notification.type": {
        "record": AlertNotificationTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "credentialsID": "com.orcatech.integration.credential",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.integration.credential": "credentialsID",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.alert.status": {
        "record": AlertStatusRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.alert.type": {
        "record": AlertTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.algorithms.lineCalibration": {
        "record": AlgorithmsLineCalibrationRecord,
        "fieldsWithRelationships": {
            "lineID": "com.orcatech.sensor.line",
        },
        "relatedSchemas": {
            "com.orcatech.sensor.line": "lineID",
        },
    },
    "com.orcatech.algorithms.lineCalibration.parameters": {
        "record": AlgorithmsLineCalibrationParametersRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.algorithms.lineCalibration.segment": {
        "record": AlgorithmsLineCalibrationSegmentRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.algorithms.transitions": {
        "record": AlgorithmsTransitionsRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.algorithms.walkCandidate": {
        "record": AlgorithmsWalkCandidateRecord,
        "fieldsWithRelationships": {
            "lineID": "com.orcatech.sensor.line",
        },
        "relatedSchemas": {
            "com.orcatech.sensor.line": "lineID",
        },
    },
    "com.orcatech.algorithms.walkSegment": {
        "record": AlgorithmsWalkSegmentRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.algorithms.walkingSpeed": {
        "record": AlgorithmsWalkingSpeedRecord,
        "fieldsWithRelationships": {
            "lineID": "com.orcatech.sensor.line",
        },
        "relatedSchemas": {
            "com.orcatech.sensor.line": "lineID",
        },
    },
    "com.orcatech.algorithms.walkingSpeed.calibration": {
        "record": AlgorithmsWalkingSpeedCalibrationRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.algorithms.walkingSpeed.parameters": {
        "record": AlgorithmsWalkingSpeedParametersRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.animal": {
        "record": AnimalRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "homeIDs": "com.orcatech.home",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "typeID": "com.orcatech.animal.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.animal.type": "typeID",
            "com.orcatech.home": "homeIDs",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.animal.tag": {
        "record": AnimalTagRecord,
        "fieldsWithRelationships": {
            "animalIDs": "com.orcatech.animal",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.animal": "animalIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.animal.type": {
        "record": AnimalTypeRecord,
        "fieldsWithRelationships": {
            "animalIDs": "com.orcatech.animal",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.animal": "animalIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.app": {
        "record": AppRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "roleIDs": "com.orcatech.role",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.role": "roleIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.area": {
        "record": AreaRecord,
        "fieldsWithRelationships": {
            "adjacentAreaIDs": "com.orcatech.area",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "dwellingID": "com.orcatech.location.dwelling",
            "itemIDs": "com.orcatech.inventory.item",
            "lineID": "com.orcatech.sensor.line",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "tagIDs": "com.orcatech.area.tag",
            "typeID": "com.orcatech.area.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.area": "adjacentAreaIDs",
            "com.orcatech.area.tag": "tagIDs",
            "com.orcatech.area.type": "typeID",
            "com.orcatech.inventory.item": "itemIDs",
            "com.orcatech.location.dwelling": "dwellingID",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.sensor.line": "lineID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.area.category": {
        "record": AreaCategoryRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "typeIDs": "com.orcatech.area.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.area.type": "typeIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.area.tag": {
        "record": AreaTagRecord,
        "fieldsWithRelationships": {
            "areaIDs": "com.orcatech.area",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.area": "areaIDs",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.area.type": {
        "record": AreaTypeRecord,
        "fieldsWithRelationships": {
            "areaIDs": "com.orcatech.area",
            "categoryID": "com.orcatech.area.category",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.area": "areaIDs",
            "com.orcatech.area.category": "categoryID",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.automatic.address": {
        "record": AutomaticAddressRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.automatic.credentials": {
        "record": AutomaticCredentialsRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.automatic.location": {
        "record": AutomaticLocationRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.automatic.trip": {
        "record": AutomaticTripRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.automatic.trip.tag": {
        "record": AutomaticTripTagRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.automatic.user": {
        "record": AutomaticUserRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.automatic.user.metadata": {
        "record": AutomaticUserMetadataRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.automatic.user.profile": {
        "record": AutomaticUserProfileRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.automatic.vehicle": {
        "record": AutomaticVehicleRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.automatic.vehicle.event": {
        "record": AutomaticVehicleEventRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.automatic.vehicle.mil": {
        "record": AutomaticVehicleMilRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.beiwe.credential": {
        "record": BeiweCredentialRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyID": "com.orcatech.study",
            "subjectID": "com.orcatech.subject",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyID",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.beiwe.device.accelerometer": {
        "record": BeiweDeviceAccelerometerRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.beiwe.device.app.usage": {
        "record": BeiweDeviceAppUsageRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.beiwe.device.bluetooth": {
        "record": BeiweDeviceBluetoothRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.beiwe.device.call": {
        "record": BeiweDeviceCallRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.beiwe.device.gps": {
        "record": BeiweDeviceGpsRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.beiwe.device.gyroscope": {
        "record": BeiweDeviceGyroscopeRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.beiwe.device.log.android": {
        "record": BeiweDeviceLogAndroidRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.beiwe.device.log.ios": {
        "record": BeiweDeviceLogIosRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.beiwe.device.magnetometer": {
        "record": BeiweDeviceMagnetometerRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.beiwe.device.motion": {
        "record": BeiweDeviceMotionRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.beiwe.device.power": {
        "record": BeiweDevicePowerRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.beiwe.device.proximity": {
        "record": BeiweDeviceProximityRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.beiwe.device.reachability": {
        "record": BeiweDeviceReachabilityRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.beiwe.device.setting": {
        "record": BeiweDeviceSettingRecord,
        "fieldsWithRelationships": {
            "accelerometerID": "com.orcatech.beiwe.setting.state",
            "bluetoothID": "com.orcatech.beiwe.setting.state",
            "callsID": "com.orcatech.beiwe.setting.state",
            "consentSectionIDs": "com.orcatech.beiwe.device.setting.consent.section",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "deviceID": "com.orcatech.inventory.item",
            "deviceMotionID": "com.orcatech.beiwe.setting.state",
            "gpsID": "com.orcatech.beiwe.setting.state",
            "gyroID": "com.orcatech.beiwe.setting.state",
            "magnetometerID": "com.orcatech.beiwe.setting.state",
            "organizationID": "com.orcatech.organization",
            "powerStateID": "com.orcatech.beiwe.setting.state",
            "proximityID": "com.orcatech.beiwe.setting.state",
            "reachabilityID": "com.orcatech.beiwe.setting.state",
            "studyIDs": "com.orcatech.study",
            "textsID": "com.orcatech.beiwe.setting.state",
            "updatedBy": "com.orcatech.user",
            "wifiID": "com.orcatech.beiwe.setting.state",
        },
        "relatedSchemas": {
            "com.orcatech.beiwe.device.setting.consent.section": "consentSectionIDs",
            "com.orcatech.beiwe.setting.state": "accelerometerID"
            "gpsID"
            "callsID"
            "textsID"
            "wifiID"
            "bluetoothID"
            "powerStateID"
            "proximityID"
            "gyroID"
            "magnetometerID"
            "deviceMotionID"
            "reachabilityID",
            "com.orcatech.inventory.item": "deviceID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.beiwe.device.setting.consent.section": {
        "record": BeiweDeviceSettingConsentSectionRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "requiredConsentIDs": "com.orcatech.beiwe.device.setting.consent.section.required",
            "settingID": "com.orcatech.beiwe.device.setting",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.beiwe.device.setting": "settingID",
            "com.orcatech.beiwe.device.setting.consent.section.required": "requiredConsentIDs",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.beiwe.device.setting.consent.section.required": {
        "record": BeiweDeviceSettingConsentSectionRequiredRecord,
        "fieldsWithRelationships": {
            "consentsID": "com.orcatech.beiwe.device.setting.consent.section",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "settingID": "com.orcatech.beiwe.device.setting.required",
            "studyID": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.beiwe.device.setting.consent.section": "consentsID",
            "com.orcatech.beiwe.device.setting.required": "settingID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.beiwe.device.setting.required": {
        "record": BeiweDeviceSettingRequiredRecord,
        "fieldsWithRelationships": {
            "consentSectionIDs": "com.orcatech.beiwe.device.setting.consent.section.required",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyID": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.beiwe.device.setting.consent.section.required": "consentSectionIDs",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.beiwe.device.sms": {
        "record": BeiweDeviceSmsRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.beiwe.device.wifi": {
        "record": BeiweDeviceWifiRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.beiwe.setting.state": {
        "record": BeiweSettingStateRecord,
        "fieldsWithRelationships": {
            "accelerometerSettingIDs": "com.orcatech.beiwe.device.setting",
            "bluetoothSettingIDs": "com.orcatech.beiwe.device.setting",
            "callsSettingIDs": "com.orcatech.beiwe.device.setting",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "deviceMotionSettingIDs": "com.orcatech.beiwe.device.setting",
            "gpsSettingIDs": "com.orcatech.beiwe.device.setting",
            "gyroSettingIDs": "com.orcatech.beiwe.device.setting",
            "magnetometerSettingIDs": "com.orcatech.beiwe.device.setting",
            "organizationIDs": "com.orcatech.organization",
            "powerStateSettingIDs": "com.orcatech.beiwe.device.setting",
            "proximitySettingIDs": "com.orcatech.beiwe.device.setting",
            "reachabilitySettingIDs": "com.orcatech.beiwe.device.setting",
            "studyIDs": "com.orcatech.study",
            "textsSettingIDs": "com.orcatech.beiwe.device.setting",
            "updatedBy": "com.orcatech.user",
            "wifiSettingIDs": "com.orcatech.beiwe.device.setting",
        },
        "relatedSchemas": {
            "com.orcatech.beiwe.device.setting": "accelerometerSettingIDs"
            "gpsSettingIDs"
            "callsSettingIDs"
            "textsSettingIDs"
            "wifiSettingIDs"
            "bluetoothSettingIDs"
            "powerStateSettingIDs"
            "proximitySettingIDs"
            "gyroSettingIDs"
            "magnetometerSettingIDs"
            "deviceMotionSettingIDs"
            "reachabilitySettingIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.coordinate": {
        "record": CoordinateRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.device.event.type": {
        "record": DeviceEventTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.device.input": {
        "record": DeviceInputRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.device.input.event": {
        "record": DeviceInputEventRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.emfit.bedexit": {
        "record": EmfitBedexitRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.emfit.calc": {
        "record": EmfitCalcRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.emfit.event": {
        "record": EmfitEventRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.emfit.hrv": {
        "record": EmfitHrvRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.emfit.hrvLinear": {
        "record": EmfitHrvLinearRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.emfit.hrvrmssd": {
        "record": EmfitHrvrmssdRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.emfit.liveHRV": {
        "record": EmfitLiveHRVRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.emfit.poll": {
        "record": EmfitPollRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.emfit.sleep": {
        "record": EmfitSleepRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.emfit.summary": {
        "record": EmfitSummaryRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.emfit.summaryString": {
        "record": EmfitSummaryStringRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.emfit.vitals": {
        "record": EmfitVitalsRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.event": {
        "record": EventRecord,
        "fieldsWithRelationships": {
            "source": "com.orcatech.inventory.item",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.item": "source",
        },
    },
    "com.orcatech.event.change.field": {
        "record": EventChangeFieldRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.event.type": {
        "record": EventTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.fibaro.event": {
        "record": FibaroEventRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.history.association": {
        "record": HistoryAssociationRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.history.field": {
        "record": HistoryFieldRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.home": {
        "record": HomeRecord,
        "fieldsWithRelationships": {
            "animalIDs": "com.orcatech.animal",
            "attributeIDs": "com.orcatech.home.attribute",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "dwellingID": "com.orcatech.location.dwelling",
            "identifierIDs": "com.orcatech.home.identifier",
            "integrationCredentialIDs": "com.orcatech.integration.credential",
            "issueIDs": "com.orcatech.issue",
            "itemIDs": "com.orcatech.inventory.item",
            "organizationID": "com.orcatech.organization",
            "personIDs": "com.orcatech.person",
            "phoneID": "com.orcatech.phone",
            "sensorLineIDs": "com.orcatech.sensor.line",
            "studyIDs": "com.orcatech.study",
            "subjectIDs": "com.orcatech.subject",
            "tagIDs": "com.orcatech.home.tag",
            "taskIDs": "com.orcatech.task",
            "updatedBy": "com.orcatech.user",
            "userIDs": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.animal": "animalIDs",
            "com.orcatech.home.attribute": "attributeIDs",
            "com.orcatech.home.identifier": "identifierIDs",
            "com.orcatech.home.tag": "tagIDs",
            "com.orcatech.integration.credential": "integrationCredentialIDs",
            "com.orcatech.inventory.item": "itemIDs",
            "com.orcatech.issue": "issueIDs",
            "com.orcatech.location.dwelling": "dwellingID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.person": "personIDs",
            "com.orcatech.phone": "phoneID",
            "com.orcatech.sensor.line": "sensorLineIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectIDs",
            "com.orcatech.task": "taskIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy" "userIDs",
        },
    },
    "com.orcatech.home.attribute": {
        "record": HomeAttributeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "homeID": "com.orcatech.home",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "typeID": "com.orcatech.home.attribute.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.home": "homeID",
            "com.orcatech.home.attribute.type": "typeID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.home.attribute.type": {
        "record": HomeAttributeTypeRecord,
        "fieldsWithRelationships": {
            "attributeIDs": "com.orcatech.home.attribute",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.home.attribute": "attributeIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.home.identifier": {
        "record": HomeIdentifierRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "homeID": "com.orcatech.home",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "typeID": "com.orcatech.home.identifier.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.home": "homeID",
            "com.orcatech.home.identifier.type": "typeID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.home.identifier.type": {
        "record": HomeIdentifierTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "identifierIDs": "com.orcatech.home.identifier",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.home.identifier": "identifierIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.home.tag": {
        "record": HomeTagRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "homeIDs": "com.orcatech.home",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.home": "homeIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.integration": {
        "record": IntegrationRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "credentialIDs": "com.orcatech.integration.credential",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyID": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.integration.credential": "credentialIDs",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.integration.credential": {
        "record": IntegrationCredentialRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "homeID": "com.orcatech.home",
            "integrationID": "com.orcatech.integration",
            "organizationID": "com.orcatech.organization",
            "stateIDs": "com.orcatech.integration.credential.state",
            "studyID": "com.orcatech.study",
            "subjectID": "com.orcatech.subject",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.home": "homeID",
            "com.orcatech.integration": "integrationID",
            "com.orcatech.integration.credential.state": "stateIDs",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyID",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.integration.credential.state": {
        "record": IntegrationCredentialStateRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "credentialID": "com.orcatech.integration.credential",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyID": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.integration.credential": "credentialID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.inventory.item": {
        "record": InventoryItemRecord,
        "fieldsWithRelationships": {
            "areaID": "com.orcatech.area",
            "attributeIDs": "com.orcatech.inventory.item.attribute",
            "beiweDeviceSettingID": "com.orcatech.beiwe.device.setting",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "firstLineSegmentID": "com.orcatech.sensor.line.segment",
            "homeID": "com.orcatech.home",
            "identifierIDs": "com.orcatech.inventory.item.identifier",
            "issueIDs": "com.orcatech.issue",
            "modelID": "com.orcatech.inventory.model",
            "organizationID": "com.orcatech.organization",
            "secondLineSegmentID": "com.orcatech.sensor.line.segment",
            "stateID": "com.orcatech.inventory.item.state",
            "studyIDs": "com.orcatech.study",
            "subjectID": "com.orcatech.subject",
            "tagIDs": "com.orcatech.inventory.tag",
            "updatedBy": "com.orcatech.user",
            "userIDs": "com.orcatech.inventory.item.user",
        },
        "relatedSchemas": {
            "com.orcatech.area": "areaID",
            "com.orcatech.beiwe.device.setting": "beiweDeviceSettingID",
            "com.orcatech.home": "homeID",
            "com.orcatech.inventory.item.attribute": "attributeIDs",
            "com.orcatech.inventory.item.identifier": "identifierIDs",
            "com.orcatech.inventory.item.state": "stateID",
            "com.orcatech.inventory.item.user": "userIDs",
            "com.orcatech.inventory.model": "modelID",
            "com.orcatech.inventory.tag": "tagIDs",
            "com.orcatech.issue": "issueIDs",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.sensor.line.segment": "firstLineSegmentID"
            "secondLineSegmentID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.inventory.item.attribute": {
        "record": InventoryItemAttributeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "itemID": "com.orcatech.inventory.item",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "typeID": "com.orcatech.inventory.item.attribute.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.item": "itemID",
            "com.orcatech.inventory.item.attribute.type": "typeID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.inventory.item.attribute.type": {
        "record": InventoryItemAttributeTypeRecord,
        "fieldsWithRelationships": {
            "attributeIDs": "com.orcatech.inventory.item.attribute",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.item.attribute": "attributeIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.inventory.item.identifier": {
        "record": InventoryItemIdentifierRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "itemID": "com.orcatech.inventory.item",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "typeID": "com.orcatech.inventory.item.identifier.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.item": "itemID",
            "com.orcatech.inventory.item.identifier.type": "typeID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.inventory.item.identifier.type": {
        "record": InventoryItemIdentifierTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "identifierIDs": "com.orcatech.inventory.item.identifier",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.item.identifier": "identifierIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.inventory.item.state": {
        "record": InventoryItemStateRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "itemIDs": "com.orcatech.inventory.item",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.item": "itemIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.inventory.item.status": {
        "record": InventoryItemStatusRecord,
        "fieldsWithRelationships": {
            "itemID": "com.orcatech.inventory.item",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.item": "itemID",
        },
    },
    "com.orcatech.inventory.item.user": {
        "record": InventoryItemUserRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "itemID": "com.orcatech.inventory.item",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.item": "itemID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.inventory.model": {
        "record": InventoryModelRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "itemIDs": "com.orcatech.inventory.item",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "tagIDs": "com.orcatech.inventory.tag",
            "updatedBy": "com.orcatech.user",
            "vendorID": "com.orcatech.inventory.vendor",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.item": "itemIDs",
            "com.orcatech.inventory.tag": "tagIDs",
            "com.orcatech.inventory.vendor": "vendorID",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.inventory.tag": {
        "record": InventoryTagRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "itemIDs": "com.orcatech.inventory.item",
            "modelIDs": "com.orcatech.inventory.model",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
            "userID": "com.orcatech.user",
            "vendorIDs": "com.orcatech.inventory.vendor",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.item": "itemIDs",
            "com.orcatech.inventory.model": "modelIDs",
            "com.orcatech.inventory.vendor": "vendorIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy" "userID",
        },
    },
    "com.orcatech.inventory.user": {
        "record": InventoryUserRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyID": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.inventory.vendor": {
        "record": InventoryVendorRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "modelIDs": "com.orcatech.inventory.model",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "tagIDs": "com.orcatech.inventory.tag",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.model": "modelIDs",
            "com.orcatech.inventory.tag": "tagIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.irb.document": {
        "record": IrbDocumentRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "stateID": "com.orcatech.irb.state",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.irb.state": "stateID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.irb.state": {
        "record": IrbStateRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "documentIDs": "com.orcatech.irb.document",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.irb.document": "documentIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.issue": {
        "record": IssueRecord,
        "fieldsWithRelationships": {
            "assignedToIDs": "com.orcatech.user",
            "commentIDs": "com.orcatech.issue.comment",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "hemisphereCassetteIDs": "com.orcatech.pathology.hemisphere.cassette",
            "hemisphereIDs": "com.orcatech.pathology.hemisphere",
            "hemisphereSliceIDs": "com.orcatech.pathology.hemisphere.slice",
            "hemisphereSlideIDs": "com.orcatech.pathology.hemisphere.slide",
            "homeIDs": "com.orcatech.home",
            "itemIDs": "com.orcatech.inventory.item",
            "organizationIDs": "com.orcatech.organization",
            "sourceID": "com.orcatech.issue.source",
            "stateID": "com.orcatech.issue.state",
            "studyIDs": "com.orcatech.study",
            "subjectIDs": "com.orcatech.subject",
            "tagIDs": "com.orcatech.issue.tag",
            "taskIDs": "com.orcatech.task",
            "trackingIDs": "com.orcatech.user",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.home": "homeIDs",
            "com.orcatech.inventory.item": "itemIDs",
            "com.orcatech.issue.comment": "commentIDs",
            "com.orcatech.issue.source": "sourceID",
            "com.orcatech.issue.state": "stateID",
            "com.orcatech.issue.tag": "tagIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.pathology.hemisphere": "hemisphereIDs",
            "com.orcatech.pathology.hemisphere.cassette": "hemisphereCassetteIDs",
            "com.orcatech.pathology.hemisphere.slice": "hemisphereSliceIDs",
            "com.orcatech.pathology.hemisphere.slide": "hemisphereSlideIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectIDs",
            "com.orcatech.task": "taskIDs",
            "com.orcatech.user": "createdBy"
            "updatedBy"
            "deletedBy"
            "trackingIDs"
            "assignedToIDs",
        },
    },
    "com.orcatech.issue.comment": {
        "record": IssueCommentRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "issueID": "com.orcatech.issue",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.issue": "issueID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.issue.source": {
        "record": IssueSourceRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "issueIDs": "com.orcatech.issue",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.issue": "issueIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.issue.state": {
        "record": IssueStateRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "issueIDs": "com.orcatech.issue",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.issue": "issueIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.issue.tag": {
        "record": IssueTagRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "issueIDs": "com.orcatech.issue",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.issue": "issueIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.location": {
        "record": LocationRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "dwellingIDs": "com.orcatech.location.dwelling",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "typeID": "com.orcatech.location.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.location.dwelling": "dwellingIDs",
            "com.orcatech.location.type": "typeID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.location.dwelling": {
        "record": LocationDwellingRecord,
        "fieldsWithRelationships": {
            "areaIDs": "com.orcatech.area",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "homeID": "com.orcatech.home",
            "locationID": "com.orcatech.location",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.area": "areaIDs",
            "com.orcatech.home": "homeID",
            "com.orcatech.location": "locationID",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.location.type": {
        "record": LocationTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "locationIDs": "com.orcatech.location",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.location": "locationIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.log": {
        "record": LogRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.access.period": {
        "record": MeasureAccessPeriodRecord,
        "fieldsWithRelationships": {
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "user": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "user",
        },
    },
    "com.orcatech.measure.access.request": {
        "record": MeasureAccessRequestRecord,
        "fieldsWithRelationships": {
            "user": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.user": "user",
        },
    },
    "com.orcatech.measure.activity.physical.period": {
        "record": MeasureActivityPhysicalPeriodRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.application.user.period": {
        "record": MeasureApplicationUserPeriodRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.battery": {
        "record": MeasureBatteryRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.bed.activity": {
        "record": MeasureBedActivityRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.bed.awake.period": {
        "record": MeasureBedAwakePeriodRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.bed.exit.period": {
        "record": MeasureBedExitPeriodRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.body.weight": {
        "record": MeasureBodyWeightRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.checkin": {
        "record": MeasureCheckinRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.contact": {
        "record": MeasureContactRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.coordinate": {
        "record": MeasureCoordinateRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.device.event": {
        "record": MeasureDeviceEventRecord,
        "fieldsWithRelationships": {
            "deviceID": "com.orcatech.inventory.item",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.item": "deviceID",
        },
    },
    "com.orcatech.measure.heart.rate": {
        "record": MeasureHeartRateRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.heart.rate.period": {
        "record": MeasureHeartRatePeriodRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.heart.rate.variability.period": {
        "record": MeasureHeartRateVariabilityPeriodRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.heart.rate.variability.rmssd": {
        "record": MeasureHeartRateVariabilityRmssdRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.pillbox.state": {
        "record": MeasurePillboxStateRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.presence": {
        "record": MeasurePresenceRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.respiration.rate": {
        "record": MeasureRespirationRateRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.respiration.rate.period": {
        "record": MeasureRespirationRatePeriodRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.sleep.movement.fast": {
        "record": MeasureSleepMovementFastRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.sleep.movement.fast.period": {
        "record": MeasureSleepMovementFastPeriodRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.sleep.movement.period": {
        "record": MeasureSleepMovementPeriodRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.sleep.period": {
        "record": MeasureSleepPeriodRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.sleep.score.period": {
        "record": MeasureSleepScorePeriodRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.sleep.state.period": {
        "record": MeasureSleepStatePeriodRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.step.period": {
        "record": MeasureStepPeriodRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.swim.period": {
        "record": MeasureSwimPeriodRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.trip": {
        "record": MeasureTripRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.trip.event": {
        "record": MeasureTripEventRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.vehicle.event": {
        "record": MeasureVehicleEventRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.vehicle.mil": {
        "record": MeasureVehicleMilRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.vehicle.state": {
        "record": MeasureVehicleStateRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.measure.web.search": {
        "record": MeasureWebSearchRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.medication": {
        "record": MedicationRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.medtracker.device": {
        "record": MedtrackerDeviceRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.medtracker.report": {
        "record": MedtrackerReportRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.medtracker.report.state": {
        "record": MedtrackerReportStateRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.medtracker.status": {
        "record": MedtrackerStatusRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.mfa.webauthn.credential": {
        "record": MfaWebauthnCredentialRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "updatedBy": "com.orcatech.user",
            "userID": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy" "userID",
        },
    },
    "com.orcatech.microservice": {
        "record": MicroserviceRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.microservice.change": {
        "record": MicroserviceChangeRecord,
        "fieldsWithRelationships": {
            "userID": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.user": "userID",
        },
    },
    "com.orcatech.migration.state": {
        "record": MigrationStateRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.milestone": {
        "record": MilestoneRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "stateID": "com.orcatech.milestone.state",
            "studyID": "com.orcatech.study",
            "typeID": "com.orcatech.milestone.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.milestone.state": "stateID",
            "com.orcatech.milestone.type": "typeID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.milestone.state": {
        "record": MilestoneStateRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "milestoneIDs": "com.orcatech.milestone",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.milestone": "milestoneIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.milestone.type": {
        "record": MilestoneTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "milestoneIDs": "com.orcatech.milestone",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.milestone": "milestoneIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.nonce": {
        "record": NonceRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.nyce.event": {
        "record": NyceEventRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.observation.generic": {
        "record": ObservationGenericRecord,
        "fieldsWithRelationships": {
            "homeID": "com.orcatech.home",
            "hubItemID": "com.orcatech.inventory.item",
            "itemID": "com.orcatech.inventory.item",
            "organizationID": "com.orcatech.organization",
            "studyID": "com.orcatech.study",
            "subjectID": "com.orcatech.subject",
            "surveyID": "com.orcatech.survey",
            "userID": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.home": "homeID",
            "com.orcatech.inventory.item": "itemID" "hubItemID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyID",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.survey": "surveyID",
            "com.orcatech.user": "userID",
        },
    },
    "com.orcatech.observation.generic.event.alert.meta": {
        "record": ObservationGenericEventAlertMetaRecord,
        "fieldsWithRelationships": {
            "areaID": "com.orcatech.area",
            "homeAnimalIDs": "com.orcatech.animal",
            "homeDwellingID": "com.orcatech.location.dwelling",
            "homeID": "com.orcatech.home",
            "homeResidentIDs": "com.orcatech.person",
            "homeSubjectIDs": "com.orcatech.subject",
            "homeTagIDs": "com.orcatech.home.tag",
            "hubItemID": "com.orcatech.inventory.item",
            "itemID": "com.orcatech.inventory.item",
            "itemStateID": "com.orcatech.inventory.item.state",
            "itemTagIDs": "com.orcatech.inventory.tag",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectHomeIDs": "com.orcatech.home",
            "subjectID": "com.orcatech.subject",
            "subjectTagIDs": "com.orcatech.subject.tag",
        },
        "relatedSchemas": {
            "com.orcatech.animal": "homeAnimalIDs",
            "com.orcatech.area": "areaID",
            "com.orcatech.home": "homeID" "subjectHomeIDs",
            "com.orcatech.home.tag": "homeTagIDs",
            "com.orcatech.inventory.item": "itemID" "hubItemID",
            "com.orcatech.inventory.item.state": "itemStateID",
            "com.orcatech.inventory.tag": "itemTagIDs",
            "com.orcatech.location.dwelling": "homeDwellingID",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.person": "homeResidentIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "homeSubjectIDs" "subjectID",
            "com.orcatech.subject.tag": "subjectTagIDs",
        },
    },
    "com.orcatech.observation.generic.event.status.meta": {
        "record": ObservationGenericEventStatusMetaRecord,
        "fieldsWithRelationships": {
            "areaID": "com.orcatech.area",
            "homeAnimalIDs": "com.orcatech.animal",
            "homeDwellingID": "com.orcatech.location.dwelling",
            "homeID": "com.orcatech.home",
            "homeResidentIDs": "com.orcatech.person",
            "homeSubjectIDs": "com.orcatech.subject",
            "homeTagIDs": "com.orcatech.home.tag",
            "hubItemID": "com.orcatech.inventory.item",
            "itemID": "com.orcatech.inventory.item",
            "itemStateID": "com.orcatech.inventory.item.state",
            "itemTagIDs": "com.orcatech.inventory.tag",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectHomeIDs": "com.orcatech.home",
            "subjectID": "com.orcatech.subject",
            "subjectTagIDs": "com.orcatech.subject.tag",
        },
        "relatedSchemas": {
            "com.orcatech.animal": "homeAnimalIDs",
            "com.orcatech.area": "areaID",
            "com.orcatech.home": "homeID" "subjectHomeIDs",
            "com.orcatech.home.tag": "homeTagIDs",
            "com.orcatech.inventory.item": "itemID" "hubItemID",
            "com.orcatech.inventory.item.state": "itemStateID",
            "com.orcatech.inventory.tag": "itemTagIDs",
            "com.orcatech.location.dwelling": "homeDwellingID",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.person": "homeResidentIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "homeSubjectIDs" "subjectID",
            "com.orcatech.subject.tag": "subjectTagIDs",
        },
    },
    "com.orcatech.observation.generic.event.storage.meta": {
        "record": ObservationGenericEventStorageMetaRecord,
        "fieldsWithRelationships": {
            "userID": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.user": "userID",
        },
    },
    "com.orcatech.observation.generic.measure.meta": {
        "record": ObservationGenericMeasureMetaRecord,
        "fieldsWithRelationships": {
            "areaID": "com.orcatech.area",
            "homeAnimalIDs": "com.orcatech.animal",
            "homeDwellingID": "com.orcatech.location.dwelling",
            "homeID": "com.orcatech.home",
            "homeResidentIDs": "com.orcatech.person",
            "homeSubjectIDs": "com.orcatech.subject",
            "homeTagIDs": "com.orcatech.home.tag",
            "hubItemID": "com.orcatech.inventory.item",
            "itemID": "com.orcatech.inventory.item",
            "itemStateID": "com.orcatech.inventory.item.state",
            "itemTagIDs": "com.orcatech.inventory.tag",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectHomeIDs": "com.orcatech.home",
            "subjectID": "com.orcatech.subject",
            "subjectTagIDs": "com.orcatech.subject.tag",
        },
        "relatedSchemas": {
            "com.orcatech.animal": "homeAnimalIDs",
            "com.orcatech.area": "areaID",
            "com.orcatech.home": "homeID" "subjectHomeIDs",
            "com.orcatech.home.tag": "homeTagIDs",
            "com.orcatech.inventory.item": "itemID" "hubItemID",
            "com.orcatech.inventory.item.state": "itemStateID",
            "com.orcatech.inventory.tag": "itemTagIDs",
            "com.orcatech.location.dwelling": "homeDwellingID",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.person": "homeResidentIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "homeSubjectIDs" "subjectID",
            "com.orcatech.subject.tag": "subjectTagIDs",
        },
    },
    "com.orcatech.observation.generic.report.meta": {
        "record": ObservationGenericReportMetaRecord,
        "fieldsWithRelationships": {
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectID": "com.orcatech.subject",
            "subjectTagIDs": "com.orcatech.subject.tag",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.subject.tag": "subjectTagIDs",
        },
    },
    "com.orcatech.observation.generic.survey.meta": {
        "record": ObservationGenericSurveyMetaRecord,
        "fieldsWithRelationships": {
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectID": "com.orcatech.subject",
            "subjectTagIDs": "com.orcatech.subject.tag",
            "surveyID": "com.orcatech.survey",
            "userID": "com.orcatech.user",
            "userTagIDs": "com.orcatech.user.tag",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.subject.tag": "subjectTagIDs",
            "com.orcatech.survey": "surveyID",
            "com.orcatech.user": "userID",
            "com.orcatech.user.tag": "userTagIDs",
        },
    },
    "com.orcatech.observation.generic.test.meta": {
        "record": ObservationGenericTestMetaRecord,
        "fieldsWithRelationships": {
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectID": "com.orcatech.subject",
            "subjectTagIDs": "com.orcatech.subject.tag",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.subject.tag": "subjectTagIDs",
        },
    },
    "com.orcatech.observation.vendor": {
        "record": ObservationVendorRecord,
        "fieldsWithRelationships": {
            "homeID": "com.orcatech.home",
            "hubItemID": "com.orcatech.inventory.item",
            "itemID": "com.orcatech.inventory.item",
            "organizationID": "com.orcatech.organization",
            "studyID": "com.orcatech.study",
            "subjectID": "com.orcatech.subject",
            "surveyID": "com.orcatech.survey",
            "userID": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.home": "homeID",
            "com.orcatech.inventory.item": "itemID" "hubItemID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyID",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.survey": "surveyID",
            "com.orcatech.user": "userID",
        },
    },
    "com.orcatech.organization": {
        "record": OrganizationRecord,
        "fieldsWithRelationships": {
            "pluginIDs": "com.orcatech.plugin",
            "roleIDs": "com.orcatech.role",
            "studyIDs": "com.orcatech.study",
        },
        "relatedSchemas": {
            "com.orcatech.plugin": "pluginIDs",
            "com.orcatech.role": "roleIDs",
            "com.orcatech.study": "studyIDs",
        },
    },
    "com.orcatech.organization.identifier": {
        "record": OrganizationIdentifierRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.organization.identifier.type": {
        "record": OrganizationIdentifierTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.organization.status": {
        "record": OrganizationStatusRecord,
        "fieldsWithRelationships": {
            "organizationID": "com.orcatech.organization",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
        },
    },
    "com.orcatech.pathology.apoe.allele": {
        "record": PathologyApoeAlleleRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "summaryIDs": "com.orcatech.pathology.clinical.summary",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.pathology.clinical.summary": "summaryIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.autopsy": {
        "record": PathologyAutopsyRecord,
        "fieldsWithRelationships": {
            "autopsyHemisphereID": "com.orcatech.pathology.autopsy.hemisphere",
            "caseTypeID": "com.orcatech.pathology.autopsy.caseType",
            "clinicalSummaryID": "com.orcatech.pathology.clinical.summary",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "genderID": "com.orcatech.subject.gender",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.autopsy.caseType": "caseTypeID",
            "com.orcatech.pathology.autopsy.hemisphere": "autopsyHemisphereID",
            "com.orcatech.pathology.clinical.summary": "clinicalSummaryID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject.gender": "genderID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.autopsy.caseType": {
        "record": PathologyAutopsyCaseTypeRecord,
        "fieldsWithRelationships": {
            "autopsyIDs": "com.orcatech.pathology.autopsy",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.pathology.autopsy": "autopsyIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.autopsy.hemisphere": {
        "record": PathologyAutopsyHemisphereRecord,
        "fieldsWithRelationships": {
            "autopsyID": "com.orcatech.pathology.autopsy",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "diagnosisIDs": "com.orcatech.pathology.diagnosis.autopsy.hemisphere",
            "hemisphereID": "com.orcatech.pathology.hemisphere",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.autopsy": "autopsyID",
            "com.orcatech.pathology.diagnosis.autopsy.hemisphere": "diagnosisIDs",
            "com.orcatech.pathology.hemisphere": "hemisphereID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.clinical.summary": {
        "record": PathologyClinicalSummaryRecord,
        "fieldsWithRelationships": {
            "apoeAllele1ID": "com.orcatech.pathology.apoe.allele",
            "apoeAllele2ID": "com.orcatech.pathology.apoe.allele",
            "autopsyID": "com.orcatech.pathology.autopsy",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "diagnosisAtLastVisitID": "com.orcatech.pathology.diagnosis.type.visit",
            "diagnosisClinicalIDs": "com.orcatech.pathology.diagnosis.type.clinical",
            "hemisphereID": "com.orcatech.pathology.hemisphere",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectID": "com.orcatech.subject",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.apoe.allele": "apoeAllele1ID" "apoeAllele2ID",
            "com.orcatech.pathology.autopsy": "autopsyID",
            "com.orcatech.pathology.diagnosis.type.clinical": "diagnosisClinicalIDs",
            "com.orcatech.pathology.diagnosis.type.visit": "diagnosisAtLastVisitID",
            "com.orcatech.pathology.hemisphere": "hemisphereID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.diagnosis.autopsy.hemisphere": {
        "record": PathologyDiagnosisAutopsyHemisphereRecord,
        "fieldsWithRelationships": {
            "autopsyHemisphereIDs": "com.orcatech.pathology.autopsy.hemisphere",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.autopsy.hemisphere": "autopsyHemisphereIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.diagnosis.type.clinical": {
        "record": PathologyDiagnosisTypeClinicalRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "summaryIDs": "com.orcatech.pathology.clinical.summary",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.pathology.clinical.summary": "summaryIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.diagnosis.type.visit": {
        "record": PathologyDiagnosisTypeVisitRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "summaryIDs": "com.orcatech.pathology.clinical.summary",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.pathology.clinical.summary": "summaryIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.hemisphere": {
        "record": PathologyHemisphereRecord,
        "fieldsWithRelationships": {
            "autopsyHemisphereID": "com.orcatech.pathology.autopsy.hemisphere",
            "clinicalSummaryID": "com.orcatech.pathology.clinical.summary",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "issueIDs": "com.orcatech.issue",
            "maskIDs": "com.orcatech.pathology.mask.hemisphere",
            "montageID": "com.orcatech.pathology.scan.processing.montage",
            "organizationID": "com.orcatech.organization",
            "scanIDs": "com.orcatech.pathology.scan.hemisphere",
            "sliceIDs": "com.orcatech.pathology.hemisphere.slice",
            "studyIDs": "com.orcatech.study",
            "subjectID": "com.orcatech.subject",
            "tagIDs": "com.orcatech.pathology.tag",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.issue": "issueIDs",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.autopsy.hemisphere": "autopsyHemisphereID",
            "com.orcatech.pathology.clinical.summary": "clinicalSummaryID",
            "com.orcatech.pathology.hemisphere.slice": "sliceIDs",
            "com.orcatech.pathology.mask.hemisphere": "maskIDs",
            "com.orcatech.pathology.scan.hemisphere": "scanIDs",
            "com.orcatech.pathology.scan.processing.montage": "montageID",
            "com.orcatech.pathology.tag": "tagIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.hemisphere.cassette": {
        "record": PathologyHemisphereCassetteRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "issueIDs": "com.orcatech.issue",
            "organizationID": "com.orcatech.organization",
            "processingID": "com.orcatech.pathology.scan.processing.hemisphere.cassette",
            "referenceImageIDs": "com.orcatech.pathology.image.hemisphere.cassette",
            "regionImageIDs": "com.orcatech.pathology.image.hemisphere.cassette.stain.region",
            "regionMapImageID": "com.orcatech.pathology.image.hemisphere.cassette.map.region",
            "registeredImageIDs": "com.orcatech.pathology.image.hemisphere.cassette.stain",
            "registrationID": "com.orcatech.pathology.registration.hemisphere.cassette",
            "sliceID": "com.orcatech.pathology.hemisphere.slice",
            "slideIDs": "com.orcatech.pathology.hemisphere.slide",
            "studyIDs": "com.orcatech.study",
            "tagIDs": "com.orcatech.pathology.tag",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.issue": "issueIDs",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.hemisphere.slice": "sliceID",
            "com.orcatech.pathology.hemisphere.slide": "slideIDs",
            "com.orcatech.pathology.image.hemisphere.cassette": "referenceImageIDs",
            "com.orcatech.pathology.image.hemisphere.cassette.map.region": "regionMapImageID",
            "com.orcatech.pathology.image.hemisphere.cassette.stain": "registeredImageIDs",
            "com.orcatech.pathology.image.hemisphere.cassette.stain.region": "regionImageIDs",
            "com.orcatech.pathology.registration.hemisphere.cassette": "registrationID",
            "com.orcatech.pathology.scan.processing.hemisphere.cassette": "processingID",
            "com.orcatech.pathology.tag": "tagIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.hemisphere.slice": {
        "record": PathologyHemisphereSliceRecord,
        "fieldsWithRelationships": {
            "cassetteIDs": "com.orcatech.pathology.hemisphere.cassette",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "hemisphereID": "com.orcatech.pathology.hemisphere",
            "issueIDs": "com.orcatech.issue",
            "organizationID": "com.orcatech.organization",
            "scanIDs": "com.orcatech.pathology.scan.hemisphere.slice",
            "studyIDs": "com.orcatech.study",
            "tagIDs": "com.orcatech.pathology.tag",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.issue": "issueIDs",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.hemisphere": "hemisphereID",
            "com.orcatech.pathology.hemisphere.cassette": "cassetteIDs",
            "com.orcatech.pathology.scan.hemisphere.slice": "scanIDs",
            "com.orcatech.pathology.tag": "tagIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.hemisphere.slide": {
        "record": PathologyHemisphereSlideRecord,
        "fieldsWithRelationships": {
            "cassetteID": "com.orcatech.pathology.hemisphere.cassette",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "issueIDs": "com.orcatech.issue",
            "organizationID": "com.orcatech.organization",
            "processingID": "com.orcatech.pathology.scan.processing.hemisphere.slide",
            "stainID": "com.orcatech.pathology.stain",
            "studyIDs": "com.orcatech.study",
            "tagIDs": "com.orcatech.pathology.tag",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.issue": "issueIDs",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.hemisphere.cassette": "cassetteID",
            "com.orcatech.pathology.scan.processing.hemisphere.slide": "processingID",
            "com.orcatech.pathology.stain": "stainID",
            "com.orcatech.pathology.tag": "tagIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.image.hemisphere.cassette": {
        "record": PathologyImageHemisphereCassetteRecord,
        "fieldsWithRelationships": {
            "cassetteID": "com.orcatech.pathology.hemisphere.cassette",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "typeID": "com.orcatech.pathology.image.hemisphere.cassette.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.hemisphere.cassette": "cassetteID",
            "com.orcatech.pathology.image.hemisphere.cassette.type": "typeID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.image.hemisphere.cassette.map.region": {
        "record": PathologyImageHemisphereCassetteMapRegionRecord,
        "fieldsWithRelationships": {
            "cassetteID": "com.orcatech.pathology.hemisphere.cassette",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.hemisphere.cassette": "cassetteID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.image.hemisphere.cassette.stain": {
        "record": PathologyImageHemisphereCassetteStainRecord,
        "fieldsWithRelationships": {
            "cassetteID": "com.orcatech.pathology.hemisphere.cassette",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "stainID": "com.orcatech.pathology.stain",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.hemisphere.cassette": "cassetteID",
            "com.orcatech.pathology.stain": "stainID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.image.hemisphere.cassette.stain.region": {
        "record": PathologyImageHemisphereCassetteStainRegionRecord,
        "fieldsWithRelationships": {
            "cassetteID": "com.orcatech.pathology.hemisphere.cassette",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "regionID": "com.orcatech.pathology.region",
            "stainID": "com.orcatech.pathology.stain",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.hemisphere.cassette": "cassetteID",
            "com.orcatech.pathology.region": "regionID",
            "com.orcatech.pathology.stain": "stainID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.image.hemisphere.cassette.type": {
        "record": PathologyImageHemisphereCassetteTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "imageIDs": "com.orcatech.pathology.image.hemisphere.cassette",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.pathology.image.hemisphere.cassette": "imageIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.mask.hemisphere": {
        "record": PathologyMaskHemisphereRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "hemisphereID": "com.orcatech.pathology.hemisphere",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.hemisphere": "hemisphereID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.region": {
        "record": PathologyRegionRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "imageIDs": "com.orcatech.pathology.image.hemisphere.cassette.stain.region",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.pathology.image.hemisphere.cassette.stain.region": "imageIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.registration.hemisphere.cassette": {
        "record": PathologyRegistrationHemisphereCassetteRecord,
        "fieldsWithRelationships": {
            "cassetteID": "com.orcatech.pathology.hemisphere.cassette",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "fileIDs": "com.orcatech.pathology.registration.hemisphere.cassette.file",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.hemisphere.cassette": "cassetteID",
            "com.orcatech.pathology.registration.hemisphere.cassette.file": "fileIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.registration.hemisphere.cassette.file": {
        "record": PathologyRegistrationHemisphereCassetteFileRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "registrationCassetteID": "com.orcatech.pathology.registration.hemisphere.cassette",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.registration.hemisphere.cassette": "registrationCassetteID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.registration.hemisphere.slice": {
        "record": PathologyRegistrationHemisphereSliceRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "scanHemisphereID": "com.orcatech.pathology.scan.hemisphere",
            "scanSliceID": "com.orcatech.pathology.scan.hemisphere.slice",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.scan.hemisphere": "scanHemisphereID",
            "com.orcatech.pathology.scan.hemisphere.slice": "scanSliceID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.scan.hemisphere": {
        "record": PathologyScanHemisphereRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "hemisphereID": "com.orcatech.pathology.hemisphere",
            "organizationID": "com.orcatech.organization",
            "processingID": "com.orcatech.pathology.scan.processing.hemisphere",
            "registrationID": "com.orcatech.pathology.registration.hemisphere.slice",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.hemisphere": "hemisphereID",
            "com.orcatech.pathology.registration.hemisphere.slice": "registrationID",
            "com.orcatech.pathology.scan.processing.hemisphere": "processingID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.scan.hemisphere.slice": {
        "record": PathologyScanHemisphereSliceRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "processingID": "com.orcatech.pathology.scan.processing.hemisphere.slice",
            "registrationID": "com.orcatech.pathology.registration.hemisphere.slice",
            "sliceID": "com.orcatech.pathology.hemisphere.slice",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.hemisphere.slice": "sliceID",
            "com.orcatech.pathology.registration.hemisphere.slice": "registrationID",
            "com.orcatech.pathology.scan.processing.hemisphere.slice": "processingID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.scan.processing.hemisphere": {
        "record": PathologyScanProcessingHemisphereRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "scanHemisphereID": "com.orcatech.pathology.scan.hemisphere",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.scan.hemisphere": "scanHemisphereID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.scan.processing.hemisphere.cassette": {
        "record": PathologyScanProcessingHemisphereCassetteRecord,
        "fieldsWithRelationships": {
            "cassetteID": "com.orcatech.pathology.hemisphere.cassette",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.hemisphere.cassette": "cassetteID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.scan.processing.hemisphere.slice": {
        "record": PathologyScanProcessingHemisphereSliceRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "scanSliceID": "com.orcatech.pathology.scan.hemisphere.slice",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.scan.hemisphere.slice": "scanSliceID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.scan.processing.hemisphere.slide": {
        "record": PathologyScanProcessingHemisphereSlideRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "slideID": "com.orcatech.pathology.hemisphere.slide",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.hemisphere.slide": "slideID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.scan.processing.montage": {
        "record": PathologyScanProcessingMontageRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "hemisphereID": "com.orcatech.pathology.hemisphere",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.hemisphere": "hemisphereID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.stain": {
        "record": PathologyStainRecord,
        "fieldsWithRelationships": {
            "cassetteImageIDs": "com.orcatech.pathology.image.hemisphere.cassette.stain",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "regionImageIDs": "com.orcatech.pathology.image.hemisphere.cassette.stain.region",
            "slideIDs": "com.orcatech.pathology.hemisphere.slide",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.pathology.hemisphere.slide": "slideIDs",
            "com.orcatech.pathology.image.hemisphere.cassette.stain": "cassetteImageIDs",
            "com.orcatech.pathology.image.hemisphere.cassette.stain.region": "regionImageIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.pathology.tag": {
        "record": PathologyTagRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "hemisphereCassetteIDs": "com.orcatech.pathology.hemisphere.cassette",
            "hemisphereIDs": "com.orcatech.pathology.hemisphere",
            "hemisphereSliceIDs": "com.orcatech.pathology.hemisphere.slice",
            "hemisphereSlideIDs": "com.orcatech.pathology.hemisphere.slide",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.pathology.hemisphere": "hemisphereIDs",
            "com.orcatech.pathology.hemisphere.cassette": "hemisphereCassetteIDs",
            "com.orcatech.pathology.hemisphere.slice": "hemisphereSliceIDs",
            "com.orcatech.pathology.hemisphere.slide": "hemisphereSlideIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.permission": {
        "record": PermissionRecord,
        "fieldsWithRelationships": {
            "actionID": "com.orcatech.permission.action",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "endpointID": "com.orcatech.permission.endpoint",
            "roleIDs": "com.orcatech.role",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.permission.action": "actionID",
            "com.orcatech.permission.endpoint": "endpointID",
            "com.orcatech.role": "roleIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.permission.action": {
        "record": PermissionActionRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "permissionIDs": "com.orcatech.permission",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.permission": "permissionIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.permission.endpoint": {
        "record": PermissionEndpointRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "permissionIDs": "com.orcatech.permission",
            "pluginIDs": "com.orcatech.plugin",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.permission": "permissionIDs",
            "com.orcatech.plugin": "pluginIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.person": {
        "record": PersonRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "homeIDs": "com.orcatech.home",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "tagIDs": "com.orcatech.subject.tag",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.home": "homeIDs",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject.tag": "tagIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.person.comment": {
        "record": PersonCommentRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "personID": "com.orcatech.person",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.person": "personID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.phone": {
        "record": PhoneRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "homeID": "com.orcatech.home",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectID": "com.orcatech.subject",
            "typeID": "com.orcatech.phone.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.home": "homeID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.phone.type": "typeID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.phone.type": {
        "record": PhoneTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "phoneIDs": "com.orcatech.phone",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.phone": "phoneIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.plugin": {
        "record": PluginRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "endpointIDs": "com.orcatech.permission.endpoint",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.permission.endpoint": "endpointIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.qualtrics.imagerecog": {
        "record": QualtricsImagerecogRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.qualtrics.input": {
        "record": QualtricsInputRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.qualtrics.question": {
        "record": QualtricsQuestionRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.qualtrics.question.choice": {
        "record": QualtricsQuestionChoiceRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.qualtrics.stroop": {
        "record": QualtricsStroopRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.qualtrics.survey": {
        "record": QualtricsSurveyRecord,
        "fieldsWithRelationships": {
            "surveyID": "com.orcatech.survey",
        },
        "relatedSchemas": {
            "com.orcatech.survey": "surveyID",
        },
    },
    "com.orcatech.qualtrics.survey.block": {
        "record": QualtricsSurveyBlockRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.qualtrics.survey.block.element": {
        "record": QualtricsSurveyBlockElementRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.qualtrics.survey.column": {
        "record": QualtricsSurveyColumnRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.qualtrics.survey.expiration": {
        "record": QualtricsSurveyExpirationRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.qualtrics.survey.flow": {
        "record": QualtricsSurveyFlowRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.qualtrics.survey.loop": {
        "record": QualtricsSurveyLoopRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.qualtrics.survey.loop.questionMeta": {
        "record": QualtricsSurveyLoopQuestionMetaRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.qualtrics.survey.question": {
        "record": QualtricsSurveyQuestionRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.qualtrics.survey.question.choice": {
        "record": QualtricsSurveyQuestionChoiceRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.qualtrics.survey.question.type": {
        "record": QualtricsSurveyQuestionTypeRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.qualtrics.survey.question.validation": {
        "record": QualtricsSurveyQuestionValidationRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.qualtrics.survey.response": {
        "record": QualtricsSurveyResponseRecord,
        "fieldsWithRelationships": {
            "surveyID": "com.orcatech.survey",
        },
        "relatedSchemas": {
            "com.orcatech.survey": "surveyID",
        },
    },
    "com.orcatech.qualtrics.trails": {
        "record": QualtricsTrailsRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.report.life.event": {
        "record": ReportLifeEventRecord,
        "fieldsWithRelationships": {
            "primaryCategoryID": "com.orcatech.subject.life.event.category.primary",
            "secondaryCategoryID": "com.orcatech.subject.life.event.category.secondary",
            "sourceID": "com.orcatech.subject.life.event.source",
            "tagIDs": "com.orcatech.subject.life.event.tag",
            "verifiedByID": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.subject.life.event.category.primary": "primaryCategoryID",
            "com.orcatech.subject.life.event.category.secondary": "secondaryCategoryID",
            "com.orcatech.subject.life.event.source": "sourceID",
            "com.orcatech.subject.life.event.tag": "tagIDs",
            "com.orcatech.user": "verifiedByID",
        },
    },
    "com.orcatech.role": {
        "record": RoleRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "permissionIDs": "com.orcatech.permission",
            "studyID": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
            "userIDs": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.permission": "permissionIDs",
            "com.orcatech.study": "studyID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy" "userIDs",
        },
    },
    "com.orcatech.schema": {
        "record": SchemaRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.sensor.alert": {
        "record": SensorAlertRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.sensor.line": {
        "record": SensorLineRecord,
        "fieldsWithRelationships": {
            "areaID": "com.orcatech.area",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "homeID": "com.orcatech.home",
            "organizationID": "com.orcatech.organization",
            "segmentIDs": "com.orcatech.sensor.line.segment",
            "studyIDs": "com.orcatech.study",
            "typeID": "com.orcatech.sensor.line.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.area": "areaID",
            "com.orcatech.home": "homeID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.sensor.line.segment": "segmentIDs",
            "com.orcatech.sensor.line.type": "typeID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.sensor.line.segment": {
        "record": SensorLineSegmentRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "firstID": "com.orcatech.inventory.item",
            "lineID": "com.orcatech.sensor.line",
            "organizationID": "com.orcatech.organization",
            "secondID": "com.orcatech.inventory.item",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.item": "firstID" "secondID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.sensor.line": "lineID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.sensor.line.type": {
        "record": SensorLineTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "lineIDs": "com.orcatech.sensor.line",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.sensor.line": "lineIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.sharp.audio": {
        "record": SharpAudioRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "inventoryItemID": "com.orcatech.inventory.item",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectIDs": "com.orcatech.subject",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.item": "inventoryItemID",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.sharp.coordinate": {
        "record": SharpCoordinateRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "inventoryItemID": "com.orcatech.inventory.item",
            "subjectID": "com.orcatech.subject",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.item": "inventoryItemID",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.sharp.event": {
        "record": SharpEventRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "inventoryItemID": "com.orcatech.inventory.item",
            "subjectID": "com.orcatech.subject",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.item": "inventoryItemID",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.sharp.participant.token": {
        "record": SharpParticipantTokenRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "subjectID": "com.orcatech.subject",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.subject": "subjectID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.sharp.path": {
        "record": SharpPathRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.sharp.path.marker": {
        "record": SharpPathMarkerRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.software": {
        "record": SoftwareRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "inventoryTagID": "com.orcatech.inventory.tag",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.inventory.tag": "inventoryTagID",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.software.apt": {
        "record": SoftwareAptRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.software.apt.repo": {
        "record": SoftwareAptRepoRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.sso.account": {
        "record": SsoAccountRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "providerID": "com.orcatech.sso.provider",
            "updatedBy": "com.orcatech.user",
            "userID": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.sso.provider": "providerID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy" "userID",
        },
    },
    "com.orcatech.sso.oauth2.scope": {
        "record": SsoOauth2ScopeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "providerID": "com.orcatech.sso.provider",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.sso.provider": "providerID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.sso.oauth2.token": {
        "record": SsoOauth2TokenRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "providerID": "com.orcatech.sso.provider",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.sso.provider": "providerID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.sso.provider": {
        "record": SsoProviderRecord,
        "fieldsWithRelationships": {
            "accountIDs": "com.orcatech.sso.account",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "scopeIDs": "com.orcatech.sso.oauth2.scope",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.sso.account": "accountIDs",
            "com.orcatech.sso.oauth2.scope": "scopeIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.study": {
        "record": StudyRecord,
        "fieldsWithRelationships": {
            "organizationIDs": "com.orcatech.organization",
            "pluginIDs": "com.orcatech.plugin",
            "roleIDs": "com.orcatech.role",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.plugin": "pluginIDs",
            "com.orcatech.role": "roleIDs",
        },
    },
    "com.orcatech.study.enrollment": {
        "record": StudyEnrollmentRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "stateID": "com.orcatech.study.enrollment.state",
            "studyID": "com.orcatech.study",
            "subjectIDs": "com.orcatech.subject",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyID",
            "com.orcatech.study.enrollment.state": "stateID",
            "com.orcatech.subject": "subjectIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.study.enrollment.state": {
        "record": StudyEnrollmentStateRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "enrollmentIDs": "com.orcatech.study.enrollment",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "taskTypeIDs": "com.orcatech.task.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.study.enrollment": "enrollmentIDs",
            "com.orcatech.task.type": "taskTypeIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.study.identifier": {
        "record": StudyIdentifierRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyID": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.study.identifier.type": {
        "record": StudyIdentifierTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.study.status": {
        "record": StudyStatusRecord,
        "fieldsWithRelationships": {
            "studyID": "com.orcatech.study",
        },
        "relatedSchemas": {
            "com.orcatech.study": "studyID",
        },
    },
    "com.orcatech.subject": {
        "record": SubjectRecord,
        "fieldsWithRelationships": {
            "attributeIDs": "com.orcatech.subject.attribute",
            "beiweCredentialIDs": "com.orcatech.beiwe.credential",
            "clinicalSummaryID": "com.orcatech.pathology.clinical.summary",
            "commentIDs": "com.orcatech.subject.comment",
            "contactIDs": "com.orcatech.subject.contact",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "ethnicityID": "com.orcatech.subject.ethnicity",
            "genderID": "com.orcatech.subject.gender",
            "hemisphereID": "com.orcatech.pathology.hemisphere",
            "homeIDs": "com.orcatech.home",
            "identifierIDs": "com.orcatech.subject.identifier",
            "integrationCredentialIDs": "com.orcatech.integration.credential",
            "issueIDs": "com.orcatech.issue",
            "itemIDs": "com.orcatech.inventory.item",
            "organizationID": "com.orcatech.organization",
            "phoneIDs": "com.orcatech.phone",
            "raceID": "com.orcatech.subject.race",
            "studiesEnrollmentIDs": "com.orcatech.study.enrollment",
            "studyIDs": "com.orcatech.study",
            "tagIDs": "com.orcatech.subject.tag",
            "taskIDs": "com.orcatech.task",
            "updatedBy": "com.orcatech.user",
            "userIDs": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.beiwe.credential": "beiweCredentialIDs",
            "com.orcatech.home": "homeIDs",
            "com.orcatech.integration.credential": "integrationCredentialIDs",
            "com.orcatech.inventory.item": "itemIDs",
            "com.orcatech.issue": "issueIDs",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.pathology.clinical.summary": "clinicalSummaryID",
            "com.orcatech.pathology.hemisphere": "hemisphereID",
            "com.orcatech.phone": "phoneIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.study.enrollment": "studiesEnrollmentIDs",
            "com.orcatech.subject.attribute": "attributeIDs",
            "com.orcatech.subject.comment": "commentIDs",
            "com.orcatech.subject.contact": "contactIDs",
            "com.orcatech.subject.ethnicity": "ethnicityID",
            "com.orcatech.subject.gender": "genderID",
            "com.orcatech.subject.identifier": "identifierIDs",
            "com.orcatech.subject.race": "raceID",
            "com.orcatech.subject.tag": "tagIDs",
            "com.orcatech.task": "taskIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy" "userIDs",
        },
    },
    "com.orcatech.subject.attribute": {
        "record": SubjectAttributeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectID": "com.orcatech.subject",
            "typeID": "com.orcatech.subject.attribute.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.subject.attribute.type": "typeID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.subject.attribute.type": {
        "record": SubjectAttributeTypeRecord,
        "fieldsWithRelationships": {
            "attributeIDs": "com.orcatech.subject.attribute",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject.attribute": "attributeIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.subject.comment": {
        "record": SubjectCommentRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectID": "com.orcatech.subject",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.subject.contact": {
        "record": SubjectContactRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "reasonID": "com.orcatech.subject.contact.reason",
            "studyIDs": "com.orcatech.study",
            "subjectID": "com.orcatech.subject",
            "typeID": "com.orcatech.subject.contact.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.subject.contact.reason": "reasonID",
            "com.orcatech.subject.contact.type": "typeID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.subject.contact.reason": {
        "record": SubjectContactReasonRecord,
        "fieldsWithRelationships": {
            "contactIDs": "com.orcatech.subject.contact",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject.contact": "contactIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.subject.contact.type": {
        "record": SubjectContactTypeRecord,
        "fieldsWithRelationships": {
            "contactIDs": "com.orcatech.subject.contact",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject.contact": "contactIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.subject.ethnicity": {
        "record": SubjectEthnicityRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectIDs": "com.orcatech.subject",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.subject.gender": {
        "record": SubjectGenderRecord,
        "fieldsWithRelationships": {
            "autopsyIDs": "com.orcatech.pathology.autopsy",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectIDs": "com.orcatech.subject",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.pathology.autopsy": "autopsyIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.subject.identifier": {
        "record": SubjectIdentifierRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectID": "com.orcatech.subject",
            "typeID": "com.orcatech.subject.identifier.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.subject.identifier.type": "typeID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.subject.identifier.type": {
        "record": SubjectIdentifierTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "identifierIDs": "com.orcatech.subject.identifier",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject.identifier": "identifierIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.subject.life.event.category.primary": {
        "record": SubjectLifeEventCategoryPrimaryRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "secondaryIDs": "com.orcatech.subject.life.event.category.secondary",
            "studyIDs": "com.orcatech.study",
            "tagIDs": "com.orcatech.subject.life.event.tag",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject.life.event.category.secondary": "secondaryIDs",
            "com.orcatech.subject.life.event.tag": "tagIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.subject.life.event.category.secondary": {
        "record": SubjectLifeEventCategorySecondaryRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "primaryID": "com.orcatech.subject.life.event.category.primary",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject.life.event.category.primary": "primaryID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.subject.life.event.source": {
        "record": SubjectLifeEventSourceRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.subject.life.event.tag": {
        "record": SubjectLifeEventTagRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "primaryID": "com.orcatech.subject.life.event.category.primary",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject.life.event.category.primary": "primaryID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.subject.race": {
        "record": SubjectRaceRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectIDs": "com.orcatech.subject",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.subject.tag": {
        "record": SubjectTagRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "distributionIDs": "com.orcatech.survey.distribution",
            "organizationIDs": "com.orcatech.organization",
            "personIDs": "com.orcatech.person",
            "studyIDs": "com.orcatech.study",
            "subjectIDs": "com.orcatech.subject",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.person": "personIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectIDs",
            "com.orcatech.survey.distribution": "distributionIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.survey": {
        "record": SurveyRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "distributionIDs": "com.orcatech.survey.distribution",
            "organizationID": "com.orcatech.organization",
            "studyID": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyID",
            "com.orcatech.survey.distribution": "distributionIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.survey.distribution": {
        "record": SurveyDistributionRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "surveyID": "com.orcatech.survey",
            "tagIDs": "com.orcatech.subject.tag",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject.tag": "tagIDs",
            "com.orcatech.survey": "surveyID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.survey.event": {
        "record": SurveyEventRecord,
        "fieldsWithRelationships": {
            "primaryCategoryID": "com.orcatech.survey.event.category.primary",
            "secondaryCategoryID": "com.orcatech.survey.event.category.secondary",
            "tagIDs": "com.orcatech.survey.event.tag",
        },
        "relatedSchemas": {
            "com.orcatech.survey.event.category.primary": "primaryCategoryID",
            "com.orcatech.survey.event.category.secondary": "secondaryCategoryID",
            "com.orcatech.survey.event.tag": "tagIDs",
        },
    },
    "com.orcatech.survey.event.category.primary": {
        "record": SurveyEventCategoryPrimaryRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "secondaryIDs": "com.orcatech.survey.event.category.secondary",
            "studyIDs": "com.orcatech.study",
            "tagIDs": "com.orcatech.survey.event.tag",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.survey.event.category.secondary": "secondaryIDs",
            "com.orcatech.survey.event.tag": "tagIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.survey.event.category.secondary": {
        "record": SurveyEventCategorySecondaryRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "primaryID": "com.orcatech.survey.event.category.primary",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.survey.event.category.primary": "primaryID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.survey.event.error": {
        "record": SurveyEventErrorRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.survey.event.tag": {
        "record": SurveyEventTagRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "primaryID": "com.orcatech.survey.event.category.primary",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.survey.event.category.primary": "primaryID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.survey.form": {
        "record": SurveyFormRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.survey.input": {
        "record": SurveyInputRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.survey.question": {
        "record": SurveyQuestionRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.survey.question.choice": {
        "record": SurveyQuestionChoiceRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.survey.response": {
        "record": SurveyResponseRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.survey.response.question": {
        "record": SurveyResponseQuestionRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.survey.response.question.metric": {
        "record": SurveyResponseQuestionMetricRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.survey.response.question.metric.click": {
        "record": SurveyResponseQuestionMetricClickRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.task": {
        "record": TaskRecord,
        "fieldsWithRelationships": {
            "completedByID": "com.orcatech.user",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "homeIDs": "com.orcatech.home",
            "issueIDs": "com.orcatech.issue",
            "missedByID": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectIDs": "com.orcatech.subject",
            "typeID": "com.orcatech.task.type",
            "updatedBy": "com.orcatech.user",
            "userIDs": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.home": "homeIDs",
            "com.orcatech.issue": "issueIDs",
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectIDs",
            "com.orcatech.task.type": "typeID",
            "com.orcatech.user": "createdBy"
            "updatedBy"
            "deletedBy"
            "userIDs"
            "completedByID"
            "missedByID",
        },
    },
    "com.orcatech.task.type": {
        "record": TaskTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "enrollmentTriggerID": "com.orcatech.study.enrollment.state",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "taskIDs": "com.orcatech.task",
            "taskTriggerID": "com.orcatech.task.type",
            "triggeredTaskIDs": "com.orcatech.task.type",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.study.enrollment.state": "enrollmentTriggerID",
            "com.orcatech.task": "taskIDs",
            "com.orcatech.task.type": "triggeredTaskIDs" "taskTriggerID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.test.neuropsych.imagerecog": {
        "record": TestNeuropsychImagerecogRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.test.neuropsych.imagerecog.coord": {
        "record": TestNeuropsychImagerecogCoordRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.test.neuropsych.imagerecog.selection": {
        "record": TestNeuropsychImagerecogSelectionRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.test.neuropsych.stroop": {
        "record": TestNeuropsychStroopRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.test.neuropsych.stroop.selection": {
        "record": TestNeuropsychStroopSelectionRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.test.neuropsych.trails": {
        "record": TestNeuropsychTrailsRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.test.neuropsych.trails.selection": {
        "record": TestNeuropsychTrailsSelectionRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.test.neuropsych.trails.token": {
        "record": TestNeuropsychTrailsTokenRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.thunderboard.snapshot": {
        "record": ThunderboardSnapshotRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.timeline": {
        "record": TimelineRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.timercap.closeEventRecord": {
        "record": TimercapCloseEventRecordRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.timercap.device": {
        "record": TimercapDeviceRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.timercap.heartbeat": {
        "record": TimercapHeartbeatRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.trip.event.type": {
        "record": TripEventTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.user": {
        "record": UserRecord,
        "fieldsWithRelationships": {
            "accountIDs": "com.orcatech.sso.account",
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "homeIDs": "com.orcatech.home",
            "identifierIDs": "com.orcatech.user.identifier",
            "inventoryTagIDs": "com.orcatech.inventory.tag",
            "issueIDs": "com.orcatech.issue",
            "issuesAssignedIDs": "com.orcatech.issue",
            "organizationIDs": "com.orcatech.organization",
            "roleIDs": "com.orcatech.role",
            "studyIDs": "com.orcatech.study",
            "subjectIDs": "com.orcatech.subject",
            "tagIDs": "com.orcatech.user.tag",
            "taskIDs": "com.orcatech.task",
            "updatedBy": "com.orcatech.user",
            "webAuthCredentialIDs": "com.orcatech.mfa.webauthn.credential",
        },
        "relatedSchemas": {
            "com.orcatech.home": "homeIDs",
            "com.orcatech.inventory.tag": "inventoryTagIDs",
            "com.orcatech.issue": "issueIDs" "issuesAssignedIDs",
            "com.orcatech.mfa.webauthn.credential": "webAuthCredentialIDs",
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.role": "roleIDs",
            "com.orcatech.sso.account": "accountIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectIDs",
            "com.orcatech.task": "taskIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
            "com.orcatech.user.identifier": "identifierIDs",
            "com.orcatech.user.tag": "tagIDs",
        },
    },
    "com.orcatech.user.identifier": {
        "record": UserIdentifierRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "typeID": "com.orcatech.user.identifier.type",
            "updatedBy": "com.orcatech.user",
            "userID": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy" "userID",
            "com.orcatech.user.identifier.type": "typeID",
        },
    },
    "com.orcatech.user.identifier.type": {
        "record": UserIdentifierTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "identifierIDs": "com.orcatech.user.identifier",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
            "com.orcatech.user.identifier": "identifierIDs",
        },
    },
    "com.orcatech.user.tag": {
        "record": UserTagRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
            "userIDs": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy" "userIDs",
        },
    },
    "com.orcatech.user.token": {
        "record": UserTokenRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.vehicle": {
        "record": VehicleRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.vehicle.event.type": {
        "record": VehicleEventTypeRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.withings.body": {
        "record": WithingsBodyRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.withings.device": {
        "record": WithingsDeviceRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.withings.device.checkin": {
        "record": WithingsDeviceCheckinRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.withings.device.heartbeat": {
        "record": WithingsDeviceHeartbeatRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.withings.heart": {
        "record": WithingsHeartRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.withings.highfreq.activity": {
        "record": WithingsHighfreqActivityRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.withings.user": {
        "record": WithingsUserRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.withings.vasistas": {
        "record": WithingsVasistasRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.worktime.session": {
        "record": WorktimeSessionRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.worktime.user": {
        "record": WorktimeUserRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationID": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "subjectID": "com.orcatech.subject",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationID",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.subject": "subjectID",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.zigbee.device": {
        "record": ZigbeeDeviceRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zigbee.zone.status": {
        "record": ZigbeeZoneStatusRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.address": {
        "record": ZubieAddressRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.device": {
        "record": ZubieDeviceRecord,
        "fieldsWithRelationships": {
            "createdBy": "com.orcatech.user",
            "deletedBy": "com.orcatech.user",
            "organizationIDs": "com.orcatech.organization",
            "studyIDs": "com.orcatech.study",
            "updatedBy": "com.orcatech.user",
        },
        "relatedSchemas": {
            "com.orcatech.organization": "organizationIDs",
            "com.orcatech.study": "studyIDs",
            "com.orcatech.user": "createdBy" "updatedBy" "deletedBy",
        },
    },
    "com.orcatech.zubie.event": {
        "record": ZubieEventRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.event.context.device": {
        "record": ZubieEventContextDeviceRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.event.context.device.claim": {
        "record": ZubieEventContextDeviceClaimRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.event.context.trip": {
        "record": ZubieEventContextTripRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.event.context.trip.alert": {
        "record": ZubieEventContextTripAlertRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.event.context.trip.tagged": {
        "record": ZubieEventContextTripTaggedRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.event.context.vehicle.geofence": {
        "record": ZubieEventContextVehicleGeofenceRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.event.context.vehicle.location": {
        "record": ZubieEventContextVehicleLocationRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.event.device": {
        "record": ZubieEventDeviceRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.event.place": {
        "record": ZubieEventPlaceRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.event.point": {
        "record": ZubieEventPointRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.event.trip": {
        "record": ZubieEventTripRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.event.vehicle": {
        "record": ZubieEventVehicleRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.point": {
        "record": ZubiePointRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.tag": {
        "record": ZubieTagRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.trip": {
        "record": ZubieTripRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.trip.bound": {
        "record": ZubieTripBoundRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.trip.point": {
        "record": ZubieTripPointRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.zubie.vehicle.trip.point": {
        "record": ZubieVehicleTripPointRecord,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.graph.node": {
        "record": any,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
    "com.orcatech.graph.edge": {
        "record": any,
        "fieldsWithRelationships": {},
        "relatedSchemas": {},
    },
}


@dataclass
class GraphNodeRecord:

    # The graph node record id

    id: APIID

    # The graph node record schema

    schema: any


GraphEdgeRecord = {
    # The id of the record that represents the relationship, if any
    "id": Optional[APIID],
    # The schema of the record that represents the relationship, if any
    "schema": Optional[any],
    # The first record of the relationship
    "to": GraphNodeRecord,
    # The second record of the relationship
    "from": GraphNodeRecord,
    # The type of the relationship
    "relationship": GraphRelationship,
}

# External representations of records. These are returned by the getExternal function
RecordExternal = {"com.orcatech.qualtrics.survey": Dict[str, str]}

# Set of available record schemas in the API

PrivateSchemaType = Literal[
    "com.orcatech.alert.status", "com.orcatech.alert.type", "com.orcatech.event.type"
]

# Set of available record schemas in the API
RecordSchemaType = Literal[
    "com.orcatech.animal",
    "com.orcatech.animal.type",
    "com.orcatech.area",
    "com.orcatech.area.category",
    "com.orcatech.area.tag",
    "com.orcatech.area.type",
    "com.orcatech.beiwe.credential",
    "com.orcatech.beiwe.device.setting",
    "com.orcatech.beiwe.device.setting.consent.section",
    "com.orcatech.beiwe.device.setting.consent.section.required",
    "com.orcatech.beiwe.device.setting.required",
    "com.orcatech.beiwe.setting.state",
    "com.orcatech.home",
    "com.orcatech.home.attribute",
    "com.orcatech.home.attribute.type",
    "com.orcatech.home.identifier",
    "com.orcatech.home.identifier.type",
    "com.orcatech.home.tag",
    "com.orcatech.integration",
    "com.orcatech.integration.credential",
    "com.orcatech.integration.credential.state",
    "com.orcatech.inventory.item",
    "com.orcatech.inventory.item.attribute",
    "com.orcatech.inventory.item.attribute.type",
    "com.orcatech.inventory.item.identifier",
    "com.orcatech.inventory.item.identifier.type",
    "com.orcatech.inventory.item.state",
    "com.orcatech.inventory.item.user",
    "com.orcatech.inventory.model",
    "com.orcatech.inventory.tag",
    "com.orcatech.inventory.user",
    "com.orcatech.inventory.vendor",
    "com.orcatech.irb.document",
    "com.orcatech.irb.state",
    "com.orcatech.issue",
    "com.orcatech.issue.comment",
    "com.orcatech.issue.source",
    "com.orcatech.issue.state",
    "com.orcatech.issue.tag",
    "com.orcatech.location",
    "com.orcatech.location.dwelling",
    "com.orcatech.location.type",
    "com.orcatech.mfa.webauthn.credential",
    "com.orcatech.milestone",
    "com.orcatech.milestone.state",
    "com.orcatech.milestone.type",
    "com.orcatech.organization",
    "com.orcatech.pathology.apoe.allele",
    "com.orcatech.pathology.autopsy",
    "com.orcatech.pathology.autopsy.caseType",
    "com.orcatech.pathology.autopsy.hemisphere",
    "com.orcatech.pathology.clinical.summary",
    "com.orcatech.pathology.diagnosis.autopsy.hemisphere",
    "com.orcatech.pathology.diagnosis.type.clinical",
    "com.orcatech.pathology.diagnosis.type.visit",
    "com.orcatech.pathology.hemisphere",
    "com.orcatech.pathology.hemisphere.cassette",
    "com.orcatech.pathology.hemisphere.slice",
    "com.orcatech.pathology.hemisphere.slide",
    "com.orcatech.pathology.image.hemisphere.cassette",
    "com.orcatech.pathology.image.hemisphere.cassette.map.region",
    "com.orcatech.pathology.image.hemisphere.cassette.stain",
    "com.orcatech.pathology.image.hemisphere.cassette.stain.region",
    "com.orcatech.pathology.image.hemisphere.cassette.type",
    "com.orcatech.pathology.mask.hemisphere",
    "com.orcatech.pathology.region",
    "com.orcatech.pathology.registration.hemisphere.cassette",
    "com.orcatech.pathology.registration.hemisphere.cassette.file",
    "com.orcatech.pathology.registration.hemisphere.slice",
    "com.orcatech.pathology.scan.hemisphere",
    "com.orcatech.pathology.scan.hemisphere.slice",
    "com.orcatech.pathology.scan.processing.hemisphere",
    "com.orcatech.pathology.scan.processing.hemisphere.cassette",
    "com.orcatech.pathology.scan.processing.hemisphere.slice",
    "com.orcatech.pathology.scan.processing.hemisphere.slide",
    "com.orcatech.pathology.scan.processing.montage",
    "com.orcatech.pathology.stain",
    "com.orcatech.pathology.tag",
    "com.orcatech.permission",
    "com.orcatech.permission.action",
    "com.orcatech.permission.endpoint",
    "com.orcatech.person",
    "com.orcatech.phone",
    "com.orcatech.phone.type",
    "com.orcatech.plugin",
    "com.orcatech.role",
    "com.orcatech.sensor.line",
    "com.orcatech.sensor.line.segment",
    "com.orcatech.sensor.line.type",
    "com.orcatech.sso.account",
    "com.orcatech.sso.oauth2.scope",
    "com.orcatech.sso.provider",
    "com.orcatech.study",
    "com.orcatech.study.enrollment",
    "com.orcatech.study.enrollment.state",
    "com.orcatech.subject",
    "com.orcatech.subject.attribute",
    "com.orcatech.subject.attribute.type",
    "com.orcatech.subject.comment",
    "com.orcatech.subject.contact",
    "com.orcatech.subject.contact.reason",
    "com.orcatech.subject.contact.type",
    "com.orcatech.subject.ethnicity",
    "com.orcatech.subject.gender",
    "com.orcatech.subject.identifier",
    "com.orcatech.subject.identifier.type",
    "com.orcatech.subject.life.event.category.primary",
    "com.orcatech.subject.life.event.category.secondary",
    "com.orcatech.subject.life.event.source",
    "com.orcatech.subject.life.event.tag",
    "com.orcatech.subject.race",
    "com.orcatech.subject.tag",
    "com.orcatech.survey",
    "com.orcatech.survey.distribution",
    "com.orcatech.survey.event.category.primary",
    "com.orcatech.survey.event.category.secondary",
    "com.orcatech.survey.event.tag",
    "com.orcatech.task",
    "com.orcatech.task.type",
    "com.orcatech.user",
    "com.orcatech.user.identifier",
    "com.orcatech.user.identifier.type",
    "com.orcatech.user.tag",
]


# Set of available observations in the API
ObservationSchemaType = Literal["com.orcatech.observation.generic"]


# Set of available observation meta schemas in the API
ObservationMetaSchemaType = Literal[
    "com.orcatech.observation.generic.report.meta",
    "com.orcatech.observation.generic.measure.meta",
    "com.orcatech.observation.generic.survey.meta",
    "com.orcatech.observation.generic.event.alert.meta",
    "com.orcatech.observation.generic.event.storage.meta",
    "com.orcatech.observation.generic.test.meta",
]


# Set of graph schemas
GraphSchemaType = Literal["com.orcatech.graph.node", "com.orcatech.graph.edge"]


# The possible set of schemas that can be used as graph maps
GraphMapSchemaType = "com.orcatech.location.dwelling"


# Set of history schemas
HistorySchemaType = Literal[
    "com.orcatech.history.association", "com.orcatech.history.field"
]


# Set of records with observation schemas
ObservationRecordSchemaType = Literal[
    "com.orcatech.subject",
    "com.orcatech.home",
    "com.orcatech.inventory.item",
    "com.orcatech.user",
    "com.orcatech.survey",
]


# Set of schemas that are loaded from an external source and can be used with the getExternal function
ExternalSchemaType = "com.orcatech.qualtrics.survey"


# Scopes that can be represented by a schema
ScopeSchemas = {
    "organization": "com.orcatech.organization",
    "study": "com.orcatech.study",
    "account": "com.orcatech.user",
}


# Scopes that can be represented by a schema that can be created
ScopeCreateSchemas = {
    "organization": "com.orcatech.organization",
    "study": "com.orcatech.study",
}

SchemaWithScope = {
    "com.orcatech.organization": "organization",
    "com.orcatech.study": "study",
    "com.orcatech.user": "account",
}

CreateSchemaWithScope = {
    "com.orcatech.organization": "organization",
    "com.orcatech.study": "study",
}
