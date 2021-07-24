
START TRANSACTION;

LOCK TABLE data_aspect, data_aspectspresent_source, data_aspectlabel IN EXCLUSIVE MODE;

DROP VIEW IF EXISTS data_aspectspresent;
DROP TABLE IF EXISTS data_aspectspresent_temp;
DROP TABLE IF EXISTS data_aspectspresent_source;

DROP FUNCTION refresh_cached_label_data();

DO $$
DECLARE
    label_columns INT[];
    label_columns_cross TEXT;
BEGIN
    label_columns = ARRAY_AGG(DISTINCT id ORDER BY id) FROM data_aspectlabel;
    label_columns_cross = STRING_AGG(FORMAT('NULLIF(l.all_labels[%1$s] = ANY(agg.labels), FALSE) label_%1$s', id), ', ' ORDER BY id) FROM UNNEST(label_columns) AS id;

    EXECUTE 'CREATE TABLE data_aspectspresent AS (
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

    CREATE INDEX data_aspectspresent_ix_source_id ON data_aspectspresent(project_id, source_id);
    CREATE INDEX data_aspectspresent_ix_date_created ON data_aspectspresent(project_id, date_created);
    CREATE INDEX data_aspectspresent_ix_language ON data_aspectspresent(project_id, language);
    CREATE INDEX data_aspectspresent_ix_data_id ON data_aspectspresent(data_id);
END
$$;


create or replace function recreate_update_data_aspectspresent() returns void
	language plpgsql
as $REC$
DECLARE
    func TEXT;
    label_columns INT[];
    label_columns_cross TEXT;
    label_columns_list TEXT;
BEGIN
    label_columns = ARRAY_AGG(DISTINCT id ORDER BY id) FROM data_aspectlabel;
    label_columns_cross = STRING_AGG(FORMAT('NULLIF(l.all_labels[%1$s] = ANY(agg.labels), FALSE) label_%1$s', id), ', ' ORDER BY id) FROM UNNEST(label_columns) AS id;
    label_columns_list = STRING_AGG(FORMAT('label_%1$s', id), ', ' ORDER BY id) FROM UNNEST(label_columns) AS id;

    func = '
create or replace function update_data_aspectspresent(_data_id INT) returns void
	language plpgsql
as $$
BEGIN
    DELETE FROM data_aspectspresent WHERE data_id = _data_id;
    INSERT INTO data_aspectspresent(data_id, label, project_id, date_created, source_id, language, ' || label_columns_list || ')
            SELECT agg.data_id, agg.label,
                agg.project_id, agg.date_created, agg.source_id, agg.language,
                ' || label_columns_cross || '
            FROM (
                SELECT DISTINCT dd.project_id, dd.date_created, dd.source_id, dd.language,
                    da.data_id, da.label, ARRAY_AGG(da.label) OVER (PARTITION BY da.data_id) labels
                FROM data_aspect da
                    JOIN data_data dd ON da.data_id = dd.id
                WHERE dd.id = _data_id
            ) agg
                CROSS JOIN (
                    SELECT ARRAY_AGG(label ORDER BY id) all_labels
                    FROM data_aspectlabel
                    WHERE project_id = (SELECT project_id FROM data_data WHERE id = _data_id)
                ) l
    ;
END
$$;
';
    EXECUTE func;
END
$REC$;

SELECT recreate_update_data_aspectspresent();

create or replace function data_data_updated(_data_id INT) returns void
	language plpgsql
as $$
DECLARE
    _project_id INT = (SELECT project_id FROM data_data WHERE id = _data_id);
    new_label TEXT;
    new_label_id INT;
    has_label_column BOOLEAN;
BEGIN
    -- add missing aspectlabels
    FOR new_label IN
        SELECT DISTINCT label FROM data_aspect WHERE data_id = _data_id
        EXCEPT
        SELECT label FROM data_aspectlabel WHERE project_id = _project_id
    LOOP
        INSERT INTO data_aspectlabel(project_id, label, id)
            SELECT _project_id, new_label, (SELECT COALESCE(MAX(id), 0) + 1 FROM data_aspectlabel WHERE project_id = _project_id)
        RETURNING id
        INTO new_label_id
        ;

        has_label_column = COUNT(*) = 2
            FROM pg_attribute
            WHERE attrelid IN ('data_entity_aspect'::REGCLASS, 'data_aspectspresent'::REGCLASS) AND attname = 'label_' || new_label_id AND NOT attisdropped
        ;

        IF (has_label_column IS DISTINCT FROM TRUE)
        THEN
            EXECUTE 'ALTER TABLE data_entity_aspect ADD COLUMN IF NOT EXISTS label_' || new_label_id || ' BOOLEAN';
            PERFORM recreate_update_data_entity_aspect();

            EXECUTE 'ALTER TABLE data_aspectspresent ADD COLUMN IF NOT EXISTS label_' || new_label_id || ' BOOLEAN';
            PERFORM recreate_update_data_aspectspresent();
        END IF;
    END Loop;
END
$$;


COMMIT;
