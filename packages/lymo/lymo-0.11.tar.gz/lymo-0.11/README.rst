====
Lymo
====

Python HTTP micro-framework for AWS Lambda.

Lymo provides a Flask/Django-inspired API for building serverless web applications on AWS Lambda with minimal boilerplate. It handles routing, request/response abstraction, templating, and includes an optional Django-style ORM for PostgreSQL.

------------
Installation
------------

Basic installation:

.. code-block:: bash

    pip install lymo

With optional dependencies:

.. code-block:: bash

    # For Jinja2 templating support
    pip install lymo[templates]

    # For PostgreSQL database support
    pip install lymo[db]

    # For development
    pip install lymo[dev]

    # All extras
    pip install lymo[templates,db,dev]

------------
Requirements
------------

* Python 3.10 or higher
* AWS Lambda environment with API Gateway v1 events
* Optional: PostgreSQL (for database features)
* Optional: Jinja2 (for templating)

-----------
Quick Start
-----------

Basic Lambda Handler
====================

.. code-block:: python

    from lymo import App
    from lymo.http_handler import http_handler
    import routes  # Your routes package

    app = App(routes=routes)

    def lambda_handler(event, context):
        return http_handler(event, context, app)

Defining Routes
===============

Create a ``routes`` package with modules containing route handlers:

.. code-block:: python

    # routes/users.py
    from lymo.router import route
    from lymo.http_responses import JsonResponse

    @route("/users/{user_id}", "GET")
    def get_user(request):
        user_id = request.path_params["user_id"]
        return JsonResponse(
            request=request,
            data={"user_id": user_id, "name": "John Doe"}
        )

    @route("/users/", "POST")
    def create_user(request):
        # Access request body
        data = request.body
        return JsonResponse(
            request=request,
            data={"message": "User created"},
            status_code=201
        )

Edge Caching
============

Add cache-control headers for GET requests:

.. code-block:: python

    from lymo.router import route
    from lymo.http_responses import JsonResponse

    @route("/quotes/", "GET", cache_ttl=300)  # 5 minute cache
    def get_quotes(request):
        return JsonResponse(request=request, data={"quotes": []})

Note: ``cache_ttl`` only applies to safe methods (GET, HEAD, OPTIONS) and is ignored for state changing operations (POST, PUT, PATCH, DELETE).

-------------
Core Concepts
-------------

Application Object
==================

The ``App`` class is the central configuration object:

.. code-block:: python

    from lymo import App

    app = App(
        routes=routes,                    # Required: routes package
        template_dir="templates",         # Optional: Jinja2 template directory
        template_globals={"site": "My"},  # Optional: global template variables
        template_extensions=[],           # Optional: Jinja2 extensions
        resources={"db": db_conn},        # Optional: shared resources (DB, etc.)
        logger=logger                     # Optional: Python logger
    )

Request Object
==============

The ``HttpRequest`` object provides access to Lambda event data:

* ``request.method`` - HTTP method (GET, POST, etc.)
* ``request.path`` - Request path
* ``request.headers`` - Request headers dict
* ``request.queryparams`` - Query string parameters dict
* ``request.body`` - Request body
* ``request.path_params`` - URL path parameters from route pattern
* ``request.template_env`` - Jinja2 environment (if configured)
* ``request.resources`` - Shared resources dict from App

Response Types
==============

HttpResponse
------------

Plain text or HTML response:

.. code-block:: python

    from lymo.http_responses import HttpResponse

    return HttpResponse(
        request=request,
        body="<h1>Hello World</h1>",
        status_code=200,
        headers={"Custom-Header": "value"}
    )

JsonResponse
------------

Automatic JSON serialization with support for datetime, UUID, Decimal, and Pydantic models:

.. code-block:: python

    from lymo.http_responses import JsonResponse

    return JsonResponse(
        request=request,
        data={"message": "Success", "timestamp": datetime.now()},
        status_code=200
    )

TemplateResponse
----------------

Render Jinja2 templates:

.. code-block:: python

    from lymo.http_responses import TemplateResponse

    return TemplateResponse(
        request=request,
        template="users/detail.html",
        context={"user": user},
        status_code=200
    )

The ``request`` object is automatically added to the template context.

Routing
=======

Routes are defined using the ``@route`` decorator and automatically discovered when the app initializes.

Path Parameters
---------------

Extract parameters from URLs using ``{param}`` syntax:

.. code-block:: python

    @route("/posts/{post_id}/comments/{comment_id}", "GET")
    def get_comment(request):
        post_id = request.path_params["post_id"]
        comment_id = request.path_params["comment_id"]
        return JsonResponse(request=request, data={...})

Route Organization
------------------

Organize routes in a package structure:

.. code-block:: text

    routes/
        __init__.py
        users.py
        posts.py
        comments.py

All modules in the routes package are automatically imported and their ``@route`` decorators registered.

-----------------
Database Features
-----------------

Lymo includes an optional Django-style ORM for PostgreSQL using Pydantic and psycopg.

Model Definition
================

.. code-block:: python

    from lymo.db import Model
    from datetime import datetime

    class User(Model):
        id: int
        email: str
        name: str
        created_at: datetime
        updated_at: datetime

Table names are automatically derived from the class name (``User`` → ``user``, ``BlogPost`` → ``blog_post``).

Database Connection
===================

Pass database connections explicitly using ``.using(conn)``:

.. code-block:: python

    import psycopg

    # In your Lambda handler setup
    conn = psycopg.connect("postgresql://...")

    app = App(
        routes=routes,
        resources={"db": conn}
    )

    # In your route handler
    @route("/users/{user_id}", "GET")
    def get_user(request):
        db = request.resources["db"]
        user = User.objects.using(db).find(id=user_id).get()
        return JsonResponse(request=request, data=user.model_dump())

AWS DSQL Support
================

Lymo includes built-in support for AWS DSQL (Aurora DSQL) connections with IAM authentication:

.. code-block:: python

    from lymo.dsql import create_dsql_connection

    # Create DSQL connection with IAM auth
    conn = create_dsql_connection(
        cluster_identifier="my-cluster",
        region="us-east-1",
        cluster_user="admin",  # Optional, defaults to "admin"
        schema="public",       # Optional, defaults to "public"
        expires_in=3600        # Optional, token TTL in seconds
    )

    app = App(
        routes=routes,
        resources={"db": conn}
    )

The DSQL connection helper:

* Automatically generates IAM authentication tokens via boto3
* Configures SSL/TLS with the correct settings for DSQL
* Sets the PostgreSQL search_path to your specified schema
* Supports psycopg 3.x with optimized SSL negotiation for newer versions

**Note:** The connection token expires after ``expires_in`` seconds (default: 3600). For long-running Lambda containers, consider implementing connection refresh logic or using shorter expiration times.

Query API
=========

Basic Queries
-------------

.. code-block:: python

    # Get all records
    users = User.objects.using(conn).list()

    # Get single record (raises ValueError if not found or multiple found)
    user = User.objects.using(conn).find(id=123).get()

    # Count records
    count = User.objects.using(conn).count()

Filtering
---------

.. code-block:: python

    # Equality filters
    active_users = User.objects.using(conn).find(status="active").list()

    # Multiple filters (AND)
    users = User.objects.using(conn).find(status="active", verified=True).list()

Chainable Methods
-----------------

.. code-block:: python

    # Order by
    users = (
        User.objects.using(conn)
        .find(status="active")
        .order_by("created_at", "DESC")
        .list()
    )

    # Limit and offset
    users = User.objects.using(conn).limit(10, offset=20).list()

    # Pagination
    users = User.objects.using(conn).paginate(page=2, per_page=50).list()

Date Filtering
--------------

.. code-block:: python

    from datetime import datetime, date

    # Inclusive range (BETWEEN)
    users = User.objects.using(conn).date_range(
        "created_at",
        date_from=datetime(2024, 1, 1),
        date_to=datetime(2024, 12, 31)
    ).list()

    # Exclusive range (>= AND <)
    users = User.objects.using(conn).date_between(
        "created_at",
        date_from=datetime(2024, 1, 1),
        date_to=datetime(2024, 1, 31)
    ).list()

    # Exact date match
    today_users = User.objects.using(conn).date("created_at", date.today()).list()

Generic Range Filtering
-----------------------

.. code-block:: python

    # Works with any type (numeric, string, UUID, etc.)
    users = User.objects.using(conn).between("age", 18, 65).list()

JSON Output
-----------

.. code-block:: python

    # Return JSON strings instead of model instances
    users_json = User.objects.using(conn).find(status="active").list(json=True)
    user_json = User.objects.using(conn).find(id=123).get(json=True)

Async Support
-------------

All query methods have async equivalents:

.. code-block:: python

    import psycopg

    async with await psycopg.AsyncConnection.connect("postgresql://...") as conn:
        users = await User.objects.using(conn).alist()
        user = await User.objects.using(conn).find(id=123).aget()
        count = await User.objects.using(conn).acount()

----------
Templating
----------

When ``template_dir`` is provided, Lymo configures Jinja2 with:

* Auto-escaping for HTML/XML
* Custom filters: ``urlencode``, ``base64``
* Optional custom globals and extensions

Example:

.. code-block:: python

    app = App(
        routes=routes,
        template_dir="templates",
        template_globals={"site_name": "My Site"},
        template_extensions=["jinja2.ext.do"]
    )

In templates:

.. code-block:: html

    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ site_name }}</title>
    </head>
    <body>
        <h1>{{ user.name }}</h1>
        <a href="/profile?user={{ user.id|urlencode }}">Profile</a>
        <img src="data:image/png;base64,{{ image_data|base64 }}">
    </body>
    </html>

------------
Architecture
------------

Request Flow
============

1. **AWS Lambda** receives API Gateway v1 event
2. **http_handler()** creates HttpRequest wrapper
3. **Router** matches path and HTTP method to handler via regex
4. **Route handler** executes with request object
5. **Response object** (HttpResponse/JsonResponse/TemplateResponse) is returned
6. Lambda returns response dict to API Gateway

Path Processing
===============

API Gateway base paths are automatically stripped:

* Resource: ``/api/{proxy+}``
* Path: ``/api/users/123``
* Processed: ``/users/123``

Error Handling
==============

Uncaught exceptions return 500 responses with error details and traceback (if logger is configured, errors are logged).

Data Serialization
==================

The custom JSON serializer handles:

* ``datetime`` and ``date`` → ISO format strings
* ``uuid.UUID`` → string representation
* ``Decimal`` → float
* Pydantic models → ``model_dump()`` output
* Other objects → ``str()`` representation

-----------
Development
-----------

Setup
=====

.. code-block:: bash

    # Clone repository
    git clone https://github.com/newadventures/lymo.git
    cd lymo

    # Create virtual environment
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate

    # Install with dev dependencies
    pip install -e ".[dev,db,templates]"

Linting
=======

.. code-block:: bash

    ruff check src/ tests/

Building
========

.. code-block:: bash

    # Build distribution
    python -m build

    # Check package
    twine check dist/*

-------
License
-------

See LICENSE file for details.

-------
Authors
-------

* New Adventures In Coding - mail@neiladventures.dev

-----
Links
-----

* GitHub: https://github.com/newadventures/lymo
* PyPI: https://pypi.org/project/lymo/
