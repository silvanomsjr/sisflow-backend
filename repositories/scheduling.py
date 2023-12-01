""" Defines the Scheduling repository """

from models import Scheduling, SchedulingStateTransition

class SchedulingRepository:
    """ The repository for singe scheduling """

    @staticmethod
    def create_scheduling(scheduled_action, scheduled_datetime, scheduled_status="Pending"):
        """ Create a scheduling """
        scheduling = Scheduling(scheduled_action, scheduled_datetime, scheduled_status)
        return scheduling.save()

    @staticmethod
    def create_scheduling_state_transition(scheduling_id, state_transition_scheduled_id, user_has_solicitation_state_id):
        """ Create a scheduling state transition """
        sst = SchedulingStateTransition(scheduling_id, state_transition_scheduled_id, user_has_solicitation_state_id)
        return sst.save()
    
    @staticmethod
    def read_scheduling(scheduling_id):
        """ Query a scheduling by its id """
        scheduling_query = Scheduling.query.filter_by(id=scheduling_id)
        return scheduling_query.one() if scheduling_query.count() == 1 else None
    
    @staticmethod
    def update_scheduling(scheduled_id, scheduled_status):
        """ Update a scheduling """
        
        scheduling = SchedulingRepository.read_scheduling(scheduled_id)
        if not scheduling:
            return None

        scheduling.scheduled_status = scheduled_status
        return scheduling.save()

class SchedulingsRepository:
    """ The repository for multiple schedulings """

    @staticmethod
    def read_schedulings(user_has_state_id=None):
        """ Query all schedulings """

        if user_has_state_id == None:
            return Scheduling.query.all()
        
        Schedulings_query = Scheduling.query\
            .join(SchedulingStateTransition, Scheduling.id == SchedulingStateTransition.scheduling_id)\
            .filter(SchedulingStateTransition.user_has_solicitation_state_id == user_has_state_id)
        
        return Schedulings_query.all() if Schedulings_query.count() > 0 else []