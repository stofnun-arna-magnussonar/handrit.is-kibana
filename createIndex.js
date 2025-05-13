let elasticsearch = require('elasticsearch');

const argv = require('minimist')(process.argv.slice(2));

if (process.argv.length < 3) {
	console.log('node createIndex --url --index --mappings --settings');

	return;
}

let indexName = argv.index;

let client = new elasticsearch.Client({
	host: argv.url || 'localhost:9200',
});

let body = {};

if (argv.mappings) {
	console.log(argv.mappings)
	body.mappings = JSON.parse(argv.mappings);
}
if (argv.settings) {
	body.settings = JSON.parse(argv.settings);
}

client.indices.create({
	index: indexName,
	body: body
}, function(error, response) {
	if (error) {
		console.log(error);
	}
});
