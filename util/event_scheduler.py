"""
Event Scheduler

Does assincronous events used by solicitations
"""
from datetime import datetime

import logging
import sched
import threading
import time
import util

from repositories import SchedulingsRepository

logging = logging.getLogger(__name__)

class EventScheduler:

    def __init__(self):
        # Creates an event scheduler object using:
        #   time.monotonic as the time function to measure time intervals
        #   time.sleep as the delay function compatible with time function to suspend thread execution
        #
        #   time.sleep: Uses OSs schedulling syscalls to suspend execution of the current thread
        #   time.monotonic: Uses OSs clock syscalls to create a monotonic clock based on what time the system is on
        #   python scheduler class can be safely used in multi-threaded environments
        self.scheduler = sched.scheduler(timefunc=time.monotonic, delayfunc=time.sleep)
        self.scheduler_events = {}
    
    def start(self, flask_server, smtp_server_ref):

        # used to do thing with app_context
        self.flask_server = flask_server

        # utilized to mail sending events
        self.smtp_server_ref = smtp_server_ref

        # load old schedulings if system is restarted
        self.__load_from_db()

        # Start thread to run scheduler and not block main thread, self is shared
        self.finish_thread = False
        threading.Thread(target = self.__run).start()
    
    def __load_from_db(self):

        # Load database stored events
        schedulings = SchedulingsRepository.read_schedulings()

        # Stores in scheduler
        added_events = 0
        for sch in schedulings:
            print(sch.id, sch.scheduled_action, sch.scheduled_datetime, sch.scheduled_status)
            print(sch.scheduling_state_transition.user_has_solicitation_state_id, )
            if sch.scheduled_status == "Pending":
                added_events += 1
                self.add_transition(
                    sch.id,
                    sch.scheduled_datetime,
                    sch.scheduling_state_transition.user_has_solicitation_state_id,
                    sch.scheduling_state_transition.state_transition_scheduled_id,
                    util.resolve_scheduled_solicitation
                )

    # Private method used by thread to run scheduler asynchronous
    def __run(self):
        logging.info(f"EventScheduler thread {threading.get_ident()}: Scheduler running")
        while self.finish_thread == False:
            with self.flask_server.app_context():
                self.scheduler.run(blocking=False)
                time.sleep(1)

    # Stops thread
    def stop(self):
        self.finish_thread = True

    # Enters a event in queue using:
    #   event id - ignores repeated ids
    #   delay in seconds
    #   action function that takes arguments kwargs
    #   dictionary arguments kwargs
    #   priority with default value 1
    def enter_event(self, event_id, delay, priority, action, kwargs):
        if not self.scheduler_events.get(event_id):
            event = self.scheduler.enter(delay, priority, action, kwargs=kwargs)
            self.scheduler_events[event_id] = event
        else:
            logging.info(f"# EventScheduler thread {threading.get_ident()}: Repeated event id ignorated")
  
    # Removes a event in queue using:
    #   event id
    def remove_event(self, event_id):
        if self.scheduler_events.get(event_id):
        
            # avoid finished event remotion exception
            try:
                self.scheduler.cancel(self.scheduler_events[event_id])
            except ValueError:
                pass
        
            del self.scheduler_events[event_id]
    
    def add_transition(self, event_id, send_datetime, user_has_state_id, transition_id, action, priority=1):

        kwargs = {
            'event_id': event_id,
            'user_has_state_id': user_has_state_id,
            'transition_id': transition_id
        }

        delay = (send_datetime - datetime.now()).total_seconds()
        self.enter_event(event_id, delay, priority, action, kwargs)
    
    def add_mail(self, event_id, send_datetime, raw_to, raw_subject, raw_body, priority=1):

        kwargs = {
            'raw_to': raw_to,
            'raw_subject': raw_subject,
            'raw_body': raw_body
        }

        actual_datetime = datetime.now()
        delay = (send_datetime - actual_datetime).total_seconds()

        self.enter_event(event_id, delay, priority, self.smtp_server_ref.add_email, kwargs)

    # prints event id list and (time, priority, action, argument, kwargs) of each queue object
    def print_events(self):
        print(self.scheduler_events)
        print(self.scheduler.queue)
    
    # resolves scheduled solicitations
    def resolve_scheduled_solicitation(self, event_id, user_has_state_id, transition_id):
        logging.info(f"scheduling resolved {event_id} {user_has_state_id} {transition_id}")