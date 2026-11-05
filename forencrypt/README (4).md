# ForenCrypt

### Privacy-Preserving Digital Forensic Evidence Management System

ForenCrypt is an academic project exploring how digital forensic
evidence can be managed with integrity verification, tamper-evident
activity records, privacy-preserving numerical processing, and
AI-assisted anomaly detection.

The project combines a Python/FastAPI backend, MySQL, Docker Compose,
SHA-256 hashing, a MySQL-backed hash-chain prototype, bcrypt password
hashing, JWT authentication, and a demonstration anomaly-detection
pipeline using Isolation Forest and TenSEAL/CKKS.

> **Project status:** Academic prototype / proof of concept. It is not a
> production-ready digital forensics platform. This README distinguishes
> implemented functionality from limitations and possible future work.

------------------------------------------------------------------------

## Table of contents

-   [Objectives](#objectives)
-   [Core features](#core-features)
-   [Technology stack](#technology-stack)
-   [System architecture](#system-architecture)
-   [Evidence processing workflow](#evidence-processing-workflow)
-   [Security and privacy mechanisms](#security-and-privacy-mechanisms)
-   [AI anomaly detection](#ai-anomaly-detection)
-   [Database design](#database-design)
-   [Project structure](#project-structure)
-   [Prerequisites](#prerequisites)
-   [Getting started](#getting-started)
-   [Configuration](#configuration)
-   [Running with Docker Compose](#running-with-docker-compose)
-   [API overview](#api-overview)
-   [Testing the main workflows](#testing-the-main-workflows)
-   [Implementation boundaries and
    limitations](#implementation-boundaries-and-limitations)
-   [Production hardening and future
    enhancements](#production-hardening-and-future-enhancements)
-   [Troubleshooting](#troubleshooting)
-   [Contributing](#contributing)
-   [Disclaimer](#disclaimer)

------------------------------------------------------------------------

## Objectives

ForenCrypt explores the following goals:

1.  **Evidence integrity:** calculate a SHA-256 digest when evidence is
    uploaded and compare it with a newly calculated digest during
    verification.
2.  **Traceability:** record evidence-related actions in a hash-linked
    chain so that changes to recorded block data can be detected.
3.  **Authenticated access:** authenticate users with bcrypt password
    verification and JWT bearer tokens.
4.  **Privacy-preserving computation:** demonstrate selected arithmetic
    preprocessing on encrypted numerical features using CKKS homomorphic
    encryption.
5.  **Anomaly detection:** use an Isolation Forest model to flag unusual
    patterns in manually supplied forensic activity features.
6.  **Containerized development:** run the FastAPI backend and MySQL
    database using Docker Compose.

## Core features

  -----------------------------------------------------------------------
  Feature                             Current implementation
  ----------------------------------- -----------------------------------
  User authentication                 bcrypt password hashing and JWT
                                      access tokens

  Evidence upload                     Uploaded files stored in the
                                      backend's local `uploads/`
                                      directory

  Evidence integrity                  SHA-256 hash calculated at upload
                                      and recalculated for verification

  Chain-of-custody prototype          Hash-linked blocks stored in MySQL

  Chain verification                  Checks block hashes and
                                      previous-hash links

  Homomorphic encryption              TenSEAL CKKS encryption and
                                      selected element-wise preprocessing

  AI anomaly detection                Scikit-learn Isolation Forest using
                                      six numerical features

  Database                            MySQL with SQLAlchemy

  Containerization                    Docker and Docker Compose
  -----------------------------------------------------------------------

## Technology stack

-   **Language:** Python
-   **Backend framework:** FastAPI
-   **Database:** MySQL 8.0
-   **ORM / database access:** SQLAlchemy
-   **Authentication:** JWT using HS256
-   **Password hashing:** bcrypt
-   **Evidence integrity:** SHA-256
-   **Homomorphic encryption:** TenSEAL with CKKS
-   **Machine learning:** Scikit-learn Isolation Forest
-   **Model persistence:** Joblib
-   **Containerization:** Docker, Docker Compose
-   **API server:** Uvicorn

------------------------------------------------------------------------

## System architecture

``` text
                    Investigator / Client
                            |
                            | HTTP requests
                            v
                    FastAPI Backend
                            |
          +-----------------+------------------+
          |                 |                  |
          v                 v                  v
   Authentication     Evidence Service   Forensic Analysis
   bcrypt + JWT       Upload / Verify     CKKS preprocessing
          |                 |             Isolation Forest
          |                 |                  |
          +-----------------+------------------+
                            |
                            v
                       MySQL Database
                 +----------+-----------+
                 |          |           |
               users     evidence   blockchain_blocks
                                       |
                                 forensic_analysis
```

The backend and database are run as separate Docker Compose services.
Compose creates a default network for the services, allowing the backend
to reach MySQL using the service hostname `db`.

## Evidence processing workflow

The main evidence workflow is:

1.  An investigator authenticates with the backend.
2.  The investigator uploads an evidence file.
3.  The backend stores the file in its local uploads directory.
4.  The backend calculates a SHA-256 hash for the uploaded file.
5.  Evidence metadata and the hash are stored in MySQL.
6.  An upload-related block is added to the MySQL-backed hash chain.
7.  During integrity verification, the backend recalculates the file's
    SHA-256 hash.
8.  The newly calculated hash is compared with the originally stored
    hash.
9.  The evidence is reported as `VALID` if the hashes match, or
    `COMPROMISED` if they do not.

### Simplified integrity example

``` text
Original evidence file
        |
        v
SHA-256 calculation
        |
        v
Original hash stored in evidence record
        |
        v
File is checked later
        |
        v
Calculate SHA-256 again
        |
        +---- Hash matches ----> VALID
        |
        +---- Hash differs ----> COMPROMISED
```

SHA-256 is a one-way cryptographic hash function. It is used here to
detect changes, not to encrypt or conceal the evidence file.

## Security and privacy mechanisms

### 1. Password hashing with bcrypt

-   User passwords are hashed before they are stored.
-   During login, bcrypt verifies the submitted password against the
    stored password hash.
-   bcrypt uses a salt and is deliberately computationally expensive
    compared with general-purpose hashes.
-   Passwords should never be stored as plaintext.

### 2. JWT authentication

The login endpoint issues a signed JWT access token after successful
credential verification.

The current token includes: - `sub`: the user's ID, represented as a
string. - `exp`: the token expiration time.

The configured access-token lifetime is 60 minutes by default.

Clients should send the token on protected requests using:

``` http
Authorization: Bearer <access_token>
```

**Important:** JWTs are signed, not encrypted. Do not put passwords,
password hashes, secret keys, or confidential evidence data in the token
payload.

### 3. SHA-256 evidence integrity

-   A SHA-256 digest is calculated when the file is uploaded.
-   The digest is stored with the evidence metadata.
-   Verification recalculates the digest from the stored file and
    compares the result.
-   A mismatch indicates that the file content no longer matches the
    content originally hashed.

A hash mismatch does not identify who changed a file or when the change
occurred. It indicates a difference in content.

### 4. Hash-linked chain-of-custody prototype

Each block records information such as:

-   Block index
-   Evidence ID
-   Action
-   User who performed the action
-   Evidence hash
-   Previous block hash
-   Current block hash
-   Creation timestamp

The first block uses a genesis previous hash consisting of 64 zero
characters. Each later block stores the preceding block's hash as its
`previous_hash`.

The block hash is calculated from the block's recorded fields using
SHA-256. The verification operation checks both the stored block hash
and the link to the previous block.

**Implementation note:** this is a hash-chain prototype stored in MySQL.
It is not a decentralized blockchain network. It does not currently use
distributed consensus, independent blockchain nodes, smart contracts,
Ethereum, Hyperledger Fabric, or IPFS.

### 5. Homomorphic encryption with TenSEAL and CKKS

The project uses TenSEAL with the CKKS scheme to demonstrate arithmetic
on encrypted numerical feature vectors.

Current processing: 1. A vector of six numerical forensic activity
features is encrypted. 2. Selected element-wise scaling is performed on
the encrypted vector. 3. The processed vector is decrypted. 4. The
resulting numerical features are passed to the Isolation Forest model.

The current example scales the `data_transfer_mb` feature by `0.01`
while it is encrypted.

**Important boundary:** the complete Isolation Forest prediction is not
performed on encrypted data. The project demonstrates homomorphic
preprocessing, followed by decryption and ordinary model inference. CKKS
is an approximate arithmetic scheme, so numerical results may be
approximate.

------------------------------------------------------------------------

## AI anomaly detection

ForenCrypt uses the **Isolation Forest** algorithm from Scikit-learn.

Isolation Forest is an unsupervised learning algorithm. It identifies
observations that are unusual compared with the patterns represented in
its training data.

### Input features

The current analysis workflow uses six numerical features:

  Feature               Meaning
  --------------------- ------------------------------------------------
  `failed_logins`       Number of failed login attempts
  `file_access_count`   Number of file access operations
  `data_transfer_mb`    Amount of data transferred, in MB
  `unique_ips`          Number of distinct IP addresses
  `login_frequency`     Login frequency value supplied to the analysis
  `execution_count`     Number of executions represented by the input

The current workflow accepts these values as analysis input. It does not
automatically extract them from operating-system logs or forensic
evidence files.

### Model behaviour

Isolation Forest returns: - `1` for a normal observation. - `-1` for an
anomaly.

The application maps the prediction and anomaly score to a demonstration
risk label: - `HIGH` - `MEDIUM` - `LOW`

The current risk mapping uses a project-defined score threshold. It
should not be treated as a clinically, legally, or operationally
validated risk scale.

### Training data

The current training script uses a small, manually prepared
demonstration dataset and saves the trained model as `anomaly_model.pkl`
using Joblib.

This is suitable for demonstrating the pipeline, but it is not enough to
establish real-world forensic detection accuracy. A production system
would require a larger, representative dataset, careful feature
engineering, evaluation, threshold calibration, and human review.

------------------------------------------------------------------------

## Database design

The project currently uses four main tables.

### `users`

Stores user account information: - `id` - `username` - `email` -
`password_hash` - `role` - `created_at`

The current role values include `admin` and `investigator`.

### `evidence`

Stores evidence metadata, including: - Evidence ID - Original filename -
Stored filename - File path - File size - SHA-256 hash - Uploading
user - Status - Creation timestamp

The evidence file itself is stored in the backend's local uploads
directory, rather than as a binary object in the evidence table.

### `blockchain_blocks`

Stores the hash-linked chain records: - Block index - Evidence ID -
Action - User who performed the action - Evidence hash - Previous hash -
Block hash - Timestamp

### `forensic_analysis`

Stores anomaly-analysis input and output: - Evidence ID - Six numerical
input features - Anomaly score - Risk level - Analysis timestamp

### Entity relationships

``` text
users (1) -------- (many) evidence
users (1) -------- (many) blockchain_blocks
evidence (1) ----- (many) blockchain_blocks
evidence (1) ----- (many) forensic_analysis
```

------------------------------------------------------------------------

## Project structure

The following is a representative structure based on the backend
components used by the project. Adjust names if your current repository
has changed.

``` text
ForenCrypt/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── ml/
│   │   │   ├── train.py
│   │   │   └── anomaly_model.pkl
│   │   ├── services/
│   │   │   └── fhe.py
│   │   ├── uploads/
│   │   └── ...
│   ├── Dockerfile
│   └── requirements.txt
├── database/
│   └── init.sql
├── docker-compose.yml
├── .env
├── .env.example
├── .gitignore
└── README.md
```

The exact router, schema, and service filenames may differ in the
current repository. Keep the README structure synchronized with the
actual code as the project evolves.

------------------------------------------------------------------------

## Prerequisites

For the Docker-based setup:

-   Git
-   Docker Desktop or Docker Engine
-   Docker Compose (the `docker compose` command)

For running the backend directly without Docker, you will also need a
compatible Python installation and a running MySQL server. The Docker
workflow is the recommended development setup for this project.

## Getting started

### 1. Clone the repository

``` bash
git clone https://github.com/heyGladwin/Advanced-Privacy-Preservation-in-Digital-Forensics.git
cd Advanced-Privacy-Preservation-in-Digital-Forensics
```

If your repository URL or default branch differs, use the URL and branch
shown in your Git hosting account.

### 2. Create the environment file

Create a `.env` file in the project root. Use `.env.example` as a
template if it exists.

Example development configuration:

``` env
MYSQL_ROOT_PASSWORD=replace_with_a_local_root_password
MYSQL_DATABASE=forencrypt
MYSQL_USER=forencrypt_user
MYSQL_PASSWORD=replace_with_a_local_database_password
MYSQL_HOST=db
MYSQL_PORT=3306

SECRET_KEY=replace_with_a_long_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

These are development settings. Do not commit real credentials or secret
keys to Git. The `.env` file should be excluded by `.gitignore`.

### 3. Build and start the services

``` bash
docker compose up --build
```

The Compose configuration starts: - The FastAPI backend on host port
`8000`. - MySQL on host port `3307`, mapped to container port `3306`.

The backend connects to MySQL using `db:3306` from inside the Compose
network. Do not change the backend's database host to `localhost` when
it is running inside its container.

### 4. Check the API

Open the FastAPI documentation in a browser:

``` text
http://localhost:8000/docs
```

This page lists the endpoints exposed by the running backend.

### 5. Stop the services

``` bash
docker compose down
```

This stops and removes the containers but preserves the named MySQL
volume.

> **Warning:** `docker compose down -v` also removes named volumes. In
> this project, that can delete the persisted MySQL database data. Do
> not use it unless you intentionally want to remove that data.

------------------------------------------------------------------------

## Configuration

The backend reads database and authentication settings from environment
variables through its settings class.

  -----------------------------------------------------------------------
  Variable                            Purpose
  ----------------------------------- -----------------------------------
  `MYSQL_HOST`                        MySQL hostname used by the backend

  `MYSQL_PORT`                        MySQL port inside the Docker
                                      network

  `MYSQL_DATABASE`                    Database name

  `MYSQL_USER`                        Application database user

  `MYSQL_PASSWORD`                    Application database password

  `SECRET_KEY`                        JWT signing secret

  `ALGORITHM`                         JWT signing algorithm; current
                                      configuration uses `HS256`

  `ACCESS_TOKEN_EXPIRE_MINUTES`       Access-token lifetime in minutes
  -----------------------------------------------------------------------

For local development outside Docker, the database host and port must
match the MySQL server reachable from the host machine. Inside Docker
Compose, use the service hostname and internal port.

------------------------------------------------------------------------

## API overview

The exact request and response schemas should be checked in the running
FastAPI documentation at `http://localhost:8000/docs`.

Known project routes include:

  -----------------------------------------------------------------------
  Route                               Purpose
  ----------------------------------- -----------------------------------
  `POST /api/auth/login`              Authenticate a user and obtain a
                                      JWT access token

  `/evidence`                         Evidence-related operations,
                                      including upload and verification
                                      workflows

  `GET /api/blockchain/chain`         Retrieve the stored hash-chain
                                      records

  `GET /api/blockchain/verify`        Verify the hash-chain links and
                                      block hashes
  -----------------------------------------------------------------------

The evidence router may expose additional methods and paths depending on
the current code. Use `/docs` as the source of truth for HTTP methods,
request fields, response models, and authentication requirements.

------------------------------------------------------------------------

## Testing the main workflows

### 1. Authentication

1.  Open `http://localhost:8000/docs`.
2.  Locate the login route.
3.  Submit valid credentials using the request format shown by the API
    documentation.
4.  Copy the returned access token.
5.  Use the **Authorize** control in Swagger UI if the endpoint requires
    bearer authentication.
6.  Call a protected endpoint and confirm that a valid token is
    accepted.

Do not assume that storing a user role automatically enforces role-based
permissions. Fine-grained admin/investigator authorization must be
implemented and tested separately.

### 2. Evidence integrity

1.  Authenticate.
2.  Upload a test evidence file using the documented evidence upload
    endpoint.
3.  Record the returned evidence ID.
4.  Run the evidence verification operation for that evidence.
5.  Confirm that an unchanged file is reported as `VALID`.
6.  In a controlled test environment, modify the stored test file.
7.  Run verification again and confirm that a hash mismatch is reported
    as `COMPROMISED`.

Only use disposable test evidence for tampering experiments.

### 3. Hash-chain verification

1.  Upload evidence to create an upload-related block.
2.  Retrieve the chain using `GET /api/blockchain/chain`.
3.  Verify it using `GET /api/blockchain/verify`.
4.  In a test database only, modify a block field.
5.  Run chain verification again and inspect whether the altered block
    or broken previous-hash link is detected.

Do not tamper with a database containing evidence needed for actual
investigations.

### 4. AI-assisted analysis

1.  Select an evidence record.
2.  Submit the six numerical features through the analysis endpoint
    documented by the running API.
3.  Inspect the returned anomaly prediction, score, and risk level.
4.  Review the stored analysis record in MySQL if required.

The current workflow uses manually supplied feature values. A risk label
is an automated flag for review, not proof that an investigator or user
acted maliciously.

### 5. Homomorphic preprocessing

Use the project's configured analysis workflow to submit a numerical
feature vector. The current implementation encrypts the vector with
CKKS, applies selected element-wise scaling to the encrypted vector,
decrypts the processed values, and then invokes the normal Isolation
Forest prediction.

This test demonstrates the preprocessing step; it does not demonstrate
fully encrypted machine-learning inference.

------------------------------------------------------------------------

## Implementation boundaries and limitations

The following points are important when evaluating or extending the
project:

1.  **Prototype blockchain:** block records are stored in the same MySQL
    database as the application data. The project does not currently
    have independent distributed nodes or consensus.
2.  **Database trust boundary:** a sufficiently privileged attacker who
    can alter the evidence file, its stored hash, and the complete
    hash-chain records in the same database may be able to rewrite the
    records. Independent storage, signed checkpoints, protected backups,
    or a separately administered ledger would provide stronger
    assurance.
3.  **Local evidence storage:** uploaded files are stored locally under
    the backend uploads directory. IPFS or other distributed evidence
    storage is not currently implemented.
4.  **No full encrypted AI inference:** CKKS is used for selected
    feature preprocessing only. The processed values are decrypted
    before Isolation Forest inference.
5.  **Manual AI features:** the six analysis features are supplied to
    the API; automatic extraction from real forensic logs is not
    currently implemented.
6.  **Demonstration training data:** the Isolation Forest uses a small,
    manually prepared dataset. Its results are not validated for
    operational forensic decisions.
7.  **Role enforcement:** user roles are represented in the database,
    but complete role-specific authorization across endpoints must not
    be assumed. Enforce and test permissions before deployment.
8.  **Token lifecycle:** the current implementation uses expiring JWT
    access tokens. Refresh-token rotation and a token
    revocation/blocklist mechanism are not currently implemented.
9.  **Evidence protection at rest:** SHA-256 provides integrity
    checking, not confidentiality. The current project does not
    implement AES-based encryption of stored evidence.
10. **Production controls:** file type/size validation, comprehensive
    audit logging, hardened evidence download permissions, monitoring,
    backups, and deployment hardening require further work.

These limitations do not invalidate the project as an academic proof of
concept. They define what the current implementation demonstrates and
what would be required for a real forensic deployment.

------------------------------------------------------------------------

## Production hardening and future enhancements

Potential next steps include:

-   Enforce role-based access control using FastAPI dependencies and
    deny-by-default endpoint permissions.
-   Restrict public registration to the investigator role; create
    administrator accounts through a controlled process.
-   Add file type and size validation, safe filename handling, malware
    scanning where appropriate, and strict evidence download
    authorization.
-   Use secure persistent object storage for evidence, with encryption
    at rest and protected backups.
-   Keep evidence hashes and chain checkpoints in an independently
    controlled location.
-   Consider a permissioned blockchain such as Hyperledger Fabric only
    if multiple independent organizations need to share and verify
    custody records.
-   Add signed custody events and stronger identity attribution.
-   Add automatic, validated extraction of forensic activity features
    from trusted logs.
-   Train and evaluate the anomaly model using representative datasets;
    measure false positives and false negatives and keep a human
    investigator in the decision loop.
-   Investigate more extensive encrypted inference only after defining
    the threat model and acceptable performance cost.
-   Use a secrets manager, strong randomly generated signing keys, key
    rotation, HTTPS/TLS, restricted database networking, and
    least-privilege database accounts.
-   Add structured audit logs, monitoring, dependency scanning,
    automated tests, and CI/CD.
-   Configure persistent storage and backup/restore procedures for both
    database records and evidence files.
-   Remove development settings such as Uvicorn `--reload` from
    production deployment.

------------------------------------------------------------------------

## Troubleshooting

### Backend cannot connect to MySQL

-   Confirm that the database container is healthy.
-   Check that `MYSQL_HOST=db` and `MYSQL_PORT=3306` are used by the
    backend container.
-   Check the database name and credentials in `.env`.
-   Inspect service logs:

``` bash
docker compose ps
docker compose logs backend
docker compose logs db
```

### Port 8000 or 3307 is already in use

Stop the process using the port or change the host-side port mapping in
`docker-compose.yml`. If you change the host-side MySQL port, remember
that the backend container should still use the MySQL service's internal
port `3306`.

### Database changes do not appear

The initialization SQL mounted into `/docker-entrypoint-initdb.d/` is
normally run when the MySQL data directory is first initialized. If a
named volume already contains a database, changing the initialization
file may not rerun it. Apply schema changes using an appropriate
migration or controlled database update.

### Homomorphic encryption errors

-   Confirm that TenSEAL is installed in the backend environment.
-   Check that the input vector contains the expected six numerical
    values.
-   CKKS vectors are encrypted vector objects; do not treat them like
    ordinary Python lists or index them directly.
-   Decrypt the processed vector before passing its values to the
    current Isolation Forest inference function.
-   Keep preprocessing consistent between training and inference.

### Model file is missing

Run the project's training script in the backend environment to generate
the model artifact, then confirm that the output path matches the path
used by the inference code.

------------------------------------------------------------------------

## Contributing

For academic or development contributions:

1.  Create a feature branch.
2.  Keep secrets and real forensic evidence out of source control.
3.  Add tests for changes to authentication, evidence verification,
    chain verification, and analysis.
4.  Update this README whenever implementation behaviour changes.
5.  Clearly label experimental features and distinguish them from
    completed functionality.

------------------------------------------------------------------------

## Disclaimer

ForenCrypt is an academic research and development prototype intended
for learning and demonstration. It has not been established as a
validated forensic evidence platform and should not be relied upon as
the sole mechanism for preserving evidence, proving chain of custody, or
making legal or security decisions.

Use synthetic or authorized test data. A real deployment would require
independent security review, validated procedures, access controls,
secure storage, auditability, operational testing, and legal review
appropriate to the jurisdiction and investigation.
