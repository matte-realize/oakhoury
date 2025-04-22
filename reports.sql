-- The following link helped me figure out how to extract that year from a timestamp
-- https://www.commandprompt.com/education/how-to-extract-year-from-date-in-postgresql/#:~:text=To%20extract%20a%20year%20from%20a%20date%2C%20the%20built%2Din,dateField'%20FROM%20TIMESTAMP%20%7C%20INTERVAL%20)%3B
-- The following link taught me about the LIMIT keyword
-- https://razorsql.com/articles/postgresql_select_top_syntax.html#:~:text=Postgres%20does%20have%20a%20way,limit%20keyword%20must%20be%20used.&text=PostgreSQL%20also%20gives%20the%20ability,limit%20N%20offset%20Y%20syntax.

-- The following query gets us a report about the most active volunteers, this is important because it helps the organization
-- keep track of the impact that each volunteer has helped cause. Year has been parameterized so that the user can query
-- data for whichever year they desire, this parameterization allows for the organization to track the impact and activity
-- of each volunteer more clearly.

SELECT
    r.first_name || ' ' || r.last_name AS volunteer_name,
    MIN(sp.event_timestamp)            AS first_planting,
    MAX(sp.event_timestamp)            AS most_recent_planting,
    COUNT(pev)                         AS trees_planted,
    (SELECT
         EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     FROM
         planting_events_have_volunteers AS pev2
             INNER JOIN planting_events AS p2 ON pev2.planting_event_id = p2.scheduled_planting_id
             INNER JOIN scheduled_plantings AS sp2 ON p2.scheduled_planting_id = sp2.event_id
     WHERE
         pev2.volunteer_id = r.id
     GROUP BY
         EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     ORDER BY COUNT(*) DESC
     LIMIT 1)                          AS peak_year,
    (SELECT
         COUNT(*)
     FROM
         planting_events_have_volunteers pev2
             INNER JOIN planting_events AS p2 ON pev2.planting_event_id = p2.scheduled_planting_id
             INNER JOIN scheduled_plantings AS sp2 ON p2.scheduled_planting_id = sp2.event_id
     WHERE
         pev2.volunteer_id = r.id
     GROUP BY
         EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     ORDER BY COUNT(*) DESC
     LIMIT 1)                          AS trees_planted_in_peak_year
FROM
    residents AS r
        INNER JOIN planting_events_have_volunteers AS pev ON r.id = pev.volunteer_id
        INNER JOIN planting_events AS pe ON pev.planting_event_id = pe.scheduled_planting_id
        INNER JOIN scheduled_plantings AS sp ON pe.scheduled_planting_id = sp.event_id
WHERE
      r.is_volunteer = TRUE
  AND pe.successful = TRUE
  AND EXTRACT(YEAR FROM sp.event_timestamp::TIMESTAMP) = :p_year
GROUP BY r.first_name, r.last_name, r.id
ORDER BY trees_planted DESC, trees_planted_in_peak_year DESC;

-- The following query gives us a report regarding the organization members that lead plantings and attend visits; it
-- displays the amount of plantings they've led, visits they've attended, their peak years and activity for both plantings
-- and visits. This information is important for the higher up organization members so that they can make any necessary
-- changes to lower level organization members. Year has been parameterized so that the user can query data for whichever
-- year they desire, this parameterization allows for the organization to track the activity and success of each organization
-- member more clearly.

SELECT
    r.first_name || ' ' || r.last_name AS org_member_name,
    COUNT(sp) AS plantings_led,
    COUNT(pe) AS successful_plantings_led,
    (SELECT
         EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     FROM
         organization_members_lead_scheduled_plantings AS ompe2
             INNER JOIN scheduled_plantings sp2 ON ompe2.scheduled_planting_id = sp2.event_id
             INNER JOIN planting_events pe2 ON sp2.event_id = pe2.scheduled_planting_id
     WHERE
             ompe2.organization_member_id = om.resident_id
         AND pe2.successful = TRUE
     GROUP BY EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     ORDER BY COUNT(*) DESC
     LIMIT 1)   AS plantings_led_peak_year,
    (SELECT
         COUNT(*)
     FROM
         organization_members_lead_scheduled_plantings AS ompe2
             INNER JOIN scheduled_plantings sp2 ON ompe2.scheduled_planting_id = sp2.event_id
             INNER JOIN planting_events pe2 ON sp2.event_id = pe2.scheduled_planting_id
     WHERE
             ompe2.organization_member_id = om.resident_id
         AND pe2.successful = TRUE
     GROUP BY EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     ORDER BY COUNT(*) DESC
     LIMIT 1)   AS plantings_led_in_peak_year,
    COUNT(sv)   AS visits_attended,
    (SELECT
         EXTRACT(YEAR FROM sv2.event_timestamp::TIMESTAMP)
     FROM
         scheduled_visits AS sv2
     WHERE
             sv2.organization_member_id = om.resident_id
         AND sv2.cancelled = FALSE
     GROUP BY EXTRACT(YEAR FROM sv2.event_timestamp::TIMESTAMP)
     ORDER BY COUNT(*) DESC
     LIMIT 1)   AS visits_attended_peak_year,
    (SELECT
         COUNT(*)
     FROM
         scheduled_visits AS sv2
     WHERE
           sv2.organization_member_id = om.resident_id
       AND sv2.cancelled = FALSE
     GROUP BY EXTRACT(YEAR FROM sv2.event_timestamp::TIMESTAMP)
     ORDER BY COUNT(*) DESC
     LIMIT 1)   AS visits_attended_in_peak_year
FROM
    organization_members AS om
        INNER JOIN residents AS r ON om.resident_id = r.id
        LEFT OUTER JOIN organization_members_lead_scheduled_plantings AS ompe ON om.resident_id = ompe.organization_member_id
        LEFT OUTER JOIN scheduled_visits AS sv ON om.resident_id = sv.organization_member_id
                                                      AND sv.cancelled = FALSE
                                                      AND EXTRACT(YEAR FROM sv.event_timestamp::TIMESTAMP) = :p_year
        INNER JOIN scheduled_plantings AS sp ON ompe.scheduled_planting_id = sp.event_id
        LEFT OUTER JOIN planting_events AS pe ON sp.event_id = pe.scheduled_planting_id AND pe.successful = TRUE
WHERE
        sp.cancelled = FALSE
    AND EXTRACT(YEAR FROM sp.event_timestamp::TIMESTAMP) = :p_year
GROUP BY r.first_name, r.last_name, r.id, om.resident_id
ORDER BY plantings_led DESC, visits_attended DESC;

-- The following query gives us a report regarding the total number of trees planted in neighborhood where they have been
-- planted previously, the number planted in said neighborhood this year, as well as the peak year of planting in that
-- neighborhood and the number planted during this year. This data is important for the organization so they can keep
-- track of where the planted trees have gone, and monitor the amount that gets planted in each neighborhood.

SELECT
    t.common_name,
    r.neighborhood,
    (SELECT
         COUNT(*)
     FROM
         tree_requests AS tr2
             INNER JOIN residents AS r2 ON tr2.resident_id = r2.id
             INNER JOIN scheduled_plantings sp2 ON tr2.id = sp2.tree_request_id
             INNER JOIN planting_events pe2 ON sp2.event_id = pe2.scheduled_planting_id
     WHERE
           r2.neighborhood = r.neighborhood
       AND tr2.tree_id = t.id
       AND pe2.successful = TRUE) AS num_in_neighborhood,
    (SELECT
         COUNT(*)
     FROM    tree_requests AS tr2
                 INNER JOIN residents AS r2 ON tr2.resident_id = r2.id
                 INNER JOIN scheduled_plantings AS sp2 ON tr2.id = sp2.tree_request_id
                 INNER JOIN planting_events pe2 ON sp2.event_id = pe2.scheduled_planting_id
     WHERE
           r2.neighborhood = r.neighborhood
       AND pe2.successful = TRUE
       AND EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP) = EXTRACT(YEAR FROM CURRENT_DATE::DATE)) AS num_planted_this_year,
    (SELECT
         EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     FROM
         tree_requests AS tr2
             INNER JOIN residents AS r2 ON tr2.resident_id = r2.id
             INNER JOIN scheduled_plantings AS sp2 ON tr2.id = sp2.tree_request_id
             INNER JOIN planting_events pe2 ON sp2.event_id = pe2.scheduled_planting_id
     WHERE
           r2.neighborhood = r.neighborhood
       AND pe2.successful = TRUE
     GROUP BY EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     ORDER BY COUNT(*) DESC
     LIMIT 1)                   AS plantings_peak_year,
    (SELECT
         COUNT(*)
     FROM
         tree_requests AS tr2
             INNER JOIN residents AS r2 ON tr2.resident_id = r2.id
             INNER JOIN scheduled_plantings AS sp2 ON tr2.id = sp2.tree_request_id
             INNER JOIN planting_events pe2 ON sp2.event_id = pe2.scheduled_planting_id
     WHERE
           r2.neighborhood = r.neighborhood
       AND pe2.successful = TRUE
     GROUP BY EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     ORDER BY COUNT(*) DESC
     LIMIT 1)                   AS plantings_in_peak_year
FROM
    trees AS t
        INNER JOIN public.tree_requests tr ON t.id = tr.tree_id
        INNER JOIN residents r ON tr.resident_id = r.id
        INNER JOIN scheduled_plantings sp ON tr.id = sp.tree_request_id
        INNER JOIN planting_events pe ON sp.event_id = pe.scheduled_planting_id
WHERE
        pe.successful = TRUE
    AND t.common_name = :p_tree_name
GROUP BY t.common_name, r.neighborhood, t.id
ORDER BY t.common_name ASC;