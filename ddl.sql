-- Creates tables in Postgres v.17.4

-- DROP TABLE neighborhoods;
-- DROP TABLE residents;

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
    zipCode char(5),
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
CREATE TYPE foliage AS ENUM ('deciduous', 'evergreen', 'semi-evergreen', 'late-deciduous');
CREATE TYPE root_damage AS ENUM ('low', 'moderate', 'high');
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
    visual_attraction varchar(20)[],
    pZHarshSites boolean,
    pZBay boolean,
    pZUrbanized boolean,
    pZNearNaturalAreas boolean
);

