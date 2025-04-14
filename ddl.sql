-- Creates tables in Postgres v.17.4

CREATE TABLE neighborhoods
(
    name VARCHAR(100) PRIMARY KEY
);

CREATE TABLE residents
(
    id           SERIAL PRIMARY KEY,
    first_name   VARCHAR(50) NOT NULL,
    last_name    VARCHAR(50) NOT NULL,
    email        VARCHAR(100) UNIQUE NOT NULL,
    password     VARCHAR(50),
    street       VARCHAR(50),
    zip_code     CHAR(5),
    is_volunteer BOOLEAN,
    neighborhood VARCHAR(100) REFERENCES neighborhoods (name) NOT NULL
);

CREATE TABLE organization_members
(
    resident_id INTEGER PRIMARY KEY REFERENCES residents (id) NOT NULL,
    role        VARCHAR(50) NOT NULL,
    start_date  DATE
);

CREATE TABLE volunteer_applications
(
    resident_id INTEGER PRIMARY KEY REFERENCES residents (id) NOT NULL,
    created     DATE NOT NULL,
    approved    BOOLEAN,
    notes       TEXT
);

CREATE TYPE tolerance AS ENUM ('moderate', 'high', 'very high');
CREATE TYPE rate AS ENUM ('slow', 'moderate', 'fast', 'very fast');
CREATE TYPE foliage AS ENUM ('deciduous', 'drought-deciduous', 'evergreen', 'semi-evergreen', 'late-deciduous');
CREATE TYPE root_damage AS ENUM ('low', 'moderate', 'high');
CREATE TYPE nursery_availability AS ENUM ('low', 'moderate', 'high');
CREATE TABLE trees
(
    id                          SERIAL PRIMARY KEY NOT NULL,
    common_name                 VARCHAR(100) UNIQUE,
    scientific_name             VARCHAR(100) UNIQUE NOT NULL,
    height_range                int4range,
    width_range                 int4range,
    minimum_planting_bed_width  INTEGER,
    plantable_under_power_lines BOOLEAN,
    native_to_ca                BOOLEAN,
    drought_tolerance           tolerance,
    growth_rate                 rate,
    foliage_type                foliage,
    debris                      VARCHAR(50),
    root_damage_potential       root_damage,
    nursery_availability        nursery_availability,
    visual_attraction           VARCHAR(50)[],
    pzharshsites                BOOLEAN,
    pzbay                       BOOLEAN,
    pzurbanized                 BOOLEAN,
    pznearnaturalareas          BOOLEAN,
    inventory                   INTEGER CHECK (inventory >= 0)
);

CREATE TABLE tree_requests
(
    id                   SERIAL PRIMARY KEY NOT NULL,
    resident_id          INTEGER REFERENCES residents (id) NOT NULL,
    submission_timestamp TIMESTAMP NOT NULL,
    tree_id              INTEGER REFERENCES trees (id) NOT NULL,
    site_description     TEXT,
    approved             BOOLEAN,
    UNIQUE (resident_id, submission_timestamp)
);

CREATE TYPE status AS ENUM ('pending', 'approved', 'denied');
CREATE TABLE permits
(
    resident_id     INTEGER REFERENCES residents (id),
    tree_request_id INTEGER REFERENCES tree_requests (id),
    status          status NOT NULL,
    decision_date   DATE,
    PRIMARY KEY (resident_id, tree_request_id)
);

-- Abstract table to hold scheduled_events
CREATE TABLE scheduled_events
(
    event_id        SERIAL PRIMARY KEY NOT NULL,
    tree_request_id INTEGER REFERENCES tree_requests (id) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    cancelled       BOOLEAN,
    notes           TEXT
);

CREATE TABLE scheduled_plantings
(
    -- inherits all from scheduled_events
    PRIMARY KEY (event_id)
) INHERITS (scheduled_events);


CREATE TABLE scheduled_visits
(
    organization_member_id INTEGER REFERENCES organization_members (resident_id) NOT NULL,
    PRIMARY KEY (event_id)
) INHERITS (scheduled_events);

CREATE TABLE visit_events
(
    scheduled_visit_id        INTEGER PRIMARY KEY REFERENCES scheduled_visits (event_id),
    observations              TEXT,
    photo_library_link        VARCHAR(100),
    additional_visit_required BOOLEAN
);

CREATE TABLE planting_events
(
    scheduled_planting_id      INTEGER PRIMARY KEY REFERENCES scheduled_plantings (event_id),
    observations               TEXT,
    before_photos_library_link VARCHAR(100),
    after_photos_library_link  VARCHAR(100),
    successful                 BOOLEAN NOT NULL
);

-- junction tables

CREATE TABLE organization_members_lead_planting_events
(
    organization_member_id INTEGER REFERENCES organization_members (resident_id),
    planting_event_id      INTEGER REFERENCES planting_events (scheduled_planting_id),
    PRIMARY KEY (organization_member_id, planting_event_id)
);

CREATE TABLE scheduled_plantings_have_volunteers
(
    planting_event_id INTEGER REFERENCES scheduled_plantings (event_id),
    volunteer_id      INTEGER REFERENCES residents (id),
    PRIMARY KEY (planting_event_id, volunteer_id)
);

CREATE TABLE planting_events_have_volunteers
(
    planting_event_id INTEGER REFERENCES planting_events (scheduled_planting_id),
    volunteer_id      INTEGER REFERENCES residents (id),
    PRIMARY KEY (planting_event_id, volunteer_id)
);