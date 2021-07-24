START TRANSACTION;

LOCK TABLE data_data, data_data_entities, data_entity_classifications, data_entity_aspect_source IN EXCLUSIVE MODE;

DROP FUNCTION refresh_cached_entity_aspect_data();

DROP VIEW IF EXISTS data_entity_aspect;
DROP TABLE IF EXISTS data_entity_aspect_source;
DROP TABLE IF EXISTS data_entity_aspect_temp;

DO $$
DECLARE
    label_columns INT[];
    label_columns_cross TEXT;
BEGIN
    label_columns = ARRAY_AGG(DISTINCT id ORDER BY id) FROM data_aspectlabel;
    label_columns_cross = STRING_AGG(FORMAT('NULLIF(l.all_labels[%1$s] = ANY(ARRAY_AGG(DISTINCT a.label)), FALSE) label_%1$s', id), ', ' ORDER BY id) FROM UNNEST(label_columns) AS id;

    EXECUTE 'CREATE TABLE data_entity_aspect AS (
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
END
$$;

create or replace function recreate_update_data_entity_aspect() returns void
	language plpgsql
as $REC$
DECLARE
    func TEXT;
    label_columns INT[];
    label_columns_cross TEXT;
    label_columns_list TEXT;

BEGIN
    label_columns = ARRAY_AGG(DISTINCT id ORDER BY id) FROM data_aspectlabel;
    label_columns_cross = STRING_AGG(FORMAT('NULLIF(l.all_labels[%1$s] = ANY(ARRAY_AGG(DISTINCT a.label)), FALSE) label_%1$s', id), ', ' ORDER BY id) FROM UNNEST(label_columns) AS id;
    label_columns_list = STRING_AGG(FORMAT('label_%1$s', id), ', ' ORDER BY id) FROM UNNEST(label_columns) AS id;

    func = '
create or replace function update_data_entity_aspect(_data_id INT) returns void
	language plpgsql
as $$
BEGIN
    DELETE FROM data_entity_aspect WHERE data_id = _data_id;
    INSERT INTO data_entity_aspect(data_id, filters, entities, date_created, ' || label_columns_list || ')
        SELECT
            d.id,
            ARRAY_AGG(DISTINCT ''c='' || ec.classification_id) || ARRAY_AGG(DISTINCT ''p='' || d.project_id) || ARRAY_AGG(DISTINCT ''l='' || d.language) || ARRAY_AGG(DISTINCT ''s='' || d.source_id) filters,
            ARRAY_AGG(DISTINCT dde.entity_id) entities,
            d.date_created,
            ' || label_columns_cross || '
        FROM data_data d
            CROSS JOIN LATERAL (
                SELECT ARRAY_AGG(label ORDER BY id) all_labels
                FROM data_aspectlabel
                WHERE project_id = d.project_id
            ) l
            JOIN data_data_entities dde ON d.id = dde.data_id
            JOIN data_entity_classifications ec ON dde.entity_id = ec.entity_id
            LEFT OUTER JOIN data_aspect a ON d.id = a.data_id
        WHERE d.id = _data_id
        GROUP BY d.id, l.all_labels
    ;
END
$$;
';
    EXECUTE func;
END
$REC$;

SELECT recreate_update_data_entity_aspect();

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

        has_label_column = TRUE
            FROM pg_attribute
            WHERE attrelid = 'data_entity_aspect'::REGCLASS AND attname = 'label_' || new_label_id AND NOT attisdropped
        ;

        IF (has_label_column IS DISTINCT FROM TRUE)
        THEN
            EXECUTE 'ALTER TABLE data_entity_aspect ADD COLUMN IF NOT EXISTS label_' || new_label_id || ' BOOLEAN';

            PERFORM recreate_update_data_entity_aspect();
        END IF;
    END Loop;
END
$$;


ALTER TABLE data_entity_aspect
  ADD PRIMARY KEY (data_id);

CREATE INDEX data_entity_aspect_ix_filters ON data_entity_aspect USING GIN (filters);

COMMIT;

/*
SELECT update_data_entity_aspect(data_id);
*/
