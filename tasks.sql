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

-- Get the status of a tree
-- https://neon.tech/postgresql/postgresql-plpgsql/postgresql-create-function
CREATE OR REPLACE FUNCTION get_tree_request_status(p_tree_request_id INTEGER)
    RETURNS TEXT
AS
$$
DECLARE
    v_status TEXT;
BEGIN
    SELECT
        -- https://www.w3schools.com/sql/sql_case.asp
        CASE
            WHEN pe.successful IS TRUE THEN 'completed'
            WHEN ve.additional_visit_required IS FALSE THEN 'waiting for planting'
            WHEN p.status = 'approved' THEN 'waiting for visit'
            WHEN tr.approved IS TRUE THEN 'needs permit'
            ELSE 'pending approval'
            END
    INTO v_status
    FROM tree_requests tr
             LEFT JOIN permits p
                       ON tr.id = p.tree_request_id
             LEFT JOIN scheduled_visits sv
                       ON tr.id = sv.tree_request_id
             LEFT JOIN visit_events ve
                       ON sv.event_id = ve.scheduled_visit_id
             LEFT JOIN scheduled_plantings sp
                       ON tr.id = sp.tree_request_id
             LEFT JOIN planting_events pe
                       ON sp.event_id = pe.scheduled_planting_id
    WHERE tr.id = p_tree_request_id;
    RETURN v_status;
END;
$$ LANGUAGE plpgsql;

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

-- chisos red oak tree appears twice so the years_with_most_planted is not working correctly

WITH years_with_most_planted AS (SELECT t.id,
                                        EXTRACT(YEAR FROM sp.event_timestamp::DATE) AS year_planted
                                 FROM trees t
                                          JOIN tree_requests tr
                                               ON t.id = tr.tree_id
                                          JOIN scheduled_plantings sp
                                               ON tr.id = sp.tree_request_id
                                          JOIN planting_events pe
                                               ON sp.event_id = pe.scheduled_planting_id
                                 WHERE pe.successful = TRUE
                                 GROUP BY t.id, sp.event_timestamp),
     number_of_planted_for_peak_year AS (SELECT t.id,
                                                COUNT(*) AS count
                                         FROM trees t
                                                  JOIN tree_requests tr
                                                       ON t.id = tr.tree_id
                                                  JOIN scheduled_plantings sp
                                                       ON tr.id = sp.tree_request_id
                                                  JOIN planting_events pe
                                                       ON sp.event_id = pe.scheduled_planting_id
                                                  JOIN years_with_most_planted ymp
                                                       ON t.id = ymp.id
                                         WHERE pe.successful = TRUE
                                           AND EXTRACT(YEAR FROM sp.event_timestamp::DATE) = ymp.year_planted
                                         GROUP BY t.id)
SELECT t.common_name,
       COUNT(tr.id)                                                                       AS number_of_trees_planted,
       MIN(EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM sp.event_timestamp::DATE)) AS years_since_planting,
       ymp.year_planted AS peak_planting_year,
       nppy.count AS number_planted_in_peak_year
FROM trees t
         JOIN tree_requests tr
              ON t.id = tr.tree_id
         JOIN scheduled_plantings sp
              ON tr.id = sp.tree_request_id
         JOIN planting_events pe
              ON sp.event_id = pe.scheduled_planting_id
                  AND pe.successful = TRUE
         JOIN years_with_most_planted ymp
              ON t.id = ymp.id
         JOIN number_of_planted_for_peak_year nppy
              ON t.id = nppy.id
GROUP BY t.common_name, ymp.year_planted, nppy.count
ORDER BY number_of_trees_planted DESC;


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