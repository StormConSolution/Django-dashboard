/*

SELECT * FROM get_keyword_counts(3155);

SELECT * FROM get_keyword_counts(3155, language := 'en', source_id := 187, classification_id := 1, aspect := 'Appearance', sql_filter := $SQL$date_created > '2019-01-01'$SQL$, max_rows := 10);

 */

DROP FUNCTION IF EXISTS get_keyword_counts;
CREATE OR REPLACE FUNCTION get_keyword_counts(project_id INT, language VARCHAR = NULL, source_id INT = NULL, classification_id INT = NULL, aspect TEXT = NULL, sql_filter TEXT = NULL, max_rows INT = NULL) RETURNS TABLE(keyword TEXT, keyword_count INT)
LANGUAGE plpgsql
PARALLEL SAFE
AS $$
DECLARE
    filters TEXT[] = ARRAY['project_id = ' || project_id];
BEGIN
    IF (language IS NOT NULL) THEN filters = ARRAY_APPEND(filters, 'language = ' || quote_literal(language)); END IF;
    IF (source_id IS NOT NULL) THEN filters = ARRAY_APPEND(filters, 'source_id = ' || quote_literal(source_id)); END IF;
    IF (sql_filter IS NOT NULL) THEN filters = ARRAY_APPEND(filters, sql_filter); END IF;
    IF (classification_id IS NOT NULL) THEN filters = ARRAY_APPEND(filters, 'id IN (SELECT dde.data_id FROM data_data_entities dde JOIN data_entity_classifications ec ON dde.entity_id = ec.entity_id WHERE ec.classification_id = ' || quote_literal(classification_id) || ')'); END IF;
    IF (aspect IS NOT NULL) THEN filters = ARRAY_APPEND(filters, 'id IN (SELECT data_id FROM data_aspect WHERE label = ' || quote_literal(aspect) || ')'); END IF;

    RETURN QUERY EXECUTE '
        WITH counts AS (
            SELECT keyword, ct::INT
            FROM data_data
                CROSS JOIN LATERAL each(keywords) AS k(keyword, ct)
            WHERE ' || ARRAY_TO_STRING(filters, ' AND ') || '
        )
        SELECT keyword, SUM(ct)::INT keyword_count
        FROM counts
        GROUP BY keyword
        ORDER BY keyword_count DESC
        ' || CASE WHEN max_rows IS NOT NULL THEN 'LIMIT ' || max_rows ELSE '' END
    ;
END
$$;
