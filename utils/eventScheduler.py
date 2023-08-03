from datetime import datetime
import sched, time
import threading
import traceback

import service.scheduleService

import utils.dbUtils
import utils.smtpMails

systemEventScheduler = None

def startEventScheduler():

  global systemEventScheduler

  if systemEventScheduler == None:
    systemEventScheduler = EventScheduler()
  
  loadEventScheduler()

def loadEventScheduler():

  # Load database stored events to Scheduler
  try:
    schQuery = """
      SELECT sch.id AS id, sch.scheduled_action, sch.scheduled_datetime, sch.scheduled_status, 
      scht.state_transition_scheduled_id, scht.user_has_solicitation_state_id  
        FROM sisgesteste.scheduling sch 
        JOIN scheduling_state_transition scht ON sch.id = scht.scheduling_id;
      """
    schs = utils.dbUtils.dbGetAll(schQuery)
    
    # insert pending events to system schedule 
    eventsAdded = 0
    for sch in schs:
      if sch["scheduled_status"] == "Pending":
        eventsAdded += 1
        addTransitionToEventScheduler(
          sch["id"],
          sch["scheduled_datetime"],
          sch["user_has_solicitation_state_id"],
          sch["state_transition_scheduled_id"],
          service.scheduleService.resolveScheduledSolicitation
        )
    print(f"# {eventsAdded} events added to event scheduler")
  
  except Exception as e:
    print("# Error while loading schedule events:")
    print(e)
    traceback.print_exc()

def addToEventScheduler(eventId, delay, action, kwargs=None, priority=1):

  global systemEventScheduler

  if systemEventScheduler == None:
    systemEventScheduler = EventScheduler()

  systemEventScheduler.enterEvent(eventId, delay, priority, action, kwargs)

def addMailToEventScheduler(eventId, sendDatetime, rawTo, rawSubject, rawBody, priority=1):

  global systemEventScheduler

  if systemEventScheduler == None:
    systemEventScheduler = EventScheduler()

  kwargs = {
    'rawTo': rawTo,
    'rawSubject': rawSubject,
    'rawBody': rawBody
  }

  actualDatetime = datetime.now()
  delay = (sendDatetime - actualDatetime).total_seconds()

  systemEventScheduler.enterEvent(eventId, delay, priority, utils.smtpMails.addToSmtpMailServer, kwargs)

def addTransitionToEventScheduler(eventId, sendDatetime, userHasStateId, transitionId, action, priority=1):
  
  global systemEventScheduler

  if systemEventScheduler == None:
    systemEventScheduler = EventScheduler()

  kwargs = {
    'eventId': eventId,
    'userHasStateId': userHasStateId,
    'transitionId': transitionId
  }

  delay = (sendDatetime - datetime.now()).total_seconds()
  systemEventScheduler.enterEvent(eventId, delay, priority, action, kwargs)

def removeEventFromScheduler(eventId):

  global systemEventScheduler

  if systemEventScheduler == None:
    systemEventScheduler = EventScheduler()

  systemEventScheduler.removeEvent(eventId)

def printEventSchedulerInfo():

  global systemEventScheduler

  if systemEventScheduler != None:
    systemEventScheduler.printEvents()

def stopEventScheduler():

  global systemEventScheduler

  if systemEventScheduler != None:
    systemEventScheduler.stop()

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
    self.schedulerEvents = {}

    # Start thread to run scheduler and not block main thread, self is shared
    self.finishThread = False
    threading.Thread(target = self.__run).start()

  # Private method used by thread to run scheduler asynchronous
  def __run(self):
    print(f'# EventScheduler thread {threading.get_ident()}: Scheduler running!')
    while self.finishThread == False:
      self.scheduler.run(blocking=False)
      time.sleep(1)

  # Stops thread
  def stop(self):
    self.finishThread = True

  # Enters a event in queue using:
  #   event id - ignores repeated ids
  #   delay in seconds
  #   action function that takes arguments kwargs
  #   dictionary arguments kwargs
  #   priority with default value 1
  def enterEvent(self, eventId, delay, priority, action, kwargs):
    if not self.schedulerEvents.get(eventId):
      event = self.scheduler.enter(delay, priority, action, kwargs=kwargs)
      self.schedulerEvents[eventId] = event
    else:
      print(f'# EventScheduler thread {threading.get_ident()}: Repeated event id ignorated!')
  
  # Removes a event in queue using:
  #   event id
  def removeEvent(self, eventId):
    if self.schedulerEvents.get(eventId):
      
      # avoid finished event remotion exception
      try:
        self.scheduler.cancel(self.schedulerEvents[eventId])
      except ValueError:
        pass
      
      del self.schedulerEvents[eventId]

  # prints event id list and (time, priority, action, argument, kwargs) of each queue object
  def printEvents(self):
    print(self.schedulerEvents)
    print(self.scheduler.queue)