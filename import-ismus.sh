source auth.env

PGPASSWORD="2pbPgdzH" psql -h mimisbrunnur.arnastofnun.is -d ismus -U traustid -t -A -c "SELECT json_agg(items) FROM (
	SELECT 'audio' AS record_type, a.id, (SELECT name FROM im_copy WHERE im_copy.id = a.copy_id) as title, a.contents AS text, 
	(SELECT jsonb_agg(informants) FROM (
		SELECT im_person.id, im_person.name, im_person.date_of_birth_iso date_of_birth, im_person.date_of_death_iso date_of_death,
		(SELECT jsonb_agg(home) FROM (
			SELECT im_location.id, im_location.name, jsonb_build_object('lat', im_location.lat::double precision, 'lon', im_location.lng::double precision) as location
			FROM im_link_person_location JOIN im_location ON im_location.id = im_link_person_location.location_id WHERE im_link_person_location.person_id = im_person.id
		) home) as home
		FROM im_link_audio_source JOIN im_person ON im_person.id = im_link_audio_source.person_id WHERE im_link_audio_source.audio_id = a.id
	) informants) as informants,
	(SELECT jsonb_agg(recorder) FROM (
		SELECT im_person.id, im_person.name, im_person.date_of_birth_iso date_of_birth, im_person.date_of_death_iso date_of_death,
		(SELECT jsonb_agg(home) FROM (
			SELECT im_location.id, im_location.name, jsonb_build_object('lat', im_location.lat::double precision, 'lon', im_location.lng::double precision) as location
			FROM im_link_person_location JOIN im_location ON im_location.id = im_link_person_location.location_id WHERE im_link_person_location.person_id = im_person.id
		) home) as home
		FROM im_link_audio_interviewer JOIN im_person ON im_person.id = im_link_audio_interviewer.person_id WHERE im_link_audio_interviewer.audio_id = a.id
	) recorder) as recorder,
	(SELECT jsonb_agg(keywords) FROM (
		SELECT im_keyword.id, im_keyword.name
		FROM im_link_audio_keyword JOIN im_keyword ON im_keyword.id = im_link_audio_keyword.keyword_id WHERE im_link_audio_keyword.audio_id = a.id
	) keywords) as keywords,
	(SELECT jsonb_agg(folklore_type) FROM (
		SELECT im_audio_type.id, im_audio_type.name
		FROM im_link_audio_type JOIN im_audio_type ON im_audio_type.id = im_link_audio_type.audio_type_id WHERE im_link_audio_type.audio_id = a.id
	) folklore_type) folklore_type,
	(SELECT jsonb_agg(location_mentions) FROM (
		SELECT im_location.id, im_location.name, jsonb_build_object('lat', im_location.lat::double precision, 'lon', im_location.lng::double precision) as location
		FROM im_link_audio_location_mentions JOIN im_location ON im_location.id = im_link_audio_location_mentions.location_id WHERE im_link_audio_location_mentions.audio_id = a.id
	) location_mentions) location_mentions
	FROM (SELECT * FROM im_audio LIMIT 100) a

	UNION

	SELECT 'printed' AS record_type, s.id, s.name as title, s.abstract AS text, 
	(SELECT jsonb_agg(informants) FROM (
		SELECT im_person.id, im_person.name, im_person.date_of_birth_iso date_of_birth, im_person.date_of_death_iso date_of_death,
		(SELECT jsonb_agg(home) FROM (
			SELECT im_location.id, im_location.name, jsonb_build_object('lat', im_location.lat::double precision, 'lon', im_location.lng::double precision) as location
			FROM im_link_person_location JOIN im_location ON im_location.id = im_link_person_location.location_id WHERE im_link_person_location.person_id = im_person.id
		) home) as home
		FROM sg_link_folklore_person JOIN im_person ON im_person.id = sg_link_folklore_person.person_id WHERE sg_link_folklore_person.folklore_id = s.id AND sg_link_folklore_person.type = 'heimildarmadur'
	) informants) as informants,
	(SELECT jsonb_agg(recorder) FROM (
		SELECT im_person.id, im_person.name, im_person.date_of_birth_iso date_of_birth, im_person.date_of_death_iso date_of_death,
		(SELECT jsonb_agg(home) FROM (
			SELECT im_location.id, im_location.name, jsonb_build_object('lat', im_location.lat::double precision, 'lon', im_location.lng::double precision) as location
			FROM im_link_person_location JOIN im_location ON im_location.id = im_link_person_location.location_id WHERE im_link_person_location.person_id = im_person.id
		) home) as home
		FROM sg_link_folklore_person JOIN im_person ON im_person.id = sg_link_folklore_person.person_id WHERE sg_link_folklore_person.folklore_id = s.id AND sg_link_folklore_person.type = 'skrasetjari'
	) recorder) as recorder,
	(SELECT jsonb_agg(keywords) FROM (
		SELECT im_keyword.id, im_keyword.name
		FROM sg_link_folklore_keywords JOIN im_keyword ON im_keyword.id = sg_link_folklore_keywords.keyword_id WHERE sg_link_folklore_keywords.folklore_id = s.id
	) keywords) as keywords,
	(SELECT jsonb_agg(folklore_type) FROM (
		SELECT im_audio_type.id, im_audio_type.name
		FROM sg_link_folklore_type JOIN im_audio_type ON im_audio_type.id = sg_link_folklore_type.audio_type_id WHERE sg_link_folklore_type.folklore_id = s.id
	) folklore_type) folklore_type,
	(SELECT jsonb_agg(location_mentions) FROM (
		SELECT im_location.id, im_location.name, jsonb_build_object('lat', im_location.lat::double precision, 'lon', im_location.lng::double precision) as location
		FROM sg_link_folklore_location JOIN im_location ON im_location.id = sg_link_folklore_location.location_id WHERE sg_link_folklore_location.folklore_id = s.id
	) location_mentions) location_mentions
	FROM (SELECT * FROM sg_folklore WHERE language = 'is' LIMIT 100) s
) items" > ismus.json

curl -XDELETE http://localhost:9201/ismus -u elastic:${ES_PASS}
node createIndex.js --url=elastic:${ES_PASS}@localhost:9201 --index=ismus --mappings="{
	\"properties\": {
		\"informants\": {
			\"properties\": {
				\"date_of_birth\": {
					\"type\": \"text\"
				},
				\"date_of_death\": {
					\"type\": \"text\"
				},
				\"home\": {
					\"properties\": {
						\"location\": {
							\"type\": \"geo_point\"
						}
					}
				}
			}
		},
		\"recorder\": {
			\"properties\": {
				\"date_of_birth\": {
					\"type\": \"text\"
				},
				\"date_of_death\": {
					\"type\": \"text\"
				},
				\"home\": {
					\"properties\": {
						\"location\": {
							\"type\": \"geo_point\"
						}
					}
				}
			}
		},
		\"location_mentions\": {
			\"properties\": {
				\"location\": {
					\"type\": \"geo_point\"
				}
			}
		}
	}
}"
node esImportJson.js --url http://elastic:${ES_PASS}@localhost:9201 --fileName ismus.json --indexName ismus
