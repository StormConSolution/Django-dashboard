drop function get_keyword_counts;

-- select * from get_keyword_counts(3155, ARRAY['en', 'zh']);

create or replace function get_keyword_counts(project_id integer, languages character varying[] DEFAULT NULL, source_ids integer[] DEFAULT NULL, classification_id integer DEFAULT NULL::integer, aspect text DEFAULT NULL::text, sql_filter text DEFAULT NULL::text, max_rows integer DEFAULT NULL::integer) returns TABLE(keyword text, keyword_count integer)
	parallel safe
	language plpgsql
as $$
DECLARE
    filters TEXT[] = ARRAY['project_id = ' || project_id];
BEGIN
    IF (languages IS NOT NULL) THEN filters = ARRAY_APPEND(filters, 'language = ANY($1)'); END IF;
    IF (source_ids IS NOT NULL) THEN filters = ARRAY_APPEND(filters, 'source_id = ANY($2)'); END IF;
    IF (sql_filter IS NOT NULL) THEN filters = ARRAY_APPEND(filters, sql_filter); END IF;
    IF (classification_id IS NOT NULL) THEN filters = ARRAY_APPEND(filters, 'id IN (SELECT dde.data_id FROM data_data_entities dde JOIN data_entity_classifications ec ON dde.entity_id = ec.entity_id WHERE ec.classification_id = ' || quote_literal(classification_id) || ')'); END IF;
    IF (aspect IS NOT NULL) THEN filters = ARRAY_APPEND(filters, 'id IN (SELECT data_id FROM data_aspect WHERE label = ' || quote_literal(aspect) || ')'); END IF;

    RETURN QUERY EXECUTE '
        WITH counts AS (
            SELECT keyword, ct::INT
            FROM data_data
                CROSS JOIN LATERAL jsonb_each_text(keywords) AS k(keyword, ct)
            WHERE ' || ARRAY_TO_STRING(filters, ' AND ') || '
        )
        SELECT keyword, SUM(ct)::INT keyword_count
        FROM counts
        GROUP BY keyword
        ORDER BY keyword_count DESC
        ' || CASE WHEN max_rows IS NOT NULL THEN 'LIMIT ' || max_rows ELSE '' END
        USING languages, source_ids
    ;
END
$$;
