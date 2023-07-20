from datetime import datetime
import sched, time
import threading
from utils.smtpMails import addToSmtpMailServer

systemEventScheduler = None

def startEventScheduler():

  global systemEventScheduler

  if systemEventScheduler == None:
    systemEventScheduler = EventScheduler()

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

  systemEventScheduler.enterEvent(eventId, delay, priority, addToSmtpMailServer, kwargs)

def addTransitionToEventScheduler(eventId, sendDatetime, userHasStateId, userData, transitionId, action, priority=1):
  
  global systemEventScheduler

  if systemEventScheduler == None:
    systemEventScheduler = EventScheduler()

  userHasStateId, userData, transitionId
  kwargs = {
    'userHasStateId': userHasStateId,
    'userData': userData,
    'transitionId': transitionId
  }

  delay = (sendDatetime - datetime.now()).total_seconds()
  systemEventScheduler.enterEvent(eventId, delay, priority, action, kwargs)

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
    self.schedulerEventIds = []

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
  #   delay in seconds
  #   action function that takes arguments kwargs
  #   dictionary arguments kwargs
  #   priority with default value 1
  def enterEvent(self, eventId, delay, priority, action, kwargs):
    self.schedulerEventIds.append(eventId);
    self.scheduler.enter(delay, priority, action, kwargs=kwargs)
    
  # prints event id list and (time, priority, action, argument, kwargs) of each queue object
  def printEvents(self):
    print(self.schedulerEventIds)
    print(self.scheduler.queue)