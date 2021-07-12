CREATE EXTENSION IF NOT EXISTS btree_gin;



CREATE OR REPLACE FUNCTION refresh_cached_entity_aspect_data() RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    key TEXT = TO_CHAR(clock_timestamp(), 'YYYYMMDDHH24MISS');
    label_columns INT[];
    label_columns_cross TEXT;
BEGIN
    label_columns = ARRAY_AGG(DISTINCT id ORDER BY id) FROM data_aspectlabel;
    label_columns_cross = STRING_AGG(FORMAT('NULLIF(l.all_labels[%1$s] = ANY(ARRAY_AGG(DISTINCT a.label)), FALSE) label_%1$s', id), ', ' ORDER BY id) FROM UNNEST(label_columns) AS id;

    DROP TABLE IF EXISTS data_entity_aspect_temp;
    EXECUTE 'CREATE TABLE data_entity_aspect_temp AS (
        SELECT
            d.id AS data_id,
            ARRAY_AGG(DISTINCT ''c='' || ec.classification_id) || ARRAY_AGG(DISTINCT ''p='' || d.project_id) || ARRAY_AGG(DISTINCT ''l='' || d.language) || ARRAY_AGG(DISTINCT ''s='' || d.source_id) filters,
            ARRAY_AGG(DISTINCT dde.entity_id) entities,
            d.date_created,
            ' || label_columns_cross || '
        FROM data_data d
            JOIN data_data_entities dde ON d.id = dde.data_id
            JOIN data_entity_classifications ec ON dde.entity_id = ec.entity_id
            LEFT OUTER JOIN data_aspect a ON d.id = a.data_id
            JOIN (
                SELECT project_id, ARRAY_AGG(label ORDER BY id) all_labels
                FROM data_aspectlabel
                GROUP BY project_id
            ) l ON d.project_id = l.project_id
        GROUP BY d.id, l.all_labels
    )';

    EXECUTE 'CREATE INDEX data_entity_aspect_un_' || key || ' ON data_entity_aspect_temp USING GIN (filters)';

    DROP VIEW IF EXISTS data_entity_aspect;
    CREATE VIEW data_entity_aspect AS SELECT * FROM data_entity_aspect_temp;

    DROP TABLE IF EXISTS data_entity_aspect_source;

    ALTER TABLE data_entity_aspect_temp RENAME TO data_entity_aspect_source;
END
$$;


drop function if exists get_entity_aspect_counts(integer, integer, varchar, integer, text);
drop function if exists get_entity_aspect_counts(integer, integer, character varying[], integer[], text);

create function get_entity_aspect_counts(classification_id integer, project_id integer, languages character varying[] DEFAULT NULL::character varying[], source_ids integer[] DEFAULT NULL::integer[], sql_filter text DEFAULT NULL::text) returns TABLE(entity character varying, entity_count integer, aspect character varying, aspect_count integer)
	parallel safe
	language plpgsql
as $$
DECLARE
    label_columns_select TEXT;
    filters TEXT[] = ARRAY['c=' || classification_id, 'p=' || project_id];
    languages_filter TEXT[];
    sources_filter TEXT[];
BEGIN
    sql_filter = 'AND (' || COALESCE(sql_filter, 'TRUE') || ')';
    IF (languages IS NOT NULL)
    THEN
        languages_filter = ARRAY_AGG('l=' || unnest) FROM UNNEST(languages);
        sql_filter = sql_filter || ' AND filters && $2';
    END IF;
    IF (source_ids IS NOT NULL)
    THEN
        sources_filter = ARRAY_AGG('s=' || unnest) FROM UNNEST(source_ids);
        sql_filter = sql_filter || ' AND filters && $3';
    END IF;

    label_columns_select = STRING_AGG(FORMAT('%1$s::TEXT, SUM(label_%1$s::INT)', id), ', ' ORDER BY id) FROM data_aspectlabel l WHERE l.project_id = get_entity_aspect_counts.project_id;

    RETURN QUERY EXECUTE '
        WITH per_entity AS (
            SELECT *,
                UNNEST(entities) entity_id
            FROM data_entity_aspect
            WHERE filters @> $1
                ' || sql_filter || '
        ), counts AS (
            SELECT
                e.label entity,
                COUNT(DISTINCT pe.data_id)::INT entity_count,
                JSONB_BUILD_OBJECT(
                    ' || label_columns_select || '
                ) aspect_counts
            FROM per_entity pe
                JOIN data_entity e ON pe.entity_id = e.id
                JOIN data_entity_classifications ec ON pe.entity_id = ec.entity_id
            WHERE ec.classification_id = ' || classification_id || '
            GROUP BY e.label
        )

        SELECT c.entity, c.entity_count, l.label, NULLIF((lp.ct #> ''{}''), ''null''::JSONB)::INT
        FROM counts c
            CROSS JOIN LATERAL JSONB_EACH(c.aspect_counts) lp(id, ct)
            JOIN data_aspectlabel l ON l.project_id = ' || get_entity_aspect_counts.project_id || ' AND l.id = lp.id::INT
        WHERE NULLIF((lp.ct #> ''{}''), ''null''::JSONB) IS NOT NULL
    ' USING filters, languages_filter, sources_filter;
END
$$;


SELECT refresh_cached_entity_aspect_data()

/*

SELECT * FROM get_entity_aspect_counts(13, 3155) ORDER BY entity, aspect;
SELECT * FROM get_entity_aspect_counts(13, 3155, sql_filter := $SQL$date_created > '2020-01-01'$SQL$) ORDER BY entity, aspect;
SELECT * FROM get_entity_aspect_counts(13, 3155, languages := ARRAY['en'], source_ids := ARRAY[17], sql_filter := $SQL$date_created > '2019-01-01'$SQL$) ORDER BY entity, aspect;
SELECT * FROM get_entity_aspect_counts(13, 3155, languages := ARRAY['en', 'zh']) ORDER BY entity, aspect;

*/
