/*

SELECT refresh_cached_label_data()

*/

CREATE OR REPLACE FUNCTION refresh_cached_label_data() RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    key TEXT = TO_CHAR(clock_timestamp(), 'YYYYMMDDHH24MISS');
    label_columns INT[];
    label_columns_cross TEXT;
BEGIN
    DROP TABLE IF EXISTS data_aspectlabel_temp;
    CREATE TABLE data_aspectlabel_temp AS (
        SELECT project_id, label, row_number() OVER (PARTITION BY project_id ORDER BY label)::SMALLINT id
        FROM (
            SELECT DISTINCT dd.project_id, da.label
            FROM data_aspect da
                JOIN data_data dd ON da.data_id = dd.id
        ) un
    );

    EXECUTE 'CREATE UNIQUE INDEX data_aspectlabel_un_' || key || ' ON data_aspectlabel_temp(project_id, id) INCLUDE (label)';

    DROP TABLE IF EXISTS data_aspectlabel;
    CREATE TABLE data_aspectlabel AS SELECT * FROM data_aspectlabel_temp;

    DROP TABLE IF EXISTS data_aspectlabel_source;

    ALTER TABLE data_aspectlabel_temp RENAME TO data_aspectlabel_source;

    --

    label_columns = ARRAY_AGG(DISTINCT id ORDER BY id) FROM data_aspectlabel;
    label_columns_cross = STRING_AGG(FORMAT('NULLIF(l.all_labels[%1$s] = ANY(agg.labels), FALSE) label_%1$s', id), ', ' ORDER BY id) FROM UNNEST(label_columns) AS id;

    DROP TABLE IF EXISTS data_aspectspresent_temp;
    EXECUTE 'CREATE TABLE data_aspectspresent_temp AS (
            SELECT agg.data_id, agg.label,
                agg.project_id, agg.date_created, agg.source_id, agg.language,
                ' || label_columns_cross || '
            FROM (
                SELECT DISTINCT dd.project_id, dd.date_created, dd.source_id, dd.language,
                    da.data_id, da.label, ARRAY_AGG(da.label) OVER (PARTITION BY da.data_id) labels
                FROM data_aspect da
                    JOIN data_data dd ON da.data_id = dd.id
            ) agg
                JOIN (
                    SELECT project_id, ARRAY_AGG(label ORDER BY id) all_labels
                    FROM data_aspectlabel
                    GROUP BY project_id
                ) l ON agg.project_id = l.project_id
    )';

    EXECUTE 'CREATE INDEX data_aspectspresent_source_id_' || key || ' ON data_aspectspresent_temp(project_id, source_id)';
    EXECUTE 'CREATE INDEX data_aspectspresent_date_created_' || key || ' ON data_aspectspresent_temp(project_id, date_created)';
    EXECUTE 'CREATE INDEX data_aspectspresent_language_' || key || ' ON data_aspectspresent_temp(project_id, language)';

	DROP VIEW IF EXISTS data_aspectspresent;
    CREATE VIEW data_aspectspresent AS SELECT * FROM data_aspectspresent_temp;

    DROP TABLE IF EXISTS data_aspectspresent_source;

    ALTER TABLE data_aspectspresent_temp RENAME TO data_aspectspresent_source;
END
$$;

SELECT refresh_cached_label_data();

/*

SELECT * FROM get_aspect_label_percentages(3155) ORDER BY label1, label2;
SELECT * FROM get_aspect_label_percentages(3155, $SQL$date_created > '2020-01-01'$SQL$) ORDER BY label1, label2;
SELECT * FROM get_aspect_label_percentages(3171, $SQL$date_created > '2019-01-01' AND source_id = 1$SQL$) ORDER BY label1, label2;

*/
DROP FUNCTION IF EXISTS get_aspect_label_percentages;
CREATE OR REPLACE FUNCTION get_aspect_label_percentages(project_id INT, filter VARCHAR = NULL) RETURNS TABLE(label1 VARCHAR, label2 VARCHAR, percentage NUMERIC)
LANGUAGE plpgsql
PARALLEL SAFE
AS $$
DECLARE
    label_columns_select TEXT;
BEGIN
    label_columns_select = STRING_AGG(FORMAT('%1$s::TEXT, COALESCE(SUM(label_%1$s::INT)::NUMERIC / COUNT(*)::NUMERIC * 100, 0)', id), ', ' ORDER BY id) FROM data_aspectlabel l WHERE l.project_id = get_aspect_label_percentages.project_id;

    RETURN QUERY EXECUTE '
        WITH percentages AS (
            SELECT ap.label,
                COUNT(*) total_label_count,
                JSONB_BUILD_OBJECT(
                    ' || label_columns_select || '
                ) label_percs
            FROM data_aspectspresent ap
            WHERE project_id = ' || get_aspect_label_percentages.project_id::TEXT || '
                AND (' || COALESCE(filter, 'TRUE') || ')
            GROUP BY ap.label
        )

        SELECT p.label, l.label, ROUND((lp.perc #> ''{}'')::NUMERIC, 2)
        FROM percentages p
            CROSS JOIN LATERAL JSONB_EACH(p.label_percs) lp(id, perc)
            JOIN data_aspectlabel l ON l.project_id = ' || get_aspect_label_percentages.project_id::TEXT || ' AND l.id = lp.id::INT
    ';
END
$$;
