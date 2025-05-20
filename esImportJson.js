var request = require('request');
let fs = require('fs');
let _ = require('underscore');
let elasticsearch = require('elasticsearch');

let argv = require('minimist')(process.argv.slice(2));

if (process.argv.length < 3) {
	console.log('node esImportJson --url --fileName --indexName --idField --locationFields=[lat,lng]');

	return;
}

/*
GET /handrit/_count

DELETE handrit

PUT handrit
{
  "mappings": {
    "properties": {
      "dateFrom": {
        "type": "date"
      },
      "dateTo": {
        "type": "date"
      },
      "history": {
        "properties": {
          "places": {
            "properties": {
              "location": {
                "type": "geo_point"
              }
            }
          }
        }
      }
    }
  }
}

GET /handrit/_search
*/

let pageSize = argv.pageSize || 50;

let client = new elasticsearch.Client({
	host: argv.url || 'localhost:9200',
	log: 'trace'
});

fs.readFile(argv.fileName, function(error, data) {
	let json = JSON.parse(data);

	let chunkSize = 10;
	let arrayIndex = 0;
	let itemCounter = 0;

	let processChunk = function() {
		let bulkBody = [];

		console.log(arrayIndex)

		let chunk = json.slice(arrayIndex, arrayIndex+chunkSize);

		_.each(chunk, function(item, index) {
			itemCounter++;
			let docId = argv.idField && item[argv.idField] ? item[argv.idField] : itemCounter+1;

			bulkBody.push({
				create: {
					_index: argv.indexName,
					_id: docId
				}
			});

			if (argv.locationFields && argv.locationFields.split(',').length == 2) {
				let locationFields = argv.locationFields.split(',');

				if (!isNaN(item[locationFields[0]]) && !isNaN(item[locationFields[1]])) {
					item.location = {
						lat: item[locationFields[0]],
						lon: item[locationFields[1]]
					};

					delete item[locationFields[0]];
					delete item[locationFields[1]];
				}
			}

			bulkBody.push(item);

		});

		client.bulk({
			body: bulkBody
		}, function(error) {
			if (error) {
				console.log(error);
			}

			arrayIndex += chunkSize;

			if (json.length > arrayIndex) {
				setTimeout(function() {
					processChunk();
				}, 500);
			}
		});
	}

	processChunk();

});

return;
