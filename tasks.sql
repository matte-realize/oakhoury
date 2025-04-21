-- Registering a new user
INSERT INTO residents (first_name, last_name, email, password, street, zip_code, is_volunteer, neighborhood)
VALUES (:first_name,
        :last_name,
        :email,
        :password,
        :street,
        :zipcode,
        FALSE,
        :neighborhood);

-- Confirming user login details are correct (login)
SELECT *
FROM residents r
WHERE r.email = :email
  AND r.password = :password;

-- Accepting a request for a tree
INSERT INTO tree_requests (resident_id, submission_timestamp, tree_id, site_description, approved)
VALUES (:resident_id,
        CURRENT_TIMESTAMP,
        :tree_id, -- find tree id
        :site_description,
        FALSE);

-- Approve a request for a tree
UPDATE tree_requests
SET approved = TRUE
WHERE id = :id;

-- Schedule a visit
INSERT INTO scheduled_visits (tree_request_id, event_timestamp, cancelled, notes, organization_member_id)
VALUES (:tree_request_id,
        :timestamp,
        FALSE,
        :notes,
        :organization_member_id);


-- Cancel a visit
UPDATE scheduled_visits
SET cancelled = TRUE
WHERE event_id = :event_id;

-- Record info gathered from a visit
INSERT INTO visit_events (scheduled_visit_id, observations, photo_library_link, additional_visit_required)
VALUES (:scheduled_visit_id,
        :observations
        :photo_library_link,
        :additional_visit_required);

-- Schedule a planting (without any org members or volunteers yet)
INSERT INTO scheduled_plantings (tree_request_id, event_timestamp, cancelled, notes)
VALUES (:tree_request_id,
        :timestamp,
        FALSE,
        :notes);

-- Add an organization member to a scheduled planting
INSERT INTO organization_members_lead_scheduled_plantings (organization_member_id, scheduled_planting_id)
VALUES (:organization_member_id,
        :scheduled_planting_id);

-- Add a volunteer to a scheduled planting
INSERT INTO scheduled_plantings_have_volunteers (volunteer_id, planting_event_id)
VALUES (:volunteer_id,
        :planting_event_id);

-- Record info after a scheduled planting
INSERT INTO planting_events (scheduled_planting_id, observations, before_photos_library_link, after_photos_library_link,
                             successful)
VALUES (:scheduled_planting_id,
        :observations,
        :before_photos_library_link,
        :after_photos_library_link,
        :successful);

-- Decrement the inventory for that tree planted
UPDATE trees
SET inventory = inventory - 1
WHERE id = :id;

-- Add a volunteer that actually participated
INSERT INTO planting_events_have_volunteers (planting_event_id, volunteer_id)
VALUES (:planting_event_id,
        :volunteer_id);

-- Update the inventory for a tree
UPDATE trees
SET inventory = :inventory
WHERE id = :id;

--
-- QUERIES
--


-- For all requests to plant a tree that have not yet completed, show its status, and the number of
-- days that has transpired since it was first submitted.
SELECT id,
       get_tree_request_status(id)               AS status,
       -- https://stackoverflow.com/questions/45487731/postgres-get-number-of-days-since-date
       CURRENT_DATE - submission_timestamp::DATE AS days_since_submission
FROM tree_requests tr
WHERE get_tree_request_status(id) <> 'completed';

-- Find all trees planted within a selection of Oakland neighborhoods or zip codes specified by a
-- user in the app. Parameterized neighbor value to allow for user input.
SELECT t.common_name,
       COUNT(*) AS number_of_trees
FROM neighborhoods n
         INNER JOIN residents r
                    ON n.name = r.neighborhood
         INNER JOIN tree_requests tr
                    ON r.id = tr.resident_id
         INNER JOIN scheduled_plantings sp
                    ON tr.id = sp.tree_request_id
         INNER JOIN planting_events pe
                    ON sp.event_id = pe.scheduled_planting_id
                        AND pe.successful = TRUE
         INNER JOIN trees t
                    ON tr.tree_id = t.id
WHERE n.name = :p_neighborhood
GROUP BY t.common_name;

-- For every species of trees, find the number of trees planted and some basic statistics on when
-- trees were planted: the number of years since the first tree of the species was planted, the
-- number of years since the most recent tree of the species was planted. In addition, include the
-- year that had the most trees of the species planted and the number of trees planted.
-- https://www.scaler.com/topics/datediff-in-postgresql/

SELECT t.common_name,
       COUNT(pe)                                                                       AS number_of_trees_planted,
       MIN(EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM sp.event_timestamp::TIMESTAMP)) AS years_since_planting,
       (SELECT
            EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
        FROM
            trees AS t2
                INNER JOIN tree_requests ON t2.id = tree_requests.tree_id
                INNER JOIN scheduled_plantings sp2 ON tree_requests.id = sp2.tree_request_id
                INNER JOIN planting_events pe2 ON sp2.event_id = pe2.scheduled_planting_id
        WHERE
              t2.id = t.id
          AND pe2.successful = TRUE
        GROUP BY EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
        ORDER BY COUNT(*) DESC
        LIMIT 1)                                                                          AS year_most_planted,
       (SELECT
            COUNT(*)
        FROM
            trees AS t2
                INNER JOIN tree_requests ON t2.id = tree_requests.tree_id
                INNER JOIN scheduled_plantings sp2 ON tree_requests.id = sp2.tree_request_id
                INNER JOIN planting_events pe2 ON sp2.event_id = pe2.scheduled_planting_id
        WHERE
              t2.id = t.id
          AND pe2.successful = TRUE
        GROUP BY EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
        ORDER BY COUNT(*) DESC
        LIMIT 1)                                                                          AS num_planted_in_peak_year
FROM trees t
    INNER JOIN tree_requests tr ON t.id = tr.tree_id
    INNER JOIN scheduled_plantings sp ON tr.id = sp.tree_request_id
    INNER JOIN planting_events pe ON sp.event_id = pe.scheduled_planting_id
WHERE pe.successful = TRUE
GROUP BY t.common_name, t.id;

-- For each Oakland neighborhood, create a report that summarizes the requests, their progress
-- (pending, in-process, completed, ec), the trees planted, etc. This is an opportunity for your
-- team to demonstrate your skills, so it's expected that you'll demonstrate sophisticated database
-- querying skills
SELECT n.name,
       t.common_name,
       tr.id AS tree_request_id,
       get_tree_request_status(tr.id) AS request_status,
       tr.site_description
FROM neighborhoods n
    INNER JOIN residents r
               ON n.name = r.neighborhood
    INNER JOIN tree_requests tr
               ON r.id = tr.resident_id
    INNER JOIN trees t
               ON tr.tree_id = t.id
GROUP BY n.name, tr.id, t.common_name
ORDER BY n.name ASC;