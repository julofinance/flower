import time
import logging
import datetime
import collections

from tornado import web
from tornado import gen
from tornado import util

from ..views import BaseHandler


logger = logging.getLogger(__name__)


class ControlHandler(BaseHandler):
    def is_worker(self, workername):
        return workername and workername in self.application.workers

    def error_reason(self, workername, response):
        "extracts error message from response"
        for r in response:
            try:
                return r[workername].get('error', 'Unknown reason')
            except KeyError:
                pass
        logger.error("Failed to extract error reason from '%s'", response)
        return 'Unknown reason'


class WorkerShutDown(ControlHandler):
    @web.authenticated
    def post(self, workername):
        """
Shut down a worker

**Example request**:

.. sourcecode:: http

  POST /api/worker/shutdown/celery@worker2 HTTP/1.1
  Content-Length: 0
  Host: localhost:5555

**Example response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Length: 29
  Content-Type: application/json; charset=UTF-8

  {
      "message": "Shutting down!"
  }

:reqheader Authorization: optional OAuth token to authenticate
:statuscode 200: no error
:statuscode 401: unauthorized request
:statuscode 404: unknown worker
        """
        if not self.is_worker(workername):
            raise web.HTTPError(404, "Unknown worker '%s'" % workername)

        self.set_status(403)
        self.write(dict(message="You do not have permission!!!"))


class WorkerPoolRestart(ControlHandler):
    @web.authenticated
    def post(self, workername):
        """
Restart worker's pool

**Example request**:

.. sourcecode:: http

  POST /api/worker/pool/restart/celery@worker2 HTTP/1.1
  Content-Length: 0
  Host: localhost:5555

**Example response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Length: 56
  Content-Type: application/json; charset=UTF-8

  {
      "message": "Restarting 'celery@worker2' worker's pool"
  }

:reqheader Authorization: optional OAuth token to authenticate
:statuscode 200: no error
:statuscode 401: unauthorized request
:statuscode 403: pool restart is not enabled (see CELERYD_POOL_RESTARTS)
:statuscode 404: unknown worker
        """
        if not self.is_worker(workername):
            raise web.HTTPError(404, "Unknown worker '%s'" % workername)

        self.set_status(403)
        self.write(dict(message="You do not have permission!!!"))


class WorkerPoolGrow(ControlHandler):
    @web.authenticated
    def post(self, workername):
        """
Grow worker's pool

**Example request**:

.. sourcecode:: http

  POST /api/worker/pool/grow/celery@worker2?n=3 HTTP/1.1
  Content-Length: 0
  Host: localhost:5555

**Example response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Length: 58
  Content-Type: application/json; charset=UTF-8

  {
      "message": "Growing 'celery@worker2' worker's pool by 3"
  }

:query n: number of pool processes to grow, default is 1
:reqheader Authorization: optional OAuth token to authenticate
:statuscode 200: no error
:statuscode 401: unauthorized request
:statuscode 403: failed to grow
:statuscode 404: unknown worker
        """

        if not self.is_worker(workername):
            raise web.HTTPError(404, "Unknown worker '%s'" % workername)

        self.set_status(403)
        self.write("You do not have permission!!!")


class WorkerPoolShrink(ControlHandler):
    @web.authenticated
    def post(self, workername):
        """
Shrink worker's pool

**Example request**:

.. sourcecode:: http

  POST /api/worker/pool/shrink/celery@worker2 HTTP/1.1
  Content-Length: 0
  Host: localhost:5555

**Example response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Length: 60
  Content-Type: application/json; charset=UTF-8

  {
      "message": "Shrinking 'celery@worker2' worker's pool by 1"
  }

:query n: number of pool processes to shrink, default is 1
:reqheader Authorization: optional OAuth token to authenticate
:statuscode 200: no error
:statuscode 401: unauthorized request
:statuscode 403: failed to shrink
:statuscode 404: unknown worker
        """

        if not self.is_worker(workername):
            raise web.HTTPError(404, "Unknown worker '%s'" % workername)

        self.set_status(403)
        self.write("You do not have permission!!!")


class WorkerPoolAutoscale(ControlHandler):
    @web.authenticated
    def post(self, workername):
        """
Autoscale worker pool

**Example request**:

.. sourcecode:: http

  POST /api/worker/pool/autoscale/celery@worker2?min=3&max=10 HTTP/1.1
  Content-Length: 0
  Content-Type: application/x-www-form-urlencoded; charset=utf-8
  Host: localhost:5555

**Example response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Length: 66
  Content-Type: application/json; charset=UTF-8

  {
      "message": "Autoscaling 'celery@worker2' worker (min=3, max=10)"
  }

:query min: minimum number of pool processes
:query max: maximum number of pool processes
:reqheader Authorization: optional OAuth token to authenticate
:statuscode 200: no error
:statuscode 401: unauthorized request
:statuscode 403: autoscaling is not enabled (see CELERYD_AUTOSCALER)
:statuscode 404: unknown worker
        """

        if not self.is_worker(workername):
            raise web.HTTPError(404, "Unknown worker '%s'" % workername)

        self.set_status(403)
        self.write("You do not have permission!!!")


class WorkerQueueAddConsumer(ControlHandler):
    @web.authenticated
    def post(self, workername):
        """
Start consuming from a queue

**Example request**:

.. sourcecode:: http

  POST /api/worker/queue/add-consumer/celery@worker2?queue=sample-queue
  Content-Length: 0
  Content-Type: application/x-www-form-urlencoded; charset=utf-8
  Host: localhost:5555

**Example response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Length: 40
  Content-Type: application/json; charset=UTF-8

  {
      "message": "add consumer sample-queue"
  }

:query queue: the name of a new queue
:reqheader Authorization: optional OAuth token to authenticate
:statuscode 200: no error
:statuscode 401: unauthorized request
:statuscode 403: failed to add consumer
:statuscode 404: unknown worker
        """
        if not self.is_worker(workername):
            raise web.HTTPError(404, "Unknown worker '%s'" % workername)

        self.set_status(403)
        self.write("You do not have permission!!!")


class WorkerQueueCancelConsumer(ControlHandler):
    @web.authenticated
    def post(self, workername):
        """
Stop consuming from a queue

**Example request**:

.. sourcecode:: http

  POST /api/worker/queue/cancel-consumer/celery@worker2?queue=sample-queue
  Content-Length: 0
  Content-Type: application/x-www-form-urlencoded; charset=utf-8
  Host: localhost:5555

**Example response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Length: 52
  Content-Type: application/json; charset=UTF-8

  {
      "message": "no longer consuming from sample-queue"
  }

:query queue: the name of queue
:reqheader Authorization: optional OAuth token to authenticate
:statuscode 200: no error
:statuscode 401: unauthorized request
:statuscode 403: failed to cancel consumer
:statuscode 404: unknown worker
        """
        if not self.is_worker(workername):
            raise web.HTTPError(404, "Unknown worker '%s'" % workername)

        self.set_status(403)
        self.write("You do not have permission!!!")


class TaskRevoke(ControlHandler):
    @web.authenticated
    def post(self, taskid):
        """
Revoke a task

**Example request**:

.. sourcecode:: http

  POST /api/task/revoke/1480b55c-b8b2-462c-985e-24af3e9158f9?terminate=true
  Content-Length: 0
  Content-Type: application/x-www-form-urlencoded; charset=utf-8
  Host: localhost:5555

**Example response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Length: 61
  Content-Type: application/json; charset=UTF-8

  {
      "message": "Revoked '1480b55c-b8b2-462c-985e-24af3e9158f9'"
  }

:query terminate: terminate the task if it is running
:query signal: name of signal to send to process if terminate (default: 'SIGTERM')
:reqheader Authorization: optional OAuth token to authenticate
:statuscode 200: no error
:statuscode 401: unauthorized request
        """
        self.set_status(403)
        self.write("You do not have permission!!!")


class TaskTimout(ControlHandler):
    @web.authenticated
    def post(self, taskname):
        """
Change soft and hard time limits for a task

**Example request**:

.. sourcecode:: http

    POST /api/task/timeout/tasks.sleep HTTP/1.1
    Content-Length: 44
    Content-Type: application/x-www-form-urlencoded; charset=utf-8
    Host: localhost:5555

    soft=30&hard=100&workername=celery%40worker1

**Example response**:

.. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Length: 46
    Content-Type: application/json; charset=UTF-8

    {
        "message": "time limits set successfully"
    }

:query workername: worker name
:reqheader Authorization: optional OAuth token to authenticate
:statuscode 200: no error
:statuscode 401: unauthorized request
:statuscode 404: unknown task/worker
        """
        workername = self.get_argument('workername')
        hard = self.get_argument('hard', default=None, type=float)
        soft = self.get_argument('soft', default=None, type=float)

        self.set_status(403)
        self.write("You do not have permission!!!")


class TaskRateLimit(ControlHandler):
    @web.authenticated
    def post(self, taskname):
        """
Change rate limit for a task

**Example request**:

.. sourcecode:: http

    POST /api/task/rate-limit/tasks.sleep HTTP/1.1
    Content-Length: 41
    Content-Type: application/x-www-form-urlencoded; charset=utf-8
    Host: localhost:5555

    ratelimit=200&workername=celery%40worker1

**Example response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Length: 61
  Content-Type: application/json; charset=UTF-8

  {
      "message": "new rate limit set successfully"
  }

:query workername: worker name
:reqheader Authorization: optional OAuth token to authenticate
:statuscode 200: no error
:statuscode 401: unauthorized request
:statuscode 404: unknown task/worker
        """
        workername = self.get_argument('workername')
        ratelimit = self.get_argument('ratelimit')

        self.set_status(403)
        self.write("You do not have permission!!!")
