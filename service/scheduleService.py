from datetime import datetime, timedelta
import threading

import service.solicitationService
import service.transitionService

from utils.dbUtils import *
import utils.eventScheduler

def scheduleTransitions(userHasStateId, stateTransitions, transactionMode, dbObjectIns):

  for transition in stateTransitions:
    if transition["type"] == "scheduled":

      sendDatetime = (datetime.now() + timedelta(seconds=transition["transition_delay_seconds"]))
      sendDatetimeFormated = sendDatetime.strftime("%Y-%m-%d %H:%M:%S")

      # insert scheduling
      dbExecute(
        " INSERT INTO scheduling "
        " (scheduled_action, scheduled_datetime) VALUES "
        "   (%s, %s); ",
        ["Solicitation State Transition", sendDatetimeFormated], transactionMode, dbObjectIns)

      # select added scheduling id
      scheduledId = dbGetSingle("SELECT LAST_INSERT_ID() AS id;", (), transactionMode, dbObjectIns)['id']
      
      # insert transition to schedule table
      dbExecute(
        " INSERT INTO scheduling_state_transition "
        " (scheduling_id, state_transition_scheduled_id, user_has_solicitation_state_id) VALUES "
        "   (%s, %s, %s); ",
        [scheduledId, transition["id"], userHasStateId], transactionMode, dbObjectIns)

      # insert to system schedule
      utils.eventScheduler.addTransitionToEventScheduler(scheduledId, sendDatetime, userHasStateId, transition["id"], resolveScheduledSolicitation)

      print(f"# Added transition {transition['id']} to event Scheduler!")

def resolveScheduledSolicitation(eventId, userHasStateId, transitionId):

  # gets solicitation state(sstate) data
  solStateData, error = service.solicitationService.getSolStateDataByUserStateId(userHasStateId)
  if error or not solStateData:
    print(f"# EventScheduler thread {threading.get_ident()}: Error: Usuario não possui o estado da solicitação!", 401)
    return
  
  # parses sstate data to student and advisor data format
  studentData, advisorData = service.solicitationService.createProfileDataBySolStateData(solStateData)

  # Verify solicitation args correcteness
  print(f"# EventScheduler thread {threading.get_ident()}: Validating data")
  
  errorMsg = service.solicitationService.getSolStateChangeInvalidMsg(solStateData)
  if errorMsg != None:
    print(f"# EventScheduler thread {threading.get_ident()}: Error: {errorMsg}", 401)
    return
  
  # gets sstate transitions and validade
  transitions = service.transitionService.getTransitions(solStateData["solicitation_state_id"])

  if not transitions or len(transitions) == 0:
    print(f"# EventScheduler thread {threading.get_ident()}: Solicitação inválida!", 401)
    return

  transition = None
  for ts in transitions:
    if ts["id"] == transitionId:
      transition = ts
      break
  
  if transition == None:
    print(f"# EventScheduler thread {threading.get_ident()}: Transição não encontrada para este estado!", 404)
    return

  # gets next sstate data
  nextSolStateData, error = service.solicitationService.getTransitionSolStateData(transitionId)
  if error or not solStateData:
    print(f"# EventScheduler thread {threading.get_ident()}: Erro ou transição não encontrada para este estado!", 404)
    return
  
  # get parsed solicitation user data
  parsedSolicitationUserData = service.solicitationService.getParsedSolicitationUserData(solStateData, None)

  # resolve solicitation change
  print("# Updating and Inserting data in db for state change")

  dbObjectIns = dbStartTransactionObj()
  try:
    response, status = service.solicitationService.resolveSolStateChange(
      solStateData, transition, nextSolStateData, parsedSolicitationUserData, studentData, advisorData, dbObjectIns
    )

    if status != 200:
      raise Exception(response)
    else:
      dbExecute(
        " UPDATE scheduling SET "
        "   scheduled_status = %s "
        "   WHERE id = %s ",
        ["Sended", eventId], True, dbObjectIns)

      dbCommit(dbObjectIns)
      print(f"# EventScheduler thread {threading.get_ident()}: Done without errors")

  except Exception as e:
    dbRollback(dbObjectIns)
    print(f"# EventScheduler thread {threading.get_ident()}: # Scheduled solicitation resolve error: {e}")
    print(e)
    traceback.print_exc()

def removeScheduledSolicitation(userHasStateId, transactionMode, dbObjectIns):

  schQuery = """
    SELECT sch.id AS id, sch.scheduled_action, sch.scheduled_datetime, sch.scheduled_status, 
    scht.state_transition_scheduled_id, scht.user_has_solicitation_state_id  
      FROM sisgesteste.scheduling sch 
      JOIN scheduling_state_transition scht ON sch.id = scht.scheduling_id
      WHERE user_has_solicitation_state_id = %s;
    """
  schs = dbGetAll(schQuery,(userHasStateId,), transactionMode, dbObjectIns)

  for sch in schs:
    service.solicitationService.removeEventFromScheduler(sch['id'])
    dbExecute(
      " UPDATE scheduling SET "
      "   scheduled_status = %s "
      "   WHERE id = %s; ",
      ["Canceled", sch['id']],  transactionMode, dbObjectIns)