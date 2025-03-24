-- Registering a new user
INSERT INTO residents (first_name, last_name, email, password, street, zipCode, is_volunteer, neighborhood)
    VALUES (
    :first_name,
    :last_name,
    :email,
    :password,
    :street,
    :zipcode,
    false,
    :neighborhood
);

-- Confirming user login details are correct (login)
SELECT * FROM residents r
WHERE r.email = :email
  AND r.password = :password;

-- Accepting a request for a tree
INSERT INTO tree_requests (resident_id, submission_timestamp, tree_id, site_description, approved)
VALUES (
        :resident_id,
        current_timestamp,
        :tree_id, -- find tree id
        :site_description,
        false
       );

-- Approve a request for a tree
UPDATE tree_requests
SET approved = true
WHERE id = :id;

-- Schedule a visit
INSERT INTO scheduled_visits (event_timestamp, cancelled, notes, organization_member_id)
VALUES (
        :timestamp,
        false,
        :notes,
        :organization_member_id
       );


-- Cancel a visit
UPDATE scheduled_visits
SET cancelled = true
WHERE event_id = :event_id;

-- Record info gathered from a visit
INSERT INTO visit_events (scheduled_visit_id, observations, photo_library_link, additional_visit_required)
VALUES (
        :scheduled_visit_id,
        :observations
        :photo_library_link,
        :additional_visit_required
       );

-- Schedule a planting (without any org members or volunteers yet)
INSERT INTO scheduled_plantings (event_timestamp, cancelled, notes)
VALUES (
        :timestamp,
        false,
        :notes
       );

-- Add an organization member to a scheduled planting
INSERT INTO organization_members_lead_planting_events (organization_member_id, planting_event_id)
VALUES (
        :organization_member_id,
        :planting_event_id
       );

-- Add a volunteer to a scheduled planting
INSERT INTO scheduled_plantings_have_volunteers (volunteer_id, planting_event_id)
VALUES (
        :volunteer_id,
        :planting_event_id
       );

-- Record info after a scheduled planting
INSERT INTO planting_events (scheduled_planting_id, observations, before_photos_library_link, after_photos_library_link, successful)
VALUES (
        :scheduled_planting_id,
        :observations,
        :before_photos_library_link,
        :after_photos_library_link,
        :successful
       );

-- Decrement the inventory for that tree planted
UPDATE trees
SET inventory = inventory - 1
WHERE id = :id;

-- Add a volunteer that actually participated
INSERT INTO planting_events_have_volunteers (planting_event_id, volunteer_id)
VALUES (
        :planting_event_id,
        :volunteer_id
       );

-- Update the inventory for a tree
UPDATE trees
SET inventory = :inventory
WHERE id = :id;
