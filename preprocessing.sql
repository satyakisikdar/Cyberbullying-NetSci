ATTACH '<path to DB>/ctsr.duckdb' AS ctsr (READ_ONLY);

ATTACH 'dbname=<DBNAME> user=<username> password= host=<host IP>' AS yoda_db (TYPE postgres);

CREATE TEMP TABLE majority_calculation AS
SELECT 
    comments.unit_id,
    anons.*,
    CASE 
      WHEN anons.bullying_severity = 'mild'
      THEN 1.0
      WHEN anons.bullying_severity = 'moderate'
      THEN 2.0
      WHEN anons.bullying_severity = 'severe'
      THEN 3.0
    ELSE 1.0 END AS severity,
    CASE 
      WHEN anons.bullying_role = 'non_aggressive_defender'
      THEN anons.bullying_role || ':' || anons.defense_type
      ELSE anons.bullying_role END AS role,
    CASE
      WHEN role = 'aggressive_defender'
      THEN 1
      WHEN role = 'non_aggressive_defender:support_of_the_victim'
      THEN 2
      WHEN role = 'non_aggressive_defender:direct_to_the_bully'
      THEN 3
      WHEN role = 'aggressive_victim'
      THEN 4
      WHEN role = 'non_aggressive_victim'
      THEN 5
      WHEN role = 'bully_assistant'
      THEN 6
      WHEN role = 'bully'
      THEN 7
    ELSE 8 END AS role_over_rule,
    sum(anons.is_cyberbullying::DOUBLE) OVER (PARTITION BY anons.comment_id) AS bullying_votes,
    (count(*) OVER (PARTITION BY anons.comment_id))::DOUBLE AS number_annotators,
    ceil(number_annotators / 2.0) AS majority_vote,
    (bullying_votes >= majority_vote)::BOOL AS is_majority_cyberbullying
FROM ctsr.mturk.comment_annotations AS anons
INNER JOIN ctsr.instagram.comments
  ON anons.comment_id = comments.comment_id
WHERE anons.bullying_role IS NOT NULL
  AND comments.comment_content <> ''
QUALIFY anons.is_cyberbullying = is_majority_cyberbullying;

CREATE TEMP TABLE roles_majority AS
SELECT
  comment_id,
  is_cyberbullying,
  role,
  role_over_rule,
  count(*) AS role_votes,
  dense_rank() OVER (PARTITION BY comment_id ORDER BY role_votes DESC, role_over_rule) AS roles_preferenced
FROM majority_calculation 
GROUP BY comment_id, is_cyberbullying, role, role_over_rule
QUALIFY roles_preferenced = 1;


SELECT *
FROM roles_majority
QUALIFY count(*) OVER (PARTITION BY comment_id) > 1;


SELECT *
FROM majority_calculation
QUALIFY count(*) OVER (PARTITION BY comment_id, assignment_id) > 1;


CREATE TEMP TABLE majority_topics AS
SELECT majority.unit_id, topics.*
FROM ctsr.mturk.comment_topics AS topics
INNER JOIN majority_calculation AS majority
  ON majority.comment_id = topics.comment_id
  AND majority.assignment_id = topics.assignment_id;


CREATE TEMP TABLE comment_topic_vectors AS
WITH pivoted_topics AS (
  PIVOT majority_topics
  ON topic
  USING count(*)
  GROUP BY comment_id
)
SELECT 
  comment_id,
  array_value(
    disability,
    gender,
    intellectual,
    physical,
    political,
    race,
    religious,
    sexual,
    social_status,
    none
  ) AS topic_vector
FROM pivoted_topics;


CREATE TEMP TABLE severity AS
SELECT comment_id, avg(severity) AS severity
FROM majority_calculation
GROUP BY comment_id;

CREATE OR REPLACE TABLE yoda_db.cyberbullying_motifs.comments AS
SELECT comments.*, 
  roles_majority.is_cyberbullying,
  roles_majority.role,
  severity.severity,
  comment_topic_vectors.topic_vector
FROM ctsr.instagram.comments
INNER JOIN ctsr.instagram.sessions
  ON comments.unit_id = sessions.unit_id
INNER JOIN roles_majority
  ON comments.comment_id = roles_majority.comment_id
INNER JOIN severity
  ON comments.comment_id = severity.comment_id
INNER JOIN comment_topic_vectors
  ON comments.comment_id = comment_topic_vectors.comment_id
WHERE comments.comment_content <> ''
  AND sessions.number_of_bully_annotations >= 3;

CREATE TEMP TABLE remapping_main_victim AS
WITH merging_main_victim_labels AS (
  SELECT
    unit_id, 
    CASE 
        WHEN session_main_victim IN ('people_in_picture', 'user')
        THEN 'OP'
        WHEN session_main_victim = 'participants'
        THEN 'Participants'
        ELSE 'NA'
    END AS main_victim,
    CASE 
      WHEN main_victim = 'OP'
      THEN 1
      WHEN main_victim = 'Participants'
      THEN 2
    ELSE 3 END AS victim_over_rule
  FROM ctsr.mturk.assignments
)
SELECT unit_id, main_victim, victim_over_rule, count(*) AS victim_count
FROM merging_main_victim_labels 
GROUP BY unit_id, main_victim, victim_over_rule
QUALIFY dense_rank() OVER (PARTITION BY unit_id ORDER BY victim_count DESC, victim_over_rule) = 1;


SELECT *
FROM remapping_main_victim
QUALIFY count(*) OVER (PARTITION BY unit_id) > 1;


CREATE TEMP TABLE session_topic_vectors AS
WITH pivoted_topics AS (
  PIVOT majority_topics
  ON topic
  USING count(*)
  GROUP BY unit_id
)
SELECT
  unit_id,
  array_value(
    disability,
    gender,
    intellectual,
    physical,
    political,
    race,
    religious,
    sexual,
    social_status,
    none
  ) AS topic_vector
FROM pivoted_topics;


CREATE OR REPLACE TABLE yoda_db.cyberbullying_motifs.sessions AS
SELECT 
  remapping_main_victim.main_victim, 
  sessions.*, 
  session_topic_vectors.topic_vector
FROM ctsr.instagram.sessions
INNER JOIN session_topic_vectors
  ON sessions.unit_id = session_topic_vectors.unit_id
INNER JOIN remapping_main_victim
  ON sessions.unit_id = remapping_main_victim.unit_id
WHERE sessions.number_of_bully_annotations >= 3;


CREATE OR REPLACE TABLE yoda_db.cyberbullying_motifs.session_digraphs (
    session_graph_id UUID DEFAULT (gen_random_uuid()),
    unit_id INTEGER NOT NULL,

    serialized_graph BLOB NOT NULL,
    is_true_graph BOOL NOT NULL,

    num_nodes INTEGER NOT NULL DEFAULT 0,
    num_edges INTEGER NOT NULL DEFAULT 0,
    num_bullies INTEGER NOT NULL DEFAULT 0,

    num_victims INTEGER NOT NULL DEFAULT 0,
    num_non_agg_victims INTEGER NOT NULL DEFAULT 0,
    num_agg_victims INTEGER NOT NULL DEFAULT 0,

    num_defenders INTEGER NOT NULL DEFAULT 0,
    num_non_agg_defenders INTEGER NOT NULL DEFAULT 0,
    num_agg_defenders INTEGER NOT NULL DEFAULT 0,

    main_victim_in_deg DOUBLE NOT NULL DEFAULT 0,
    main_victim_weighted_in_deg DOUBLE NOT NULL DEFAULT 0,

    main_victim_out_deg DOUBLE NOT NULL DEFAULT 0,
    main_victim_weighted_out_deg DOUBLE NOT NULL DEFAULT 0,

    victim_avg_in_deg DOUBLE NOT NULL DEFAULT 0,
    victim_avg_weighted_in_deg DOUBLE NOT NULL DEFAULT 0,

    victim_avg_out_deg DOUBLE NOT NULL DEFAULT 0,
    victim_avg_weighted_out_deg DOUBLE NOT NULL DEFAULT 0,

    victim_score DOUBLE NOT NULL DEFAULT 0,
    victim_score_weighted DOUBLE NOT NULL DEFAULT 0,

    bully_avg_in_deg DOUBLE NOT NULL DEFAULT 0,
    bully_avg_weighted_in_deg DOUBLE NOT NULL DEFAULT 0,

    bully_avg_out_deg DOUBLE NOT NULL DEFAULT 0,
    bully_avg_weighted_out_deg DOUBLE NOT NULL DEFAULT 0,

    bully_score DOUBLE NOT NULL DEFAULT 0,
    bully_score_weighted DOUBLE NOT NULL DEFAULT 0,

    main_victim_score DOUBLE NOT NULL DEFAULT 0,
    main_victim_score_weighted DOUBLE NOT NULL DEFAULT 0,
);

CREATE OR REPLACE TABLE yoda_db.cyberbullying_motifs.plain_motifs (
  plain_motif_id UUID NOT NULL,
  unit_id BIGINT NOT NULL,
  size INTEGER NOT NULL,
  iso_class INTEGER NOT NULL,
  motif_hash TEXT NOT NULL,
  serialized_motif BLOB NOT NULL
);


CREATE OR REPLACE TABLE yoda_db.cyberbullying_motifs.flavored_motifs (
  flavored_motif_id UUID NOT NULL,
  plain_motif_id UUID NOT NULL,
  node_flavor TEXT NOT NULL,
  edge_flavor TEXT NOT NULL,
  motif_hash TEXT NOT NULL,
  serialized_motif BLOB NOT NULL
);
