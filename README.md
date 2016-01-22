# gofed - next generation

Golang analysis system

## System Overview
Gofed next generation (gofed-ng) is a system based on original gofed tool. It
tends to utilize original approach and extend it with distributed computation
and data storage. The whole system consists of 3 main components - a service
registry, a client and services.

### Services

The concept of gofed-ng is based on services, which are provided for clients.
These services can run remotely and locally as well, based on user
configuration.  Running analysis remotely allows a user to use up-to-date
analysis and use the power of the system in order to get the most accurate
results. Local execution acts like local function call, so it does not affect
performance anyhow (network communication overhead is bypassed).

A service is semantically uniquely identified by its name, but its name does
not necessarily restricts system to have only one service of a type. There can
be multiple services with the same name (implementing same actions). This
scenario is suitable for load balancing.

A service provides actions for a client, which can be done. Each action has
predefined input and output. It's implementation is hidden for the client.

Actions are encapsulated with a service envelope. The service envelop is
responsible for service execution, configuration loading and communication;
moreover it is shared across all services, so one code rules them all!

### Registry

Each service can register to a registry. The registry is the main point of
contact if a client wants to use a service, but does not know its location (IP,
port). The registry holds information about connection information (IP, port),
service name for all active services (it is responsible for dead service
detection as well).

### Client

A client is able to connect to the system and use its resources. If the client
does not know service location, it queries registry to get list of all services
with a name.

The main concept of the client is hidden in scenarios. A client implements
scenarios, which describe data flow across actions. Client can modify, specify
or adopt actions output in scenarios.

The client can be configured to use specific actions remotely or locally, as
desired.

## Data Flow Overview

The system provides analysis (code) and data as well. We can look at database as
a service we provide besides analysis, so databases are services too. Databases
implement API which is shared across the whole system, so service or even client
can access data by its API implemented in database driver.

A client has a power to specify which data will be used in which action. The
client can use precomputed data stored in database services, or can pass it's
own data, which will be accessible to service via database API.

If a client does not provide database driver, called service uses system in
order to get data needed to perform specific action.

## Requirements

Execution
```
python, pyhon-plumbum, python-rpyc
```

For development, install following packages as well:
```
python-jinja2, python-ast
```

## Setup

To run the service registry, use following command in the root of git tree:
```
$ ./registry
Starting registry on port 18811...
DEBUG:REGSRV/UDP/18811:server started on 0.0.0.0:18811
```
You can configure registry in registry.conf. For all supported options, see:
```
git/$ ./registry --help

```

To run a service, enter services directory and prepare services to be run
(add service envelope and configuration for each service):
```
git/services/$ ./bootstrap.py
...
```
Now you are ready to run a service:
```
git/services/$ ./service1/service1Service.py --config ./service1/service1Service.conf
INFO:SERVICE1/18236:server started on [127.0.0.1]:18236
INFO:SERVICE1/18236:started background auto-register thread (interval = 60)
INFO:REGCLNT/UDP:registering on localhost:18811
INFO:REGCLNT/UDP:registry 127.0.0.1:18811 acknowledged

```
You can adopt configuration file to your needs. To see all available options,
run service with --help option.

