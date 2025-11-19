# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import os
import logging
import argparse
import uuid
from time import gmtime, strftime
from packaging import version
from cegalprizm.hub import HubConnector
from . import __version__, logger, constants, globals
from .task_registry import get_task_registry
from .workflow_library import initialise_workflow_library

parser = argparse.ArgumentParser()
parser.add_argument('--name', help='Name to be assigned to the pycoderunner environment', required=True, default='python')
parser.add_argument('--libdir', help='Path to directories in which available workflows are described. Use ";" to separate multiple paths', required=False)
parser.add_argument('--workdir', help='Path to working directory to be used when running workflows', required=False)
parser.add_argument('--logdir', help='Path to directory in which to write the logfile', required=False)
parser.add_argument('--loglevel', help='Level of logging [debug, info, warning, error]', required=False, default='warning')
parser.add_argument('--join-token', help='Join token to be used when connecting to Cegal Hub', required=False)
parser.add_argument('--auth', help='Use authentication', required=False)
parser.add_argument('--port', help='Port to use when connecting to Cegal Hub', required=False)
parser.add_argument('--host', help='Host to use when connecting to Cegal Hub', required=False)
parser.add_argument('--tls', help='Use TLS when connecting to Cegal Hub', required=False)

args = parser.parse_args()

# These environmental variables will be handled in this module.
if args.join_token is not None:
    os.environ["CEGAL_HUB_CONNECTOR_JOIN_TOKEN"] = args.join_token

# These environmental variables will be handled by the cegalprizm.hub module.
if args.auth is not None:
    os.environ["CEGAL_HUB_USE_AUTH"] = args.auth
if args.port is not None:
    os.environ["CEGAL_HUB_PORT"] = args.port
if args.host is not None:
    os.environ["CEGAL_HUB_HOST"] = args.host
if args.tls is not None:
    os.environ["CEGAL_HUB_USE_TLS"] = args.tls

pycoderunner_uuid = uuid.uuid4()

if args.loglevel.startswith('debug'):
    level = logging.DEBUG
elif args.loglevel.startswith('warning'):
    level = logging.WARNING
elif args.loglevel.startswith('error'):
    level = logging.ERROR
else:
    level = logging.INFO

if args.logdir is None:
    if os.name == 'nt':
        logdir = os.path.join(os.getenv("LOCALAPPDATA"), "Cegal", "Hub", "log")
        if not os.path.isdir(logdir):
            os.makedirs(logdir)
    elif os.name == 'posix':
        logdir = os.path.join(os.getenv("HOME"), "Cegal", "Hub", "log")
        if not os.path.isdir(logdir):
            os.makedirs(logdir)
    else:
        raise Exception("You must supply a logdir argument when running on this OS") 
else:
    logdir = args.logdir

if not os.path.isdir(logdir):
    print("Error: Specified logdir does not exist")
    exit(0)

filename = f"pycoderunner_{strftime('%Y-%m-%d_%H-%M-%S', gmtime())}_{pycoderunner_uuid}.log"

logging.basicConfig(
    handlers=[logging.FileHandler(filename=os.path.join(logdir, filename), encoding='utf-8', mode='a+')],
    format='%(asctime)s [%(levelname)-8s] %(message)s',
    level=level,
    datefmt='%Y-%m-%d %H:%M:%S')

token_provider = None
join_token = ""
supports_public_requests = True

try:
    join_token = os.environ["CEGAL_HUB_CONNECTOR_JOIN_TOKEN"]
    supports_public_requests = True
except Exception:
    join_token = ""

default_num_of_concurrent_tasks = constants.DEFAULT_NUM_OF_CONCURRENT_TASKS

try:
    num_of_concurrent_tasks = int(os.getenv("CEGAL_PWR_CONCURRENT_TASKS", default_num_of_concurrent_tasks))
except Exception:
    num_of_concurrent_tasks = default_num_of_concurrent_tasks

if num_of_concurrent_tasks != default_num_of_concurrent_tasks:
    globals.set_num_of_concurrent_tasks(num_of_concurrent_tasks)

pwr_connector_label = ""

try:
    pwr_connector_label = os.environ["CEGAL_PWR_CONNECTOR_LABEL"]
except Exception:
    pwr_connector_label = ""

try:
    ver = version.parse(__version__)
    ver.major
except Exception:
    logger.info("cannot parse major version, you are probably running a development version")
    ver = version.parse("0.0.1")

logging.getLogger("cegalprizm.keystone_auth").setLevel(logging.INFO)
logging.getLogger("cegalprizm.hub").setLevel(logging.INFO)

logger.info(f"Starting Pycoderunner {str(ver)}")
logger.info(f"Log level set to     : {logging.getLevelName(level)}")
logger.info(f"Hub join token       : {join_token if join_token else 'None'}")
logger.info(f"Hub connector public : {str(supports_public_requests)}")
logger.info(f"Num concurrent tasks : {num_of_concurrent_tasks}")

if args.libdir is not None:
    try:
        if args.workdir is None:
            raise ValueError("A workdir must be specified when specifying libdir")
        else:
            initialise_workflow_library(args.name, args.libdir.replace("\\", "/"), args.workdir.replace("\\", "/"))
    except Exception as e:
        msg = f"Exception raised when initializing workflow library: {str(e)}"
        logger.error(msg)
        print(f"pycoderunner error: {msg}")
        exit(1)

labels = {
    "pycoderunner-environment": args.name,
    "pycoderunner-uuid": str(pycoderunner_uuid)
}

if len(pwr_connector_label) > 0:
    logger.info(f"Connector label      : {pwr_connector_label}")
    labels["pycoderunner-label"] = pwr_connector_label

connector = HubConnector(wellknown_identifier="cegal.pycoderunner",
                         friendly_name="Cegal Pycoderunner",
                         description="A Cegal provided server allowing python code to be executed remotely using Cegal Hub",
                         version=str(ver),
                         build_version="local",
                         supports_public_requests=supports_public_requests,
                         join_token=join_token,
                         token_provider=token_provider,
                         additional_labels=labels,
                         num_of_concurrent_tasks=num_of_concurrent_tasks)

try:
    connector.start(get_task_registry())
except KeyboardInterrupt:
    logger.info("Keyboard interrupt received, stopping...")
except Exception as e:
    logger.error(f"Exception raised: {str(e)}")
