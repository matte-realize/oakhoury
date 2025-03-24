-- Creates tables in Postgres v.17.4

CREATE TABLE neighborhoods (
    name varchar(100) primary key
);

CREATE TABLE residents (
    id serial primary key,
    first_name varchar(50),
    last_name varchar(50),
    email varchar(100) unique not null,
    password varchar(50),
    street varchar(50),
    zip_code char(5) CHECK(zip_code > 0),
    is_volunteer boolean,
    neighborhood varchar(100) references neighborhoods(name)
);

CREATE TABLE organization_members (
    resident_id integer primary key references residents(id),
    role varchar(50),
    start_date date
);

CREATE TABLE volunteer_applications (
    resident_id integer primary key references residents(id),
    created date,
    approved boolean,
    notes text
);

CREATE TYPE tolerance AS ENUM ('moderate', 'high', 'very high');
CREATE TYPE rate AS ENUM ('slow', 'moderate', 'fast', 'very fast');
CREATE TYPE foliage AS ENUM ('deciduous', 'drought-deciduous', 'evergreen', 'semi-evergreen', 'late-deciduous');
CREATE TYPE root_damage AS ENUM ('low', 'moderate', 'high');
CREATE TYPE nursery_availability AS ENUM ('low', 'moderate', 'high');
CREATE TABLE trees (
    id serial primary key,
    common_name varchar(100) unique,
    scientific_name varchar(100) unique,
    height_range int4range,
    width_range int4range,
    minimum_planting_bed_width integer,
    plantable_under_power_lines boolean,
    native_to_ca boolean,
    drought_tolerance tolerance,
    growth_rate rate,
    foliage_type foliage,
    debris varchar(50),
    root_damage_potential root_damage,
    nursery_availability nursery_availability,
    visual_attraction varchar(20)[],
    pZHarshSites boolean,
    pZBay boolean,
    pZUrbanized boolean,
    pZNearNaturalAreas boolean,
    inventory integer check(inventory >= 0)
);

CREATE TABLE tree_requests (
    id serial primary key,
    resident_id integer references residents(id),
    submission_timestamp timestamp,
    tree_id integer references trees(id),
    site_description text,
    approved boolean,
    unique(resident_id, submission_timestamp)
);

CREATE TYPE status AS ENUM ('pending', 'approved', 'denied');
CREATE TABLE permits (
    resident_id integer references residents(id),
    tree_request_id integer references tree_requests(id),
    status status,
    approval_date date,
    PRIMARY KEY(resident_id, tree_request_id)
);

-- Abstract table to hold scheduled_events
CREATE TABLE scheduled_events (
    event_id serial primary key,
    event_timestamp timestamp,
    cancelled boolean,
    notes text
);

CREATE TABLE scheduled_plantings (
    -- inherits all from scheduled_events
    primary key (event_id)
) inherits (scheduled_events);


CREATE TABLE scheduled_visits (
    organization_member_id integer references organization_members(resident_id),
    primary key (event_id)
) inherits (scheduled_events);

CREATE TABLE visit_events (
    scheduled_visit_id integer primary key references scheduled_plantings(event_id),
    observations text,
    photo_library_link varchar(50),
    additional_visit_required boolean
);

CREATE TABLE planting_events (
    scheduled_planting_id integer primary key references scheduled_visits(event_id),
    observations text,
    before_photos_library_link varchar(100),
    after_photos_library_link varchar(100),
    successful boolean
);

-- junction tables

CREATE TABLE organization_members_lead_planting_events (
    organization_member_id integer references organization_members(resident_id),
    planting_event_id integer references planting_events(scheduled_planting_id),
    primary key(organization_member_id, planting_event_id)
);

CREATE TABLE scheduled_plantings_have_volunteers (
    planting_event_id integer references scheduled_plantings(event_id),
    volunteer_id integer references residents(id),
    primary key(planting_event_id, volunteer_id)
);

CREATE TABLE planting_events_have_volunteers (
    planting_event_id integer references planting_events(scheduled_planting_id),
    volunteer_id integer references residents(id),
    primary key(planting_event_id,  volunteer_id)
);