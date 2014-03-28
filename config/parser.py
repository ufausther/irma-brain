import os
from kombu import Queue
from lib.irma.configuration.ini import TemplatedConfiguration

# ______________________________________________________________________________ TEMPLATE

template_brain_config = {
                         'broker_brain': [
                                    ('host', TemplatedConfiguration.string, None),
                                    ('port', TemplatedConfiguration.integer, 5672),
                                    ('vhost', TemplatedConfiguration.string, None),
                                    ('username', TemplatedConfiguration.string, None),
                                    ('password' , TemplatedConfiguration.string, None),
                                    ('queue' , TemplatedConfiguration.string, None)
                                    ],
                         'broker_probe': [
                                    ('host', TemplatedConfiguration.string, None),
                                    ('port', TemplatedConfiguration.integer, 5672),
                                    ('vhost', TemplatedConfiguration.string, None),
                                    ('username', TemplatedConfiguration.string, None),
                                    ('password' , TemplatedConfiguration.string, None),
                                    ('queue' , TemplatedConfiguration.string, None)
                                    ],
                         'broker_frontend': [
                                    ('host', TemplatedConfiguration.string, None),
                                    ('port', TemplatedConfiguration.integer, 5672),
                                    ('vhost', TemplatedConfiguration.string, None),
                                    ('username', TemplatedConfiguration.string, None),
                                    ('password' , TemplatedConfiguration.string, None),
                                    ('queue' , TemplatedConfiguration.string, None)
                                    ],
                         'backend_brain': [
                                   ('host', TemplatedConfiguration.string, None),
                                   ('port', TemplatedConfiguration.integer, 6379),
                                   ('db', TemplatedConfiguration.integer, None),
                                   ],
                         'backend_probe': [
                                   ('host', TemplatedConfiguration.string, None),
                                   ('port', TemplatedConfiguration.integer, 6379),
                                   ('db', TemplatedConfiguration.integer, None),
                                   ],
                         'sql_brain': [
                                   ('engine', TemplatedConfiguration.string, None),
                                   ('dbname', TemplatedConfiguration.string, None),
                                   ],
                         'ftp_brain': [
                                    ('host', TemplatedConfiguration.string, None),
                                    ('port', TemplatedConfiguration.integer, 21),
                                    ('username', TemplatedConfiguration.string, None),
                                    ('password' , TemplatedConfiguration.string, None),
                                    ]
                         }

cfg_file = "{0}/{1}".format(os.path.abspath(os.path.dirname(__file__)), "brain.ini")
brain_config = TemplatedConfiguration(cfg_file, template_brain_config)

# ______________________________________________________________________________ CELERY HELPERS

def _conf_celery(app, broker, backend=None, queue=None):
    app.conf.update(
                     BROKER_URL=broker,
                     CELERY_RESULT_BACKEND=backend,
                     CELERY_ACCEPT_CONTENT=['json'],
                     CELERY_TASK_SERIALIZER='json',
                     CELERY_RESULT_SERIALIZER='json'
                     )
    if backend is not None:
        app.conf.update(CELERY_RESULT_BACKEND=backend)
    if queue is not None:
        app.conf.update(
                        CELERY_DEFAULT_QUEUE=queue,
                        # delivery_mode=1 enable transient mode (don't survive to a server restart)
                        CELERY_QUEUES=(
                                       Queue(queue, routing_key=queue),
                                       )
                        )
    return

def conf_brain_celery(app):
    broker = get_brain_broker_uri()
    backend = get_brain_backend_uri()
    queue = brain_config.broker_brain.queue
    _conf_celery(app, broker, backend=backend, queue=queue)

def conf_probe_celery(app):
    broker = get_probe_broker_uri()
    backend = get_probe_backend_uri()
    _conf_celery(app, broker, backend=backend)

def conf_frontend_celery(app):
    broker = get_frontend_broker_uri()
    queue = brain_config.broker_frontend.queue
    _conf_celery(app, broker, queue=queue)

def conf_results_celery(app):
    broker = get_probe_broker_uri()
    queue = brain_config.broker_probe.queue
    _conf_celery(app, broker, queue=queue)
# ______________________________________________________________________________ BACKEND HELPERS

def _get_backend_uri(backend_config):
    return "redis://%s:%s/%s" % (backend_config.host, backend_config.port, backend_config.db)

def get_brain_backend_uri():
    return _get_backend_uri(brain_config.backend_brain)

def get_probe_backend_uri():
    return _get_backend_uri(brain_config.backend_probe)
# ______________________________________________________________________________ BROKER HELPERS

def _get_broker_uri(broker_config):
    return  "amqp://%s:%s@%s:%s/%s" % (broker_config.username, broker_config.password, broker_config.host, broker_config.port, broker_config.vhost)

def get_brain_broker_uri():
    return _get_broker_uri(brain_config.broker_brain)

def get_probe_broker_uri():
    return _get_broker_uri(brain_config.broker_probe)

def get_frontend_broker_uri():
    return _get_broker_uri(brain_config.broker_frontend)