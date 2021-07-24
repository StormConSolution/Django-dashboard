
START TRANSACTION;

LOCK TABLE data_aspectlabel_source, data_entity_aspect_source, data_aspect, data_data, data_entity, data_entity_classifications, data_data_entities IN EXCLUSIVE MODE;

DROP VIEW IF EXISTS data_aspectlabel;
DROP TABLE IF EXISTS data_aspectlabel_temp;
DROP TABLE IF EXISTS data_aspectlabel_source;


CREATE TABLE data_aspectlabel AS (
    SELECT project_id, label, row_number() OVER (PARTITION BY project_id ORDER BY label)::SMALLINT id
    FROM (
        SELECT DISTINCT dd.project_id, da.label
        FROM data_aspect da
            JOIN data_data dd ON da.data_id = dd.id
    ) un
);

CREATE UNIQUE INDEX data_aspectlabel_un_project_id_label ON data_aspectlabel(project_id, label);
CREATE UNIQUE INDEX data_aspectlabel_un_project_id_id ON data_aspectlabel(project_id, id) INCLUDE (label);


create or replace function refresh_cached_label_data() returns void
	language plpgsql
as $$
DECLARE
    key TEXT = TO_CHAR(clock_timestamp(), 'YYYYMMDDHH24MISS');
    label_columns INT[];
    label_columns_cross TEXT;
BEGIN
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

    CREATE OR REPLACE VIEW data_aspectspresent AS SELECT * FROM data_aspectspresent_temp;

    DROP TABLE IF EXISTS data_aspectspresent_source;

    ALTER TABLE data_aspectspresent_temp RENAME TO data_aspectspresent_source;
END
$$;

create or replace function data_data_updated(_data_id INT) returns void
	language plpgsql
as $$
DECLARE
    _project_id INT = (SELECT project_id FROM data_data WHERE id = _data_id);
    new_label TEXT;
BEGIN
RAISE NOTICE '%', _data_id;
RAISE NOTICE '%', (SELECT STRING_AGG(label, ', ') FROM data_aspect WHERE data_id = _data_id);
    -- add missing aspectlabels
    FOR new_label IN
        SELECT DISTINCT label FROM data_aspect WHERE data_id = _data_id
        EXCEPT
        SELECT label FROM data_aspectlabel WHERE project_id = _project_id
    LOOP
        INSERT INTO data_aspectlabel(project_id, label, id)
            SELECT _project_id, new_label, (SELECT COALESCE(MAX(id), 0) + 1 FROM data_aspectlabel WHERE project_id = _project_id)
        ;
    END Loop;
END
$$;

CREATE OR REPLACE FUNCTION data_aspect_changed() RETURNS trigger AS $$
BEGIN

    IF (TG_OP = 'INSERT')
    THEN
        PERFORM data_data_updated(data_id)
        FROM (SELECT DISTINCT data_id FROM new_table) z;
    END IF;

    IF (TG_OP = 'UPDATE')
    THEN
        PERFORM data_data_updated(data_id)
        FROM (
            SELECT data_id FROM new_table
            UNION
            SELECT data_id FROM old_table
        ) z;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER data_aspect_inserted_tr
    AFTER INSERT ON data_aspect
    REFERENCING NEW TABLE AS new_table
    FOR EACH STATEMENT EXECUTE FUNCTION data_aspect_changed();

CREATE TRIGGER data_aspect_updated_tr
    AFTER UPDATE ON data_aspect
    REFERENCING OLD TABLE AS old_table NEW TABLE AS new_table
    FOR EACH STATEMENT EXECUTE FUNCTION data_aspect_changed();

/*
-- fixup all records, not normally required
do $$
DECLARE
    _id INT;
BEGIN
    FOR _id IN SELECT id FROM data_data
    LOOP
        PERFORM data_data_updated(_id);
    END LOOP;
END
$$;
*/



--ROLLBACK;
COMMIT;
