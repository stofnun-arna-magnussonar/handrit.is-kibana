source auth.env

#./getXmlFiles.sh
#sudo apt install git-restore-mtime
cd Manuscripts
#git restore-mtime
cd ..
python parse.py > manuscripts.json
curl -XDELETE http://localhost:9201/handrit -u elastic:${ES_PASS}
node createIndex.js --url=elastic:${ES_PASS}@localhost:9201 --index=handrit --mappings="{
	\"properties\": {
		\"modified\": {
			\"type\": \"date\",
			\"format\": \"yyyy-MM-dd HH:mm:ss||strict_date_optional_time ||epoch_millis\"
		},
		\"dateFrom\": {
			\"type\": \"date\"
		},
		\"dateTo\": {
			\"type\": \"date\"
		},
		\"acquisition\": {
			\"type\": \"date\"
		},
		\"history\": {
			\"properties\": {
				\"places\": {
					\"properties\": {
						\"location\": {
						\"type\": \"geo_point\"
						}
					}
				}
			}
		}
	}
}"
node esImportJson.js --url http://elastic:${ES_PASS}@localhost:9201 --fileName manuscripts.json --indexName handrit
