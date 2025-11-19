from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from orcatech_python_api_client.config import APIID


@dataclass
class AlertIncidentRecord:
    id: APIID
    created_at: datetime
    created_by: int
    updated_at: Optional[datetime]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
    type_id: APIID
    status_id: APIID
    notification_Ids = List[APIID]
    notification_Id = APIID
    study_id: APIID
    is_frozen: bool


@dataclass
class AlertNotificationGroupRecord:
    #  The  unique identifier
    id: APIID
    #  When the record was created
    createdAt: datetime
    #  The com.orcatech.user.id for the user who created the record
    createdBy: int
    #  When the record was updated
    updatedAt: Optional[datetime]
    #  The com.orcatech.user.id for the user who updated the record
    updatedBy: Optional[int]
    #  When the record was deleted
    deletedAt: Optional[datetime]
    #  The com.orcatech.user.id for the user who deleted the record
    deletedBy: Optional[int]
    #  Lookup id numbers for roles
    roleIDs: List[APIID]
    #  Lookup id numbers for studies
    studyIDs: List[APIID]
    #  Lookup id numbers for organizations
    organizationIDs: List[APIID]
    #  Lookup id numbers for users
    userIDs: List[APIID]
    #  Lookup id number for notificationType
    notificationTypeID: APIID
    #  Lookup id number for alertType
    alertTypeID: APIID
    #  If true, indicates that the record is frozen
    isFrozen: bool


@dataclass
class AlertNotificationSentRecord:
    # The  unique identifier
    id: APIID
    # When the record was created
    createdAt: datetime
    # The com.orcatech.user.id for the user who created the record
    createdBy: int
    # When the record was updated
    updatedAt: Optional[datetime]
    # The com.orcatech.user.id for the user who updated the record
    updatedBy: Optional[int]
    # When the record was deleted
    deletedAt: Optional[datetime]
    # The com.orcatech.user.id for the user who deleted the record
    deletedBy: Optional[int]
    # Lookup id numbers for users
    userIDs: List[APIID]
    # Lookup id number for alertIncident
    alertIncidentID: APIID
    # Lookup id number for type
    typeID: APIID
    # If true, indicates that the record is frozen
    isFrozen: bool
    
@dataclass
class AlertNotificationTypeRecord:
    # The unique identifier
    id: APIID
    # A short descriptive name for the type. eg 'email', 'sms', 'im'
    name: str
    # Detailed information about the notification type
    description: str
    # When the record was created
    createdAt: datetime
    # The com.orcatech.user.id for the user who created the record
    createdBy: int
    # When the record was updated
    updatedAt: Optional[datetime]
    # The com.orcatech.user.id for the user who updated the record
    updatedBy: Optional[int]
    # When the record was deleted
    deletedAt: Optional[datetime]
    # The com.orcatech.user.id for the user who deleted the record
    deletedBy: Optional[int]
    # user text to publish with alert
    userText: Optional[str]
    # email address or phone # (sms)
    destinationAddress: Optional[str]
    # Lookup id numbers for organizations
    organizationIDs: List[APIID]
    # Lookup id numbers for studies
    studyIDs: List[APIID]
    # Lookup id numbers for notifications
    notificationIDs: List[APIID]
    # Lookup id numbers for groups
    groupIDs: List[APIID]
    # Lookup id number for credentials
    credentialsID: APIID
    # If true, indicates that the record is frozen
    isFrozen: bool

@dataclass
class AlertStatusRecord:
    # The  unique identifier
    id: APIID
    # A short name for the alert state type
    name: str
    # A longer description of the alert state type
    description: str
    # When the record was created
    createdAt: datetime
    # The com.orcatech.user.id for the user who created the record
    createdBy: int
    # When the record was updated
    updatedAt:  Optional[datetime]
    # The com.orcatech.user.id for the user who updated the record
    updatedBy: Optional[int]
    # When the record was deleted
    deletedAt: Optional[datetime]
    # The com.orcatech.user.id for the user who deleted the record
    deletedBy: Optional[int]
    # Lookup id numbers for studies
    studyIDs: List[APIID]
    # Lookup id numbers for organizations
    organizationIDs: List[APIID]
    # Lookup id numbers for alertIncidents
    alertIncidentIDs: List[APIID]
    # If true, indicates that the record is frozen
    isFrozen: bool
    
    