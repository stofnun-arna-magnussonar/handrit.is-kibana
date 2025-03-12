#./getXmlFiles.sh
#sudo apt install git-restore-mtime
cd Manuscripts
#git restore-mtime
cd ..
python parse.py > manuscripts.json
curl -XDELETE http://localhost:9200/handrit
node createIndex.js --url=localhost:9200 --index=handrit --mappings="{
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
node esImportJson.js --url http://localhost:9200 --fileName manuscripts.json --indexName handrit