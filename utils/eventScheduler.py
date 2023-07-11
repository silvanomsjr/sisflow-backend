import sched, time
from threading import Thread

systemEventScheduler = None

def startSystemEventScheduler():

  global systemEventScheduler

  if systemEventScheduler == None:
    systemEventScheduler = EventScheduler()

def addToSystemEventScheduler(eventId, delay, action, kwargs=None, priority=1):

  global systemEventScheduler

  if systemEventScheduler == None:
    systemEventScheduler = EventScheduler()

  if kwargs == None:
    kwargs = {}
  kwargs['event_id'] = eventId

  systemEventScheduler.enterEvent(delay, priority, action, kwargs)
  
def stopSystemEventScheduler():

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

    # Start thread to run scheduler and not block main thread, self is shared
    self.finishThread = False
    Thread(target = self.__run).start()

  # Private method used by thread to run scheduler asynchronous
  def __run(self):
    print("# Event Scheduler thread created and running!")
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
  def enterEvent(self, delay, priority, action, kwargs):
    self.scheduler.enter(delay, priority, action, kwargs=kwargs)
    
  # prints (time, priority, action, argument, kwargs) of each queue object 
  def printEventQueue(self):
    print(self.scheduler.queue)

# For testing
def test():

  def printMonotomicTime(event_id=0):
    print("From printMonotomicTime: " + str(time.monotonic()) + ", With Kwargs event_id: " + str(event_id))

  printMonotomicTime()

  startSystemEventScheduler

  addToSystemEventScheduler(0, 10, printMonotomicTime)
  addToSystemEventScheduler(1, 10, printMonotomicTime)

  addToSystemEventScheduler(2, -1, printMonotomicTime)
  addToSystemEventScheduler(3, 0, printMonotomicTime)

  addToSystemEventScheduler(4, 2, printMonotomicTime)
  addToSystemEventScheduler(5, 2, printMonotomicTime)

  addToSystemEventScheduler(6, 5, printMonotomicTime)
  addToSystemEventScheduler(7, 15, printMonotomicTime)

  time.sleep(20)
  
  addToSystemEventScheduler(8, 1, printMonotomicTime)

  time.sleep(2)

  stopSystemEventScheduler()