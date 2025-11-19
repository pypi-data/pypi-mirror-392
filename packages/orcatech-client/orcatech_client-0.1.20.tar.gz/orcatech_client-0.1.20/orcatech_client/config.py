from typing import Literal, Union, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

Scope = {
    "PUBLIC": "public",
    "ACCOUNT": "account",
    "ADMIN": "admin",
    "GLOBAL": "global",
    "ORGANIZATION": "organization",
    "STUDY": "study",
}


ExternalSchemaType = "com.orcatech.qualtrics.survey"

"""
    Set of available observation data schemas in the API
"""

# ObservationDataSchemaType = Literal[
#     "com.orcatech.measure.access.period",
#     "com.orcatech.measure.access.request",
#     "com.orcatech.measure.activity.physical.period",
#     "com.orcatech.measure.application.user.period",
#     "com.orcatech.measure.battery",
#     "com.orcatech.measure.bed.activity",
#     "com.orcatech.measure.bed.awake.period",
#     "com.orcatech.measure.bed.exit.period",
#     "com.orcatech.measure.body.weight",
#     "com.orcatech.measure.checkin",
#     "com.orcatech.measure.contact",
#     "com.orcatech.measure.coordinate",
#     "com.orcatech.measure.heart.rate",
#     "com.orcatech.measure.heart.rate.period",
#     "com.orcatech.measure.heart.rate.variability.period",
#     "com.orcatech.measure.heart.rate.variability.rmssd",
#     "com.orcatech.measure.pillbox.state",
#     "com.orcatech.measure.presence",
#     "com.orcatech.measure.respiration.rate",
#     "com.orcatech.measure.respiration.rate.period",
#     "com.orcatech.measure.sleep.movement.fast",
#     "com.orcatech.measure.sleep.movement.fast.period",
#     "com.orcatech.measure.sleep.movement.period",
#     "com.orcatech.measure.sleep.period",
#     "com.orcatech.measure.sleep.score.period",
#     "com.orcatech.measure.sleep.state.period",
#     "com.orcatech.measure.step.period",
#     "com.orcatech.measure.swim.period",
#     "com.orcatech.measure.trip",
#     "com.orcatech.measure.vehicle.event",
#     "com.orcatech.measure.vehicle.mil",
#     "com.orcatech.measure.vehicle.state",
#     "com.orcatech.measure.web.search",
#     "com.orcatech.report.life.event",
#     "com.orcatech.survey.event",
#     "com.orcatech.survey.event.error",
#     "com.orcatech.survey.form",
#     "com.orcatech.survey.input",
#     "com.orcatech.survey.response",
#     "com.orcatech.test.neuropsych.imagerecog",
#     "com.orcatech.test.neuropsych.stroop",
#     "com.orcatech.test.neuropsych.trails",
# ]



APIID = Union[int, str]


class APIOption:
    def __init__(self, header: Dict[str, str] = None, param: Dict[str, str] = None):
        self.header = header if header else {}
        self.param = param if param else {}


from typing import TypeVar, Generic

T = TypeVar("T")


class APIResponse(Generic[T]):
    def __init__(self, data: T):
        self.data = data


class GetRecordPayload(Generic[T]):
    def __init__(self, record: T):
        self.record = record


class Config:
    HOST_URL = os.getenv("HOST_URL")
    AUTH_TOKEN = os.getenv("AUTH_TOKEN")

    @staticmethod
    def validate():
        if not Config.HOST_URL or not Config.AUTH_TOKEN:
            raise ValueError(
                "Please set the HOST_URL and AUTH_TOKEN environment variables."
            )