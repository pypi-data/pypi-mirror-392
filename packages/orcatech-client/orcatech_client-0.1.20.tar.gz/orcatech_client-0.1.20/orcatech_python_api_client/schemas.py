from dataclasses import dataclass

"""
    The scopes in which the API call is to work under. Each scope contains a set RBAC permissions and provides context
    for the API calls
    @readonly
"""

Scope = {
    "PUBLIC" : "public",
    "ACCOUNT" : "account",
    "ADMIN" : "admin",
    "GLOBAL" : "global",
    "ORGANIZATION" : "organization",
    "STUDY" : "study",
}

"""
    The names of the parameters that can be found in the path
@readonly
"""

PathParam = {
	"SCOPE" : "scope",
	"SCOPE_ID" : "scopeID",
	"RECORD_SCHEMA" : "recordSchema",
	"RECORD_ID" : "recordID",
	"FIELD" : "field",
	"RELATED_ID" : "relatedID",
	"HISTORY_SCHEMA" : "historySchema",
	"HISTORY_ID" : "historyID",
	"DATA_SCHEMA" : "dataSchema",
	"OBSERVATION_UUID" : "observationUUID",
	"TOKEN_UUID" : "tokenUUID",
	"HUB_NAME" : "hubName",
}

"""
    The possible HTTP actions for the API calls
    @readonly
"""

HTTPAction = {
	"VIEW" : "View",
	"DELETE" : "Delete",
	"EDIT" : "Edit",
	"CREATE" : "Create",
}


"""
    The possible SSO Protocols
    @readonly
"""

SSOProtocol  = {
    "PASSWORD" : "Password",
    "OAUTH2" : "OAuth2",
    "SAML2" : "SAML2",
}


"""
    The possible Integrations
    @readonly
"""

Integration = {
    "QUALTRICS" : "Qualtrics",
    "RED_CAP" : "RedCap",
    "BOX" : "Box",
    "WITHINGS" : "Withings",
    "AIRC" : "AIRC",
    "EMAIL" : "Email",
    "ZUBIE" : "Zubie",
    "GOOGLE_MAPS_API" : "Google Maps API",
}


"""The possible set of Graph Relationships"""

GraphRelationship = {
    "NEXT_TO" : "nextTo",
    "IN" : "in",
    "BEFORE" : "before",
    "FIRST_MEMBER" : "firstMember",
}

"""
    The possible API action requests
    @readonly
"""

Request = {
	"IMPORT_QUALTRICS_SURVEY" : "Import Qualtrics Survey",
	"MIGRATE" : "Migrate",
	"SEND_ADD_ACCOUNT" : "Send Add Account",
	"SEND_RESET_ACCOUNT" : "Send Reset Account",
	"SEND_INVITE" : "Send Invite",
}


"""
    The plugins that exist within the platform
    @readonly
"""

Plugin = {
	"ANIMAL" : "Animal",
	"AUTOPSY" : "Autopsy",
	"BRAIN_IMAGING" : "Brain Imaging",
	"HOME" : "Home",
	"INVENTORY" : "Inventory",
	"ISSUE" : "Issue",
	"LIFE_EVENT" : "Life Event",
	"NEUROLOGY" : "Neurology",
	"OMAR" : "OMAR",
	"SUBJECT" : "Subject",
	"SURVEY" : "Survey",
	"TASK" : "Task",
}


"""
    The schema names that exist within the platform
    @readonly
"""

Schema = {
	# The type of alert
	"ALERT_INCIDENT" : "com.orcatech.alert.incident",
	# how a user/role wants to be notified for an alert
	"ALERT_NOTIFICATION_GROUP" : "com.orcatech.alert.notification.group",
	# A record of notifications issued
	"ALERT_NOTIFICATION_SENT" : "com.orcatech.alert.notification.sent",
	# Type definition of an alert notification
	"ALERT_NOTIFICATION_TYPE" : "com.orcatech.alert.notification.type",
	# The state of a given alert
	"ALERT_STATUS" : "com.orcatech.alert.status",
	# The type of alert
	"ALERT_TYPE" : "com.orcatech.alert.type",
	# Calibration parameters (i.e. deltax and C) for each sensor line
	"ALGORITHMS_LINE_CALIBRATION" : "com.orcatech.algorithms.lineCalibration",
	# Parameters used to create the model used for determining which walking speeds are valid (i.e. the walks used to calculate the calibration parameters deltaX and C)
	"ALGORITHMS_LINE_CALIBRATION_PARAMETERS" : "com.orcatech.algorithms.lineCalibration.parameters",
	# A pair of two sensors that compose a segment within a sensor line
	"ALGORITHMS_LINE_CALIBRATION_SEGMENT" : "com.orcatech.algorithms.lineCalibration.segment",
	# Room transitions derived from sequential sensor fires from different rooms. The transition algorithm does not check that the rooms are adjacent.
	"ALGORITHMS_TRANSITIONS" : "com.orcatech.algorithms.transitions",
	# Sequential sensor line firings which represent a candidate for a walk
	"ALGORITHMS_WALK_CANDIDATE" : "com.orcatech.algorithms.walkCandidate",
	# Sequential sensor firings of a com.orcatech.sensor.line.segment
	"ALGORITHMS_WALK_SEGMENT" : "com.orcatech.algorithms.walkSegment",
	# Estimated walking speeds calculated from the walking speed algorithm
	"ALGORITHMS_WALKING_SPEED" : "com.orcatech.algorithms.walkingSpeed",
	# Calibration parameters (i.e. deltaX and C) used to calculate walkingSpeed.speed and metadata about the estimation of the calibration parameters
	"ALGORITHMS_WALKING_SPEED_CALIBRATION" : "com.orcatech.algorithms.walkingSpeed.calibration",
	# Parameters used calculate walkingSpeed.speed and to create the model used for determining which walkingSpeed.speed are valid
	"ALGORITHMS_WALKING_SPEED_PARAMETERS" : "com.orcatech.algorithms.walkingSpeed.parameters",
	# A generic animal to be tracked.
	"ANIMAL" : "com.orcatech.animal",
	# A tag used to categorize a set of animals
	"ANIMAL_TAG" : "com.orcatech.animal.tag",
	# A type of animal that can be tracked.
	"ANIMAL_TYPE" : "com.orcatech.animal.type",
	# An web application within the  system.
	"APP" : "com.orcatech.app",
	# A generic area such as a living room, bedroom, bathroom, toilet, top drawer, etc
	"AREA" : "com.orcatech.area",
	# A category of area such a chair, toilet, bed, room, etc
	"AREA_CATEGORY" : "com.orcatech.area.category",
	# A tag used to categorize a set of area
	"AREA_TAG" : "com.orcatech.area.tag",
	# A type of area such a chair, toilet, bed, room, etc
	"AREA_TYPE" : "com.orcatech.area.type",
	# Location as an address
	"AUTOMATIC_ADDRESS" : "com.orcatech.automatic.address",
	# Credentials for accessing automatic data
	"AUTOMATIC_CREDENTIALS" : "com.orcatech.automatic.credentials",
	# Location as a set of geocoordinates
	"AUTOMATIC_LOCATION" : "com.orcatech.automatic.location",
	# Trip A trip is created when a vehicle is understood to have one full cycle of ignition:on to ignition:off. In some vehicles, these signals must be inferred. Trips are the most commonly used objects in the API. They contain a wealth of metadata about a vehicle's usage history and a user's behavior. At present, one write is possible: adding a tag to a trip. The mobile apps have a feature that allows combining of trips that happened within 15 minutes of each other. This merge is applied on the apps' frontend only and does not affect the REST objects, which would show the multiple 'segments' as distinct and unrelated entities. Trips must have a minimum distance of 10 meters or they will be discarded as invalid. In the United States, fuel price is retrieved automatically based on location at the time of fillup. If a car does not report its fuel level, then each trip's cost will be estimated using prevailing local prices. Outside the United States, our fuel costing will currently provide unreliable results. This will be improved in the future. For the time being, it is recommended to use fuel volume as the reliable metric instead.
	"AUTOMATIC_TRIP" : "com.orcatech.automatic.trip",
	# Tag used for grouping of trips
	"AUTOMATIC_TRIP_TAG" : "com.orcatech.automatic.trip.tag",
	# User is the object representing an Automatic account holder. In practice this represents an owner or driver of a vehicle. A user may have many vehicles (and a vehicle may have many users).
	"AUTOMATIC_USER" : "com.orcatech.automatic.user",
	# Additional information about the user / phone
	"AUTOMATIC_USER_METADATA" : "com.orcatech.automatic.user.metadata",
	# Information about the vehicle the sensor is plugged into
	"AUTOMATIC_USER_PROFILE" : "com.orcatech.automatic.user.profile",
	# Information about the vehicle the sensor is plugged into
	"AUTOMATIC_VEHICLE" : "com.orcatech.automatic.vehicle",
	# A vehicle event measured by the automatic sensor
	"AUTOMATIC_VEHICLE_EVENT" : "com.orcatech.automatic.vehicle.event",
	# Vehicle malfunction indicator light
	"AUTOMATIC_VEHICLE_MIL" : "com.orcatech.automatic.vehicle.mil",
	# Credentials for encrypting and decrypting data sent by Beiwe clients
	"BEIWE_CREDENTIAL" : "com.orcatech.beiwe.credential",
	# Accelerometer data collected by the Beiwe app for android and ios devices
	"BEIWE_DEVICE_ACCELEROMETER" : "com.orcatech.beiwe.device.accelerometer",
	# The observed app usage of a device with the Beiwe app installed for Android devices
	"BEIWE_DEVICE_APP_USAGE" : "com.orcatech.beiwe.device.app.usage",
	# Bluetooth device observation collected by the Beiwe app for android devices
	"BEIWE_DEVICE_BLUETOOTH" : "com.orcatech.beiwe.device.bluetooth",
	# A call made or received by a device collected with the Beiwe app installed
	"BEIWE_DEVICE_CALL" : "com.orcatech.beiwe.device.call",
	# GPS coordinates observed by a device observation with the Beiwe app installed
	"BEIWE_DEVICE_GPS" : "com.orcatech.beiwe.device.gps",
	# Gyroscope data collected by the Beiwe app for android and ios devices
	"BEIWE_DEVICE_GYROSCOPE" : "com.orcatech.beiwe.device.gyroscope",
	# A log made by an android device collected with the Beiwe app installed
	"BEIWE_DEVICE_LOG_ANDROID" : "com.orcatech.beiwe.device.log.android",
	# A log made by an android device collected with the Beiwe app installed
	"BEIWE_DEVICE_LOG_IOS" : "com.orcatech.beiwe.device.log.ios",
	# Magnetometer data collected by the Beiwe app for android and ios devices
	"BEIWE_DEVICE_MAGNETOMETER" : "com.orcatech.beiwe.device.magnetometer",
	# Motion data collected by the Beiwe app for iOS devices
	"BEIWE_DEVICE_MOTION" : "com.orcatech.beiwe.device.motion",
	# The observed power state of a device with the Beiwe app installed
	"BEIWE_DEVICE_POWER" : "com.orcatech.beiwe.device.power",
	# Proximity observed by a device collected with the Beiwe app installed
	"BEIWE_DEVICE_PROXIMITY" : "com.orcatech.beiwe.device.proximity",
	# A reachability status observed by a device collected with the Beiwe app installed
	"BEIWE_DEVICE_REACHABILITY" : "com.orcatech.beiwe.device.reachability",
	# The actual state of the settings on the device for the OMAR app
	"BEIWE_DEVICE_SETTING" : "com.orcatech.beiwe.device.setting",
	# Text used for consenting subjects
	"BEIWE_DEVICE_SETTING_CONSENT_SECTION" : "com.orcatech.beiwe.device.setting.consent.section",
	# Text used for consenting subjects
	"BEIWE_DEVICE_SETTING_CONSENT_SECTION_REQUIRED" : "com.orcatech.beiwe.device.setting.consent.section.required",
	# The required state of the OMAR app settings for a study or organization
	"BEIWE_DEVICE_SETTING_REQUIRED" : "com.orcatech.beiwe.device.setting.required",
	# A sms made by a device collected with the Beiwe app installed
	"BEIWE_DEVICE_SMS" : "com.orcatech.beiwe.device.sms",
	# A wifi access point observed by a device collected with the Beiwe app installed
	"BEIWE_DEVICE_WIFI" : "com.orcatech.beiwe.device.wifi",
	# A state of the beiwe setting. i.e. requested, denied, enabled, or disabled.
	"BEIWE_SETTING_STATE" : "com.orcatech.beiwe.setting.state",
	# A 2d geological coordinate 
	"COORDINATE" : "com.orcatech.coordinate",
	# The type of device event
	"DEVICE_EVENT_TYPE" : "com.orcatech.device.event.type",
	# The input events captured while a subject is using a device.
	"DEVICE_INPUT" : "com.orcatech.device.input",
	# An input event.
	"DEVICE_INPUT_EVENT" : "com.orcatech.device.input.event",
	# Periods spent out of the bed
	"EMFIT_BEDEXIT" : "com.orcatech.emfit.bedexit",
	# No description. Series of calculations?
	"EMFIT_CALC" : "com.orcatech.emfit.calc",
	# Events are reported by an emfit device every 30s
	"EMFIT_EVENT" : "com.orcatech.emfit.event",
	# Heart rate variability information for Evening and Morning. There are two version of the data. BasedFirstLast90: based on first and last 90 mins of 3 min RMSSD datapoints, and also whole night RMSSD graph which included the integratingRecovery field. BasedWholeNight: ased on linear fit of whole night RMSSD datapoints
	"EMFIT_HRV" : "com.orcatech.emfit.hrv",
	# Heart rate variability information for Evening and Morning based on linear fit of whole night RMSSD datapoints
	"EMFIT_HRV_LINEAR" : "com.orcatech.emfit.hrvLinear",
	# Heart rate variability root mean square of successive differences
	"EMFIT_HRVRMSSD" : "com.orcatech.emfit.hrvrmssd",
	# Heart Rate Variability is calculated every 3 minutes per device. If these fields are omitted then they are equal to NULL, which usually indicates absence or not enough signal quality(movement artefact or else) data for HRV calculation for the period
	"EMFIT_LIVE_HRV" : "com.orcatech.emfit.liveHRV",
	# Information routinely requested from a local emfit bed mat
	"EMFIT_POLL" : "com.orcatech.emfit.poll",
	# Heart rate variability root mean square of successive differences
	"EMFIT_SLEEP" : "com.orcatech.emfit.sleep",
	# Sleep Summary data is POST--ed by webhook in JSON format to consumers once the user bed presence period is ended. Approximate delay between actual bed exit that starts period data processing, to the delivery of the Sleep Summary data, is at about 5--20 minutes.Note that if user return to bed within following 20 minutes after bed exit and the Night/Day setting is not used, after the next bed exit the same data is send again from the whole sleep period. You need to have means to delete doubled data. Sleep summary data is associated with a particular device. It contains information about device, presence period and all calculated dataof the period.
	"EMFIT_SUMMARY" : "com.orcatech.emfit.summary",
	# Body of the request that is POST--ed by Emfit's API in JSON format after a mat recognizes a sleep period
	"EMFIT_SUMMARY_STRING" : "com.orcatech.emfit.summaryString",
	# Heart Rate, Respiration Rate and movement Activity level. If Heart Rate, Respiration Rate fields are omitted then they are equal to NULL. In such case Activity value is 0 - it means that device is turned on,but nobody is in the bed.Thedefault behavior of the webhook is to POSTonly one record per device per 30 seconds.But there is an option to includeall past 30 seconds window of data(15 data points). Activity values arebetween 0 - 32767
	"EMFIT_VITALS" : "com.orcatech.emfit.vitals",
	# The occurrence of an event
	"EVENT" : "com.orcatech.event",
	# The type of event
	"EVENT_CHANGE_FIELD" : "com.orcatech.event.change.field",
	# The type of event
	"EVENT_TYPE" : "com.orcatech.event.type",
	# Fibaro sensor events collected over a z-wave network
	"FIBARO_EVENT" : "com.orcatech.fibaro.event",
	# A history of associations between records
	"HISTORY_ASSOCIATION" : "com.orcatech.history.association",
	# A history of record field values
	"HISTORY_FIELD" : "com.orcatech.history.field",
	# The home is a collection of common objects that reside in a dwelling.
	"HOME" : "com.orcatech.home",
	# The value portion of a key value pair belonging to an home
	"HOME_ATTRIBUTE" : "com.orcatech.home.attribute",
	# A type of home attribute for the home. This will act as the key in the key value pair
	"HOME_ATTRIBUTE_TYPE" : "com.orcatech.home.attribute.type",
	# An external identifier for the study to map the it's data to an external database
	"HOME_IDENTIFIER" : "com.orcatech.home.identifier",
	# A type of external identifier for the home to map the their data to an external database
	"HOME_IDENTIFIER_TYPE" : "com.orcatech.home.identifier.type",
	# A tag used to categorize a set of homes
	"HOME_TAG" : "com.orcatech.home.tag",
	# Credentials and connection parameters for 3rd party application integrations
	"INTEGRATION" : "com.orcatech.integration",
	# A set of credentials used for authenticating with an integration
	"INTEGRATION_CREDENTIAL" : "com.orcatech.integration.credential",
	# The pulling status for a particular API client.
	"INTEGRATION_CREDENTIAL_STATE" : "com.orcatech.integration.credential.state",
	# A tracked piece of equipment such as sensors, computers, etc
	"INVENTORY_ITEM" : "com.orcatech.inventory.item",
	# The value portion of a key value pair belonging to an inventory item
	"INVENTORY_ITEM_ATTRIBUTE" : "com.orcatech.inventory.item.attribute",
	# A type of item attribute for the item. This will act as the key in the key value pair
	"INVENTORY_ITEM_ATTRIBUTE_TYPE" : "com.orcatech.inventory.item.attribute.type",
	# An external identifier for the item to map the their data to an external database
	"INVENTORY_ITEM_IDENTIFIER" : "com.orcatech.inventory.item.identifier",
	# A type of external identifier for the item to map the their data to an external database
	"INVENTORY_ITEM_IDENTIFIER_TYPE" : "com.orcatech.inventory.item.identifier.type",
	# A state of the item in the inventory. i.e. working vs. not working.
	"INVENTORY_ITEM_STATE" : "com.orcatech.inventory.item.state",
	# The status of the inventory item
	"INVENTORY_ITEM_STATUS" : "com.orcatech.inventory.item.status",
	# User account credentials for an inventory item
	"INVENTORY_ITEM_USER" : "com.orcatech.inventory.item.user",
	# Information shared across items that share the same hardware
	"INVENTORY_MODEL" : "com.orcatech.inventory.model",
	# A tag used to categorize the inventory records
	"INVENTORY_TAG" : "com.orcatech.inventory.tag",
	# A user account managed on a set of devices
	"INVENTORY_USER" : "com.orcatech.inventory.user",
	# A company that makes equipment purchased by
	"INVENTORY_VENDOR" : "com.orcatech.inventory.vendor",
	# An internal review board document for the study
	"IRB_DOCUMENT" : "com.orcatech.irb.document",
	# An internal review board state
	"IRB_STATE" : "com.orcatech.irb.state",
	# An issue that needs to be resolved. Work resolving the issue is tracked through comments and assignments.
	"ISSUE" : "com.orcatech.issue",
	# A comment about the issue indicating an update in status.
	"ISSUE_COMMENT" : "com.orcatech.issue.comment",
	# What, who or how the issue what identified.
	"ISSUE_SOURCE" : "com.orcatech.issue.source",
	# The status of an issue. i.e. open, pending, fixed, etc.
	"ISSUE_STATE" : "com.orcatech.issue.state",
	# A tag used to categorize a set of issues
	"ISSUE_TAG" : "com.orcatech.issue.tag",
	# A home containing an individual who participates in an  affiliated study. The home should represent a real physical location and not an abstract space
	"LOCATION" : "com.orcatech.location",
	# A physical location or space for living.
	"LOCATION_DWELLING" : "com.orcatech.location.dwelling",
	# The type of location. i.e. apartments, single family housing, townhomes, etc
	"LOCATION_TYPE" : "com.orcatech.location.type",
	# An  application log line.
	"LOG" : "com.orcatech.log",
	# Audit log for when user's login to the system
	"MEASURE_ACCESS_PERIOD" : "com.orcatech.measure.access.period",
	# Audit log for when user's login to the system
	"MEASURE_ACCESS_REQUEST" : "com.orcatech.measure.access.request",
	# The observed period of physical activity
	"MEASURE_ACTIVITY_PHYSICAL_PERIOD" : "com.orcatech.measure.activity.physical.period",
	# generic application use schema that includes meta
	"MEASURE_APPLICATION_USER_PERIOD" : "com.orcatech.measure.application.user.period",
	# An event indicating the battery level of a sensor
	"MEASURE_BATTERY" : "com.orcatech.measure.battery",
	# Detected activity on the bed
	"MEASURE_BED_ACTIVITY" : "com.orcatech.measure.bed.activity",
	# A period of being awake while in bed
	"MEASURE_BED_AWAKE_PERIOD" : "com.orcatech.measure.bed.awake.period",
	# Period out of bed during a sleeping period
	"MEASURE_BED_EXIT_PERIOD" : "com.orcatech.measure.bed.exit.period",
	# A measurement of weight
	"MEASURE_BODY_WEIGHT" : "com.orcatech.measure.body.weight",
	# A heartbeat indicating that the sensor is connected and working
	"MEASURE_CHECKIN" : "com.orcatech.measure.checkin",
	# An event indicating an opened or closed state of an area monitored by a sensor
	"MEASURE_CONTACT" : "com.orcatech.measure.contact",
	# An observed location as a set of geocoordinates
	"MEASURE_COORDINATE" : "com.orcatech.measure.coordinate",
	# A device event
	"MEASURE_DEVICE_EVENT" : "com.orcatech.measure.device.event",
	# document what it does here
	"MEASURE_HEART_RATE" : "com.orcatech.measure.heart.rate",
	# document what it does here
	"MEASURE_HEART_RATE_PERIOD" : "com.orcatech.measure.heart.rate.period",
	# document what it does here
	"MEASURE_HEART_RATE_VARIABILITY_PERIOD" : "com.orcatech.measure.heart.rate.variability.period",
	# Heart rate variability root mean square of successive differences
	"MEASURE_HEART_RATE_VARIABILITY_RMSSD" : "com.orcatech.measure.heart.rate.variability.rmssd",
	# The state of the doors on a pillbox
	"MEASURE_PILLBOX_STATE" : "com.orcatech.measure.pillbox.state",
	# An event indicating presence or no presence within an area monitored by a sensor
	"MEASURE_PRESENCE" : "com.orcatech.measure.presence",
	# document what it does here
	"MEASURE_RESPIRATION_RATE" : "com.orcatech.measure.respiration.rate",
	# document what it does here
	"MEASURE_RESPIRATION_RATE_PERIOD" : "com.orcatech.measure.respiration.rate.period",
	# Fast movement that occurred while sleeping
	"MEASURE_SLEEP_MOVEMENT_FAST" : "com.orcatech.measure.sleep.movement.fast",
	# Summary information about fast movements that occurred during a sleep period
	"MEASURE_SLEEP_MOVEMENT_FAST_PERIOD" : "com.orcatech.measure.sleep.movement.fast.period",
	# Information about a period of restlessness while sleeping
	"MEASURE_SLEEP_MOVEMENT_PERIOD" : "com.orcatech.measure.sleep.movement.period",
	# document what it does here
	"MEASURE_SLEEP_PERIOD" : "com.orcatech.measure.sleep.period",
	# A scored period of sleep
	"MEASURE_SLEEP_SCORE_PERIOD" : "com.orcatech.measure.sleep.score.period",
	# The observed sleep state during a period of time
	"MEASURE_SLEEP_STATE_PERIOD" : "com.orcatech.measure.sleep.state.period",
	# Steps observed during a period of time
	"MEASURE_STEP_PERIOD" : "com.orcatech.measure.step.period",
	# The observed period of swimming
	"MEASURE_SWIM_PERIOD" : "com.orcatech.measure.swim.period",
	# A sensed vehicular trip
	"MEASURE_TRIP" : "com.orcatech.measure.trip",
	# A trip event
	"MEASURE_TRIP_EVENT" : "com.orcatech.measure.trip.event",
	# A vehicle event measured by a sensor in the car
	"MEASURE_VEHICLE_EVENT" : "com.orcatech.measure.vehicle.event",
	# Vehicle malfunction indicator light
	"MEASURE_VEHICLE_MIL" : "com.orcatech.measure.vehicle.mil",
	# Information about a particular vehicle
	"MEASURE_VEHICLE_STATE" : "com.orcatech.measure.vehicle.state",
	# A web search instance
	"MEASURE_WEB_SEARCH" : "com.orcatech.measure.web.search",
	# A medication
	"MEDICATION" : "com.orcatech.medication",
	#  medtracker device built and designed by Jon Hunt circa 2007
	"MEDTRACKER_DEVICE" : "com.orcatech.medtracker.device",
	# Door state history report from the ORCATECH Medtracker
	"MEDTRACKER_REPORT" : "com.orcatech.medtracker.report",
	# The state of the ORCATECH Medtracker's doors at a given point in time
	"MEDTRACKER_REPORT_STATE" : "com.orcatech.medtracker.report.state",
	# Status report from the ORCATECH Medtracker
	"MEDTRACKER_STATUS" : "com.orcatech.medtracker.status",
	# User credential for multi-facter authentication generated by WebAuthN
	"MFA_WEBAUTHN_CREDENTIAL" : "com.orcatech.mfa.webauthn.credential",
	# Microservices that are performed on sensor as data comes in.
	"MICROSERVICE" : "com.orcatech.microservice",
	# A change history of the observation.
	"MICROSERVICE_CHANGE" : "com.orcatech.microservice.change",
	# The migration state of a platform component
	"MIGRATION_STATE" : "com.orcatech.migration.state",
	# A milestone to track achievement
	"MILESTONE" : "com.orcatech.milestone",
	# The state of a milestone.
	"MILESTONE_STATE" : "com.orcatech.milestone.state",
	# A type of milestone.
	"MILESTONE_TYPE" : "com.orcatech.milestone.type",
	# A one time token used to prevent replay attacks
	"NONCE" : "com.orcatech.nonce",
	# NYCE sensor events collected over a zigbee network. See http://nycesensors.com
	"NYCE_EVENT" : "com.orcatech.nyce.event",
	# Vendor specific testing data
	"OBSERVATION_GENERIC" : "com.orcatech.observation.generic",
	# Contextual information about an alert event
	"OBSERVATION_GENERIC_EVENT_ALERT_META" : "com.orcatech.observation.generic.event.alert.meta",
	# Contextual information about an status event
	"OBSERVATION_GENERIC_EVENT_STATUS_META" : "com.orcatech.observation.generic.event.status.meta",
	# An meta data about platform storage events
	"OBSERVATION_GENERIC_EVENT_STORAGE_META" : "com.orcatech.observation.generic.event.storage.meta",
	# Contextual information about a sensor measurement
	"OBSERVATION_GENERIC_MEASURE_META" : "com.orcatech.observation.generic.measure.meta",
	# Contextual information about an administered test
	"OBSERVATION_GENERIC_REPORT_META" : "com.orcatech.observation.generic.report.meta",
	# Contextual information about an administered survey
	"OBSERVATION_GENERIC_SURVEY_META" : "com.orcatech.observation.generic.survey.meta",
	# Contextual information about an administered test
	"OBSERVATION_GENERIC_TEST_META" : "com.orcatech.observation.generic.test.meta",
	# Vendor specific testing data
	"OBSERVATION_VENDOR" : "com.orcatech.observation.vendor",
	# An is a managing group which maintains it's own roles and users.
	"ORGANIZATION" : "com.orcatech.organization",
	# An external identifier for the organization to map the it's data to an external database
	"ORGANIZATION_IDENTIFIER" : "com.orcatech.organization.identifier",
	# A type of external identifier for the organization to map the it's data to an external database
	"ORGANIZATION_IDENTIFIER_TYPE" : "com.orcatech.organization.identifier.type",
	# The status of the organization
	"ORGANIZATION_STATUS" : "com.orcatech.organization.status",
	# The allele of the APOE gene. This will be one of E2, E3, E4.
	"PATHOLOGY_APOE_ALLELE" : "com.orcatech.pathology.apoe.allele",
	# Autopsy results of the hemisphere
	"PATHOLOGY_AUTOPSY" : "com.orcatech.pathology.autopsy",
	# Stain used on a piece of tissue
	"PATHOLOGY_AUTOPSY_CASE_TYPE" : "com.orcatech.pathology.autopsy.caseType",
	# Autopsy results of the hemisphere
	"PATHOLOGY_AUTOPSY_HEMISPHERE" : "com.orcatech.pathology.autopsy.hemisphere",
	# Summary clinical information generated from 4D
	"PATHOLOGY_CLINICAL_SUMMARY" : "com.orcatech.pathology.clinical.summary",
	# Stain used on a piece of tissue
	"PATHOLOGY_DIAGNOSIS_AUTOPSY_HEMISPHERE" : "com.orcatech.pathology.diagnosis.autopsy.hemisphere",
	# A clinical pathology diagnosis type
	"PATHOLOGY_DIAGNOSIS_TYPE_CLINICAL" : "com.orcatech.pathology.diagnosis.type.clinical",
	# A pathology diagnosis type given during an in person visit
	"PATHOLOGY_DIAGNOSIS_TYPE_VISIT" : "com.orcatech.pathology.diagnosis.type.visit",
	# Cassette level data
	"PATHOLOGY_HEMISPHERE" : "com.orcatech.pathology.hemisphere",
	# Cassette level data
	"PATHOLOGY_HEMISPHERE_CASSETTE" : "com.orcatech.pathology.hemisphere.cassette",
	# Cassette level data
	"PATHOLOGY_HEMISPHERE_SLICE" : "com.orcatech.pathology.hemisphere.slice",
	# Slides level data
	"PATHOLOGY_HEMISPHERE_SLIDE" : "com.orcatech.pathology.hemisphere.slide",
	# Information about a hemisphere cassette image.
	"PATHOLOGY_IMAGE_HEMISPHERE_CASSETTE" : "com.orcatech.pathology.image.hemisphere.cassette",
	# Information about a hemisphere cassette image.
	"PATHOLOGY_IMAGE_HEMISPHERE_CASSETTE_MAP_REGION" : "com.orcatech.pathology.image.hemisphere.cassette.map.region",
	# Information about a hemisphere cassette image with a stain.
	"PATHOLOGY_IMAGE_HEMISPHERE_CASSETTE_STAIN" : "com.orcatech.pathology.image.hemisphere.cassette.stain",
	# Information about a region of interest within the hemisphere cassette image that has been stained.
	"PATHOLOGY_IMAGE_HEMISPHERE_CASSETTE_STAIN_REGION" : "com.orcatech.pathology.image.hemisphere.cassette.stain.region",
	# A region of interest
	"PATHOLOGY_IMAGE_HEMISPHERE_CASSETTE_TYPE" : "com.orcatech.pathology.image.hemisphere.cassette.type",
	# Masking information about the hemisphere's white matter, gray matter and white matter hyper intensity
	"PATHOLOGY_MASK_HEMISPHERE" : "com.orcatech.pathology.mask.hemisphere",
	# A region of interest
	"PATHOLOGY_REGION" : "com.orcatech.pathology.region",
	# T2-IHC Registration
	"PATHOLOGY_REGISTRATION_HEMISPHERE_CASSETTE" : "com.orcatech.pathology.registration.hemisphere.cassette",
	# T2-IHC Registration File
	"PATHOLOGY_REGISTRATION_HEMISPHERE_CASSETTE_FILE" : "com.orcatech.pathology.registration.hemisphere.cassette.file",
	# Hemisphere information processed by Core #1
	"PATHOLOGY_REGISTRATION_HEMISPHERE_SLICE" : "com.orcatech.pathology.registration.hemisphere.slice",
	# Information about a scan of the brain hemisphere
	"PATHOLOGY_SCAN_HEMISPHERE" : "com.orcatech.pathology.scan.hemisphere",
	# Information about a scan of the brain hemisphere
	"PATHOLOGY_SCAN_HEMISPHERE_SLICE" : "com.orcatech.pathology.scan.hemisphere.slice",
	# Hemisphere information processed by Core #1
	"PATHOLOGY_SCAN_PROCESSING_HEMISPHERE" : "com.orcatech.pathology.scan.processing.hemisphere",
	# Cassette processing information
	"PATHOLOGY_SCAN_PROCESSING_HEMISPHERE_CASSETTE" : "com.orcatech.pathology.scan.processing.hemisphere.cassette",
	# Hemisphere information processed by Core #1
	"PATHOLOGY_SCAN_PROCESSING_HEMISPHERE_SLICE" : "com.orcatech.pathology.scan.processing.hemisphere.slice",
	# Hemisphere information processed by Core #1
	"PATHOLOGY_SCAN_PROCESSING_HEMISPHERE_SLIDE" : "com.orcatech.pathology.scan.processing.hemisphere.slide",
	# Information about hemisphere montage images. If all paths are null then the BFO exists in the montage directory but none of the filenames match the expected values.
	"PATHOLOGY_SCAN_PROCESSING_MONTAGE" : "com.orcatech.pathology.scan.processing.montage",
	# Stain used on a piece of tissue
	"PATHOLOGY_STAIN" : "com.orcatech.pathology.stain",
	# A tag used to categorize a set of pathology tissues
	"PATHOLOGY_TAG" : "com.orcatech.pathology.tag",
	# An endpoint permission
	"PERMISSION" : "com.orcatech.permission",
	# An api action
	"PERMISSION_ACTION" : "com.orcatech.permission.action",
	# An api endpoint
	"PERMISSION_ENDPOINT" : "com.orcatech.permission.endpoint",
	# This schema is differs from a subject in that this individual is not enrolled as part of the study but whose presence should be known about
	"PERSON" : "com.orcatech.person",
	# A note or comment about the subject
	"PERSON_COMMENT" : "com.orcatech.person.comment",
	# A phone number
	"PHONE" : "com.orcatech.phone",
	# A type of phone number
	"PHONE_TYPE" : "com.orcatech.phone.type",
	# A feature set of the system. When associated with a particular study or organization, the feature set endpoints will be available
	"PLUGIN" : "com.orcatech.plugin",
	# Captured events and timing for an Image Recognition test administered via a Qualtrics survey
	"QUALTRICS_IMAGERECOG" : "com.orcatech.qualtrics.imagerecog",
	# The input events captured while the subject was taking a survey.
	"QUALTRICS_INPUT" : "com.orcatech.qualtrics.input",
	# The input events captured while the subject was taking a survey.
	"QUALTRICS_QUESTION" : "com.orcatech.qualtrics.question",
	# Information about a question choice.
	"QUALTRICS_QUESTION_CHOICE" : "com.orcatech.qualtrics.question.choice",
	# Captured events and timing for an Stroop test administered via a Qualtrics survey
	"QUALTRICS_STROOP" : "com.orcatech.qualtrics.stroop",
	# Display information about a survey administered by Qualtrics
	"QUALTRICS_SURVEY" : "com.orcatech.qualtrics.survey",
	# Display information about a survey administered by Qualtrics
	"QUALTRICS_SURVEY_BLOCK" : "com.orcatech.qualtrics.survey.block",
	# Display information about a survey administered by Qualtrics
	"QUALTRICS_SURVEY_BLOCK_ELEMENT" : "com.orcatech.qualtrics.survey.block.element",
	# Display information about a survey administered by Qualtrics
	"QUALTRICS_SURVEY_COLUMN" : "com.orcatech.qualtrics.survey.column",
	# Display information about a survey administered by Qualtrics
	"QUALTRICS_SURVEY_EXPIRATION" : "com.orcatech.qualtrics.survey.expiration",
	# Display information about a survey administered by Qualtrics
	"QUALTRICS_SURVEY_FLOW" : "com.orcatech.qualtrics.survey.flow",
	# Display information about a survey administered by Qualtrics
	"QUALTRICS_SURVEY_LOOP" : "com.orcatech.qualtrics.survey.loop",
	# Display information about a survey administered by Qualtrics
	"QUALTRICS_SURVEY_LOOP_QUESTION_META" : "com.orcatech.qualtrics.survey.loop.questionMeta",
	# Display information about a survey administered by Qualtrics
	"QUALTRICS_SURVEY_QUESTION" : "com.orcatech.qualtrics.survey.question",
	# Display information about a survey administered by Qualtrics
	"QUALTRICS_SURVEY_QUESTION_CHOICE" : "com.orcatech.qualtrics.survey.question.choice",
	# Display information about a survey administered by Qualtrics
	"QUALTRICS_SURVEY_QUESTION_TYPE" : "com.orcatech.qualtrics.survey.question.type",
	# Display information about a survey administered by Qualtrics
	"QUALTRICS_SURVEY_QUESTION_VALIDATION" : "com.orcatech.qualtrics.survey.question.validation",
	# Captured events, questions and answers from the a survey administered by Qualtrics
	"QUALTRICS_SURVEY_RESPONSE" : "com.orcatech.qualtrics.survey.response",
	# Captured events and timing for a Trails Making test administered via a Qualtrics survey
	"QUALTRICS_TRAILS" : "com.orcatech.qualtrics.trails",
	# A reported life event change that could a meaningful impact on collected data samples
	"REPORT_LIFE_EVENT" : "com.orcatech.report.life.event",
	# An role within a scope of the system. This is essentially a set of permissions
	"ROLE" : "com.orcatech.role",
	# A data structure contain the type and version information for a data schema
	"SCHEMA" : "com.orcatech.schema",
	# An alert indicating a problem with a sensor
	"SENSOR_ALERT" : "com.orcatech.sensor.alert",
	# Unique sensor line information
	"SENSOR_LINE" : "com.orcatech.sensor.line",
	# A pair of two sensors that compose a segment within a sensor line
	"SENSOR_LINE_SEGMENT" : "com.orcatech.sensor.line.segment",
	# A type of sensor line
	"SENSOR_LINE_TYPE" : "com.orcatech.sensor.line.type",
	# Audio recording for SHARP
	"SHARP_AUDIO" : "com.orcatech.sharp.audio",
	# Coordinates for SHARP
	"SHARP_COORDINATE" : "com.orcatech.sharp.coordinate",
	# Events for SHARP
	"SHARP_EVENT" : "com.orcatech.sharp.event",
	# Tokens for subject 3rd party data retrieval
	"SHARP_PARTICIPANT_TOKEN" : "com.orcatech.sharp.participant.token",
	# Path for SHARP
	"SHARP_PATH" : "com.orcatech.sharp.path",
	# Path marker for SHARP
	"SHARP_PATH_MARKER" : "com.orcatech.sharp.path.marker",
	# Software available to the organization and can be installed
	"SOFTWARE" : "com.orcatech.software",
	# An apt package repository
	"SOFTWARE_APT" : "com.orcatech.software.apt",
	# Software installed using an apt repo
	"SOFTWARE_APT_REPO" : "com.orcatech.software.apt.repo",
	# Account identifiers provided by the OAuth2 provider
	"SSO_ACCOUNT" : "com.orcatech.sso.account",
	# OAuth2 Providers scopes to be requested during authentication
	"SSO_OAUTH2_SCOPE" : "com.orcatech.sso.oauth2.scope",
	# Tokens used for access to authenticated endpoints protects by OAuth2
	"SSO_OAUTH2_TOKEN" : "com.orcatech.sso.oauth2.token",
	# Application credentials to an sso identity provider
	"SSO_PROVIDER" : "com.orcatech.sso.provider",
	# An  study is an research study consisting of a subset of subjects who and agreed to participant.
	"STUDY" : "com.orcatech.study",
	# Subject study enrollment information.
	"STUDY_ENROLLMENT" : "com.orcatech.study.enrollment",
	# A study enrollment state for a subject. The state should indicate where the subject is in the enrollment process.
	"STUDY_ENROLLMENT_STATE" : "com.orcatech.study.enrollment.state",
	# An external identifier for the study to map the it's data to an external database
	"STUDY_IDENTIFIER" : "com.orcatech.study.identifier",
	# A type of external identifier for the study to map the it's data to an external database
	"STUDY_IDENTIFIER_TYPE" : "com.orcatech.study.identifier.type",
	# The status of the study
	"STUDY_STATUS" : "com.orcatech.study.status",
	# A subject who participates in an  affiliated study
	"SUBJECT" : "com.orcatech.subject",
	# The value portion of a key value pair belonging to an subject
	"SUBJECT_ATTRIBUTE" : "com.orcatech.subject.attribute",
	# A type of subject attribute for the subject. This will act as the key in the key value pair
	"SUBJECT_ATTRIBUTE_TYPE" : "com.orcatech.subject.attribute.type",
	# A note or comment about the subject
	"SUBJECT_COMMENT" : "com.orcatech.subject.comment",
	# A contact with the subject. This can be a phone call, in person visit, etc.
	"SUBJECT_CONTACT" : "com.orcatech.subject.contact",
	# A reason for which the contact was made.
	"SUBJECT_CONTACT_REASON" : "com.orcatech.subject.contact.reason",
	# A type on contact such as phone call, in person visit, etc.
	"SUBJECT_CONTACT_TYPE" : "com.orcatech.subject.contact.type",
	# The ethnicity the subject identifies with
	"SUBJECT_ETHNICITY" : "com.orcatech.subject.ethnicity",
	# A type of gender
	"SUBJECT_GENDER" : "com.orcatech.subject.gender",
	# An external identifier for the subject to map the their data to an external database
	"SUBJECT_IDENTIFIER" : "com.orcatech.subject.identifier",
	# A type of external identifier for the subject to map the their data to an external database
	"SUBJECT_IDENTIFIER_TYPE" : "com.orcatech.subject.identifier.type",
	# The primary category of the the life event
	"SUBJECT_LIFE_EVENT_CATEGORY_PRIMARY" : "com.orcatech.subject.life.event.category.primary",
	# The secondary category of the life event
	"SUBJECT_LIFE_EVENT_CATEGORY_SECONDARY" : "com.orcatech.subject.life.event.category.secondary",
	# The source that generated the life event
	"SUBJECT_LIFE_EVENT_SOURCE" : "com.orcatech.subject.life.event.source",
	# A tag used to categorize a set of life events
	"SUBJECT_LIFE_EVENT_TAG" : "com.orcatech.subject.life.event.tag",
	# The race the subject identifies with
	"SUBJECT_RACE" : "com.orcatech.subject.race",
	# A tag used to categorize a set of subjects or people
	"SUBJECT_TAG" : "com.orcatech.subject.tag",
	# A survey that has been or can be administered to a set of subjects
	"SURVEY" : "com.orcatech.survey",
	# A distribution of the survey to a particular group of subjects
	"SURVEY_DISTRIBUTION" : "com.orcatech.survey.distribution",
	# A reported life event change that could a meaningful impact on collected data samples
	"SURVEY_EVENT" : "com.orcatech.survey.event",
	# The primary category of the generated the survey event
	"SURVEY_EVENT_CATEGORY_PRIMARY" : "com.orcatech.survey.event.category.primary",
	# The secondary category of the generated the survey event
	"SURVEY_EVENT_CATEGORY_SECONDARY" : "com.orcatech.survey.event.category.secondary",
	# A reported life event change that could a meaningful impact on collected data samples
	"SURVEY_EVENT_ERROR" : "com.orcatech.survey.event.error",
	# A tag applied to the survey event to group them together
	"SURVEY_EVENT_TAG" : "com.orcatech.survey.event.tag",
	# Display information about a survey
	"SURVEY_FORM" : "com.orcatech.survey.form",
	# Captured device input that happened during a survey
	"SURVEY_INPUT" : "com.orcatech.survey.input",
	# Display information about a survey administered by Qualtrics
	"SURVEY_QUESTION" : "com.orcatech.survey.question",
	# Display information about a survey administered by Qualtrics
	"SURVEY_QUESTION_CHOICE" : "com.orcatech.survey.question.choice",
	# Captured questions and answers from an administered survey
	"SURVEY_RESPONSE" : "com.orcatech.survey.response",
	# Information about a specific survey question. The metrics will be additive if the respondent is viewing the page multiple times, either through the use of a back button or by exiting and reopening the survey. For example, let’s say a respondent submits a page after 20 seconds, goes back to that page using the back button, and then submits the page again after 30 seconds. Their recorded Page Submit time will be 50 seconds.
	"SURVEY_RESPONSE_QUESTION" : "com.orcatech.survey.response.question",
	# Information about a specific survey question. The metrics will be additive if the respondent is viewing the page multiple times, either through the use of a back button or by exiting and reopening the survey. For example, let’s say a respondent submits a page after 20 seconds, goes back to that page using the back button, and then submits the page again after 30 seconds. Their recorded Page Submit time will be 50 seconds.
	"SURVEY_RESPONSE_QUESTION_METRIC" : "com.orcatech.survey.response.question.metric",
	# Information about a specific survey question. The metrics will be additive if the respondent is viewing the page multiple times, either through the use of a back button or by exiting and reopening the survey. For example, let’s say a respondent submits a page after 20 seconds, goes back to that page using the back button, and then submits the page again after 30 seconds. Their recorded Page Submit time will be 50 seconds.
	"SURVEY_RESPONSE_QUESTION_METRIC_CLICK" : "com.orcatech.survey.response.question.metric.click",
	# A task to be done or has been done for a project/study
	"TASK" : "com.orcatech.task",
	# A task to be done or has been done for a study
	"TASK_TYPE" : "com.orcatech.task.type",
	# Captured events and timing for an Image Recognition test administered via a web browser
	"TEST_NEUROPSYCH_IMAGERECOG" : "com.orcatech.test.neuropsych.imagerecog",
	# Coordinate location and associated image
	"TEST_NEUROPSYCH_IMAGERECOG_COORD" : "com.orcatech.test.neuropsych.imagerecog.coord",
	# The context and coordinate information about a user's selection
	"TEST_NEUROPSYCH_IMAGERECOG_SELECTION" : "com.orcatech.test.neuropsych.imagerecog.selection",
	# Captured events and timing for a Stroop test administered via a web browser
	"TEST_NEUROPSYCH_STROOP" : "com.orcatech.test.neuropsych.stroop",
	# A selection event with context relative the Stroop test being administered
	"TEST_NEUROPSYCH_STROOP_SELECTION" : "com.orcatech.test.neuropsych.stroop.selection",
	# Captured events and timing for a Trail Making test administered via a web browser
	"TEST_NEUROPSYCH_TRAILS" : "com.orcatech.test.neuropsych.trails",
	# A selection event with context relative the trails making test being administered
	"TEST_NEUROPSYCH_TRAILS_SELECTION" : "com.orcatech.test.neuropsych.trails.selection",
	# A token displayed on the Trails Making test. This is a outlined circle with text displayed in the center of the circle.
	"TEST_NEUROPSYCH_TRAILS_TOKEN" : "com.orcatech.test.neuropsych.trails.token",
	# Thunderboard snapshot encapsulates readings from the various sensors on a thunderboard, see https://www.silabs.com/products/development-tools/thunderboard/thunderboard-iot-kit-platform
	"THUNDERBOARD_SNAPSHOT" : "com.orcatech.thunderboard.snapshot",
	# An timeline event outlining what happened, who did it and to who.
	"TIMELINE" : "com.orcatech.timeline",
	# TimerCap close records collected from either iSorts or iCaps, see https://timercap.com
	"TIMERCAP_CLOSE_EVENT_RECORD" : "com.orcatech.timercap.closeEventRecord",
	# TimerCap device which is either iSorts or iCaps, see https://timercap.com
	"TIMERCAP_DEVICE" : "com.orcatech.timercap.device",
	# A set of timestamps describing the status of a timercap device data sync
	"TIMERCAP_HEARTBEAT" : "com.orcatech.timercap.heartbeat",
	# The type of trip event
	"TRIP_EVENT_TYPE" : "com.orcatech.trip.event.type",
	# An  user who has access to the data streams. This can be researchers, study admins, etc
	"USER" : "com.orcatech.user",
	# An external identifier for the user to map the it's data to an external database
	"USER_IDENTIFIER" : "com.orcatech.user.identifier",
	# A type of external identifier for the user to map the it's data to an external database
	"USER_IDENTIFIER_TYPE" : "com.orcatech.user.identifier.type",
	# A tag used to categorize a set of users
	"USER_TAG" : "com.orcatech.user.tag",
	# A short lived token used to identify the user
	"USER_TOKEN" : "com.orcatech.user.token",
	# Information about a particular vehicle
	"VEHICLE" : "com.orcatech.vehicle",
	# The type of vehicle event
	"VEHICLE_EVENT_TYPE" : "com.orcatech.vehicle.event.type",
	# An set of basic metrics measured by a withings scale
	"WITHINGS_BODY" : "com.orcatech.withings.body",
	# Nokia device information, see https://health.nokia.com
	"WITHINGS_DEVICE" : "com.orcatech.withings.device",
	# Information about the last checkin from the scale
	"WITHINGS_DEVICE_CHECKIN" : "com.orcatech.withings.device.checkin",
	# A set of timestamps describing the status of a withings device data sync
	"WITHINGS_DEVICE_HEARTBEAT" : "com.orcatech.withings.device.heartbeat",
	# An set of heart metrics measured by a withings scale
	"WITHINGS_HEART" : "com.orcatech.withings.heart",
	# intraday high frequency activity measures
	"WITHINGS_HIGHFREQ_ACTIVITY" : "com.orcatech.withings.highfreq.activity",
	# Nokia account user information, see https://health.nokia.com
	"WITHINGS_USER" : "com.orcatech.withings.user",
	# Nokia high frequency activity information, see https://health.nokia.com
	"WITHINGS_VASISTAS" : "com.orcatech.withings.vasistas",
	# Individual computer use sessions tracked using the WorkTime software. See https://www.worktime.com/
	"WORKTIME_SESSION" : "com.orcatech.worktime.session",
	# Individual computer users tracking by the WorkTime software. See https://www.worktime.com/
	"WORKTIME_USER" : "com.orcatech.worktime.user",
	# Zigbee device
	"ZIGBEE_DEVICE" : "com.orcatech.zigbee.device",
	# Zigbee zone status events
	"ZIGBEE_ZONE_STATUS" : "com.orcatech.zigbee.zone.status",
	# Address details for a Zubie point.
	"ZUBIE_ADDRESS" : "com.orcatech.zubie.address",
	# Information about the Zubie OBD sensor.
	"ZUBIE_DEVICE" : "com.orcatech.zubie.device",
	# Vehicle and device events
	"ZUBIE_EVENT" : "com.orcatech.zubie.event",
	# Contextual data about device events
	"ZUBIE_EVENT_CONTEXT_DEVICE" : "com.orcatech.zubie.event.context.device",
	# Contextual data about devices when they transition between vehicles
	"ZUBIE_EVENT_CONTEXT_DEVICE_CLAIM" : "com.orcatech.zubie.event.context.device.claim",
	# Contextual data about trip events
	"ZUBIE_EVENT_CONTEXT_TRIP" : "com.orcatech.zubie.event.context.trip",
	# Contextual data about vehicle alert events during a trip
	"ZUBIE_EVENT_CONTEXT_TRIP_ALERT" : "com.orcatech.zubie.event.context.trip.alert",
	# Contextual data about trip tagging events
	"ZUBIE_EVENT_CONTEXT_TRIP_TAGGED" : "com.orcatech.zubie.event.context.trip.tagged",
	# Contextual data about the vehicle at a particular location
	"ZUBIE_EVENT_CONTEXT_VEHICLE_GEOFENCE" : "com.orcatech.zubie.event.context.vehicle.geofence",
	# Contextual data about vehicle location
	"ZUBIE_EVENT_CONTEXT_VEHICLE_LOCATION" : "com.orcatech.zubie.event.context.vehicle.location",
	# Contextual data about device events
	"ZUBIE_EVENT_DEVICE" : "com.orcatech.zubie.event.device",
	# Current state and identification information about a place
	"ZUBIE_EVENT_PLACE" : "com.orcatech.zubie.event.place",
	# Contextual data at a location
	"ZUBIE_EVENT_POINT" : "com.orcatech.zubie.event.point",
	# Current state and identification information about a trip
	"ZUBIE_EVENT_TRIP" : "com.orcatech.zubie.event.trip",
	# Contextual data about the vehicle used in the event
	"ZUBIE_EVENT_VEHICLE" : "com.orcatech.zubie.event.vehicle",
	# Location coordinates
	"ZUBIE_POINT" : "com.orcatech.zubie.point",
	# 
	"ZUBIE_TAG" : "com.orcatech.zubie.tag",
	# 
	"ZUBIE_TRIP" : "com.orcatech.zubie.trip",
	# The coordinates of a trip with relevant vehicle state information
	"ZUBIE_TRIP_BOUND" : "com.orcatech.zubie.trip.bound",
	# Vehicle state information collected at a certain time point
	"ZUBIE_TRIP_POINT" : "com.orcatech.zubie.trip.point",
	# Location details recorded by the vehicle
	"ZUBIE_VEHICLE_TRIP_POINT" : "com.orcatech.zubie.vehicle.trip.point",
	"GRAPH_NODE" : "com.orcatech.graph.node",
	"GRAPH_EDGE" : "com.orcatech.graph.edge",
}


"""
    The possible API action requests
    @readonly
"""

# RequestsScope = {
# 	['accout']: [ Request.SEND_RESET_ACCOUNT,Request.SEND_ADD_ACCOUNT ],
# 	["admin"]: [ Request.MIGRATE ],
# 	["organization"]: [ Request.IMPORT_QUALTRICS_SURVEY ],
# 	["study"]: [ Request.IMPORT_QUALTRICS_SURVEY ],
# }

RequestsScope = {
    'accout': [Request["SEND_RESET_ACCOUNT"], Request["SEND_ADD_ACCOUNT"]],
    'admin': [Request["MIGRATE"]],
    'organization': [Request["IMPORT_QUALTRICS_SURVEY"]],
    'study': [Request["IMPORT_QUALTRICS_SURVEY"]],
}

"""
    The possible API action requests
    @readonly
"""

RequestsRecord = {
	Schema["USER"]: {
    Request["SEND_INVITE"]: [Scope["ADMIN"],Scope["ORGANIZATION"],Scope["STUDY"],Scope["GLOBAL"] ],
	}
}

"""Schema that can be represented by a scope"""

ScopeSchema = {
	Scope["ORGANIZATION"] : Schema["ORGANIZATION"],
	Scope["STUDY"] : Schema["STUDY"],
    Scope["ACCOUNT"] : Schema["USER"]
}


"""Schema that can be represented by a scope"""

ScopeCreateSchema = {
	Scope["ORGANIZATION"] : Schema["ORGANIZATION"],
	Scope["STUDY"] : Schema["STUDY"],
}


ObservationMetaSchema = {
Schema["EVENT"]: Schema["OBSERVATION_GENERIC_EVENT_ALERT_META"],
Schema["ALERT_INCIDENT"]: Schema["OBSERVATION_GENERIC_EVENT_ALERT_META"],
Schema["MEASURE_ACCESS_PERIOD"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_ACCESS_REQUEST"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_ACTIVITY_PHYSICAL_PERIOD"]:  Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_APPLICATION_USER_PERIOD"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_BATTERY"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_BED_ACTIVITY"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_BED_AWAKE_PERIOD"]:  Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_BED_EXIT_PERIOD"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_BODY_WEIGHT"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_CONTACT"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_CHECKIN"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_COORDINATE"]:  Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_DEVICE_EVENT"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_HEART_RATE"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_HEART_RATE_PERIOD"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_HEART_RATE_VARIABILITY_PERIOD"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_HEART_RATE_VARIABILITY_RMSSD"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_PRESENCE"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_PILLBOX_STATE"]:  Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_RESPIRATION_RATE"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_RESPIRATION_RATE_PERIOD"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_SLEEP_MOVEMENT_FAST"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_SLEEP_PERIOD"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_SLEEP_STATE_PERIOD"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_SLEEP_MOVEMENT_FAST"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_SLEEP_SCORE_PERIOD"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_SLEEP_MOVEMENT_PERIOD"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_SLEEP_MOVEMENT_FAST_PERIOD"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_STEP_PERIOD"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_SWIM_PERIOD"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_TRIP"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_TRIP_EVENT"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_VEHICLE_EVENT"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_VEHICLE_MIL"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_VEHICLE_STATE"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["MEASURE_WEB_SEARCH"]: Schema["OBSERVATION_GENERIC_MEASURE_META"],
Schema["REPORT_LIFE_EVENT"]:  Schema["OBSERVATION_GENERIC_REPORT_META"],
Schema["SURVEY"]:  Schema["OBSERVATION_GENERIC_SURVEY_META"],
Schema["SURVEY_EVENT"]: Schema["OBSERVATION_GENERIC_SURVEY_META"],
Schema["SURVEY_EVENT_ERROR"]: Schema["OBSERVATION_GENERIC_SURVEY_META"],
Schema["SURVEY_INPUT"]: Schema["OBSERVATION_GENERIC_SURVEY_META"],
Schema["SURVEY_RESPONSE"]: Schema["OBSERVATION_GENERIC_SURVEY_META"],
Schema["SURVEY_FORM"]: Schema["OBSERVATION_GENERIC_SURVEY_META"],
Schema["TEST_NEUROPSYCH_IMAGERECOG"]:  Schema["OBSERVATION_GENERIC_TEST_META"],
Schema["TEST_NEUROPSYCH_STROOP"]: Schema["OBSERVATION_GENERIC_TEST_META"],
Schema["TEST_NEUROPSYCH_TRAILS"]: Schema["OBSERVATION_GENERIC_TEST_META"],
}