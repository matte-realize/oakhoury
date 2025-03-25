-- The following link helped me figure out how to extract that year from a timestamp
-- https://www.commandprompt.com/education/how-to-extract-year-from-date-in-postgresql/#:~:text=To%20extract%20a%20year%20from%20a%20date%2C%20the%20built%2Din,dateField'%20FROM%20TIMESTAMP%20%7C%20INTERVAL%20)%3B
-- The following link taught me about the LIMIT keyword
-- https://razorsql.com/articles/postgresql_select_top_syntax.html#:~:text=Postgres%20does%20have%20a%20way,limit%20keyword%20must%20be%20used.&text=PostgreSQL%20also%20gives%20the%20ability,limit%20N%20offset%20Y%20syntax.

-- The following query gets us a report about the most active volunteers, this is important because it helps the organization
-- keep track of the impact that each volunteer has helped cause.

SELECT
    r.first_name || ' ' || r.last_name AS volunteer_name,
    MIN(sp.event_timestamp)            AS first_planting,
    MAX(sp.event_timestamp)            AS most_recent_planting,
    COUNT(pev)                         AS trees_planted,
    (SELECT
         DATE_PART('Year', sp2.event_timestamp)
     FROM
         planting_events_have_volunteers AS pev2
             INNER JOIN planting_events AS p2 ON pev2.planting_event_id = p2.scheduled_planting_id
             INNER JOIN scheduled_plantings AS sp2 ON p2.scheduled_planting_id = sp2.event_id
     WHERE
         pev2.volunteer_id = r.id
     GROUP BY DATE_PART('Year', sp2.event_timestamp)
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
     GROUP BY DATE_PART('Year', sp2.event_timestamp)
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
GROUP BY r.first_name, r.last_name, r.id
ORDER BY trees_planted_in_peak_year DESC, trees_planted DESC;