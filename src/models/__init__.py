from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .attachment import Attachment
from .config import Config, ConfigSystemPath, ConfigMail, ConfigYear, ConfigYearHoliday, ConfigReasonClass, ConfigReason
from .dynamic_mail import DynamicMail
from .dynamic_page import ( 
    DynamicPage, DynamicComponent, DynamicPageHasComponent, DynamicComponentInnerHtml, DynamicComponentInput, 
    DynamicComponentInputDateRule, DynamicComponentUpload, DynamicComponentSelect, DynamicComponentSelectOption,
    DynamicComponentSelectUpload, DynamicComponentDownload, DynamicComponentButton, DynamicComponentDetails
)
from .mail_validation import MailValidation
from .profile import Profile
from .scheduling import Scheduling, SchedulingStateTransition
from .solicitation import Solicitation, SolicitationStartMail, SolicitationState, SolicitationStateProfileEditors
from .transitions import (
    SolicitationStateTransition, SolicitationStateTransitionManual, SolicitationStateTransitionFromDynamicPage,
    SolicitationStateTransitionScheduled, SolicitationStateTransitionMail
)
from .user import (
    User, UserHasProfile, UserHasProfileCoordinatorData, UserHasProfileAdvisorData, UserHasProfileStudentData,
    UserHasAttachment, UserHasSolicitation, UserHasSolicitationState
)