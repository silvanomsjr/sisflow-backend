import sched, time
from threading import Thread

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
  def enterEvent(self, delay, action, kwargs, priority=1):
    self.scheduler.enter(delay, priority, action, kwargs=kwargs)
    
  # prints (time, priority, action, argument, kwargs) of each queue object 
  def printEventQueue(self):
    print(self.scheduler.queue)

def printTime(parameter=''):
  print("From printTime", time.time(), parameter)

def printMonotomicTime(parameter=''):
  print("From printMonotomicTime", time.monotonic(), parameter)

def test():

  printTime()
  printMonotomicTime()

  eventScheduler = EventScheduler()

  eventScheduler.enterEvent(10, printMonotomicTime, {'parameter': 'parametro 10'})
  eventScheduler.enterEvent(10, printMonotomicTime, {'parameter': 'parametro 10'})

  eventScheduler.enterEvent(-1, printMonotomicTime, {'parameter': 'parametro -1'})
  eventScheduler.enterEvent(0, printMonotomicTime, {'parameter': 'parametro 0'})

  eventScheduler.enterEvent(2, printMonotomicTime, {'parameter': 'parametro 2'})
  eventScheduler.enterEvent(2, printMonotomicTime, {'parameter': 'parametro 2'})

  eventScheduler.enterEvent(5, printMonotomicTime, {'parameter': 'parametro 5 added after start'})
  eventScheduler.enterEvent(15, printMonotomicTime, {'parameter': 'parametro 15 added after start'})

  time.sleep(20)
  
  eventScheduler.enterEvent(1, printMonotomicTime, {'parameter': 'parametro 21'})

  time.sleep(2)

  eventScheduler.stop()